import logging
import random
from lyfe_agent.utils.encoder_utils import EncoderManager, BaseEmbeddingMemory
from typing import Any, List
from lyfe_agent.utils.log_utils import get_colored_text
from lyfe_agent.memory.memory_utils import retrieve
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Union, Any, Optional

# import logger  # Uncomment this line if you actually use logger
logger = logging.getLogger(__name__)


class MemoryStore:
    """Buffer for storing arbitrary memories."""

    def __init__(
        self,
        buffer: List[Dict[str, Union[str, Dict[str, Any]]]] = None,
        encoder: Any = None,
        capacity: int = 1_000,
        metadata_types: List[str] = None,
        name=None,
    ):
        logger.debug(f"Initializing MemoryStore {name}...")
        self.name = name
        self.capacity = capacity
        self.metadata_type = metadata_types
        self.memory_bank = buffer or []

        assert encoder is None, "encoder must be None"
        assert (
            len(self.memory_bank) <= self.capacity
        ), "Memory count must not exceed capacity"

        self.is_summarizing = False

    @property
    def items(self) -> List[str]:
        return [item["content"] for item in self.memory_bank]

    @property
    def size(self) -> int:
        return len(self.memory_bank)

    def add(
        self, memory: str, memory_type: str = "generic", in_world_time: str = None
    ) -> None:
        """Add a memory to the buffer."""

        assert (
            memory_type in self.metadata_type
        ), "memory_type must be one of the following: {}".format(self.metadata_type)
        # Create metadata
        metadata = {
            "in_world_time": in_world_time,
            "type": memory_type,
        }

        # Form the memory
        new_memory = {"content": memory, "metadata": metadata}

        # Add memory to bank or remove the oldest one if capacity is reached
        if len(self.memory_bank) >= self.capacity:
            self.memory_bank.pop(0)
        self.memory_bank.append(new_memory)

    def clear(self) -> None:
        """Clear all memories, but keep the last one."""
        self.memory_bank = self.memory_bank[-1:]



