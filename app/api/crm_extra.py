"""Additional CRM API endpoints (calendar, schedule, attachments, export)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import (
    CrmActivity,
    CrmAttachment,
    CrmScheduledActivity,
    SalesRep,
)
from app.api.crm import _get_customer
from app.documents.service import DocumentGenerationService
from app.services.crm_service import (
    build_rep_portfolio_dashboard,
    compute_visit_suggestions,
    gather_calendar_events,
    gather_rep_calendar_events,
)
from app.storage.local import get_storage_backend


class CalendarEventResponse(BaseModel):
    id: str
    title: str
    start: str
    type: str
    source: str
    color: str
    rep_name: Optional[str] = None


class VisitSuggestionResponse(BaseModel):
    visit_frequency_target_days: int
    preferred_contact_method: str
    last_contact_at: Optional[str] = None
    last_contact_label: str
    suggested_at: Optional[str] = None
    suggested_type: str
    days_overdue: int
    urgency: str
    message: str


class ScheduledActivityCreate(BaseModel):
    activity_type: str = Field(default="visit")
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    scheduled_at: datetime
    sales_rep_id: str
    duration_minutes: Optional[int] = None
    customer_site_id: Optional[str] = None


class ScheduledActivityUpdate(BaseModel):
    activity_type: Optional[str] = None
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None
    duration_minutes: Optional[int] = None


class ScheduledActivityResponse(BaseModel):
    id: str
    customer_id: str
    activity_type: str
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    status: str
    sales_rep_id: str
    duration_minutes: Optional[int] = None

    class Config:
        from_attributes = True


class AttachmentResponse(BaseModel):
    id: str
    customer_id: str
    activity_id: Optional[str] = None
    file_name: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    caption: Optional[str] = None
    download_url: str


class CrmExportRequest(BaseModel):
    sections: List[str] = Field(
        default_factory=lambda: ["all"],
        description="sales, timeline, profile, people, scheduled, or all",
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CrmExportResponse(BaseModel):
    document_id: str
    download_url: str


class RepCustomerPortfolioRow(BaseModel):
    customer_id: str
    code: str
    name: str
    buying_group_name: Optional[str] = None
    assignment_role: str = "primary"
    order_count: int = 0
    total_inc_gst: float = 0
    last_order_date: Optional[str] = None


class RepPortfolioOrderRow(BaseModel):
    order_date: str
    order_ref: str
    customer_name: str
    status: str
    total_inc_gst: float


class RepDashboardResponse(BaseModel):
    rep_id: str
    rep_name: str
    rep_code: str
    customer_count: int
    order_count: int
    total_revenue_inc_gst: float
    total_units: float
    customers: List[RepCustomerPortfolioRow]
    orders: List[RepPortfolioOrderRow]


def register_crm_extra_routes(router: APIRouter) -> None:
    @router.get(
        "/customers/{customer_id}/calendar-events",
        response_model=List[CalendarEventResponse],
    )
    def calendar_events(
        customer_id: str,
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        db: Session = Depends(get_db),
    ):
        _get_customer(db, customer_id)
        return gather_calendar_events(db, customer_id, start_date, end_date)

    @router.get(
        "/customers/{customer_id}/suggestions",
        response_model=VisitSuggestionResponse,
    )
    def visit_suggestions(customer_id: str, db: Session = Depends(get_db)):
        customer = _get_customer(db, customer_id)
        return compute_visit_suggestions(db, customer)

    @router.get(
        "/customers/{customer_id}/scheduled",
        response_model=List[ScheduledActivityResponse],
    )
    def list_scheduled(customer_id: str, db: Session = Depends(get_db)):
        _get_customer(db, customer_id)
        rows = (
            db.execute(
                select(CrmScheduledActivity)
                .where(
                    CrmScheduledActivity.customer_id == customer_id,
                    CrmScheduledActivity.deleted_at.is_(None),
                )
                .order_by(CrmScheduledActivity.scheduled_at)
            )
            .scalars()
            .all()
        )
        return [ScheduledActivityResponse.model_validate(r) for r in rows]

    @router.post(
        "/customers/{customer_id}/scheduled",
        response_model=ScheduledActivityResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_scheduled(
        customer_id: str,
        data: ScheduledActivityCreate,
        db: Session = Depends(get_db),
    ):
        _get_customer(db, customer_id)
        rep = db.get(SalesRep, data.sales_rep_id)
        if not rep or rep.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sales rep"
            )
        row = CrmScheduledActivity(
            customer_id=customer_id,
            customer_site_id=data.customer_site_id,
            sales_rep_id=data.sales_rep_id,
            activity_type=data.activity_type,
            title=data.title,
            description=data.description,
            scheduled_at=data.scheduled_at,
            duration_minutes=data.duration_minutes,
            status="scheduled",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return ScheduledActivityResponse.model_validate(row)

    @router.put("/scheduled/{scheduled_id}", response_model=ScheduledActivityResponse)
    def update_scheduled(
        scheduled_id: str,
        data: ScheduledActivityUpdate,
        db: Session = Depends(get_db),
    ):
        row = db.get(CrmScheduledActivity, scheduled_id)
        if not row or row.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Scheduled item not found")
        for field in (
            "activity_type",
            "title",
            "description",
            "scheduled_at",
            "status",
            "duration_minutes",
        ):
            val = getattr(data, field)
            if val is not None:
                setattr(row, field, val)
        db.commit()
        db.refresh(row)
        return ScheduledActivityResponse.model_validate(row)

    @router.delete("/scheduled/{scheduled_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_scheduled(scheduled_id: str, db: Session = Depends(get_db)):
        from app.services.audit import soft_delete

        row = db.get(CrmScheduledActivity, scheduled_id)
        if not row or row.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Scheduled item not found")
        soft_delete(db, row)
        db.commit()
        return None

    @router.post(
        "/customers/{customer_id}/attachments",
        response_model=AttachmentResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_attachment(
        customer_id: str,
        file: UploadFile = File(...),
        activity_id: Optional[str] = Form(None),
        caption: Optional[str] = Form(None),
        sales_rep_id: Optional[str] = Form(None),
        db: Session = Depends(get_db),
    ):
        _get_customer(db, customer_id)
        if activity_id:
            act = db.get(CrmActivity, activity_id)
            if not act or act.deleted_at is not None:
                raise HTTPException(status_code=400, detail="Invalid activity")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file")
        ext = Path(file.filename or "upload").suffix or ".jpg"
        key = f"{customer_id}/{uuid.uuid4()}{ext}"
        storage = get_storage_backend()
        stored = storage.save(key, data, file.content_type)
        attachment = CrmAttachment(
            customer_id=customer_id,
            activity_id=activity_id,
            uploaded_by_rep_id=sales_rep_id,
            storage_backend=stored.storage_backend,
            storage_key=stored.storage_key,
            file_name=file.filename or f"photo{ext}",
            mime_type=file.content_type,
            file_size=len(data),
            caption=caption,
            taken_at=datetime.utcnow(),
        )
        db.add(attachment)
        if activity_id:
            act = db.get(CrmActivity, activity_id)
            if act and act.activity_type == "note":
                act.activity_type = "photo"
        db.commit()
        db.refresh(attachment)
        return AttachmentResponse(
            id=str(attachment.id),
            customer_id=customer_id,
            activity_id=activity_id,
            file_name=attachment.file_name,
            mime_type=attachment.mime_type,
            file_size=attachment.file_size,
            caption=attachment.caption,
            download_url=f"/api/v1/crm/attachments/{attachment.id}/download",
        )

    @router.get("/attachments/{attachment_id}/download")
    def download_attachment(attachment_id: str, db: Session = Depends(get_db)):
        att = db.get(CrmAttachment, attachment_id)
        if not att or att.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Attachment not found")
        storage = get_storage_backend()
        root = Path(__file__).resolve().parents[2] / "uploads" / "crm"
        path = root / att.storage_key
        if path.exists():
            return FileResponse(
                path,
                media_type=att.mime_type or "application/octet-stream",
                filename=att.file_name,
            )
        try:
            data = storage.read(att.storage_key)
        except Exception:
            raise HTTPException(status_code=404, detail="File not found")
        return Response(
            content=data,
            media_type=att.mime_type or "application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{att.file_name}"'},
        )

    @router.post(
        "/customers/{customer_id}/export-pdf",
        response_model=CrmExportResponse,
    )
    def export_crm_pdf(
        customer_id: str,
        body: CrmExportRequest,
        db: Session = Depends(get_db),
    ):
        from app.services.crm_export import build_crm_export_context

        _get_customer(db, customer_id)
        context = build_crm_export_context(
            db,
            customer_id,
            body.sections,
            body.start_date,
            body.end_date,
        )
        svc = DocumentGenerationService(db)
        doc_record, pdf_path, _docx, err = svc.generate_from_context(
            "CRM_Summary.docx",
            "crm_summary",
            context,
            customer_id=customer_id,
            doc_number=context.document.doc_number,
        )
        if err or not doc_record:
            raise HTTPException(status_code=500, detail=err or "Export failed")
        return CrmExportResponse(
            document_id=str(doc_record.id),
            download_url=f"/api/v1/documents/{doc_record.id}/download",
        )

    @router.get("/reps/{rep_id}/dashboard", response_model=RepDashboardResponse)
    def rep_dashboard(
        rep_id: str,
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        db: Session = Depends(get_db),
    ):
        rep = db.get(SalesRep, rep_id)
        if not rep or rep.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Sales rep not found")
        try:
            data = build_rep_portfolio_dashboard(db, rep_id, start_date, end_date)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return RepDashboardResponse(
            rep_id=data["rep_id"],
            rep_name=data["rep_name"],
            rep_code=data["rep_code"],
            customer_count=data["customer_count"],
            order_count=data["order_count"],
            total_revenue_inc_gst=data["total_revenue_inc_gst"],
            total_units=data["total_units"],
            customers=[RepCustomerPortfolioRow(**row) for row in data["customers"]],
            orders=[RepPortfolioOrderRow(**row) for row in data["orders"]],
        )

    @router.get(
        "/reps/{rep_id}/calendar-events",
        response_model=List[CalendarEventResponse],
    )
    def rep_calendar_events(
        rep_id: str,
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        db: Session = Depends(get_db),
    ):
        rep = db.get(SalesRep, rep_id)
        if not rep or rep.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Sales rep not found")
        return gather_rep_calendar_events(db, rep_id, start_date, end_date)
