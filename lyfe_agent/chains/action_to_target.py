from lyfe_agent.chains.chain_utils import LLMChain_from_template, create_pydantic_model
from lyfe_agent.utils.name_utils import name_match
from lyfe_agent.utils.log_utils import get_colored_text
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
import re
import logging
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class ActionToTargetChain:
    def __init__(
        self,
        llm,
        memory,
        target_template,
        action_template,
        target_key="target",
        parser_config=None,
        verbose=False,
    ):
        # Create Pydantic model from parser_config
        if parser_config:
            pydantic_model = create_pydantic_model(name=f"parser", fields=parser_config)
            self.parsers = PydanticOutputParser(pydantic_object=pydantic_model)
            input_variables = re.findall(r"\{(.*?)\}", action_template)
            action_template += (
                "\nProvide a response in the following format: \n{format_instructions}"
            )
        else:
            action_template_variables = {}

        self.target_chain = LLMChain_from_template(
            target_template,
            llm,
            memory,
            verbose,
        )

        prompt = PromptTemplate(
            template=action_template,
            input_variables=input_variables,
            partial_variables={
                "format_instructions": self.parsers.get_format_instructions()
            },
        )
        self.action_chain = LLMChain(prompt=prompt, llm=llm, memory=memory)
        self.target_key = target_key

    def run(self, chain_input):
        logger.debug(f"\033[1m> Entering new target chain...\033[0m")
        receiver = self.target_chain.invoke(chain_input)["text"]
        output_str = get_colored_text(receiver, "green")
        logger.debug(f"Target chain output: \033[1m>{output_str}\033[0m")
        logger.debug(f"\033[1m> Finished target chain.\033[0m")
        is_match, receiver = name_match(receiver, chain_input["contacts"])
        # wrong receiver name
        if not is_match:
            return None, None

        logger.debug(f"\033[1m> Entering new action chain...\033[0m")
        action = self.action_chain.invoke(chain_input | {self.target_key: receiver})
        output_str = get_colored_text(action, "green")
        logger.debug(f"Action chain output: \033[1m>{output_str}\033[0m")
        logger.debug(f"\033[1m> Finished action chain.\033[0m")
        return action
