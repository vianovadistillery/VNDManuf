"""Render DOCX from template + docxtpl context."""

from pathlib import Path

from docxtpl import DocxTemplate

from app.documents.contracts import DocumentContext


def render_docx(
    template_path: Path, context: DocumentContext, output_path: Path
) -> None:
    """Render template with context and write DOCX to output_path."""
    doc = DocxTemplate(str(template_path))
    ctx = context.to_dict()
    doc.render(ctx)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
