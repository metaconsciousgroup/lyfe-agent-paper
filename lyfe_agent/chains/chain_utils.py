import json
from typing import Any
from uuid import UUID
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import datetime

"""Callback Handler that prints to std out."""
from typing import Any, Dict, Optional

from langchain.callbacks.base import BaseCallbackHandler

import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LogCallbackHandler(BaseCallbackHandler):
    """Callback Handler used to log prompt input to chains."""

    def __init__(self, color: Optional[str] = None) -> None:
        """Initialize callback handler."""
        # self.color = color

    # def on_chain_start(
    #     self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    # ) -> None:
    #     """Print out that we are entering a chain."""
    #     class_name = serialized.get("name", serialized.get("id", ["<unknown>"])[-1])
    #     logger.info(f"\033[1m> Entering new {class_name} chain...\033[0m")

    # def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
    #     """Print out that we finished a chain."""
    #     logger.info(f"\033[1m> Finished chain.\033[0m")

    def on_retry(self, **kwargs: Any) -> None:
        logger.info("\033[1m> Retrying LangChain call to OpenAI Server...\033[0m")

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        end: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when agent ends."""
        # See LLMChain `prep_prompts` for modifying string font/formatting
        logger.debug(text)

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when agent ends."""
        logger.error(f"[LLM ERROR] {error} with kwargs {kwargs}")

    def on_chain_error(
        self, error: BaseException, *, run_id: UUID, parent_run_id, **kwargs: Any
    ) -> Any:
        logger.error(
            f"[CHAIN ERROR] {error} with run_id {run_id} and parent_run_id {parent_run_id} and kwargs {kwargs}"
        )

    def on_retriever_error(self, error: BaseException, **kwargs: Any) -> Any:
        logger.error(f"[RETRIEVER ERROR] {error} with kwargs {kwargs}")

    def on_tool_error(
        self, error: BaseException, *, run_id: UUID, parent_run_id, **kwargs: Any
    ) -> Any:
        logger.error(
            f"[TOOL ERROR] {error} with run_id {run_id} and parent_run_id {parent_run_id} and kwargs {kwargs}"
        )


def LLMChain_from_template(template, llm, memory, verbose=False):
    prompt = PromptTemplate.from_template(template)
    handler = LogCallbackHandler()
    return LLMChain(
        prompt=prompt, llm=llm, memory=memory, callbacks=[handler], verbose=verbose
    )


def create_pydantic_model(name, fields):
    """
    Dynamically creates a Pydantic model.

    :param name: Name of the new model.
    :param fields: A dictionary of field names and their types.
    :return: A new Pydantic model.
    """
    attributes = {
        field_name: Field(..., description=desc) if desc else Field(...)
        for field_name, desc in fields.items()
    }
    attributes.update(
        {"__annotations__": {field_name: str for field_name in attributes}}
    )

    return type(name, (BaseModel,), attributes)


def generate_merged_string(chain_input, chain_output, option):
    """
    Generates a merged string from input and output dictionaries, and an active function.

    Parameters:
    - chain_input (dict): Input dictionary.
    - chain_output (str): JSON-formatted string.
    - option (str): Active function identifier.

    Returns:
    - str: Merged JSON-formatted string.
    """

    # Ensure all values in chain_input are strings
    for key, value in chain_input.items():
        if isinstance(value, datetime.datetime):
            chain_input[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        elif not isinstance(value, str):
            try:
                chain_input[key] = str(value)
            except Exception:
                continue

    chain_input["option"] = option
    evaluation_monitor = chain_input.pop("evaluation_monitor", False)

    # Chain output processing
    chain_output_dict = json.loads(chain_output)

    # Merge the dictionaries
    merged_dict = {
        "input": chain_input,
        "output": chain_output_dict,
        "evaluation_monitor": evaluation_monitor,
    }

    return merged_dict
