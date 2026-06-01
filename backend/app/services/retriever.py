"""Multi-query retrieval for comprehensive summary context."""

from typing import List

from app.config import settings
from app.services.embedder import query_chunks

RETRIEVAL_QUERIES = [
    "main topic purpose objective",
    "key findings results conclusions",
    "important data statistics numbers dates",
    "recommendations action items next steps",
    "definitions concepts terminology",
]


def retrieve_for_summary(session_id: str, focus_prompt: str | None = None) -> List[str]:
    """
    Retrieve deduplicated chunks using multiple semantic query angles.

    Args:
        session_id: Ingest session identifier.
        focus_prompt: Optional user focus appended as an extra query.

    Returns:
        Deduplicated list of chunk texts.
    """
    queries = list(RETRIEVAL_QUERIES)
    if focus_prompt:
        queries.append(focus_prompt)

    per_query_k = max(3, settings.top_k_chunks // len(queries))
    seen: set[str] = set()
    retrieved: List[str] = []

    for query in queries:
        chunks = query_chunks(session_id, query, top_k=per_query_k)
        for chunk in chunks:
            if chunk not in seen:
                seen.add(chunk)
                retrieved.append(chunk)

    return retrieved
