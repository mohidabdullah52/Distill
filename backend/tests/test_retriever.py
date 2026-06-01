"""Tests for multi-query retrieval."""

from unittest.mock import patch

from app.services.retriever import retrieve_for_summary


def test_retrieve_deduplicates_chunks() -> None:
    """Happy path: duplicate chunks across queries are merged once."""

    def mock_query(_session_id: str, query: str, top_k: int | None = None) -> list[str]:
        if "main topic" in query:
            return ["chunk A", "chunk B"]
        if "key findings" in query:
            return ["chunk B", "chunk C"]
        return []

    with patch("app.services.retriever.query_chunks", side_effect=mock_query):
        result = retrieve_for_summary("session1")

    assert result == ["chunk A", "chunk B", "chunk C"]


def test_retrieve_includes_focus_prompt_query() -> None:
    """Edge case: focus prompt adds an extra retrieval query."""
    with patch(
        "app.services.retriever.query_chunks",
        return_value=["focused chunk"],
    ) as mock_query:
        result = retrieve_for_summary("session1", focus_prompt="financial risks")

    assert result == ["focused chunk"]
    assert any("financial risks" in str(call) for call in mock_query.call_args_list)
