from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from langchain.schema import BaseMemory


class AbstractMemoryManager(BaseMemory, ABC):
# class AbstractMemoryManager:

    """
    Abstract class for managing memories.
    The `MemoryManager` is an abstract class that outlines the structure for a custom memory manager. Its main purpose is to decide the rules for updating memories to different advanced memories, and to add incoming memories based on their information (tags etc).
    """

    @abstractmethod
    def update(self) -> None:
        """
        Method called during `slow_forward`, corresponding to conscious reflection.
        This method needs to be implemented to detail how your Memory Manager
        should handle updates.
        """
        pass

    @abstractmethod
    def summarize(self, memory_from: str, memory_to: str) -> str:
        """
        Summarizes a memory and adds it to another memory (usually into a more advanced memory type).
        The specifics of how this summarization happens need to be implemented.
        """
        pass

    @abstractmethod
    def add(self, time: Optional[str], content: str) -> None:
        """
        Adds new memories to the buffer.
        This method needs to specify how this addition should take place.
        This function is not a strong requirement, but it is recommended to implement it.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clears the memory contents.
        The specifics of how this clearing happens need to be implemented.
        """
        pass

    @abstractmethod
    def query(self, memory_key: str, text: str, k: int = 1) -> List[str]:
        """
        Queries a specific memory module.
        For memory retrieval, this method needs to be implemented
        and cohere with the memory module's query method.
        """
        pass

    @abstractmethod
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns the history buffer.
        This function is an override of the `load_memory_variables`
        method from LangChain BaseMemory class. This method needs to be implemented
        to return the memory content in the format of a dictionary so that LLMChain
        can take it as input for prompt generation.
        """
        pass
