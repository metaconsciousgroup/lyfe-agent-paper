import json
import logging

from collections import defaultdict
from langchain_community.callbacks import get_openai_callback
from threading import Lock
from typing import Dict, Optional

from lyfe_agent.brain_utils import calculate_lifespan
from lyfe_agent.chains.simple_chain import ParserChain
from lyfe_agent.interactions.option_executor import BaseOptionExecutor
from lyfe_agent.slowfast.slowfast import SlowFastModule
from lyfe_agent.states.agent_state import AgentState


logger = logging.getLogger(__name__)

# TODO: include typing information

class CognitiveController(BaseOptionExecutor):
    def __init__(
        self,
        name,
        chain,
        llm,
        memory,
        data_collector,
        executor,
    ):
        super().__init__(sources={}, targets=[])
        self.name = name
        self.module_name = "cognitive_controller"
        self.memory = memory
        self.executor = executor
        self.data_collector = data_collector
        self.lock = Lock()

        self.chain = ParserChain(llm=llm, memory=memory, name=self.name, **chain)

        self.slow_fast_module = SlowFastModule(
            executor=self.executor,
            name=f"{self.name}_cognitive_controller",
            slow_func=self.slow_forward,
            fast_func=self.fast_forward,
        )

    def execute(self, observations, agent_state: AgentState):
        self.slow_fast_module.retrieve_result()
        chain_output = self.slow_fast_module.get_result(agent_state)
        self.process_chain_output(chain_output, agent_state)

        # Submitting the slow forward
        should_submit = agent_state.get_current_option() == "cognitive_controller"
        # TODO: basic check, see if there is a talk item
        heard_someone_speak = observations.get("talk") is not None
        should_submit |= heard_someone_speak

        can_submit = self.slow_fast_module.can_submit_slow_func()
        # Also include the condition that the current option is 'cognitive_controller'

        if should_submit and can_submit:
            self.slow_fast_module.submit_slow_func(agent_state)
            
            # # TODO: add memory (eventually uncomment the data collector and place in agent state)
            # self.memory.add(
            #     content=memory_input,
            #     # data_collector=self.data_collectors["memory_input_collector"],
            # )
        

        # TODO: Modifications to the memory are not happening yet, will go here

        # return self.action_to_env, self.memory_input

    def process_chain_output(
        self,
        chain_output: Optional[Dict],
        agent_state: AgentState
    ) -> None:
        if chain_output is None or chain_output.get("option_name") is None:
            return
        # No changes if the option hasn't changed
        if chain_output["option_name"] == agent_state.get_current_option():
            return
        if agent_state.has_option(chain_output["option_name"]):
            with self.lock:
                agent_state.update_option(**chain_output)
                agent_state.set_new_event(
                    True, "cognitive_controller trigger"
                )  # The cognitive_controller itself is a new event
            self.action_to_env[self.module_name] = chain_output["option_name"]


    def run_llm(self, agent_state: AgentState):
        chain_input = agent_state.data
        with get_openai_callback() as cb:
            chain_answer = self.chain.run(chain_input, self.module_name, self.data_collector)
            # calculate how long the talk is going to last based on the number of tokens generated
            cb_info = cb.__dict__

        chain_answer = json.loads(chain_answer)
        logger.info(f"Cognitive controller output: {chain_answer}")

        # # TODO: call directly an agent state method
        # self.agent_state.options.activate_variable(
        #     self.module_name,
        #     cb_info["lifespan"],
        # )

        return chain_answer

    # TODO: consider name change
    def slow_forward(self, agent_state: AgentState):
        self.is_active = True
        chain_answer = self.run_llm(agent_state)
        self.is_active = False


        return chain_answer

    def fast_forward(self, agent_state: AgentState):
        return None