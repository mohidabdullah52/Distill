"""
Tests for ChromaDB embedder with mocked clients.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services import embedder


@pytest.fixture(autouse=True)
def reset_embedder_client():
    """
    Clears the embedder singleton before and after each test.

    Yields:
        None
    """
    embedder._client = None
    yield
    embedder._client = None


def test_upsert_chunks_calls_collection() -> None:
    """
    Verifies chunk upsert delegates to the Chroma collection API.

    Returns:
        None
    """
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
    """
    Verifies a missing collection surfaces as an error from Chroma.

    Returns:
        None
    """
    mock_client = MagicMock()
    mock_client.get_collection.side_effect = Exception("Collection not found")

    with patch.object(embedder, "_get_client", return_value=mock_client), patch.object(
        embedder, "_get_embedding_function", return_value=MagicMock()
    ):
        with pytest.raises(Exception, match="Collection not found"):
            embedder.query_chunks("missing", "query")
