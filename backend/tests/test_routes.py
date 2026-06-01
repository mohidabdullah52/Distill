"""Tests for FastAPI routes."""

from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Happy path: health check returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_no_files() -> None:
    """Edge case: ingest without files returns 400."""
    response = client.post("/api/ingest", files=[])
    assert response.status_code == 422


def test_ingest_unsupported_type() -> None:
    """Edge case: unsupported file extension returns 400."""
    response = client.post(
        "/api/ingest",
        files=[("files", ("notes.txt", BytesIO(b"hello"), "text/plain"))],
    )
    assert response.status_code == 400


@patch("app.routes.ingest.upsert_chunks", return_value=2)
@patch("app.routes.ingest.chunk_pages", return_value=[{"id": "x", "text": "t", "metadata": {}}])
@patch("app.routes.ingest.extract_text", return_value=[("a.pdf", 1, "text")])
def test_ingest_success(mock_extract, mock_chunk, mock_upsert) -> None:
    """Happy path: valid PDF upload returns session metadata."""
    response = client.post(
        "/api/ingest",
        files=[("files", ("report.pdf", BytesIO(b"%PDF"), "application/pdf"))],
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["total_chunks"] == 2


@patch("app.routes.summarize.markdown_to_pdf")
@patch("app.routes.summarize.get_source_files", return_value=["report.pdf"])
@patch("app.routes.summarize.generate_summary", return_value="## Executive Summary\n\nDone.")
@patch(
    "app.routes.summarize.retrieve_for_summary",
    return_value=["chunk"],
)
def test_summarize_success(mock_retrieve, mock_llm, mock_sources, mock_pdf) -> None:
    """Happy path: summarize returns download URL."""
    response = client.post(
        "/api/summarize",
        json={"session_id": "abc123", "focus_prompt": None},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["download_url"].startswith("/api/download/")
    assert "summary_preview" in data
