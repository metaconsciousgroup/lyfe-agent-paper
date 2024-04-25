"""
Judges are used to evaluate the correctness of an answer, typically used in agent interviews.
"""

import json
import re

from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class Extractor:
    """Base class for extractors."""

    def __init__(self, verbose=True):
        """Initialize a judge."""
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7, # default temperature
            max_retries=2, # max retries for openai api
            request_timeout=5, # timeout for openai api
        )

        self.format_instructions_template = (
            """\nProvide the answers in the following JSON format: {schema}"""
        )
        self.verbose = verbose

    def __call__(self, question, response, template, format):
        input_variables = re.findall(r"\{(.*?)\}", template)
        for var in input_variables:
            assert var in ["question", "response"], f"Unexpected variable {var}."
        
        
        schema = json.dumps(format)
        format_instructions = self.format_instructions_template.format(schema=schema)

        template += "{format_instructions}"
        prompt = PromptTemplate(
            template=template,
            input_variables=input_variables,
            partial_variables={"format_instructions": format_instructions},
        )

        chain = LLMChain(
            prompt=prompt, llm=self.llm, verbose=self.verbose, 
        )
        chain_input = {
            "question": question,
            "response": response,
        }
        chain_output = chain.run(chain_input)
        try: 
            output = json.loads(chain_output)
            for key, val in output.items():
                if val in ["N/A"]:
                    output[key] = None
        except:
            output = {key: None for key in format.keys()}

        return output

