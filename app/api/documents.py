"""Documents API: generate (sync/job), metadata, download."""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import GeneratedDocument
from app.documents.contracts import DocumentOverrides
from app.documents.repository import get_document
from app.documents.service import DocumentGenerationService

router = APIRouter(prefix="/documents", tags=["documents"])


# ---------------------------------------------------------------------------
# Request/Response schemas
# ---------------------------------------------------------------------------


class DocumentOverridesSchema(BaseModel):
    """Runtime overrides for document generation."""

    quote_date: Optional[date] = None
    delivery_date: Optional[date] = None
    notes: Optional[str] = None
    shipping: Optional[str] = None
    payment_terms: Optional[str] = None
    discount_percent: Optional[Decimal] = None


class LineItemSpecSchema(BaseModel):
    """One line item when not using quote_id/delivery_docket_id."""

    product_id: str
    quantity: Decimal = Field(..., ge=0)
    uom: str = "unit"
    unit_price: Optional[Decimal] = None


class GenerateRequest(BaseModel):
    """Request body for POST /documents/generate."""

    template_name: str = Field(
        ..., description="Template filename or key (e.g. Delivery_Docket.docx)"
    )
    doc_type: str = Field(
        default="delivery_docket", description="doc_type for naming and context"
    )
    doc_number: Optional[str] = Field(
        None, description="Override doc number; otherwise from quote/docket"
    )
    contact_id: Optional[str] = None
    customer_id: Optional[str] = None
    quote_id: Optional[str] = Field(None, description="SalesOrder id to use as quote")
    delivery_docket_id: Optional[str] = Field(None, description="DeliveryDocket id")
    line_specs: Optional[List[LineItemSpecSchema]] = Field(
        None,
        description="Ad-hoc lines when not using quote_id/delivery_docket_id",
    )
    product_summary_rows: Optional[List[dict]] = Field(
        None,
        description="Aggregated product rows for customer purchase report",
    )
    product_summary_orders: Optional[List[dict]] = Field(
        None,
        description="Order rows for customer purchase report",
    )
    product_summary_order_count: Optional[int] = None
    product_summary_period_start: Optional[date] = None
    product_summary_period_end: Optional[date] = None
    product_summary_total_ex_gst: Optional[Decimal] = None
    product_summary_total_inc_gst: Optional[Decimal] = None
    product_summary_total_qty: Optional[Decimal] = None
    overrides: Optional[DocumentOverridesSchema] = None
    output_docx: Optional[bool] = Field(
        None, description="Also save DOCX; default from settings"
    )
    async_job: bool = Field(
        default=False, description="If true, enqueue job and return job_id"
    )


class DocumentMetadataResponse(BaseModel):
    """Generated document metadata."""

    id: str
    doc_type: str
    doc_number: Optional[str]
    status: str
    template_name: str
    pdf_path: Optional[str]
    docx_path: Optional[str]
    error_message: Optional[str]
    contact_id: Optional[str]
    customer_id: Optional[str]
    sales_order_id: Optional[str]
    delivery_docket_id: Optional[str]
    job_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateResponse(BaseModel):
    """Response for sync generate: document metadata + download URL."""

    document: DocumentMetadataResponse
    download_url: str = Field(..., description="Path to GET for PDF download")
    pdf_path: Optional[str] = None
    docx_path: Optional[str] = None


class JobEnqueueResponse(BaseModel):
    """Response when async_job=true: job_id and status URL."""

    job_id: str
    status_url: str
    message: str = "Job enqueued; poll status_url for document_id when ready."


class JobStatusResponse(BaseModel):
    """Job status (GET /documents/jobs/{job_id})."""

    job_id: str
    status: str  # queued, started, finished, failed
    document_id: Optional[str] = None
    error_message: Optional[str] = None


def _overrides_from_schema(
    s: Optional[DocumentOverridesSchema],
) -> Optional[DocumentOverrides]:
    if s is None:
        return None
    return DocumentOverrides(
        quote_date=s.quote_date,
        delivery_date=s.delivery_date,
        notes=s.notes,
        shipping=s.shipping,
        payment_terms=s.payment_terms,
        discount_percent=s.discount_percent,
    )


