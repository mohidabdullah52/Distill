"""ReportLab PDF generation from markdown-style summary text."""

import re
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

ACCENT_COLOR = colors.HexColor("#1565C0")
DARK_GRAY = colors.HexColor("#424242")


def _build_styles():
    """Create custom paragraph styles for the summary PDF."""
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            fontSize=22,
            leading=28,
            textColor=ACCENT_COLOR,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="DocSubtitle",
            fontSize=10,
            leading=14,
            textColor=DARK_GRAY,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName="Helvetica",
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2",
            fontSize=13,
            leading=18,
            textColor=ACCENT_COLOR,
            spaceBefore=16,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            fontSize=10,
            leading=15,
            textColor=DARK_GRAY,
            spaceAfter=6,
            fontName="Helvetica",
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletText",
            fontSize=10,
            leading=15,
            textColor=DARK_GRAY,
            fontName="Helvetica",
            leftIndent=10,
        )
    )
    return styles


def markdown_to_pdf(summary_text: str, output_path: Path, source_files: list[str]) -> None:
    """
    Convert LLM markdown summary text into a polished PDF file.

    Args:
        summary_text: Markdown summary from the LLM.
        output_path: Destination PDF path.
        source_files: Original filenames for the title block.
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = _build_styles()
    story = []

    story.append(Paragraph("Document Summary Report", styles["DocTitle"]))
    sources_label = ", ".join(source_files) if source_files else "Multiple Files"
    ts = datetime.now().strftime("%B %d, %Y %H:%M")
    story.append(
        Paragraph(
            f"Sources: {sources_label} &nbsp;|&nbsp; Generated: {ts}",
            styles["DocSubtitle"],
        )
    )
    story.append(
        HRFlowable(width="100%", thickness=1, color=ACCENT_COLOR, spaceAfter=12)
    )

    lines = summary_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("## "):
            heading = line[3:].strip()
            story.append(Paragraph(heading, styles["H2"]))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.lightgrey,
                    spaceAfter=4,
                )
            )
        elif line.startswith("- ") or line.startswith("* "):
            bullets = []
            while i < len(lines) and (
                lines[i].startswith("- ") or lines[i].startswith("* ")
            ):
                bullet_text = lines[i][2:].strip()
                bullets.append(
                    ListItem(
                        Paragraph(bullet_text, styles["BulletText"]),
                        bulletColor=ACCENT_COLOR,
                    )
                )
                i += 1
            story.append(
                ListFlowable(
                    bullets, bulletType="bullet", start="•", leftIndent=20
                )
            )
            continue
        elif line.strip() == "":
            story.append(Spacer(1, 6))
        else:
            line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
            story.append(Paragraph(line, styles["Body"]))

        i += 1

    doc.build(story)
