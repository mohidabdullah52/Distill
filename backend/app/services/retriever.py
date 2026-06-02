"""
Runs several semantic searches and merges the results for summarization.
"""

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
    Gathers unique chunks by querying the vector store from multiple angles.

    Args:
        session_id (str): Session identifier from ingest.
        focus_prompt (str | None): Extra query text when the user sets a focus area.

    Returns:
        List[str]: Deduplicated chunk texts ranked for summary context.
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
