"""
Tests for PDF summary report generation.
"""

from pathlib import Path

from app.services.pdf_generator import markdown_to_pdf


def test_markdown_to_pdf_creates_file(tmp_path: Path) -> None:
    """
    Verifies markdown input produces a non-empty PDF on disk.

    Args:
        tmp_path (Path): Pytest temporary directory for output files.

    Returns:
        None
    """
    output = tmp_path / "summary.pdf"
    summary = """## Executive Summary
This is a test summary.

## Key Findings & Insights
- Finding one
- Finding two
"""
    markdown_to_pdf(summary, output, ["report.pdf"])

    assert output.exists()
    assert output.stat().st_size > 0


def test_markdown_to_pdf_empty_sources(tmp_path: Path) -> None:
    """
    Verifies a PDF can be generated when no source filenames are provided.

    Args:
        tmp_path (Path): Pytest temporary directory for output files.

    Returns:
        None
    """
    output = tmp_path / "empty_sources.pdf"
    markdown_to_pdf("## Executive Summary\n\nBody.", output, [])

    assert output.exists()


def test_markdown_to_pdf_xml_escaping(tmp_path: Path) -> None:
    """
    Verifies that markdown input with XML special characters (e.g. & < >)
    does not cause parsing crashes and generates a valid PDF.
    """
    output = tmp_path / "xml_escape_test.pdf"
    summary = """## XML & Special Characters
If x < y and y > z:
- Detail & more detail
- Formula: a < b
"""
    markdown_to_pdf(summary, output, ["a&b < c > d.pdf"])

    assert output.exists()
    assert output.stat().st_size > 0


def test_markdown_to_pdf_bullet_bolding(tmp_path: Path) -> None:
    """
    Verifies that markdown input with bold formatting inside headers and bullets
    is correctly parsed and generates a valid PDF.
    """
    output = tmp_path / "bold_formatting_test.pdf"
    summary = """## Executive **Summary**
- This is **bold** text in bullet
- Another **important** point
"""
    markdown_to_pdf(summary, output, ["report.pdf"])

    assert output.exists()
    assert output.stat().st_size > 0


def test_markdown_to_pdf_advanced_elements(tmp_path: Path) -> None:
    """
    Verifies that markdown input with H1, H3, and numbered lists is correctly parsed and generates a valid PDF.
    """
    output = tmp_path / "advanced_elements_test.pdf"
    summary = """# Document Title (H1)
## Section Title (H2)
### Subsection (H3)
1. First item in list
2. Second item in list
"""
    markdown_to_pdf(summary, output, ["report.pdf"])

    assert output.exists()
    assert output.stat().st_size > 0



