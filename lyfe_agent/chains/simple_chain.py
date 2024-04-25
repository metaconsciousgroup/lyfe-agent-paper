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


class CustomOutputParser(PydanticOutputParser[T]):
    """Custom parser with customized format instructions."""

    # CUSTOM_FORMAT_INSTRUCTIONS = """The output should be in the following format: {schema}"""
    CUSTOM_FORMAT_INSTRUCTIONS = (
        """\nProvide the answers in the following JSON format: {schema}"""
    )

    def get_format_instructions(self) -> str:
        schema = self.pydantic_object.schema()

        # Perform any customization to the schema as needed.

        # Remove extraneous fields if necessary
        reduced_schema = {
            key: value["description"] for key, value in schema["properties"].items()
        }

        schema_str = json.dumps(reduced_schema)

        return self.CUSTOM_FORMAT_INSTRUCTIONS.format(schema=schema_str)


class ParserChain(BaseChain):
    def __init__(
        self,
        template,
        parser_config,
        llm,
        memory,
        name=None,
        collect_data=False,
        verbose=False,
        **kwargs,
    ):
        pydantic_model = create_pydantic_model(name=f"parser", fields=parser_config)
        # self.parsers = PydanticOutputParser(pydantic_object=pydantic_model)
        self.parsers = CustomOutputParser(pydantic_object=pydantic_model)
        input_variables = re.findall(r"\{(.*?)\}", template)
        template += "\n{format_instructions}"
        prompt = PromptTemplate(
            template=template,
            input_variables=input_variables,
            partial_variables={
                "format_instructions": self.parsers.get_format_instructions()
            },
        )
    
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
        if self.collect_data and data_collector is not None:
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