import logging
from typing import Dict, List
from collections import defaultdict
from concurrent.futures import Executor

from lyfe_agent.interactions.option_executor import BaseOptionExecutor
from lyfe_agent.memory.memory_manager.abstract_memory_manager import AbstractMemoryManager
from lyfe_agent.states.agent_state import AgentState
from lyfe_agent.slowfast.slowfast import SlowFastModule
from lyfe_agent.utils.log_utils import log_message

logger = logging.getLogger(__name__)

class ActionSelection:
    """Select an atomic action to be executed by the agent."""
    def __init__(
        self,
        agent_state : AgentState,
        name: str,
        memory: AbstractMemoryManager,
        option_executor: Dict[str, BaseOptionExecutor],
        executor: Executor,
        data_collectors: Dict[str, List],
    ):
        self.agent_state = agent_state
        self.name = name
        self.memory = memory
        self.data_collectors = data_collectors
        self.executor = executor
        self.option_executor = option_executor

        # slow_forward is executing current option with the action-LLM chain
        self.slow_fast_sys = SlowFastModule(
            executor=self.executor,
            name=f"{self.name}_action_selection",
            slow_func=self.slow_forward,
            fast_func=self.fast_forward,
        )

    def execute(self, observations) -> Dict:
        """Execute the action selection process.

        Args:
            observations: The observations from the environment.

        Returns:
            actions: The actions to be taken by the agent.
        """
        # may want to move this elsewhere
        if observations.get("interview", None) is not None:
            response = self.slow_forward(observations)
            return response

        # Slow forward thread
        self.slow_fast_sys.retrieve_result()

        should_submit = self.agent_state.should_submit_action_selection()
        can_submit = self.slow_fast_sys.can_submit_slow_func(self.agent_state.suspended_time)
        if should_submit and can_submit:
            self.slow_fast_sys.submit_slow_func(observations)
        # This will use either the slow forward or fast forward
        action_to_env = self.slow_fast_sys.get_result(observations)
        
        return action_to_env


    def slow_forward(self, observations) -> Dict:
        # TODO: to replace the slow_forward function with DesireModules
        """Slow forward function for the brain, will be called every iteration."""
        # actions is dictionary with default values of None
        action_to_env = defaultdict(lambda: None)

        # Input to memory
        memory_input = defaultdict(lambda: None)

        option = self.agent_state.modify_option(
            option=self.agent_state.get_current_option(),
            talk_obs=observations.get("talk", None),
        )

        # TODO: This is a patch that should be fixed
        if "interview" in observations:
            option = "interview"

        # TODO: Cognitive controller is not an option executor for now
        if not self.agent_state.has_option(option) or option == "cognitive_controller":
        # if not self.agent_state.has_option(option):
            return action_to_env

        # remove new_event, prepare for executing the option_executor
        self.agent_state.set_new_event(False, "cancel new_event within slow_forward")

        current_option_executor = self.option_executor[option]
        action_to_env, memory_input = current_option_executor.execute(
            observations, self.agent_state.data
        )

        memory_input.update({"time": self.agent_state.get_time()})
        self.memory.add(
            content=memory_input,
            data_collector=self.data_collectors["memory_input_collector"],
        )

        # variables for logging
        if self.agent_state.has_skill(option):
            label = f"CODE - {option}"
            key = "code"
        else:
            label = option.upper()
            key = option
        
        logger.info(
            log_message(
                self.name,
                f"{label}",
                action_to_env.get(key, None),
                self.agent_state.get_time(),
                action_to_env["message"][1]
                if isinstance(action_to_env.get("message", None), tuple)
                else None,
            )
        )
        return action_to_env

    # TODO: DeprecateWarning - the terminate() function in talk_option_executor will replace current fast_forward
    def fast_forward(self, observations=None) -> Dict:
        """Fast system forward function.

        The fast system uses heuristics and simple networks to ensure
        rapid response.
        """
        if self.agent_state.exit_current_option():
            if "reflect" in self.option_executor.keys():
                self.agent_state.update_option(option_name="reflect")
            else:
                self.agent_state.update_option(
                    option_name="cognitive_controller",
                    option_goal="current goal unavailable",
                )
            self.agent_state.set_new_event(True, "repetition or expiration trigger")

        actions = defaultdict(lambda: None)
        return actions
