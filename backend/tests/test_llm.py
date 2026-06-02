"""
Tests for LLM summary generation with mocked API calls.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.llm_config import ResolvedLLMConfig
from app.services import llm

_MOCK_LLM_CONFIG = ResolvedLLMConfig(
    provider="openai",
    base_url="https://api.openai.com/v1",
    api_key="sk-test",
    model="gpt-4o-mini",
)


@patch("app.services.llm.validate_llm_config")
@patch("app.services.llm.resolve_llm_config", return_value=_MOCK_LLM_CONFIG)
@patch("app.services.llm._get_client")
def test_generate_summary_returns_content(
    mock_get_client, _mock_resolve, _mock_validate
) -> None:
    """
    Verifies a mocked chat completion returns structured summary text.

    Args:
        mock_get_client (MagicMock): Patched OpenAI client factory.
        _mock_resolve (MagicMock): Patched config resolver.
        _mock_validate (MagicMock): Patched credential validation.

    Returns:
        None
    """
    mock_message = MagicMock()
    mock_message.content = "## Executive Summary\n\nTest summary."

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    result = llm.generate_summary(["chunk one", "chunk two"], "finance")

    assert "Executive Summary" in result
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["timeout"] == 120.0


@patch("app.services.llm.validate_llm_config")
@patch("app.services.llm.resolve_llm_config", return_value=_MOCK_LLM_CONFIG)
@patch("app.services.llm._get_client")
def test_generate_summary_empty_chunks(
    mock_get_client, _mock_resolve, _mock_validate
) -> None:
    """
    Verifies the LLM is still called when no chunks are provided.

    Args:
        mock_get_client (MagicMock): Patched OpenAI client factory.
        _mock_resolve (MagicMock): Patched config resolver.
        _mock_validate (MagicMock): Patched credential validation.

    Returns:
        None
    """
    mock_message = MagicMock()
    mock_message.content = "## Executive Summary\n\nNo content."

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    result = llm.generate_summary([])

    assert result.startswith("##")


@patch(
    "app.services.llm.validate_llm_config",
    side_effect=ValueError("OPENAI_API_KEY is required"),
)
def test_generate_summary_missing_api_key(_mock_validate) -> None:
    """
    Verifies missing credentials raise before any network call is made.

    Args:
        _mock_validate (MagicMock): Patched validation that raises.

    Returns:
        None
    """
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        llm.generate_summary(["chunk"])


@patch("app.services.llm.resolve_llm_config", return_value=_MOCK_LLM_CONFIG)
def test_get_active_llm_info(_mock_resolve) -> None:
    """
    Verifies health metadata includes provider and model without secrets.

    Args:
        _mock_resolve (MagicMock): Patched config resolver.

    Returns:
        None
    """
    info = llm.get_active_llm_info()

    assert info == {"provider": "openai", "model": "gpt-4o-mini"}
    assert "api_key" not in info
