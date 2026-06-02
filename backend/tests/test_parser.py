"""
Tests for document text extraction.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.services.parser import extract_text


def test_extract_pdf_returns_page_text(tmp_path: Path) -> None:
    """
    Confirms readable PDF pages are returned with source metadata.

    Args:
        tmp_path (Path): Pytest temporary directory for test files.

    Returns:
        None
    """
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-fake")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Hello PDF world"

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("pypdf.PdfReader", return_value=mock_reader):
        result = extract_text(pdf_path)

    assert len(result) == 1
    assert result[0] == ("doc.pdf", 1, "Hello PDF world")


def test_extract_text_unsupported_extension(tmp_path: Path) -> None:
    """
    Ensures unsupported extensions raise a clear validation error.

    Args:
        tmp_path (Path): Pytest temporary directory for test files.

    Returns:
        None
    """
    bad_file = tmp_path / "notes.txt"
    bad_file.write_text("hello")

    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(bad_file)


def test_extract_pdf_skips_empty_pages(tmp_path: Path) -> None:
    """
    Ensures pages with only whitespace are not included in results.

    Args:
        tmp_path (Path): Pytest temporary directory for test files.

    Returns:
        None
    """
    pdf_path = tmp_path / "blank.pdf"
    pdf_path.write_bytes(b"%PDF-fake")

    empty_page = MagicMock()
    empty_page.extract_text.return_value = "   "

    mock_reader = MagicMock()
    mock_reader.pages = [empty_page]

    with patch("pypdf.PdfReader", return_value=mock_reader):
        result = extract_text(pdf_path)

    assert result == []
