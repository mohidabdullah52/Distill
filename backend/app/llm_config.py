"""LLM provider resolution and validation (patchable in tests)."""

from dataclasses import dataclass
from typing import Literal

from app.config import Settings, settings

LLMProvider = Literal["openai", "gemini", "ollama"]

OPENAI_DEFAULT_BASE_URL = "https://api.openai.com/v1"
GEMINI_DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434/v1"


@dataclass(frozen=True)
class ResolvedLLMConfig:
    """Resolved LLM connection settings for the active provider."""

    provider: str
    base_url: str
    api_key: str
    model: str


def _provider_name(cfg: Settings) -> LLMProvider:
    """Return validated provider name from settings."""
    provider = cfg.llm_provider.strip().lower()
    if provider not in ("openai", "gemini", "ollama"):
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{provider}'. "
            "Use: openai, gemini, or ollama."
        )
    return provider  # type: ignore[return-value]


def resolve_llm_config(cfg: Settings | None = None) -> ResolvedLLMConfig:
    """
    Resolve base URL, API key, and model for the configured LLM provider.

    Args:
        cfg: Optional settings instance (defaults to global settings).

    Returns:
        ResolvedLLMConfig for the active provider.
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
    Ensure API keys are present for cloud LLM providers.

    Args:
        cfg: Optional settings instance (defaults to global settings).

    Raises:
        ValueError: If required credentials are missing.
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
