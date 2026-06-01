"""Tests for text chunking."""

from app.services.chunker import chunk_pages


def test_chunk_pages_happy_path(sample_pages) -> None:
    """Happy path: pages produce chunks with metadata."""
    chunks = chunk_pages(sample_pages, chunk_size=40, chunk_overlap=10)

    assert len(chunks) >= 1
    assert chunks[0]["metadata"]["source"] == "report.pdf"
    assert chunks[0]["metadata"]["page"] == 1
    assert "id" in chunks[0]
    assert chunks[0]["text"]


def test_chunk_pages_empty_input() -> None:
    """Edge case: no pages yields no chunks."""
    assert chunk_pages([]) == []
