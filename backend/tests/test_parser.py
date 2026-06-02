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


def test_extract_pptx_table_and_group_shapes(tmp_path: Path) -> None:
    """
    Verifies PPTX extraction pulls text recursively from group shapes and tables.
    """
    pptx_path = tmp_path / "presentation.pptx"
    pptx_path.write_bytes(b"PK-fake")

    # 1. Normal shape
    run_normal = MagicMock()
    run_normal.text = "Normal shape text"
    para_normal = MagicMock()
    para_normal.runs = [run_normal]
    shape_normal = MagicMock()
    shape_normal.has_text_frame = True
    shape_normal.has_table = False
    shape_normal.text_frame.paragraphs = [para_normal]
    if hasattr(shape_normal, "shapes"):
        del shape_normal.shapes

    # 2. Table shape
    run_cell = MagicMock()
    run_cell.text = "Table cell text"
    para_cell = MagicMock()
    para_cell.runs = [run_cell]
    cell = MagicMock()
    cell.text_frame.paragraphs = [para_cell]
    row = MagicMock()
    row.cells = [cell]
    table = MagicMock()
    table.rows = [row]
    shape_table = MagicMock()
    shape_table.has_text_frame = False
    shape_table.has_table = True
    shape_table.table = table
    if hasattr(shape_table, "shapes"):
        del shape_table.shapes

    # 3. Group shape containing nested shape
    run_group = MagicMock()
    run_group.text = "Nested group text"
    para_group = MagicMock()
    para_group.runs = [run_group]
    sub_shape = MagicMock()
    sub_shape.has_text_frame = True
    sub_shape.has_table = False
    sub_shape.text_frame.paragraphs = [para_group]
    if hasattr(sub_shape, "shapes"):
        del sub_shape.shapes
    
    shape_group = MagicMock()
    shape_group.shapes = [sub_shape]

    mock_slide = MagicMock()
    mock_slide.shapes = [shape_normal, shape_table, shape_group]

    mock_prs = MagicMock()
    mock_prs.slides = [mock_slide]

    with patch("pptx.Presentation", return_value=mock_prs):
        result = extract_text(pptx_path)

    assert len(result) == 1
    filename, slide_num, text = result[0]
    assert filename == "presentation.pptx"
    assert slide_num == 1
    assert "Normal shape text" in text
    assert "Table cell text" in text
    assert "Nested group text" in text

