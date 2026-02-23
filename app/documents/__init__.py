# Mail-merge document generation (docxtpl + docx2pdf / LibreOffice).
from app.documents.contracts import (
    DocumentContext,
    DocumentOverrides,
    LineItemContext,
    build_document_context,
)
from app.documents.service import DocumentGenerationService

__all__ = [
    "DocumentContext",
    "DocumentOverrides",
    "LineItemContext",
    "build_document_context",
    "DocumentGenerationService",
]
