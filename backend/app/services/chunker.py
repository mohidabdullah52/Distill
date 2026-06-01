"""Sliding-window text chunking for vector indexing."""

from typing import Any, Dict, List

from app.config import settings
from app.services.parser import PageTuple


def chunk_pages(
    pages: List[PageTuple],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[Dict[str, Any]]:
    """
    Split page text into overlapping chunks ready for ChromaDB.

    Args:
        pages: List of (source, page_num, text) tuples from the parser.
        chunk_size: Optional override for chunk character length.
        chunk_overlap: Optional override for overlap between chunks.

    Returns:
        List of dicts with id, text, and metadata keys.
    """
    size = chunk_size or settings.chunk_size
    overlap = chunk_overlap or settings.chunk_overlap

    chunks: List[Dict[str, Any]] = []
    chunk_id = 0

    for source, page_num, text in pages:
        start = 0
        while start < len(text):
            end = start + size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    {
                        "id": f"{source}__p{page_num}__c{chunk_id}",
                        "text": chunk_text,
                        "metadata": {
                            "source": source,
                            "page": page_num,
                        },
                    }
                )
                chunk_id += 1
            start += size - overlap

    return chunks
