"""LLM summary generation via OpenAI-compatible APIs (ChatGPT, Gemini, Ollama)."""

from typing import List

from openai import OpenAI

from app.llm_config import ResolvedLLMConfig, resolve_llm_config, validate_llm_config

_client: OpenAI | None = None
_client_signature: tuple[str, str, str] | None = None

SYSTEM_PROMPT = """You are an expert document analyst and technical writer.
Your task is to synthesize retrieved document chunks into a single, compact, well-structured summary.

Output format (use exactly these Markdown headings):
## Executive Summary
(2-4 sentences covering the main thesis / purpose)

## Key Findings & Insights
(bullet list, max 10 bullets, each 1-2 sentences)

## Important Details & Data
(any critical numbers, dates, names, statistics, formulas)

## Action Items / Recommendations
(if any exist in the source material; otherwise omit this section)

## Glossary
(define any domain-specific terms found; 3-8 entries; omit if not applicable)

Rules:
- Be concise. Cut filler. Every word must earn its place.
- Preserve factual accuracy. Do not hallucinate.
- If information repeats across chunks, consolidate — do not duplicate.
- Do not reference "the document" or "the chunks"; write as if authoring a summary report.
"""


def _client_key(config: ResolvedLLMConfig) -> tuple[str, str, str]:
    """Build a cache key for the OpenAI client singleton."""
    return (config.base_url, config.api_key, config.provider)


def _get_client() -> OpenAI:
    """Return a singleton OpenAI-compatible client for the active LLM provider."""
    global _client, _client_signature

    validate_llm_config()
    config = resolve_llm_config()
    signature = _client_key(config)

    if _client is None or _client_signature != signature:
        _client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )
        _client_signature = signature

    return _client


def get_active_llm_info() -> dict[str, str]:
    """
    Return non-secret metadata about the configured LLM (for health/debug).

    Returns:
        Dict with provider and model name.
    """
    config = resolve_llm_config()
    return {"provider": config.provider, "model": config.model}


def generate_summary(chunks: List[str], focus_prompt: str | None = None) -> str:
    """
    Generate a structured markdown summary from retrieved chunks.

    Args:
        chunks: Retrieved document excerpts.
        focus_prompt: Optional user emphasis for the summary.

    Returns:
        Markdown-formatted summary text.

    Raises:
        ValueError: If LLM credentials are not configured.
    """
    validate_llm_config()
    config = resolve_llm_config()
    client = _get_client()

    context = "\n\n---\n\n".join(chunks)
    user_content = f"Here are the relevant document excerpts:\n\n{context}"
    if focus_prompt:
        user_content += f"\n\nUser focus area: {focus_prompt}"
    user_content += "\n\nGenerate the structured summary now."

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned an empty summary.")
    return content.strip()
