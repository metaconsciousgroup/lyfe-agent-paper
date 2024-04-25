"""Sense functions of the agent."""
import datetime
from lyfe_agent.base import BaseState, BaseInteraction
from lyfe_agent.brain_utils import RecentInputs
from lyfe_agent.states.simple_states import describe_location, Location


def process_time(self, observations, sense_natural_language):
    new_event_time_based = False
    # self.agent.current_time = observations.get("time", self.agent.current_time)
    if observations.get("time") is not None:
        self.time.update(observations.get("time"))
    sense_natural_language["time"] = observations["time"]

    if observations.get("time") == self.schedule.current_goal_time:
        self.current_option.update(
            option_name="cognitive_controller", option_goal=self.schedule.current_goal
        )
        new_event_time_based = True

    if int(observations["time"].split(":")[1]) == 0 and (
        observations["time"] not in self.recent_time_input
    ):
        # # TODO: comment this out if you don't want time-based location awareness
        # sense_natural_language["choose_destination"] = (
        #     "I am "
        #     + describe_location(self.agent.location)
        #     + " at "
        #     + observations["time"]
        # )
        pass
    self.recent_time_input.add_content(observations["time"])
    return new_event_time_based


def process_arrival(self, observations, sense_natural_language):
    if observations.get("move_ended", None):
        # self.agent.location = Location(True, observations.get("move_ended", None))
        self.location.update(True, observations.get("move_ended", None))
        sense_natural_language["choose_destination"] = describe_location(
            # self.agent.location
            self.location
        )
        return True
    return False


def process_communication(self, observations, sense_natural_language):
    new_event = False
    for key in ["message", "talk"]:
        obs_value = observations.get(key)
        if obs_value is not None and obs_value not in self.recent_event_input:
            sense_natural_language[key] = obs_value
            self.recent_event_input.add_content(obs_value)
            new_event = True
            # if key == "talk" and new_event:
            #     agent._was_talked_to = True
    return new_event


def process_vision(self, observations, sense_natural_language):
    if (
        observations.get("visible_creatures") is not None
        and observations["visible_creatures"] not in self.recent_vision_input
    ):
        agent_names = observations["visible_creatures"]

        if len(agent_names) > 0:
            creatures_list = sorted(agent_names)
            creatures_text = ", ".join(creatures_list)
            vision_text = f"I see {creatures_text}".strip()
            sense_natural_language["vision"] = vision_text
        self.recent_vision_input.add_content(observations["visible_creatures"])
    return False


def process_inner_observation(self, inner_observation, sense_natural_language):
    if inner_observation is not None:
        sense_natural_language["inner_status"] = inner_observation
        return True
    return False


class SimpleState(BaseState):
    def __init__(self, data=None):
        self._data = "" if data is None else data  # Note the underscore prefix

    @property
    def data(self):
        return str(self._data)

    def update(self, value):
        self._data = value


class CurrentOption(BaseState):
    def __init__(self, option_name, option_goal, action=None):
        self.option_name = option_name
        self.option_goal = option_goal

    def update(self, option_name, option_goal=None):
        self.option_name = option_name
        if option_goal:
            self.option_goal = option_goal

    @property
    def data(self):
        return {"option_name": self.option_name, "option_goal": self.option_goal}

    def is_same(self, action):
        for key in self.data:
            if self.data[key] != action.data[key]:
                return False
        return True


# TODO: make target not None
class ScheduleSenseInteraction(BaseInteraction):
    # def __init__(self, agent, sources, targets):
    def __init__(self, sources, targets):
        super().__init__(sources, targets)
        # self.agent = agent
        self.recent_vision_input = RecentInputs()
        self.recent_time_input = RecentInputs()
        self.recent_event_input = RecentInputs(max_size=100)

        # will want this to be a state or pushed to logic outside of agent
        self.location = sources["location"]
        self.time = sources["time"]
        self.action = sources["action"]
        self.schedule = sources["schedule"]
        self.current_option = sources["current_option"]

    def execute(self, observations):
        """
        :return: An input_to_state that consists of
        - a natural language summary of the observation
        - a boolean indicating whether a new event has occurred
        """
        sense_natural_language = {}
        new_event = any(
            [
                process_time(self, observations, sense_natural_language),
                process_arrival(self, observations, sense_natural_language),
                process_communication(self, observations, sense_natural_language),
                process_vision(self, observations, sense_natural_language),
                process_inner_observation(self, None, sense_natural_language),
            ]
        )
        # sense_natural_language = "\n".join(list(sense_natural_language.values()))

        return new_event, sense_natural_language
