"""
Tests for text chunking.
"""

import pytest
from app.services.chunker import chunk_pages


def test_chunk_pages_happy_path(sample_pages) -> None:
    """
    Verifies parsed pages are split into chunks with expected metadata.

    Args:
        sample_pages (list): Fixture providing sample page tuples.

    Returns:
        None
    """
    chunks = chunk_pages(sample_pages, chunk_size=40, chunk_overlap=10)

    assert len(chunks) >= 1
    assert chunks[0]["metadata"]["source"] == "report.pdf"
    assert chunks[0]["metadata"]["page"] == 1
    assert "id" in chunks[0]
    assert chunks[0]["text"]


def test_chunk_pages_empty_input() -> None:
    """
    Verifies an empty page list produces no chunks.

    Returns:
        None
    """
    assert chunk_pages([]) == []


def test_chunk_pages_overlap_validation() -> None:
    """
    Verifies that passing chunk_overlap >= chunk_size raises a ValueError.
    """
    with pytest.raises(ValueError, match="chunk_overlap must be less than chunk_size"):
        chunk_pages([("report.pdf", 1, "test text")], chunk_size=10, chunk_overlap=10)


def test_chunk_pages_smart_boundaries() -> None:
    """
    Verifies that chunk_pages splits on sentence or whitespace boundaries near the limit.
    """
    text = "This is a long sentence. Here is another sentence. And a third one."
    chunks = chunk_pages([("report.pdf", 1, text)], chunk_size=30, chunk_overlap=5)
    
    assert len(chunks) >= 2
    assert chunks[0]["text"] == "This is a long sentence."
    assert "Here is another sentence." in chunks[1]["text"]


