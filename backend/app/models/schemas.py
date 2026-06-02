"""
Defines request and response models exchanged by the public API.
"""

from typing import List, Optional

from pydantic import BaseModel


class IngestResponse(BaseModel):
    """
    Returned after files are parsed, chunked, and stored in ChromaDB.

    Attributes:
        session_id (str): Identifier used for later summarize requests.
        files_processed (List[str]): Names of files that were indexed.
        total_chunks (int): Number of text chunks written to the vector store.
        message (str): Human-readable summary of the ingest result.
    """

    session_id: str
    files_processed: List[str]
    total_chunks: int
    message: str


class SummarizeRequest(BaseModel):
    """
    Sent by the client to generate a summary for an existing session.

    Attributes:
        session_id (str): Session created during ingest.
        focus_prompt (Optional[str]): Optional topic emphasis for the LLM.
    """

    session_id: str
    focus_prompt: Optional[str] = None


class SummarizeResponse(BaseModel):
    """
    Returned when a summary PDF has been generated successfully.

    Attributes:
        session_id (str): Session that was summarized.
        pdf_filename (str): Filename of the generated PDF on disk.
        download_url (str): Relative URL the client uses to download the file.
        summary_preview (str): Short text preview of the summary body.
    """

    session_id: str
    pdf_filename: str
    download_url: str
    summary_preview: str
