from abc import ABC, abstractmethod
from langchain.schema import BaseMemory
from typing import Any, Dict, List, Optional


class AbstractMemoryModule(ABC):
    def __init__(self, encoder):
        self.encoder = encoder
        
    def add(self, content: str) -> None:
        """
        This method is used to add new memories to the buffer. You need to implement this method to specify how the addition should take place.
        """
        self.encoder.receive(self, content)

    def query(self, text: str, k: int) -> List[str]:
        """
        This method is used to query the memory module and get desired memory based on customized criteria.
        """
        pass

    @abstractmethod
    def _on_deliver(self, documents, embeddings) -> None:
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear memory contents."""
        ...


class AbsMemoryModule(BaseMemory, ABC):
    """
    The `MemoryModule` is an abstract class that outlines the structure for a custom memory module. Its main purpose is to create a customized container for each different memory type, and define how to effectively query and update the memory contents.

    The class extends from the `BaseMemory` abstract class and further specifies the following main methods:

    """

    output_key: Optional[str] = None
    input_key: Optional[str] = None
    memory_key: str = "history"
    buffer: List = []
    encoder: Any = None
    k: int = 1_000  # basically unbounded by default

    @property
    @abstractmethod
    def memory_variables(self) -> List[str]:
        """
        This method is a property that will always return a list of memory variables. Usually it returns a list of memory keys.
        """
        pass

    @property
    @abstractmethod
    def data(self) -> List[str]:
        """
        A property that needs to be implemented to specify what data the memory module will contain.
        """
        pass

    @abstractmethod
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        This method is used to return the content in the current container. This function is an override of the `load_memory_variables` method from LangChain BaseMemory class. You need to implement this method to return the memory content in the format of a dictionary so that LLMChain can take it as input for prompt generation.
        """
        pass

    # @abstractmethod
    # def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
    #     """Save context from this conversation to buffer."""
    #     pass

    @abstractmethod
    def add(self, content: str) -> None:
        """
        This method is used to add new memories to the buffer. You need to implement this method to specify how the addition should take place.
        """
        pass

    @abstractmethod
    def query(self, text: str, k: int) -> List[str]:
        """
        This method is used to query the memory module and get desired memory based on customized criteria.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear memory contents."""
        pass


