import logging
import json
import re

from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from typing import TypeVar
from lyfe_agent.utils.log_utils import get_colored_text

from lyfe_agent.chains.base_chain import BaseChain
from lyfe_agent.chains.chain_utils import (
    LogCallbackHandler,
    create_pydantic_model,
    generate_merged_string,
)

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


def StringToListParser(text):
    
    # data = """
    # [something here]
    # 1. item 1
    # 2. item 2
    # 3. item 3
    # """

    # Extract the part inside square brackets
    header_match = re.search(r'\[(.*?)\]', text)
    header = header_match.group(1) if header_match else None

    # Extract items
    items = re.findall(r'\d+\.\s(.*?)$', text, re.MULTILINE)

    print("Header:", header)
    print("Items:", items)
    return items


class ItemizedChain(BaseChain):
    def __init__(
        self,
        template,
        llm,
        memory,
        name=None,
        collect_data=False,
        verbose=False,
        **kwargs,
    ):
        self.parser = StringToListParser
        prompt = PromptTemplate.from_template(template)

        self.verbose = verbose
        handler = LogCallbackHandler()
        self.collect_data = collect_data
        self.chain = LLMChain(
            prompt=prompt, llm=llm, memory=memory, callbacks=[handler], verbose=verbose
        )

    def log(self, chain_output):
        # for logging
        output_str = get_colored_text(chain_output, "green")
        if self.verbose:
            logger.info(f"Chain output: {output_str}")
            pass
        else:
            logger.debug(f"Chain output: {output_str}")

    def add_data(self, chain_input, chain_output, option, data_collector):
        # for data collection
        if self.collect_data:
            merged_dict = chain_input | self.chain.memory.queried_memories
            merged_data = generate_merged_string(merged_dict, chain_output, option)
            data_collector.append(merged_data)
            self.chain.memory.queried_memories = (
                {}
            )  # ensure that queried memories are properly reset after use

    def run(self, chain_input, option=None, data_collector=None):
        chain_output = self.chain.invoke(chain_input)["text"]

        # Temporary --- this is for data collection purposes
        self.add_data(chain_input, chain_output, option, data_collector)
        self.log(chain_output)

        return chain_output

    async def arun(self, chain_input, option=None, data_collector=None):
        # no logging or data collection for async
        return await self.chain.arun(chain_input)
