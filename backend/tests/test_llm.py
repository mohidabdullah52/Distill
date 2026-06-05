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


@patch("app.services.llm.validate_llm_config")
@patch("app.services.llm.resolve_llm_config", return_value=_MOCK_LLM_CONFIG)
@patch("app.services.llm._get_client")
def test_generate_summary_context_truncation(
    mock_get_client, _mock_resolve, _mock_validate
) -> None:
    """
    Verifies that chunks exceeding the character budget are truncated.
    """
    mock_message = MagicMock()
    mock_message.content = "Summary"

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    from app.config import settings
    original_max = settings.max_context_chars
    settings.max_context_chars = 10
    try:
        # "chunk1" is 6 chars, total 6.
        # "chunk2" is 6 chars, which would make total 12. Since 12 > 10, it should truncate.
        llm.generate_summary(["chunk1", "chunk2"])
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        user_msg = call_kwargs["messages"][1]["content"]
        assert "chunk1" in user_msg
        assert "chunk2" not in user_msg
    finally:
        settings.max_context_chars = original_max
