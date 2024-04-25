"""Language Models."""
import logging
from typing import Dict
import openai
import hydra
import time
import random
from langchain.chains import LLMChain

logger = logging.getLogger(__name__)


class LangModel:
    """Simple base language model class."""

    def __call__(self, inputs):
        return self.generate(inputs)

    def generate(self, input_txt: str) -> str:
        """A high level API for generating txt given txt."""
        raise NotImplementedError


def get_api_keys(env_dict: Dict[str, str]):
    """
    return: a dictionary of api keys

    Example:
    api_keys = {
        "openai": ["key1", "key2"],
        "palm": ["key1", "key2"]
    }
    """
    ## TODO: Is it important that we have multiple API keys for each model?
    api_keys = {}
    api_keys["openai"] = env_dict.get("OPENAI_APIKEY", [])
    api_keys["palm"] = env_dict.get("PALM_APIKEY", [])
    return api_keys


class DummyLangModel(LangModel):
    """Dummy language model for testing."""

    def __init__(self):
        super().__init__()

    def generate(self, input_txt: str) -> str:
        return 'none'


class LangChainExperiment(LangModel):
    """
    Langmodel using LangChain. Once this class works, we will add more functionality (e.g. memory).
    """

    def __init__(self, llm, log_usage=False):
        super().__init__()
        self.log_usage = log_usage

        # create a list of api keys
        api_keys = get_api_keys()
        self.api_key = api_keys
        assert self.api_key, 'cfg must have an api key'

        # may do differently
        api_key = self.api_key["openai"][random.randint(0, len(self.api_key["openai"]) - 1)]
        self.llm = llm(openai_api_key=api_key)

    def chain(self, prompt):
        # Use verbose to test in 2 agent environment
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain

    def generate(self, messages):
        reply = self.chain.run(messages)
        return reply


class OpenAIGPTModel(LangModel):
    def __init__(self, chat_kwargs, log_usage=False):
        super().__init__()

        self.chat_kwargs = chat_kwargs
        self.log_usage = log_usage

        api_keys = get_api_keys()

        # create a list of api keys
        self.api_key = api_keys["openai"]

        assert self.api_key, 'cfg must have a api key'

    def generate(self, messages, max_retries=30, initial_wait_time=10, backoff_factor=3):
        """Generate messages.

        Example messages
        messages = [
            {'role': 'system',
             'content': "Suppose you are human."
                        "You are about to generate reasonable answers based on the context. "
                        "Less than 20 words"},
            {'role': 'user',
             'content': content + question}
        ]
        """
        for retry in range(max_retries):
            try:
                openai.api_key = self.api_key[random.randint(0, len(self.api_key) - 1)]
                chat = openai.ChatCompletion.create(messages=messages, **self.chat_kwargs)
                if self.log_usage:
                    usage = chat.usage
                    logger.info(f"[LM-USAGE]"
                                f"[COMPLETION]{usage.completion_tokens}"
                                f"[PROMPT]{usage.prompt_tokens}")
                reply = chat.choices[0].message.content
                return reply
            except openai.error.OpenAIError as e:
                if retry < max_retries - 1:
                    wait_time = initial_wait_time * (backoff_factor * retry)
                    time.sleep(wait_time)
                else:
                    raise

def get_langmodel(cfg, api_key=None):
    if not cfg:
        return None

    if api_key is None:
        model = hydra.utils.instantiate(cfg)()
    else:
        model = hydra.utils.instantiate(cfg)(openai_api_key=api_key)
    return model