# TODO: We'll need to simplify this class. Now it has forgetting and pinecone support all together.
class EmbeddingMemory(BaseEmbeddingMemory):
    """Buffer for storing memories with embeddings."""

    def __init__(
        self,
        encoder: EncoderManager = None,
        capacity: int = 1_000,
        num_memories_retrieved: int = 2,
        forgetting_algorithm=True,
        forgetting_threshold: float = 0.9,
        name=None,
        memory_type: Any = None,
    ):
        super().__init__()
        logger.debug(f"Initializing EmbeddingMemory {name}...")

        # Basic properties
        self.agent_name = name
        self.encoder = encoder
        self.capacity = capacity
        self.num_memories_retrieved = num_memories_retrieved
        self.forgetting_algorithm = forgetting_algorithm
        self.forgetting_threshold = forgetting_threshold

        self.counter = 0
        self._last_item = None

        # Memory info
        self.memory_type = memory_type

        # Classic local memory
        self.memory_bank = []
        self.embeddings = []

        self.is_summarizing = False

    @property
    def items(self) -> List[str]:
        return self.memory_bank

    @property
    def items_embeddings(self) -> List[str]:
        return self.embeddings

    @property
    def size(self) -> int:
        return len(self.memory_bank)

    # Forgetting algorithm
    def _update_memory_bank(self, new_embedding, new_memory_content):
        """Update memory bank by removing similar memories based on embeddings."""
        similarities = cosine_similarity(
            new_embedding.reshape(1, -1), self.embeddings
        )
        # Find indices of similar memories (similarities above or equal to the threshold)
        similar_indices = [
            i
            for i, value in enumerate(similarities[0])
            if value >= self.forgetting_threshold
        ]

        # Remove the similar memories and embeddings based on their indices
        for index in sorted(similar_indices, reverse=True):
            del self.memory_bank[index]
            del self.embeddings[index]

    def add(self, memory_or_key: str, value: Any = None) -> None:
        """Add a memory to the memory bank.
        
        Args:
            memory_or_key (str): Memory content or key to be encoded.
            value (Any): Value to be stored in memory. If None, memory_or_key is stored.
        """
        if len(self.memory_bank) == self.capacity:
            with self.lock:
                self.memory_bank.pop(0)
                self.embeddings.pop(0)

        logger.debug(f"Queueing memory to {self.agent_name} module")
        value = value if value is not None else memory_or_key
        # Encoder will encode memory and add it to self
        self.encoder.queue_mem(module=self, key=memory_or_key, value=value)
        logger.debug(f"Adding memory: {get_colored_text(text=memory_or_key, color='blue')}")

    def fill_encoder_memories(self, embedding, memory_content):
        """Add memories that come from encoder."""
        if self.forgetting_algorithm and self.memory_bank:
            self._update_memory_bank(embedding, memory_content)

        self.memory_bank.append(memory_content)
        self.embeddings.append(embedding)

    def query(self, text: str, num_memories_retrieved: int = 1, timeout=5.0) -> List[str]:
        """Retrieve memories based on query content."""
        if not isinstance(self.encoder, EncoderManager):
            self.encoder.queue_query(self, text)
            results = self.retrieve(num_memories_retrieved)
            logger.debug(
                f"Query result: {get_colored_text(text=str(results), color='blue')}"
            )
            return results

        self._async_query(text)

        if not self.query_event.wait(timeout):
            logger.warning(
                f"Query {text} timed out after {timeout} seconds. Returning empty list."
            )
            return list()

        results = self.retrieve(num_memories_retrieved)
        logger.debug(
            f"[{self.agent_name}] Query result: {get_colored_text(text=str(results), color='blue')}"
        )

        return results

    def _async_query(self, text: str):
        self.query_event.clear()
        self.encoder.queue_query(self, text)

    def retrieve(self, num_memories_retrieved: int) -> List[str]:
        """Retrieve memories based on current query embeddings."""
        results = [
            memory
            for embed in self.query_embeddings
            for memory in retrieve(
                embed, self.embeddings, self.memory_bank, num_memories_retrieved
            )
        ]

        with self.lock:
            self.query_embeddings = []

        return results

    def clear(self) -> None:
        """Clear all memories and embeddings."""
        self.memory_bank = []
        self.embeddings = []
        self.query_embeddings = []


