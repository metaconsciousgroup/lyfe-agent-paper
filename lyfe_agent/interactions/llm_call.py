import json

from langchain_community.callbacks import get_openai_callback
from lyfe_agent.chains.simple_chain import ParserChain
from lyfe_agent.brain_utils import calculate_lifespan


# Unclear whether this is best as an interaction
# Right now its `execute` is its call method
class LLMCall:
    def __init__(
        self,
        name,
        llm,
        memory,
        agent_state,
        chains,
        reading_speed=1.5,
        decision_requester_step=5,
    ):
        self.name = name
        self.llm = llm
        self.memory = memory
        self.agent_state = agent_state


        self.chains = {
            key: ParserChain(llm=self.llm, memory=self.memory, name=self.name, **val)
            for key, val in chains.items()
        }

        self.reading_speed = reading_speed
        self.decision_requester_step = decision_requester_step

    def __call__(
        self,
        option=None,
        chain=None,
        chain_input=None,
        data_collector=None,
    ):
        """
        Take action based on the prompt and the current status
        """
        if option is not None:
            chain = self.chains.get(option, None)

        assert chain is not None, "Chain should not be None"
        chain_input = self.agent_state.data if chain_input is None else chain_input
        with get_openai_callback() as cb:
            chain_answer = chain.run(chain_input, option, data_collector)
            # calculate how long the talk is going to last based on the number of tokens generated
            cb_info = cb.__dict__

            lifespan = calculate_lifespan(
                cb.completion_tokens,
                self.reading_speed,
                self.decision_requester_step,
            )
            # TEMP: need to move reading_speed and decisions_requester_step
            cb_info["lifespan"] = lifespan

        return json.loads(chain_answer), cb_info
