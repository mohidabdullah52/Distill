"""
Extracts plain text from uploaded PDF and PowerPoint files.
"""

from pathlib import Path
from typing import List, Tuple

PageTuple = Tuple[str, int, str]


def extract_text(file_path: Path) -> List[PageTuple]:
    """
    Reads a document and returns non-empty page or slide text segments.

    Args:
        file_path (Path): Path to a PDF or PPTX file on disk.

    Returns:
        List[PageTuple]: Tuples of filename, 1-based page number, and text.

    Raises:
        ValueError: If the file extension is not supported.
    """
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    if suffix in (".pptx", ".ppt"):
        return _extract_pptx(file_path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _extract_pdf(path: Path) -> List[PageTuple]:
    """
    Pulls text from each page of a PDF file.

    Args:
        path (Path): Path to the PDF file.

    Returns:
        List[PageTuple]: One entry per page that contains extractable text.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    results: List[PageTuple] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            results.append((path.name, i, text))
    return results


def _extract_pptx(path: Path) -> List[PageTuple]:
    """
    Pulls text from each slide of a PowerPoint file.

    Args:
        path (Path): Path to the PPTX file.

    Returns:
        List[PageTuple]: One entry per slide that contains extractable text.
    """
    from pptx import Presentation

    prs = Presentation(str(path))
    results: List[PageTuple] = []
    for i, slide in enumerate(prs.slides, start=1):
        parts: List[str] = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    line = " ".join(run.text for run in para.runs).strip()
                    if line:
                        parts.append(line)
        text = "\n".join(parts).strip()
        if text:
            results.append((path.name, i, text))
    return results
