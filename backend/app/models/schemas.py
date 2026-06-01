"""Pydantic request and response models for API routes."""

from typing import List, Optional

from pydantic import BaseModel


class IngestResponse(BaseModel):
    """Response after successful document ingestion."""

    session_id: str
    files_processed: List[str]
    total_chunks: int
    message: str


class SummarizeRequest(BaseModel):
    """Request body for summary generation."""

    session_id: str
    focus_prompt: Optional[str] = None


class SummarizeResponse(BaseModel):
    """Response after summary PDF is generated."""

    session_id: str
    pdf_filename: str
    download_url: str
    summary_preview: str
