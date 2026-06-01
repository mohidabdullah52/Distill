"""Tests for LLM summary generation (mocked)."""

from unittest.mock import MagicMock, patch

from app.services import llm


def test_generate_summary_returns_content() -> None:
    """Happy path: mocked LLM returns summary text."""
    mock_message = MagicMock()
    mock_message.content = "## Executive Summary\n\nTest summary."

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch.object(llm, "_get_client", return_value=mock_client):
        result = llm.generate_summary(["chunk one", "chunk two"], "finance")

    assert "Executive Summary" in result
    mock_client.chat.completions.create.assert_called_once()


def test_generate_summary_empty_chunks() -> None:
    """Edge case: empty chunk list still calls the LLM."""
    mock_message = MagicMock()
    mock_message.content = "## Executive Summary\n\nNo content."

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch.object(llm, "_get_client", return_value=mock_client):
        result = llm.generate_summary([])

    assert result.startswith("##")
