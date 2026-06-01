"""ChromaDB persistence and vector search with sentence-transformers."""

from typing import Any, Dict, List

import chromadb
from chromadb.api import ClientAPI
from chromadb.utils import embedding_functions

from app.config import settings

_client: ClientAPI | None = None


def _get_client() -> ClientAPI:
    """Return a singleton persistent ChromaDB client."""
    global _client
    if _client is None:
        path = settings.chroma_path()
        path.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(path))
    return _client


def _collection_name(session_id: str) -> str:
    """Build a valid Chroma collection name for a session."""
    return f"session-{session_id.replace('_', '-')}"


def _get_embedding_function():
    """Return the sentence-transformers embedding function."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2",
    )


def upsert_chunks(session_id: str, chunks: List[Dict[str, Any]]) -> int:
    """
    Insert or update chunks in a session-scoped ChromaDB collection.

    Returns:
        Number of chunks upserted.
    """
    client = _get_client()
    ef = _get_embedding_function()
    collection = client.get_or_create_collection(
        name=_collection_name(session_id),
        embedding_function=ef,
    )
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    return len(chunks)


def query_chunks(session_id: str, query_text: str, top_k: int | None = None) -> List[str]:
    """
    Query the session collection for the most relevant chunk texts.

    Returns:
        Flat list of document strings.
    """
    k = top_k or settings.top_k_chunks
    client = _get_client()
    ef = _get_embedding_function()
    collection = client.get_collection(
        name=_collection_name(session_id),
        embedding_function=ef,
    )
    results = collection.query(query_texts=[query_text], n_results=k)
    return results["documents"][0]


def get_source_files(session_id: str) -> List[str]:
    """
    Return unique source filenames stored in session metadata.

    Returns:
        Sorted list of source file names.
    """
    client = _get_client()
    ef = _get_embedding_function()
    collection = client.get_collection(
        name=_collection_name(session_id),
        embedding_function=ef,
    )
    result = collection.get(include=["metadatas"])
    sources = {
        meta["source"]
        for meta in result.get("metadatas", [])
        if meta and "source" in meta
    }
    return sorted(sources)


def delete_session(session_id: str) -> None:
    """Best-effort deletion of a session collection."""
    try:
        client = _get_client()
        client.delete_collection(_collection_name(session_id))
    except Exception:
        pass
