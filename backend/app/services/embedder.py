"""
Stores document chunks in ChromaDB and runs similarity search per session.
"""

from typing import Any, Dict, List

import chromadb
from chromadb.api import ClientAPI
from chromadb.utils import embedding_functions

import shutil

from app.config import settings

_client: ClientAPI | None = None
_embedding_function = None


def _get_client() -> ClientAPI:
    """
    Returns a shared persistent ChromaDB client for the application.

    Returns:
        ClientAPI: Initialized Chroma client bound to the configured data path.
    """
    global _client
    if _client is None:
        path = settings.chroma_path()
        path.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(path))
    return _client


def _collection_name(session_id: str) -> str:
    """
    Builds a Chroma-safe collection name for a user session.

    Args:
        session_id (str): Session identifier from ingest.

    Returns:
        str: Collection name scoped to that session.
    """
    return f"session-{session_id.replace('_', '-')}"


def _get_embedding_function():
    """
    Creates the sentence-transformers embedding function used by Chroma.

    Returns:
        SentenceTransformerEmbeddingFunction: Embedding function for upsert and query.
    """
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model,
        )
    return _embedding_function


def upsert_chunks(session_id: str, chunks: List[Dict[str, Any]]) -> int:
    """
    Writes or updates document chunks in the session vector collection.

    Args:
        session_id (str): Session identifier from ingest.
        chunks (List[Dict[str, Any]]): Chunk dicts with id, text, and metadata.

    Returns:
        int: Number of chunks stored.
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
    Finds the most relevant chunk texts for a natural-language query.

    Args:
        session_id (str): Session identifier from ingest.
        query_text (str): Search phrase used for similarity ranking.
        top_k (int | None): Maximum chunks to return. Uses settings when omitted.

    Returns:
        List[str]: Matching chunk bodies ordered by relevance.
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
    Lists unique source filenames referenced in a session collection.

    Args:
        session_id (str): Session identifier from ingest.

    Returns:
        List[str]: Sorted filenames found in chunk metadata.
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
    """
    Removes session collection, uploaded files, and output PDF reports.

    Args:
        session_id (str): Session identifier to delete.

    Returns:
        None
    """
    # 1. Delete ChromaDB collection
    try:
        client = _get_client()
        client.delete_collection(_collection_name(session_id))
    except Exception:
        pass

    # 2. Delete uploads folder
    upload_dir = settings.upload_path() / session_id
    if upload_dir.exists() and upload_dir.is_dir():
        try:
            shutil.rmtree(upload_dir)
        except Exception:
            pass

    # 3. Delete output PDF
    pdf_filename = f"summary_{session_id}.pdf"
    pdf_path = settings.output_path() / pdf_filename
    if pdf_path.exists() and pdf_path.is_file():
        try:
            pdf_path.unlink()
        except Exception:
            pass
