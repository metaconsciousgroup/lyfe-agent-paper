# imports here
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
from typing import Any, List

class OrderedIndex:
    def __init__(
        self, memories: List = [], size: int = 100, encoder: Any = None
    ):  # MUST FIX ENCODER
        self.size = size
        self.memory_bank = []
        self.encoder = encoder

        if encoder:
            self.dim = encoder.dim
            self.embeddings = []

        assert (
            len(memories) <= size
        ), "number of memory items must not exceed memory size"
        # can be made more efficient
        for memory in memories:
            self.add(memory)

    @property
    def items(self) -> List[str]:
        return self.memory_bank

    def __len__(self) -> int:
        return len(self.memory_bank)
    
    def add(self, text: str) -> None:
        if len(self.memory_bank) == self.size:
            self.memory_bank.pop(0)
            if self.encoder:  # Check if encoder is not None before performing embedding
                self.embeddings.pop(0)

        if self.encoder:  # Check if encoder is not None before performing embedding
            self.encoder.receive(self, text)
        #     embedding = self.encoder(text).reshape(1, self.dim)
        #     self.embeddings.append(embedding[0])

        # self.memory_bank.append(text)

    def _on_deliver(self, embeddings, documents):
        for embedding, document in zip(embeddings, documents):
            self.embeddings.append(embedding)
            self.memory_bank.append(document)        

    def query(self, text: str, k: int) -> List[str]:
        assert self.encoder, "this instance does not have an encoder, cannot use query"
        query_embedding = self.encoder(text).reshape(1, self.dim)
        cosine_similarities = cosine_similarity(
            query_embedding, np.array(self.embeddings)
        )[0]

        # Get indices of top k similarities
        I = np.argsort(cosine_similarities)[::-1][:k]
        I = np.sort(I)
        return "\n".join([self.memory_bank[i] for i in I])