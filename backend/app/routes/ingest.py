"""
Handles multipart uploads and indexes parsed documents into ChromaDB.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import IngestResponse
from app.services.chunker import chunk_pages
from app.services.embedder import upsert_chunks
from app.services.parser import extract_text

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".ppt"}


@router.post("/ingest", response_model=IngestResponse)
async def ingest_files(files: list[UploadFile] = File(...)) -> IngestResponse:
    """
    Accepts uploads, extracts text, chunks it, and stores vectors for the session.

    Args:
        files (list[UploadFile]): One or more PDF or PPTX files from the client.

    Returns:
        IngestResponse: Session id, processed filenames, and chunk count.

    Raises:
        HTTPException: For validation, size, parse, or empty-content failures.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    session_id = str(uuid.uuid4()).replace("-", "")[:16]
    upload_dir = settings.upload_path() / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    files_processed: list[str] = []
    all_chunks = []

    for upload in files:
        if not upload.filename:
            raise HTTPException(status_code=400, detail="File missing filename")

        suffix = Path(upload.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{suffix}'. Allowed: PDF, PPTX",
            )

        content = await upload.read()
        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File '{upload.filename}' exceeds maximum size of "
                f"{settings.max_file_size // (1024 * 1024)}MB",
            )

        safe_filename = Path(upload.filename).name
        if not safe_filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        dest = upload_dir / safe_filename
        with open(dest, "wb") as f:
            f.write(content)

        try:
            pages = extract_text(dest)
            chunks = chunk_pages(pages)
            all_chunks.extend(chunks)
            files_processed.append(safe_filename)
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse {safe_filename}: {exc}",
            ) from exc

    if not all_chunks:
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from the uploaded files.",
        )

    total = upsert_chunks(session_id, all_chunks)

    return IngestResponse(
        session_id=session_id,
        files_processed=files_processed,
        total_chunks=total,
        message=f"Ingested {len(files_processed)} file(s) → {total} chunks indexed.",
    )
