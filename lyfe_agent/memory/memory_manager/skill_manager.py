from typing import Any, Dict, List, Optional, TypedDict
from pathlib import Path
from lyfe_agent.memory.memory_manager.abstract_memory_manager import AbstractMemoryManager
from lyfe_agent.memory.memory_module.default_modules import EmbeddingMemory
from lyfe_agent.utils.encoder_utils import EncoderManager
from lyfe_agent.utils.skill_utils import load_js_files

import time

PROGRAM_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "minecraft" / "verified"

class SkillItem(TypedDict):
    """
    Data regarding a single skill, where `key` is the name of the skill.
    """
    key: str
    description: str
    code: str


class SkillManager(AbstractMemoryManager):
    """Buffer for storing arbitrary memories."""

    output_key: Optional[str] = None
    input_key: Optional[str] = None
    memory_keys: List[str] = None
    prompt_keys: List[str] = None

    # created upon initialization
    skillmem: EmbeddingMemory = None
    
    memory_vars: Dict[str, str] = {"memory": ""}
    
    verbose: bool = False
    name: Any = None

    buffer: List[str] = []
    skill_dict: Dict[str, SkillItem] = {}
    skills: List[SkillItem] = []

    def __init__(
        self,
        encoder: EncoderManager,
        env_dict : Dict[str, str],
        executor=None,
        skills: Optional[List[SkillItem]] = [],
        init_query: str = "",
        **data: Any,
    ):
        super().__init__(**data)

        # setting up three-stage memory modules
        self.skillmem = EmbeddingMemory(
            name=self.name + "_skillmem",
            encoder=encoder,
            capacity=10,
            num_memories_retrieved=1,
            forgetting_algorithm=False,
        )

        # Used to keep track of queried memories for data collection
        assert env_dict, "env_dict must be provided"

        # set up memory variables if skills are added
        # TODO: TEMPORARY SOLUTION.
        loaded_skills = load_js_files(PROGRAM_DIR)
        skills += loaded_skills
        self.skills = skills
        self.add(skills)
        i = 0
        while len(self.memories) < len(skills):
            time.sleep(0.01)
            if i > 100:
                raise Exception("SkillManager failed to initialize")
        # initialize the buffer
        # Retrieve the top 3 memories
        self.update_skill_buffer(init_query, num_memories_retrieved=3)
        while len(self.buffer) < 1:
            time.sleep(0.01)
            if i > 100:
                raise Exception("Skill buffer failed to initialize")



    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables."""
        return self.memory_keys
    
    @property
    def memories(self) -> List[str]:
        """Returns list of keys of memories."""
        return self.skillmem.items

    def update(self, new_summary=None, is_last=False, no_summary=False) -> None:
        pass

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        self.memory_vars.update({"memory": "\n".join(self.skillmem.items)})

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        pass

    def summarize(self) -> None:
        pass

    def add(self, skills: List[SkillItem]) -> None:
        """
        Variables:
        - `skills` is a dictionary of dictionaries. The values of this dictionary are
        are skill details
        """
        for skill in skills:            
            self.skillmem.add(memory_or_key=skill["key"], value=skill)
            self.skill_dict[skill["key"]] = skill

    def query(self, query: str, num_memories_retrieved: str = 1) -> List[SkillItem]:
        """
        A query is used to retrieve the top k key-value memories.
        The keys are returned. The corresponding memories are stored in a buffer
        for later key-value retrieval.
        """       
        buffer: List[SkillItem] = self.skillmem.query(text=query, num_memories_retrieved=num_memories_retrieved)

        # remove duplicates - TODO: a hacky fix given that the query can sometimes return duplicates
        seen_keys = set()
        new_buffer = []

        for dictionary in buffer:
            # Check if any key in the current dictionary has been seen before
            if dictionary["key"] not in seen_keys:
                new_buffer.append(dictionary)
                seen_keys.add(dictionary["key"])

        return new_buffer
    
    def update_skill_buffer(self, query: str, num_memories_retrieved: str = 1) -> None:
        """
        Updates the skill buffer based on the query, does so by calling the query function.
        """
        buffer = self.query(query, num_memories_retrieved)
        self.buffer = buffer

    def get_buffer(self) -> List[SkillItem]:
        return self.buffer


    def get_buffer_keys(self) -> List[str]:
        return [item["key"] for item in self.buffer]

    def get_buffer_value(self, key: str):
        return self.skill_dict.get(key)
    
    def skill_set(self):
        return set(self.skill_dict.keys())

    def clear(self) -> None:
        """Clear memory contents."""
        self.skillmem.clear()
        self.skill_dict = {}
