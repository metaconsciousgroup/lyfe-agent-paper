import json
import logging

from collections import deque
from typing import Dict

from langchain_community.callbacks import get_openai_callback

from lyfe_agent.base import BaseInteraction
from lyfe_agent.chains.simple_chain import ParserChain
from lyfe_agent.slowfast.slow import SlowThreadModule

logger = logging.getLogger(__name__)

class SummaryInteraction(BaseInteraction):
    def __init__(self, sources, targets, chain, **kwargs):
        super().__init__(sources, targets)

        self.slow_thread_module = SlowThreadModule(
            executor=self.executor,
            name=f"{self.name}_update_world_model",
            slow_func=self.update_world_model,
        )
        self.feedback_queue = deque()

        self.chain = ParserChain(llm=self.llm, memory=self.memory, name=self.name,**chain)

    # TODO: all the inputs should become sources
    def execute(self, observations: Dict):
        # Get new_obs except time
        observations.pop("time", None)

        should_submit = False
        if "general" in observations.keys():
            self.feedback_queue.append(observations.pop("general"))
            should_submit = True

        new_obs = "\n".join(list(observations.values()))

        should_submit |= self.event_tracker.get()
        if self.slow_thread_module.can_submit_slow_func(external_signal=should_submit):
            self.slow_thread_module.submit_slow_func(new_obs)

    def update_world_model(self, observations=None):
        """Process world model thread. This thread will take care of initiliazing agent summary and
        updating it every time the agent has a new observation."""

        chain_input = self.agent_state.data | {
            "update_world_model": True,
        }

        if len(self.feedback_queue) > 0:
            chain_input["feedback"] = self.feedback_queue.popleft()
        else:
            chain_input["feedback"] = ""

        with get_openai_callback() as cb:
            chain_answer = self.chain.run(
                chain_input,
                option="update_world_model",
                data_collector=self.data_collectors["update_world_model"]
            )
            # calculate how long the talk is going to last based on the number of tokens generated
            cb_info = cb.__dict__

        chain_output = json.loads(chain_answer)
        logger.info(f"Summary output: {chain_output}")

        self.summary_state.update(**chain_output)
