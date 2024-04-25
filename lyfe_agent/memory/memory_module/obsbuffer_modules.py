import datetime
import logging
from lyfe_agent.memory.document import Document
from threading import Event, Lock
from typing import List, Dict, Union, Any, Optional

logger = logging.getLogger(__name__)


class ObsBuffer:
    """Buffer for storing observations with content and metadata."""

    def __init__(
        self,
        buffer: List[Dict[str, Union[str, Dict[str, Any]]]] = None,
        encoder: Any = None,
        capacity: int = 1_000,
        name=None,
    ):
        self.name = name
        self.capacity = capacity
        self.observation_bank = buffer or []
        self.delay = datetime.timedelta(minutes=1)

        # for embedding (query nomenclature comes from adhering to Encoder interface)
        self.encoder = encoder
        self.query_event = Event()
        self.query_embeddings = []
        self.lock = Lock()

        assert (
            len(self.observation_bank) <= self.capacity
        ), "Observation count must not exceed capacity"

    @property
    def items(self) -> List[str]:
        # return [item["content"] for item in self.observation_bank]
        return [item.content for item in self.observation_bank]

    @property
    def size(self) -> int:
        return len(self.observation_bank)

    # # TEMPORARY
    # def embed(self, document: Document, timeout=3.0):
    #     self.query_event.clear()
    #     # TODO: check if it is possible that the order of the documents is not preserved when embedding
    #     self.encoder.queue_query(self, document.content)

    #     # wait for query to return
    #     if not self.query_event.wait(timeout):
    #         logger.warning(
    #             f"Embed timed out after {timeout} seconds. Returning empty list."
    #         )

    #     # return embeddings
    #     document.metadata["embedding"] = None
    #     with self.lock:
    #         if self.query_embeddings:
    #             document.metadata["embedding"] = self.query_embeddings.pop(0)
    #     return document

    def add(
        self,
        document: str,
        obs_type: str = "audio",
        in_world_time: str = None,
    ) -> None:
        """Add an observation to the buffer."""
        # Ensure type is either 'audio' or 'visual'
        assert obs_type in [
            "audio",
            "visual",
            "spacial",
            "mental",
        ], f"obs_type must be within {['audio', 'visual', 'spacial', 'mental']}"

        # Create metadata
        metadata = {
            "in_world_time": in_world_time,
            "expire_time": datetime.datetime.now() + self.delay,
            "type": obs_type,
        }

        # observation = {"content": document, "metadata": metadata}
        observation = Document(content=document, metadata=metadata)

        # Add observation to bank or remove the oldest one if capacity is reached
        if len(self.observation_bank) >= self.capacity:
            self.observation_bank.pop(0)
        self.observation_bank.append(observation)

    def clear(self) -> None:
        """Clear all observations."""
        self.observation_bank = []

    def remove_expired(self) -> None:
        """Remove observations that are expired."""
        self.observation_bank = [
            observation
            for observation in self.observation_bank
            # if observation["metadata"]["expire_time"] > datetime.datetime.now()
            if observation.metadata["expire_time"] > datetime.datetime.now()
        ]

    def update(self) -> None:
        """Update the buffer to half-size."""
        self.remove_expired()
        self.observation_bank = self.observation_bank[-self.capacity // 2 :]
