"""
Tests for LLM provider configuration resolution and validation.
"""

import pytest

from app.config import Settings
from app.llm_config import (
    GEMINI_DEFAULT_BASE_URL,
    OPENAI_DEFAULT_BASE_URL,
    OLLAMA_DEFAULT_BASE_URL,
    ResolvedLLMConfig,
    resolve_llm_config,
    validate_llm_config,
)


def test_resolve_openai_config() -> None:
    """
    Verifies OpenAI settings map to the ChatGPT API defaults.

    Returns:
        None
    """
    cfg = Settings(
        llm_provider="openai",
        openai_api_key="sk-test",
        openai_model="gpt-4o",
    )
    resolved = resolve_llm_config(cfg)

    assert resolved == ResolvedLLMConfig(
        provider="openai",
        base_url=OPENAI_DEFAULT_BASE_URL,
        api_key="sk-test",
        model="gpt-4o",
    )


def test_resolve_gemini_config() -> None:
    """
    Verifies Gemini settings map to the Google OpenAI-compatible endpoint.

    Returns:
        None
    """
    cfg = Settings(
        llm_provider="gemini",
        gemini_api_key="gemini-test",
        gemini_model="gemini-2.0-flash",
    )
    resolved = resolve_llm_config(cfg)

    assert resolved == ResolvedLLMConfig(
        provider="gemini",
        base_url=GEMINI_DEFAULT_BASE_URL,
        api_key="gemini-test",
        model="gemini-2.0-flash",
    )


def test_resolve_ollama_config() -> None:
    """
    Verifies Ollama settings use local defaults without a cloud API key.

    Returns:
        None
    """
    cfg = Settings(llm_provider="ollama")
    resolved = resolve_llm_config(cfg)

    assert resolved.provider == "ollama"
    assert resolved.base_url == OLLAMA_DEFAULT_BASE_URL
    assert resolved.api_key == "ollama"
    assert resolved.model == "llama3"


def test_validate_openai_missing_key() -> None:
    """
    Verifies OpenAI validation fails when the API key is empty.

    Returns:
        None
    """
    cfg = Settings(llm_provider="openai", openai_api_key="")

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        validate_llm_config(cfg)


def test_validate_gemini_missing_key() -> None:
    """
    Verifies Gemini validation fails when the API key is blank.

    Returns:
        None
    """
    cfg = Settings(llm_provider="gemini", gemini_api_key="  ")

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        validate_llm_config(cfg)


def test_invalid_provider_raises() -> None:
    """
    Verifies an unknown provider name is rejected during resolution.

    Returns:
        None
    """
    cfg = Settings(llm_provider="anthropic")

    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
        resolve_llm_config(cfg)
