"""
Judges are used to evaluate the correctness of an answer, typically used in agent interviews.
"""

from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

template = """
Consider the following question: '{question}'
The correct answer to this question is: '{answer}'

Given that you know the correct answer, evaluate whether the following response is a correct answer to the question: '{response}'
Note that the response need not be a verbatim match to the correct answer, but it should be semantically equivalent.

Your response should be True or False. No additional words.
"""


class Judge:
    """Base class for judges."""

    def __init__(self, template=template, verbose=True):
        """Initialize a judge."""
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7, # default temperature
            max_retries=2, # max retries for openai api
            request_timeout=5, # timeout for openai api
        )

        prompt = PromptTemplate.from_template(template)

        self.chain = LLMChain(
            prompt=prompt, llm=llm, verbose=verbose, 
        )

    def __call__(self, question, answer, response):
        """Evaluate an answer."""
        chain_input = {
            "question": question,
            "answer": answer,
            "response": response,
        }
        str_bool = self.chain.run(chain_input)
        correctness = str_bool.strip().lower() == "true"
        return correctness