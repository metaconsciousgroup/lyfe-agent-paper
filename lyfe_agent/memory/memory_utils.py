import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


def retrieve(
    query_embedding: List[float],
    doc_embeddings: Union[List[List[float]], List[np.ndarray]],
    documents: List[str],
    num_memories_retrieved: int,
) -> List[str]:
    """Retrieve the num_memories_retrieved most similar documents for a given query."""

    if not len(documents):
        logger.debug("No documents to retrieve from.")
        return []

    if len(doc_embeddings) != len(documents):
        raise ValueError("Mismatched lengths of document embeddings and documents")

    assert num_memories_retrieved > 0, "Must retrieve at least one document"

    try:
        query_embedding_np = np.array(query_embedding).reshape(1, -1)
        doc_embeddings_np = np.vstack(doc_embeddings)
    except ValueError:
        logger.warning("Error converting embeddings to numpy arrays.")
        return []

    if (
        np.isnan(query_embedding_np).any()
        or query_embedding_np.shape[1] != doc_embeddings_np.shape[1]
    ):
        logger.warning(
            "Mismatch between query and document embeddings' dimensions or invalid query embedding."
        )
        return []

    similarities = cosine_similarity(query_embedding_np, doc_embeddings_np).flatten()
    top_k_indices = similarities.argsort()[-num_memories_retrieved:][::-1]

    return [documents[i] for i in top_k_indices]
