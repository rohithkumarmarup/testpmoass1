from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import numpy as np
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings

from .config import EMBEDDING_MODEL_NAME, USE_HF_ENDPOINT_EMBEDDINGS


_EMBEDDINGS: Embeddings | None = None


def get_embeddings() -> Embeddings:
    """
    Lazy-load embeddings implementation.

    - Default: local embeddings via `HuggingFaceEmbeddings` (sentence-transformers on your machine)
    - Optional: endpoint embeddings via `HuggingFaceEndpointEmbeddings` (requires HF API key)
    """
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        if USE_HF_ENDPOINT_EMBEDDINGS:
            _EMBEDDINGS = HuggingFaceEndpointEmbeddings(
                model=EMBEDDING_MODEL_NAME,
                task="feature-extraction",
            )
        else:
            _EMBEDDINGS = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return _EMBEDDINGS


def embed_texts(texts: Sequence[str]) -> np.ndarray:
    """
    Compute embeddings for a list of texts.
    """
    emb = get_embeddings()
    vecs = emb.embed_documents(list(texts))
    return np.array(vecs, dtype=np.float32)


def cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity matrix between two embedding matrices.
    """
    # Normalize
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-10)
    return np.dot(a_norm, b_norm.T)


@dataclass
class RetrievedChunk:
    text: str
    score: float
    index: int


def semantic_search(
    query: str,
    documents: Sequence[str],
    k: int = 5,
) -> List[RetrievedChunk]:
    """
    Simple in-memory semantic search over a small list of documents.
    """
    if not documents:
        return []

    emb = get_embeddings()
    doc_embeddings = np.array(emb.embed_documents(list(documents)), dtype=np.float32)
    query_embedding = np.array(emb.embed_query(query), dtype=np.float32)

    sims = cosine_sim_matrix(query_embedding[None, :], doc_embeddings)[0]
    top_idx = np.argsort(-sims)[:k]

    return [
        RetrievedChunk(text=documents[i], score=float(sims[i]), index=int(i))
        for i in top_idx
    ]

