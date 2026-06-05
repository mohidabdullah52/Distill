"""
Resolves and validates LLM provider settings for ChatGPT, Gemini, and Ollama.
"""

from dataclasses import dataclass
from typing import Literal

from app.config import Settings, settings

LLMProvider = Literal["openai", "gemini", "ollama"]

OPENAI_DEFAULT_BASE_URL = "https://api.openai.com/v1"
GEMINI_DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434/v1"


@dataclass(frozen=True)
class ResolvedLLMConfig:
    """
    Connection details needed to call the active language model.

    Attributes:
        provider (str): Provider key, such as openai or gemini.
        base_url (str): OpenAI-compatible API base URL.
        api_key (str): Credential sent with each request.
        model (str): Model identifier used for chat completions.
    """

    provider: str
    base_url: str
    api_key: str
    model: str


def _provider_name(cfg: Settings) -> LLMProvider:
    """
    Reads and validates the configured LLM provider from settings.

    Args:
        cfg (Settings): Application settings instance.

    Returns:
        LLMProvider: One of openai, gemini, or ollama.

    Raises:
        ValueError: If the provider name is not supported.
    """
    provider = cfg.llm_provider.strip().lower()
    if provider not in ("openai", "gemini", "ollama"):
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{provider}'. "
            "Use: openai, gemini, or ollama."
        )
    return provider  # type: ignore[return-value]


def resolve_llm_config(cfg: Settings | None = None) -> ResolvedLLMConfig:
    """
    Builds the URL, API key, and model for the selected LLM provider.

    Args:
        cfg (Settings | None): Settings to use. Defaults to the global instance.

    Returns:
        ResolvedLLMConfig: Ready-to-use connection details for the LLM client.
    """
    cfg = cfg or settings
    provider = _provider_name(cfg)

    if cfg.llm_base_url and cfg.llm_api_key and cfg.llm_model:
        return ResolvedLLMConfig(
            provider=provider,
            base_url=cfg.llm_base_url,
            api_key=cfg.llm_api_key,
            model=cfg.llm_model,
        )

    if provider == "openai":
        return ResolvedLLMConfig(
            provider=provider,
            base_url=cfg.llm_base_url or OPENAI_DEFAULT_BASE_URL,
            api_key=cfg.llm_api_key or cfg.openai_api_key,
            model=cfg.llm_model or cfg.openai_model,
        )
    if provider == "gemini":
        return ResolvedLLMConfig(
            provider=provider,
            base_url=cfg.llm_base_url or GEMINI_DEFAULT_BASE_URL,
            api_key=cfg.llm_api_key or cfg.gemini_api_key,
            model=cfg.llm_model or cfg.gemini_model,
        )
    return ResolvedLLMConfig(
        provider=provider,
        base_url=cfg.llm_base_url or cfg.ollama_base_url,
        api_key=cfg.llm_api_key or "ollama",
        model=cfg.llm_model or cfg.ollama_model,
    )


def validate_llm_config(cfg: Settings | None = None) -> None:
    """
    Checks that cloud providers have an API key before summarization runs.

    Args:
        cfg (Settings | None): Settings to use. Defaults to the global instance.

    Returns:
        None

    Raises:
        ValueError: If OpenAI or Gemini is selected without an API key.
    """
    resolved = resolve_llm_config(cfg)
    if resolved.provider == "openai" and not resolved.api_key.strip():
        raise ValueError(
            "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
            "Set it in .env (see .env.example)."
        )
    if resolved.provider == "gemini" and not resolved.api_key.strip():
        raise ValueError(
            "GEMINI_API_KEY is required when LLM_PROVIDER=gemini. "
            "Set it in .env (see .env.example)."
        )
