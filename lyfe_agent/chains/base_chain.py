import re
import logging

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from lyfe_agent.utils.log_utils import get_colored_text

from lyfe_agent.chains.chain_utils import (
    LogCallbackHandler,
    generate_merged_string,
)

logger = logging.getLogger(__name__)


class BaseChain:
    def __init__(
        self,
        template,
        llm,
        memory,
        name=None,
        collect_data=False,
        verbose=False,
    ):
        input_variables = re.findall(r"\{(.*?)\}", template)
        prompt = PromptTemplate(
            template=template,
            input_variables=input_variables,
        )

        self.verbose = verbose
        handler = LogCallbackHandler()
        self.collect_data = collect_data
        self.chain = LLMChain(
            prompt=prompt, llm=llm, memory=memory, callbacks=[handler], verbose=verbose
        )

    def run(self, chain_input, option=None, data_collector=None):
        chain_output = self.chain.invoke(chain_input)["text"]

        # Temporary --- this is for data collection purposes
        if self.collect_data:
            merged_dict = chain_input | self.chain.memory.queried_memories
            merged_data = generate_merged_string(
                merged_dict, chain_output, option
            )  # assuming it returns a dict
            data_collector.append(merged_data)
            self.chain.memory.queried_memories = (
                {}
            )  # ensure that queried memories are properly reset after use
        # Temporary --- this is for data collection purposes

        # for logging
        output_str = get_colored_text(chain_output, "green")
        if self.verbose:
            logger.info(f"Chain output: {output_str}")
            pass
        else:
            logger.debug(f"Chain output: {output_str}")

        return chain_output