def _doc_to_metadata(doc: GeneratedDocument) -> DocumentMetadataResponse:
    return DocumentMetadataResponse(
        id=doc.id,
        doc_type=doc.doc_type,
        doc_number=doc.doc_number,
        status=doc.status,
        template_name=doc.template_name,
        pdf_path=doc.pdf_path,
        docx_path=doc.docx_path,
        error_message=doc.error_message,
        contact_id=doc.contact_id,
        customer_id=doc.customer_id,
        sales_order_id=doc.sales_order_id,
        delivery_docket_id=doc.delivery_docket_id,
        job_id=doc.job_id,
        created_at=doc.created_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=GenerateResponse | JobEnqueueResponse)
async def generate_document(
    body: GenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a PDF (and optionally DOCX) from a template.
    Provide either delivery_docket_id, quote_id, or (contact_id/customer_id + line_specs).
    If async_job=true, returns job_id; poll GET /documents/jobs/{job_id} for document_id then GET /documents/{id}/download.
    """
    if body.async_job:
        try:
            from app.documents.jobs import enqueue_generation_job
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Async jobs require Redis and RQ; enqueue_generation_job not available.",
            )
        job_id = enqueue_generation_job(
            template_name=body.template_name,
            doc_type=body.doc_type,
            doc_number=body.doc_number,
            contact_id=body.contact_id,
            customer_id=body.customer_id,
            quote_id=body.quote_id,
            delivery_docket_id=body.delivery_docket_id,
            line_specs=[s.model_dump() for s in (body.line_specs or [])],
            overrides=body.overrides.model_dump() if body.overrides else None,
            output_docx=body.output_docx,
        )
        return JobEnqueueResponse(
            job_id=job_id,
            status_url=f"/api/v1/documents/jobs/{job_id}",
        )

    overrides = _overrides_from_schema(body.overrides)
    line_specs = [s.model_dump() for s in (body.line_specs or [])]
    svc = DocumentGenerationService(db)
    doc_record, pdf_path, docx_path, err = svc.generate(
        template_name=body.template_name,
        doc_type=body.doc_type,
        doc_number=body.doc_number or "doc",
        contact_id=body.contact_id,
        customer_id=body.customer_id,
        quote_id=body.quote_id,
        delivery_docket_id=body.delivery_docket_id,
        line_specs=line_specs if line_specs else None,
        overrides=overrides,
        output_docx=body.output_docx,
        product_summary_rows=body.product_summary_rows,
        product_summary_orders=body.product_summary_orders,
        product_summary_order_count=body.product_summary_order_count,
        product_summary_period_start=body.product_summary_period_start,
        product_summary_period_end=body.product_summary_period_end,
        product_summary_total_ex_gst=body.product_summary_total_ex_gst,
        product_summary_total_inc_gst=body.product_summary_total_inc_gst,
        product_summary_total_qty=body.product_summary_total_qty,
    )
    if err and (doc_record is None or doc_record.status == "failed"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err,
        )
    download_url = f"/api/v1/documents/{doc_record.id}/download"
    return GenerateResponse(
        document=_doc_to_metadata(doc_record),
        download_url=download_url,
        pdf_path=doc_record.pdf_path,
        docx_path=doc_record.docx_path,
    )


@router.get("/{document_id}", response_model=DocumentMetadataResponse)
async def get_document_metadata(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Get generated document metadata."""
    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return _doc_to_metadata(doc)


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    inline: bool = Query(
        False, description="Display in browser (inline) instead of download"
    ),
    db: Session = Depends(get_db),
):
    """Stream the generated PDF (or 404 if not found / not completed).
    Use ?inline=1 for in-browser display (e.g. in an iframe)."""
    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if doc.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document not ready: status={doc.status}",
        )
    pdf_path = doc.pdf_path
    if not pdf_path or not Path(pdf_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found",
        )
    filename = Path(pdf_path).name
    disposition = "inline" if inline else "attachment"
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'{disposition}; filename="{filename}"'},
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    """Get status of an async generation job. Returns document_id when status=finished."""
    try:
        from app.documents.jobs import get_job_status as _get_job_status
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Job status requires RQ.",
        )
    status_info = _get_job_status(job_id, db)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return JobStatusResponse(**status_info)
