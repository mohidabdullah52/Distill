"""
Splits extracted page text into overlapping chunks for vector search.
"""

from typing import Any, Dict, List

from app.config import settings
from app.services.parser import PageTuple


def chunk_pages(
    pages: List[PageTuple],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[Dict[str, Any]]:
    """
    Breaks page text into fixed-size overlapping segments for embedding.

    Args:
        pages (List[PageTuple]): Parsed pages from the document parser.
        chunk_size (int | None): Character length per chunk. Uses settings when omitted.
        chunk_overlap (int | None): Overlap between consecutive chunks.

    Returns:
        List[Dict[str, Any]]: Chunk records with id, text, and metadata fields.
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
