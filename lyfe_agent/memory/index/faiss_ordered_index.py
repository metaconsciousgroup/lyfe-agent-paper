import numpy as np

from faiss import IndexFlatL2, IndexIDMap2
from typing import Any, List


class FAISSOrderedIndex:
    def __init__(
        self, memories: List = [], size: int = 100, encoder: Any = None
    ):  # MUST FIX ENCODER
        self.size = size
        self._str_index = [""] * self.size
        self.encoder = encoder

        if encoder:
            self.dim = encoder.dim
            index = IndexFlatL2(self.dim)
            ids = np.arange(self.size)
            self._embd_index = IndexIDMap2(index)

        assert (
            len(memories) <= size
        ), "number of memory items must not exceed memory size"
        self.full = False
        self._pointer = 0
        # can be made more efficient
        for memory in memories:
            self.add(memory)

    @property
    def items(self) -> List[str]:
        if self.full:
            return self._str_index[self._pointer :] + self._str_index[: self._pointer]
        else:
            return self._str_index[: self._pointer]

    def __len__(self) -> int:
        if self.full:
            return self.size
        else:
            return self._pointer

    def add(self, text: str) -> None:
        if self._pointer >= self.size:
            self._pointer = 0
        self._str_index[self._pointer] = text

        # add embedding
        if self.encoder:
            embedding = self.encoder(text).reshape((1, self.dim))
            if self.full:
                # must remove via pointer if full
                self._embd_index.remove_ids(np.array([self._pointer]))
            self._embd_index.add_with_ids(embedding, np.array([self._pointer]))
        self._pointer += 1
        if self._pointer == self.size:
            self.full = True

    def query(self, text: str, k: int) -> List[str]:
        assert self.encoder, "this instance does not have an encoder, cannot use query"
        query_embedding = self.encoder(text).reshape((1, self.dim))
        _, I = self._embd_index.search(query_embedding, k=k)
        return "\n".join([self._str_index[i] for i in I[0]])