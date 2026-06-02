"""
Tests for FastAPI HTTP routes.
"""

from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """
    Verifies the health endpoint returns status and LLM metadata.

    Returns:
        None
    """
    with patch(
        "app.main.get_active_llm_info",
        return_value={"provider": "openai", "model": "gpt-4o-mini"},
    ):
        response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["provider"] == "openai"


@patch(
    "app.routes.summarize.generate_summary",
    side_effect=ValueError("OPENAI_API_KEY is required"),
)
@patch(
    "app.routes.summarize.retrieve_for_summary",
    return_value=["chunk"],
)
def test_summarize_llm_config_error(mock_retrieve, mock_llm) -> None:
    """
    Verifies missing LLM credentials return HTTP 503 on summarize.

    Args:
        mock_retrieve (MagicMock): Patched retrieval returning chunks.
        mock_llm (MagicMock): Patched summary generation that raises.

    Returns:
        None
    """
    response = client.post(
        "/api/summarize",
        json={"session_id": "abc123", "focus_prompt": None},
    )
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_ingest_no_files() -> None:
    """
    Verifies ingest rejects requests with no uploaded files.

    Returns:
        None
    """
    response = client.post("/api/ingest", files=[])
    assert response.status_code == 422


def test_ingest_unsupported_type() -> None:
    """
    Verifies ingest rejects unsupported file extensions.

    Returns:
        None
    """
    response = client.post(
        "/api/ingest",
        files=[("files", ("notes.txt", BytesIO(b"hello"), "text/plain"))],
    )
    assert response.status_code == 400


@patch("app.routes.ingest.upsert_chunks", return_value=2)
@patch("app.routes.ingest.chunk_pages", return_value=[{"id": "x", "text": "t", "metadata": {}}])
@patch("app.routes.ingest.extract_text", return_value=[("a.pdf", 1, "text")])
def test_ingest_success(mock_extract, mock_chunk, mock_upsert) -> None:
    """
    Verifies a valid PDF upload returns session and chunk metadata.

    Args:
        mock_extract (MagicMock): Patched text extraction.
        mock_chunk (MagicMock): Patched chunking step.
        mock_upsert (MagicMock): Patched vector upsert.

    Returns:
        None
    """
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
@patch(
    "app.routes.summarize.generate_summary",
    return_value="## Executive Summary\n\nDone.",
)
@patch(
    "app.routes.summarize.retrieve_for_summary",
    return_value=["chunk"],
)
def test_summarize_success(
    mock_retrieve, mock_llm, mock_sources, mock_pdf
) -> None:
    """
    Verifies summarize returns a download URL and text preview.

    Args:
        mock_retrieve (MagicMock): Patched chunk retrieval.
        mock_llm (MagicMock): Patched summary generation.
        mock_sources (MagicMock): Patched source filename lookup.
        mock_pdf (MagicMock): Patched PDF rendering.

    Returns:
        None
    """
    response = client.post(
        "/api/summarize",
        json={"session_id": "abc123", "focus_prompt": None},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["download_url"].startswith("/api/download/")
    assert "summary_preview" in data


@patch("app.routes.ingest.upsert_chunks", return_value=1)
@patch("app.routes.ingest.chunk_pages", return_value=[{"id": "x", "text": "t", "metadata": {}}])
@patch("app.routes.ingest.extract_text", return_value=[("report.pdf", 1, "text")])
def test_ingest_path_traversal_prevention(mock_extract, mock_chunk, mock_upsert) -> None:
    """
    Verifies that ingest sanitizes file paths and prevents directory traversal.
    """
    response = client.post(
        "/api/ingest",
        files=[("files", ("../../report.pdf", BytesIO(b"%PDF"), "application/pdf"))],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["files_processed"] == ["report.pdf"]