class PineconeEmbeddingMemory(BaseEmbeddingMemory):
    """Buffer for storing memories with embeddings using Pinecone VectorDB.
    
    Currently not maintained
    """

    def __init__(
        self,
        encoder: EncoderManager = None,
        capacity: int = 1_000,
        num_memories_retrieved: int = 2,
        forgetting_algorithm=True,
        forgetting_threshold: float = 0.9,
        name=None,
        memory_type: Any = None,
        memory_bank: Any = None,
        env_dict: Dict[str, str] = None,
    ):
        super().__init__()
        logger.debug(f"Initializing EmbeddingMemory {name}...")

        # Basic properties
        self.agent_name = name
        self.encoder = encoder
        self.capacity = capacity
        self.num_memories_retrieved = num_memories_retrieved
        self.forgetting_algorithm = forgetting_algorithm
        self.forgetting_threshold = forgetting_threshold

        self.counter = 0

        # Memory info
        self.memory_type = memory_type

        assert (env_dict != None and env_dict["PINECONE_APIKEY"])
        
        # Pinecone detected
        self.memory_bank = memory_bank
        self.ids = []
        self.pinecone = True

        self.is_summarizing = False

    @property
    def items(self) -> List[str]:
        content = self.memory_bank.fetch(self.ids, namespace="general-space")
        content = [
            vector_data["metadata"]["memory_content"]
            for vector_data in content["vectors"].values()
        ]
        return content

    @property
    def items_embeddings(self) -> List[str]:
        content = self.memory_bank.fetch(self.ids, namespace="general-space")
        content = [
            vector_data["metadata"]["values"]
            for vector_data in content["vectors"].values()
        ]
        return content

    @property
    def size(self) -> int:
        content = self.memory_bank.fetch(self.ids, namespace="general-space")
        content = [
            vector_data["metadata"]["memory_content"]
            for vector_data in content["vectors"].values()
        ]
        return len(content)

    # Forgetting algorithm
    def _update_memory_bank(self, new_embedding, new_memory_content):
        """Update memory bank by removing similar memories based on embeddings."""
        ids_to_forget = []

        results = self.memory_bank.query(
            queries=[new_embedding],
            top_k=self.capacity,
            include_metadata=True,
            filter={
                "agent_name": {"$eq": self.agent_name},
                "memory_type": {"$eq": self.memory_type},
            },
            namespace="general-space",
        )

        matches = results["results"][0]["matches"]
        for match in matches:
            if match["score"] < self.forgetting_threshold:
                break
            ids_to_forget.append(match["id"])

        if ids_to_forget:
            # content = self.memory_bank.fetch(ids_to_forget)
            # content = [vector_data['metadata']['memory_content'] for vector_data in content['vectors'].values()]
            self.memory_bank.delete(ids=ids_to_forget, namespace="general-space")
            self.ids = list(filter(lambda x: x not in ids_to_forget, self.ids))

    def add(self, memory: str) -> None:
        """Add a memory to the memory bank."""
        if len(self.ids) == self.capacity:
            with self.lock:
                self.memory_bank.delete(self.ids[0], namespace="general-space")
                self.ids.pop(0)

        logger.debug(f"Queueing memory to {self.agent_name} module")
        self.encoder.queue_mem(module=self, key=memory)
        logger.debug(f"Adding memory: {get_colored_text(text=memory, color='blue')}")

    def fill_encoder_memories(self, embedding, memory_content):
        """Add memories that come from encoder."""
        embedding = embedding.tolist()

        if self.forgetting_algorithm and self.ids:
            self._update_memory_bank(embedding, memory_content)

        # random index generator (probability two indexes are the same is 1 / 36!)
        index_generator = list("abcdefghijklmnopqrstuvwxyz1234567890")
        random.shuffle(index_generator)
        current_idx_to_fill = "".join(index_generator)

        self.ids.append(f"{current_idx_to_fill}")
        self.memory_bank.upsert(
            vectors=[
                (
                    f"{current_idx_to_fill}",
                    embedding,
                    {
                        "agent_name": self.agent_name,
                        "memory_type": self.memory_type,
                        "memory_content": memory_content,
                    },
                )
            ],
            namespace="general-space",
        )

    def query(self, text: str, num_memories_retrieved: int = 1, timeout=5.0) -> List[str]:
        """Retrieve memories based on query content."""

        if not isinstance(self.encoder, EncoderManager):
            self.encoder.queue_query(self, text)
            results = self.retrieve(num_memories_retrieved)
            logger.debug(
                f"Query result: {get_colored_text(text=str(results), color='blue')}"
            )
            return results

        self._async_query(text)

        if not self.query_event.wait(timeout):
            logger.warning(
                f"Query {text} timed out after {timeout} seconds. Returning empty list."
            )
            return []

        results = self.retrieve(num_memories_retrieved)
        logger.debug(
            f"Query result: {get_colored_text(text=str(results), color='blue')}"
        )

        return results

    def _async_query(self, text: str):
        self.query_event.clear()
        self.encoder.queue_query(self, text)

    def retrieve(self, num_memories_retrieved: int) -> List[str]:
        """Retrieve memories based on current query embeddings."""
        if self.query_embeddings:
            results = self.memory_bank.query(
                queries=self.query_embeddings,
                top_k=num_memories_retrieved,
                include_metadata=True,
                filter={
                    "agent_name": {"$eq": self.agent_name},
                    "memory_type": {"$eq": self.memory_type},
                },
                namespace="general-space",
            )
            results = [
                match["metadata"]["memory_content"]
                for result in results["results"]
                for match in result["matches"]
            ]

        with self.lock:
            self.query_embeddings = []

        return results

    def clear(self) -> None:
        """Clear all memories and embeddings."""
        with self.lock:
            self.memory_bank.delete(
                filter={
                    "agent_name": {"$eq": self.agent_name},
                    "memory_type": {"$eq": self.memory_type},
                },
                namespace="general-space",
            )
            self.query_embeddings = []