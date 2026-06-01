"""Tests for ChromaDB embedder (mocked)."""

from unittest.mock import MagicMock, patch

import pytest

from app.services import embedder


@pytest.fixture(autouse=True)
def reset_embedder_client():
    """Reset singleton client between tests."""
    embedder._client = None
    yield
    embedder._client = None


def test_upsert_chunks_calls_collection() -> None:
    """Happy path: upsert delegates to Chroma collection."""
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection

    chunks = [
        {
            "id": "a__p1__c0",
            "text": "sample",
            "metadata": {"source": "a.pdf", "page": 1},
        }
    ]

    with patch.object(embedder, "_get_client", return_value=mock_client), patch.object(
        embedder, "_get_embedding_function", return_value=MagicMock()
    ):
        count = embedder.upsert_chunks("abc123", chunks)

    assert count == 1
    mock_collection.upsert.assert_called_once()


def test_query_chunks_missing_session_raises() -> None:
    """Edge case: missing collection propagates error."""
    mock_client = MagicMock()
    mock_client.get_collection.side_effect = Exception("Collection not found")

    with patch.object(embedder, "_get_client", return_value=mock_client), patch.object(
        embedder, "_get_embedding_function", return_value=MagicMock()
    ):
        with pytest.raises(Exception, match="Collection not found"):
            embedder.query_chunks("missing", "query")
