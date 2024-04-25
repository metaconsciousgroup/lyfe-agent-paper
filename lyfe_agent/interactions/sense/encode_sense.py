import logging
import random

from threading import Lock
from typing import Optional

from lyfe_agent.base import BaseInteraction
from lyfe_agent.utils.encoder_utils import EncoderManager


logger = logging.getLogger(__name__)


# this is also like an embeddingmemory class
# Can consider merging with SenseInteraction later
class EncoderInteraction(BaseInteraction):
    expected_inputs = ["encoders"]

    def __init__(self, sources, targets, encoder_key="openai"):
        super().__init__(sources, targets)
        logger.debug(f"[{self.name}] Initializing encoder interaction with encoder key {encoder_key}")
        self.encoder: EncoderManager = self.encoders.models[encoder_key]
        self.embeddings = []
        self.memory_bank = []
        self.lock = Lock()
        self.key = "encoder_interaction"
        self.targets = targets

        # for downstream use
        self.pinecone = False

    def execute(self, observations: Optional[str] = None):
        if observations:
            logger.debug(f"[{self.name}] Encoding observations: {observations}")
            self.encoder.queue_mem(module=self, key=observations)

        # check pass on embeddings
        with self.lock:
            if self.embeddings:
                outputs = list(zip(self.memory_bank, self.embeddings))
                for target in self.targets:
                    target.receive({self.key: outputs})
                self.embeddings = []
                self.memory_bank = []

    # NOTE: this function is called in encoder_utils.py so the function name must be the same
    def fill_encoder_memories(self, embedding, memory_content):
        if self.pinecone:
            embedding = embedding.tolist()

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
        else:
            self.memory_bank.append(memory_content)
            self.embeddings.append(embedding)


from typing import Dict


class EncodeTalk(EncoderInteraction):
    """
    Encode talk from the agent.
    """

    def __init__(self, sources, targets, **kwargs):
        super().__init__(sources, targets)

    def execute(self, observations: Dict[str, str]):
        inputs = observations.get("talk", None)
        super().execute(inputs)
