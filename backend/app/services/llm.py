"""LLM summary generation via OpenAI-compatible API (Ollama or OpenAI)."""

from typing import List

from openai import OpenAI

from app.config import settings

_client: OpenAI | None = None

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


def _get_client() -> OpenAI:
    """Return a singleton OpenAI-compatible client."""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )
    return _client


def generate_summary(chunks: List[str], focus_prompt: str | None = None) -> str:
    """
    Generate a structured markdown summary from retrieved chunks.

    Args:
        chunks: Retrieved document excerpts.
        focus_prompt: Optional user emphasis for the summary.

    Returns:
        Markdown-formatted summary text.
    """
    client = _get_client()
    context = "\n\n---\n\n".join(chunks)
    user_content = f"Here are the relevant document excerpts:\n\n{context}"
    if focus_prompt:
        user_content += f"\n\nUser focus area: {focus_prompt}"
    user_content += "\n\nGenerate the structured summary now."

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
