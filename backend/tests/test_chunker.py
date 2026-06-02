"""
Tests for text chunking.
"""

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
