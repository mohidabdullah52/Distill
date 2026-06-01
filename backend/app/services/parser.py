"""PDF and PPTX text extraction."""

from pathlib import Path
from typing import List, Tuple

PageTuple = Tuple[str, int, str]


def extract_text(file_path: Path) -> List[PageTuple]:
    """
    Extract text from a PDF or PPTX file.

    Returns:
        List of (source_label, page_number, text_content) tuples.
    """
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    if suffix in (".pptx", ".ppt"):
        return _extract_pptx(file_path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _extract_pdf(path: Path) -> List[PageTuple]:
    """Extract text from each page of a PDF."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    results: List[PageTuple] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            results.append((path.name, i, text))
    return results


def _extract_pptx(path: Path) -> List[PageTuple]:
    """Extract text from each slide of a PowerPoint file."""
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
