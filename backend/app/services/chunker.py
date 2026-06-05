import re
from typing import Any, Dict, List

from app.config import settings
from app.services.parser import PageTuple


def _find_split_point(text: str, start: int, size: int) -> int:
    """
    Finds a suitable end index for a chunk starting at 'start', with max length 'size'.
    Looks for sentence boundaries first, then paragraph/whitespace boundaries,
    and falls back to strict size.
    """
    if start + size >= len(text):
        return len(text)

    end_limit = start + size
    chunk_slice = text[start:end_limit]

    # Search window for lookback: 25% of chunk size
    lookback = min(int(size * 0.25), len(chunk_slice))
    if lookback <= 0:
        return end_limit

    search_str = chunk_slice[-lookback:]

    # 1. Search for sentence boundaries in search_str (e.g. '. ', '! ', '? ')
    sentence_matches = list(re.finditer(r"[\.\!\?]\s+", search_str))
    if sentence_matches:
        last_match = sentence_matches[-1]
        return end_limit - lookback + last_match.end()

    # 2. Search for paragraph boundaries (newlines)
    newline_matches = list(re.finditer(r"\n+", search_str))
    if newline_matches:
        last_match = newline_matches[-1]
        return end_limit - lookback + last_match.end()

    # 3. Search for whitespace (word boundary)
    space_matches = list(re.finditer(r"\s+", search_str))
    if space_matches:
        last_match = space_matches[-1]
        return end_limit - lookback + last_match.end()

    # Fallback to strict size
    return end_limit


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

    if overlap >= size:
        raise ValueError("chunk_overlap must be less than chunk_size")

    chunks: List[Dict[str, Any]] = []
    chunk_id = 0

    for source, page_num, text in pages:
        start = 0
        while start < len(text):
            end = _find_split_point(text, start, size)
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

            if end >= len(text):
                break

            next_start = end - overlap
            if next_start <= start:
                next_start = start + max(1, size - overlap)
            start = next_start

    return chunks
