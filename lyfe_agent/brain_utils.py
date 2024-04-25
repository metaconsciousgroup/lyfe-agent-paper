from collections import deque
import numpy as np
import time
from datetime import datetime
from omegaconf import DictConfig

from lyfe_agent.utils.config_utils import process_config_for_instantiate
from hydra.utils import instantiate

def create_interaction(self, interaction_name, interaction_cfg, nonce):
    cfg, args_dict = process_config_for_instantiate(
        interaction_cfg, ["sources", "targets"]
    )
    kwargs = {
        "sources": {arg: getattr(self, arg, None) for arg in args_dict["sources"]},
        "targets": [getattr(self, arg, None) for arg in args_dict["targets"]],
        "nonce": nonce,
    }
    return instantiate(cfg)(**kwargs)


def create_state(self, state_name, state_cfg):
    cfg, args = process_config_for_instantiate(state_cfg, ["args"])
    # additional arguments for partially instantiated class
    kwargs = {arg: getattr(self, arg) for arg in args["args"]}
    return instantiate(cfg)(**kwargs)


def calculate_lifespan(
    tokens, reading_speed=3.0, decision_requester_step=5, frame_rate=30, magnifier=1.2
):
    """Calculate the time for a certain action to be completed
    Return:
        the number that update() should be called to finish the action
    """
    # The update() is called once a whole period
    whole_period = 1.0 / frame_rate * decision_requester_step
    return tokens / (reading_speed * whole_period * magnifier)


class RecentInputs:
    """Check if an input is in recent input.

    This essentially implements a form of slow-term adaptation.

    Args:
        max_size: max size to keep recent memory
            because input is added every call ~6Hz, the max time a memory is kept is roughly max_size/6, so 10s
    """

    def __init__(self, max_size=60):
        self.content_history = deque(maxlen=max_size)
        self.content_count = {}

    def add_content(self, new_input):
        if len(self.content_history) == self.content_history.maxlen:
            oldest_input = self.content_history.popleft()
            self.content_count[oldest_input] -= 1
            if self.content_count[oldest_input] == 0:
                del self.content_count[oldest_input]

        self.content_history.append(new_input)
        if new_input in self.content_count:
            self.content_count[new_input] += 1
        else:
            self.content_count[new_input] = 1

    def __contains__(self, new_input):
        return new_input in self.content_count

    @property
    def recently_seen(self):
        return list(self.content_count.keys())


class InnerStatus:
    """
    Record the inner status for the agent
    """

    def __init__(
        self, brain_cfg, energy_per_token=0.01
    ):
        """
        Initialize the status of the agent
        """
        self._status = {}
        self.replenish_value = {}
        self.threshold = {}

        for key, val in brain_cfg["inner_status"].items():
            if isinstance(val, DictConfig):  # check if the value is a dictionary
                self._status[key] = val["initial_value"]
                self.replenish_value[key] = val["replenish_value"]
                self.threshold[key] = val["threshold"]
            elif key == "suspended_time":  # Backward compatibility
                self.suspended_time = val
                self.default_suspended_time = val
            elif key == "magnifier":  # check if the key is 'magnifier'
                self.magnifier = val

        self.energy_per_token = energy_per_token
        self.status_info = ""

        self.token_monitor = TokenMonitor()
        self.individual_limit = 90000.0

    def __getattr__(self, attr):
        """
        Get the status of the agent
        """
        if attr in self.__dict__.get("status", {}):
            return self._status[attr]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{attr}'"
        )

    def __setattr__(self, attr, value):
        """
        Set the status of the agent
        """
        if attr == "status" or attr not in self.__dict__.get("status", {}):
            super().__setattr__(attr, value)
        else:
            self._status[attr] = value

    def add_status(self, status, value):
        """
        Add a new status to the agent
        """
        self._status[status] = value

    def update(self):
        """
        Update the status of the agent
        Called in each iteration
        """
        self.token_monitor.update()

        for key in self._status.keys():
            self._status[key] = min(100, self._status[key] + self.replenish_value[key])

        if (
            self.individual_limit
            and self.token_monitor.total_tokens_per_minute > self.individual_limit
        ):
            self.suspended_time = (
                self.default_suspended_time * self.magnifier
                - self._status["energy"] / 10.0
            )
        else:
            self.suspended_time = (
                self.default_suspended_time - self._status["energy"] / 10.0
            )

    def reward(self, status, value):
        """
        Update the status of the agent by reward
        The reward value should be generated by the RewardModel
        Called in slow_forward
        """
        self._status[status] = min(100, self._status[status] + value)

    def consume_tokens(self, status, cb):
        """
        Consume the status of the agent and update token monitor
        """
        assert status in ["energy", "hunger", "illness"], "Status not supported"
        self.token_monitor.add(
            cb.total_tokens, cb.prompt_tokens, cb.completion_tokens, cb.total_cost
        )
        status, delta_value = self.consume(status, total_token=cb.total_tokens)
        return status, delta_value

    def consume(self, status, value=0, total_token=0):
        """
        Consume the status of the agent
        Called in fast_forward and slow_forward
        """
        reserved_value = self._status[status]
        if value:
            change = value
        elif total_token:
            change = total_token * self.energy_per_token

        self._status[status] = max(0, self._status[status] - change)
        delta_value = change if change < reserved_value else reserved_value
        return status, delta_value

    def _detect_status(self):
        """
        Check the status of the agent.
        """
        warning_status = []
        for key, value in self._status.items():
            if value >= self.threshold[key]:
                self.status_info = key
                break
            else:
                self.status_info = None
        if self.status_info is not None:
            self.status_info = f"[WARNING] {self.status_info} is low."
        else:
            self.status_info = "My status is good."

    @property
    def info(self):
        """
        Return the status of the agent
        """
        output = {}
        for key in self._status.keys():
            output[key] = round(self._status[key], 3)
        output["suspended_time"] = round(self.suspended_time, 3)
        output["energy_per_token"] = round(self.energy_per_token, 3)
        return output


