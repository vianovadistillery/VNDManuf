"""GeneratedDocument persistence: create, get by id, update status/paths."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.db.models import GeneratedDocument, GeneratedDocumentStatus


def create_document_record(
    session: Session,
    doc_type: str,
    template_name: str,
    doc_number: Optional[str] = None,
    contact_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    sales_order_id: Optional[str] = None,
    delivery_docket_id: Optional[str] = None,
    job_id: Optional[str] = None,
) -> GeneratedDocument:
    """Create a pending GeneratedDocument record."""
    doc = GeneratedDocument(
        doc_type=doc_type,
        doc_number=doc_number,
        status=GeneratedDocumentStatus.PENDING.value,
        template_name=template_name,
        contact_id=contact_id,
        customer_id=customer_id,
        sales_order_id=sales_order_id,
        delivery_docket_id=delivery_docket_id,
        job_id=job_id,
    )
    session.add(doc)
    session.flush()
    return doc


def get_document(session: Session, document_id: str) -> Optional[GeneratedDocument]:
    """Get GeneratedDocument by id."""
    return session.get(GeneratedDocument, document_id)


def mark_running(session: Session, document_id: str) -> None:
    """Set status to running."""
    doc = session.get(GeneratedDocument, document_id)
    if doc:
        doc.status = GeneratedDocumentStatus.RUNNING.value
        session.flush()


def mark_completed(
    session: Session,
    document_id: str,
    pdf_path: str,
    docx_path: Optional[str] = None,
) -> None:
    """Set status to completed and store paths."""
    doc = session.get(GeneratedDocument, document_id)
    if doc:
        doc.status = GeneratedDocumentStatus.COMPLETED.value
        doc.pdf_path = pdf_path
        doc.docx_path = docx_path
        doc.error_message = None
        session.flush()


def mark_failed(session: Session, document_id: str, error_message: str) -> None:
    """Set status to failed and store error."""
    doc = session.get(GeneratedDocument, document_id)
    if doc:
        doc.status = GeneratedDocumentStatus.FAILED.value
        doc.error_message = error_message
        session.flush()
