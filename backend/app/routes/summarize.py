"""Summary generation and PDF download routes."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import SummarizeRequest, SummarizeResponse
from app.services.embedder import get_source_files
from app.services.llm import generate_summary
from app.services.pdf_generator import markdown_to_pdf
from app.services.retriever import retrieve_for_summary

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest) -> SummarizeResponse:
    """
    Retrieve chunks, generate an LLM summary, and produce a downloadable PDF.

    Returns:
        SummarizeResponse with download URL and text preview.
    """
    session_id = req.session_id

    try:
        retrieved_chunks = retrieve_for_summary(session_id, req.focus_prompt)
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found or ChromaDB error: {exc}",
        ) from exc

    if not retrieved_chunks:
        raise HTTPException(
            status_code=404,
            detail="No chunks found for this session. Please re-upload files.",
        )

    summary_text = generate_summary(retrieved_chunks, focus_prompt=req.focus_prompt)

    output_dir = settings.output_path()
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_filename = f"summary_{session_id}.pdf"
    pdf_path = output_dir / pdf_filename

    try:
        source_files = get_source_files(session_id)
    except Exception:
        source_files = []

    markdown_to_pdf(summary_text, pdf_path, source_files)

    preview = summary_text[:500] + ("..." if len(summary_text) > 500 else "")

    return SummarizeResponse(
        session_id=session_id,
        pdf_filename=pdf_filename,
        download_url=f"/api/download/{pdf_filename}",
        summary_preview=preview,
    )


@router.get("/download/{filename}")
async def download_pdf(filename: str) -> FileResponse:
    """
    Stream a generated summary PDF to the client.

    Args:
        filename: PDF filename under the outputs directory.

    Returns:
        FileResponse with application/pdf media type.
    """
    output_dir = settings.output_path().resolve()
    file_path = (output_dir / filename).resolve()

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    if not str(file_path).startswith(str(output_dir)):
        raise HTTPException(status_code=403, detail="Forbidden")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
    )