class RewardModel:
    """
    Create a reward model for the agent
    This model can arbitrarily be used to get the most rewarding action
    """

    def __init__(self, agent, model_type="ArgMaxModel", model=None, magnifier=100):
        self.agent = agent
        self.reward_method = model_type
        # if we want to use a pre-trained model, we can load it here
        model_dict = {"glove": None, "openai": None, "none": None}
        self.embedding_model_type = model
        self.embedding_model = model_dict[model] if model is not None else None
        # self.magnifier is used to magnify the reward from [0,1] to [0, magnifier]
        self.magnifier = magnifier

    def reward_func(self, status, delta, action=None):
        """
        Get the reward of the action
        """
        reward = (
            self.parametric_sigmoid(
                delta * 1.0 / self.magnifier, a=20, b=0.2, L=0.02, U=0.4
            )
            * self.magnifier
        )
        return status, reward

    def parametric_sigmoid(self, x, a, b, L=0, U=1):
        """
        Parametric sigmoid function.

        Parameters:
        - x: Input for the sigmoid function.
        - a: Steepness parameter. Higher values make the transition steeper.
        - b: Position parameter. This shifts the point where the output is 0.5 along the x-axis.
        - L: Lower bound of the function.
        - U: Upper bound of the function.
        """
        return L + (U - L) / (1 + np.exp(-a * (x - b)))

    def preferred_item(self, domain=None, observation=None):
        """
        Get the action based on the model type
        domain: domain of the action (e.g. food, utils)
        observation: observation that is used in model-free RL, but in Agent, we can always get access to the observation(i.e. the bag and preference)
        """
        if self.reward_method == "ArgMaxModel":
            return self._get_arg_max_action(domain, observation)
        elif self.reward_method == "NeuralNetworkModel":
            return self._get_neural_network_action(domain, observation)
        elif self.reward_method == "Transformer":
            return self._get_transformer_action(domain, observation)
        else:
            raise ValueError(f"Unknown model type: {self.reward_method}")

    def add_knowledge(self, item):
        if self.embedding_model_type is None:
            return np.zeros(1)
        elif self.embedding_model_type == "glove":
            # TODO: implement glove embedding
            return None
        elif self.embedding_model_type == "openai":
            # TODO: implement openai embedding
            return None
        return None

    def _get_arg_max_action(self, domain=None, observation=None):
        """
        Search for the highest reward action in the action space.
        Return the item name with the highest preference, or None if no item is available.
        """
        assert domain in ["food", "utils"], "Domain not supported"

        # Sort items by their preference scores in descending order
        sorted_items = sorted(
            self.agent.preference_knowledge[domain].items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # Check if any of the sorted items exists in the bag
        for item, _ in sorted_items:
            if self.agent.bag_knowledge[domain].get(item, 0) > 0:
                return item

        # If none of the items exist in the bag, return None
        return None

    def _get_neural_network_action(self, domain=None, observation=None):
        # TODO: implement advanced reward model
        print("neural network model is not implemented yet")
        return None

    def _get_transformer_action(self, domain=None, observation=None):
        # TODO: implement advanced reward model
        print("transformer model is not implemented yet")
        return None


class AgentMonitor:
    """
    A class used to monitor the agent's status and token usage over time.
    In future,
    """

    def __init__(self, max_size=10_000):
        """Constructor method
        Initialize a deque object with a fixed maximum length to keep track of
        the agent's status and token usage within the past 60 seconds.
        """
        self.max_size = max_size
        # Deque to keep track of the agent's status and token usage over time.
        self.history = deque(maxlen=max_size)
        # Timestamps corresponding to each update in history.
        self.timestamps = deque(maxlen=max_size)

    def update(self, inworld_time, inner_status: InnerStatus):
        """Method to add the latest agent's status and token usage to history.

        Args:
        token_monitor (TokenMonitor): An instance of the TokenMonitor class.
        inner_status (InnerStatus): An instance of the InnerStatus class.
        """
        current_time = datetime.now()
        while (
            self.timestamps
            and (current_time - self.timestamps[0]).total_seconds() > self.max_size
        ):
            self.history.popleft()
            self.timestamps.popleft()

        # Add the latest inner_status and token usage to the history.
        self.history.append(
            {
                "token_info": inner_status.token_monitor.info,
                "status_info": inner_status.info,
                "inworld_time": inworld_time,
            }
        )
        self.timestamps.append(current_time)

    @property
    def info(self):
        """Property to get all metrics as a dictionary for easy access and interpretation."""
        return list(self.history)

    @property
    def latest_info(self):
        """Property to get the most recent metrics as a dictionary for easy access and interpretation."""
        return self.history[-1] if self.history else None


class TokenMonitor:
    """
    A class used to monitor the number of tokens generated by the model and their associated cost
    within a certain period (in this case, the last 60 seconds).
    """

    def __init__(self, max_size=60):
        """Constructor method
        Initialize several deque objects with a fixed maximum length to keep track of
        different metrics within the past 60 seconds.
        """
        self.initial_time = datetime.now()
        self.max_size = max_size
        # Deques as before
        self.total_tokens = deque(maxlen=max_size)
        self.prompt_tokens = deque(maxlen=max_size)
        self.completion_tokens = deque(maxlen=max_size)
        self.total_cost = deque(maxlen=max_size)
        self.timestamps = deque(maxlen=max_size)
        # Dictionary to store tokens for each prompt with timestamp
        self.cumulative_tracker = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "simulation_run_time_seconds": (
                datetime.now() - self.initial_time
            ).total_seconds(),
        }

    def add(self, all_tokens, prompt_tokens, completion_tokens, total_cost):
        """Method to add the count of new tokens and their cost to the relevant deques."""

        current_time = time.time()

        # Add new tokens, their costs, and the current timestamp to the respective deques.
        self.total_tokens.append(all_tokens)
        self.prompt_tokens.append(prompt_tokens)
        self.completion_tokens.append(completion_tokens)
        self.total_cost.append(total_cost)
        self.timestamps.append(current_time)

        # Add prompt token details to the dictionary
        self.cumulative_tracker["prompt_tokens"] += prompt_tokens
        self.cumulative_tracker["completion_tokens"] += completion_tokens
        self.cumulative_tracker["total_cost"] += total_cost
        self.cumulative_tracker["total_tokens"] += all_tokens
        self.cumulative_tracker["simulation_run_time_seconds"] = (
            datetime.now() - self.initial_time
        ).total_seconds()

    def update(self):
        current_time = time.time()
        # Remove tokens and their corresponding costs that were recorded more than 60 seconds ago.
        # The prompt_tokens_details will not be affected here.
        while self.timestamps and current_time - self.timestamps[0] > self.max_size:
            self.total_tokens.popleft()
            self.prompt_tokens.popleft()
            self.completion_tokens.popleft()
            self.total_cost.popleft()
            self.timestamps.popleft()

    @property
    def total_tokens_per_minute(self):
        """Property to get the total number of tokens generated per minute."""
        return sum(self.total_tokens)

    @property
    def prompt_tokens_per_minute(self):
        """Property to get the number of tokens used for prompts per minute."""
        return sum(self.prompt_tokens)

    @property
    def completion_tokens_per_minute(self):
        """Property to get the number of tokens used for completions per minute."""
        return sum(self.completion_tokens)

    @property
    def total_cost_per_minute(self):
        """Property to get the total cost of tokens per minute."""
        return sum(self.total_cost)

    @property
    def prompts_info(self):
        """Property to get token details for each prompt with its timestamp."""
        return self.prompt_tokens_details

    @property
    def info(self):
        """Property to get all metrics as a dictionary for easy access and interpretation."""
        return self.cumulative_tracker
