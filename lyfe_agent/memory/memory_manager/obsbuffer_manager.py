from typing import Any, Dict, List, Optional, Union
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.schema import BaseMemory
from lyfe_agent.memory.memory_manager.abstract_memory_manager import AbstractMemoryManager
from lyfe_agent.chains.itemized_chain import ItemizedChain
import nltk
from nltk.tokenize import sent_tokenize

import re
import threading

from concurrent.futures import ThreadPoolExecutor

nltk.download("punkt")


def StringToListParser(text):
    # text = """
    # [something here]
    # 1. item 1
    # 2. item 2
    # 3. item 3
    # """

    # Extract the part inside square brackets
    header_match = re.search(r"\[(.*?)\]", text)
    header = header_match.group(1) if header_match else None

    # Extract items
    items = re.findall(r"\d+\.\s(.*?)$", text, re.MULTILINE)

    return items


class ThreeStageMemoryManager(AbstractMemoryManager):
    """Buffer for storing arbitrary memories."""

    # used for memory consolidation
    llm: BaseLanguageModel
    output_key: Optional[str] = None
    input_key: Optional[str] = None
    memory_keys: List[str] = None
    prompt_keys: List[str] = None

    # created upon initialization
    obsbuffer: Optional[BaseMemory] = None
    workmem: Optional[BaseMemory] = None
    recentmem: Optional[BaseMemory] = None
    longmem: Optional[BaseMemory] = None

    memory_prompts: Optional[Dict[str, str]] = None
    memory_vars: Optional[Dict[str, str]] = None
    counter: int = 0

    verbose: bool = False
    name: Any = None
    queried_memories: Any = None
    
    nonce : Optional[List[str]] = None

    tick_limit: int = 5

    def __init__(
        self,
        memory_modules,
        memory_prompts,  # !!!
        encoders,
        env_dict: Dict[str, str],
        executor=None,
        **data: Any,
    ):
        super().__init__(**data)
        self.memory_keys = list(memory_modules.keys())
        self.prompt_keys = list(memory_prompts.keys())
        self.memory_vars = {name: "" for name in self.memory_keys}

        object.__setattr__(
            self,
            "memory_vars_lock",
            threading.Lock(),
        )

        # setup executor for summary
        object.__setattr__(
            self,
            "executor",
            executor if executor else ThreadPoolExecutor(max_workers=3),
        )

        default_model_arg = {"encoder": None, "name": self.name}
        model_arg = {
            key: {
                # "encoder": self.encoders.models[self.encoders.rules[key]],
                "encoder": encoders.models[encoders.rules[key]],
                "name": self.name,
            }
            if key in encoders.rules.keys()
            else default_model_arg
            for key in self.memory_keys
        }

        # setting up memory modules
        for key, memory_module in memory_modules.items():
            setattr(self, key, memory_module(**model_arg[key]))

        # get memory prompts
        self.memory_prompts = {}
        for key in self.prompt_keys:
            assert key in memory_prompts, f"memory prompts must include the key {key}"
            prompt_content = memory_prompts[key]
            if isinstance(prompt_content, str):
                memory_prompts[key] = prompt_content
            # otherwise we assume that `prompt_content` is a list of strings
            else:
                memory_prompts[key] = "\n".join(prompt_content)

        self.memory_prompts = {
            key: PromptTemplate.from_template(prompt)
            for key, prompt in memory_prompts.items()
            if key in self.prompt_keys
        }

        # Used to keep track of queried memories for data collection
        self.queried_memories = {}

        assert env_dict, "env_dict must be provided"
        assert env_dict["NONCE"], "NONCE must be provided"
        self.nonce = env_dict["NONCE"]

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables."""
        return self.memory_keys

    def setup_chain(self, customized_prompt: PromptTemplate = None) -> LLMChain:
        return LLMChain(
            llm=self.llm,
            memory=self,
            prompt=customized_prompt,
            verbose=True,  # verbose=self.verbose
        )

    def fill_memories(self, memories: Dict[str, List]) -> None:
        """Used to sets of memories"""
        for key, value in memories.items():
            if key in self.memory_keys:
                mem_type = getattr(self, key)
                for item in value:
                    mem_type.add(item)
                    if key == "workmem":
                        self.obsbuffer.add(
                            document=item, in_world_time="init", obs_type="visual"
                        )

    def query(
        self, memory_key: str, text: str, num_memories_retrieved: int = 1
    ) -> List[str]:
        memory = getattr(self, memory_key)
        responses = memory.query(text=text, num_memories_retrieved=num_memories_retrieved)
        return responses

    def threaded_summarize(self, memory_from, memory_to):
        _mem = self.summarize(memory_from=memory_from, memory_to=memory_to)
        with self.memory_vars_lock:
            getattr(self, memory_to).add(_mem)

    def update(self, new_summary=None, is_last=False) -> None:
        """Called during `slow_forward`, corresponding to conscious reflection"""

        for item in self.obsbuffer.observation_bank:
            if item.metadata["type"] in ["audio", "mental"]:
                self.workmem.add(item.content, memory_type="audio")

        # clear obsbuffer after being filtered by attention
        self.obsbuffer.clear()

        # Check if new_summary exists and none of its values are None
        if (
            new_summary
            and all(value not in self.nonce for value in new_summary.values())
            and not self.recentmem.is_repetitive(new_summary)
        ):
            self.recentmem.counter += 1

            # TODO: time-based recentmem update by taking in summary of the agent
            if self.recentmem.counter >= self.tick_limit:
                self.recentmem.counter = 0  # reset counter to be 0
                # Convert the dictionary values to a paragraph
                paragraph = " ".join(new_summary.values())
                sentences = sent_tokenize(paragraph)
                for sentence in sentences:
                    cleaned_sentence = sentence.strip()
                    if cleaned_sentence:
                        self.recentmem.add(cleaned_sentence)

                self.recentmem.counter = 0

        if (
            self.recentmem.size >= self.recentmem.capacity
            and not self.recentmem.is_summarizing
        ):
            self.recentmem.is_summarizing = True
            self.executor.submit(self.threaded_summarize, "recentmem", "longmem")
            self.recentmem.clear()

        if is_last:
            future_workmem = self.executor.submit(
                self.threaded_summarize, "workmem", "recentmem"
            )

            # Wait for the future results to complete
            future_workmem.result()

            future_recentmem = self.executor.submit(
                self.threaded_summarize, "recentmem", "longmem"
            )
            future_recentmem.result()
        return

    def _load_mem(self, memory_key, k=None):
        if memory_key == "convomem":
            pattern = r"(.+?) said: (.+)"
            items = [
                item
                for item in getattr(self, "workmem").items
                if re.match(pattern, item)
            ]
        elif memory_key == "reflectmem":
            recentmems = self.recentmem.items
            # right now an arbitrary parameter of 5 (thinking a unit of time for one longmem is about 5 recentmems)
            num_longmems = (self.recentmem.capacity - len(recentmems)) // 5
            longmems = self.longmem.items[-num_longmems:]
            items = self.workmem.items + recentmems + longmems
        else:
            items = getattr(self, memory_key).items

        if not items:
            return "No conversation history yet." if memory_key == "convomem" else ""

        k = k if k else len(items)

        if memory_key == "convomem" and len(items) > 1:
            return "\n".join(items[-k:-1]) + "\nMost recently\n" + items[-1]

        return "\n".join(items[-k:])

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""

        self.obsbuffer.remove_expired()

        if inputs.get("summarize", False):
            return {}

        self.memory_vars.update({"obsbuffer": self._load_mem("obsbuffer")})
        self.memory_vars.update({"workmem": self._load_mem("workmem")})
        self.memory_vars.update({"convomem": self._load_mem("convomem")})
        self.memory_vars.update({"reflectmem": self._load_mem("reflectmem")})

        self._update_memory_vars()
        return self.memory_vars

    def _update_memory_vars(self) -> None:
        if self.workmem.items:
            query_workmem = self.workmem.items[-1]
            queried_recentmem_workmem = self.recentmem.query(
                query_workmem,
                num_memories_retrieved=self.recentmem.num_memories_retrieved,
            )
            queried_longmem_workmem = self.longmem.query(
                query_workmem, num_memories_retrieved=self.longmem.num_memories_retrieved
            )
        else:
            queried_recentmem_workmem = []
            queried_longmem_workmem = []

        queried_recentmem = set(queried_recentmem_workmem)
        queried_longmem = set(queried_longmem_workmem)

        if queried_recentmem:
            with self.memory_vars_lock:
                self.memory_vars.update({"recentmem": "\n".join(queried_recentmem)})

        if queried_longmem:
            with self.memory_vars_lock:
                self.memory_vars.update({"longmem": "\n".join(queried_longmem)})

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        for key in self.memory_vars:
            if key in inputs:
                self.queried_memories[key] = inputs[key]

    def summarize(
        self, memory_from: str = "workmem", memory_to: str = "recentmem"
    ) -> str:
        """Summarize memory_from and add to memory_to"""
        prompt_name = f"{memory_from}_to_{memory_to}"

        chain_input = {
            "name": self.name,
            memory_from: "\n- ".join([""] + getattr(self, memory_from).items),
            "summarize": True,
        }
        chain = self.setup_chain(customized_prompt=self.memory_prompts[prompt_name])
        chain_output = chain.invoke(chain_input)["text"]
        # parsed_output = StringToListParser(chain_output)
        # return parsed_output
        return chain_output

    def add(self, content: Optional[Union[dict, str]], data_collector=None) -> None:
        """Add new observation/self-actions to observation_buffer."""
        if isinstance(content, str):
            self.obsbuffer.add(
                document=content, in_world_time="init", obs_type="visual"
            )
            return

        time = content.get("time", "init")
        content.pop("time", None)
        for sub_key, memory in content.items():
            if memory in self.nonce:
                continue

            # TODO: this is a hacky way to get the memory to the data collector
            data_collector.append(memory)

            if sub_key in ["talk", "message"]:
                memory = memory.replace("says", "said").replace("say", "said")
                self.obsbuffer.add(
                    document=memory, in_world_time=time, obs_type="audio"
                )
            elif sub_key in ["reflect"]:
                self.obsbuffer.add(
                    document=memory, in_world_time=time, obs_type="mental"
                )
            elif sub_key in ["choose_destination"]:
                self.obsbuffer.add(
                    document=memory, in_world_time=time, obs_type="spacial"
                )
            elif sub_key != "time":
                self.obsbuffer.add(
                    document=memory, in_world_time=time, obs_type="visual"
                )

    def clear(self) -> None:
        """Clear memory contents."""
        for key in self.memory_keys:
            getattr(self, key).clear()
