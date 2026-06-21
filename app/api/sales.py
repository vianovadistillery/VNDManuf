"""Sales domain API router with soft delete and archive support."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
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
from pydantic import BaseModel, Field, validator
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import (
    Contact,
    DeliveryDocket,
    DeliveryDocketLine,
    GeneratedDocument,
    Invoice,
    InvoiceLine,
)
from apps.vndmanuf_sales.models import (
    Customer,
    CustomerSite,
    CustomerType,
    Pricebook,
    PricebookItem,
    SalesChannel,
    SalesOrder,
    SalesOrderLine,
    SalesOrderSource,
    SalesOrderStatus,
    SalesTag,
)
from apps.vndmanuf_sales.services.analytics import SalesAnalyticsService, default_period
from apps.vndmanuf_sales.services.customer_mapping import CustomerMappingService
from apps.vndmanuf_sales.services.import_sales_csv import SalesCSVImporter
from apps.vndmanuf_sales.services.totals import TotalsService

router = APIRouter(prefix="/sales", tags=["sales"])


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _utcnow() -> datetime:
    return datetime.utcnow()


def _apply_filters(stmt: Select, include_deleted: bool, include_archived: bool, model):
    if not include_deleted and hasattr(model, "deleted_at"):
        stmt = stmt.where(model.deleted_at.is_(None))
    if not include_archived and hasattr(model, "archived_at"):
        stmt = stmt.where(model.archived_at.is_(None))
    return stmt


def _soft_delete(instance):
    if hasattr(instance, "deleted_at"):
        instance.deleted_at = _utcnow()


def _restore(instance):
    if hasattr(instance, "deleted_at"):
        instance.deleted_at = None


def _archive(instance):
    if hasattr(instance, "archived_at"):
        instance.archived_at = _utcnow()


def _unarchive(instance):
    if hasattr(instance, "archived_at"):
        instance.archived_at = None


def _ensure_active(instance, detail: str):
    if hasattr(instance, "deleted_at") and instance.deleted_at:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# --------------------------------------------------------------------------- #
# Pydantic models
# --------------------------------------------------------------------------- #
class SalesChannelBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class SalesChannelCreate(SalesChannelBase):
    pass


class SalesChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class AuditResponse(BaseModel):
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SalesChannelResponse(SalesChannelBase, AuditResponse):
    id: str


class PricebookBase(BaseModel):
    name: str = Field(..., max_length=120)
    currency: str = Field("AUD", max_length=8)
    active_from: datetime
    active_to: Optional[datetime] = None


class PricebookCreate(PricebookBase):
    pass


class PricebookUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    currency: Optional[str] = Field(None, max_length=8)
    active_from: Optional[datetime] = None
    active_to: Optional[datetime] = None


class PricebookResponse(PricebookBase, AuditResponse):
    id: str


class PricebookItemBase(BaseModel):
    product_id: str
    unit_price_ex_gst: Decimal
    unit_price_inc_gst: Optional[Decimal] = None
    sku_code: Optional[str] = None

    @validator("unit_price_inc_gst", always=True)
    def validate_pair(cls, inc, values):
        ex = values.get("unit_price_ex_gst")
        if inc is None and ex is None:
            raise ValueError("unit_price_inc_gst or unit_price_ex_gst required")
        return inc


class PricebookItemCreate(PricebookItemBase):
    pass


class PricebookItemUpdate(BaseModel):
    unit_price_ex_gst: Optional[Decimal] = None
    unit_price_inc_gst: Optional[Decimal] = None
    sku_code: Optional[str] = None

    @validator("unit_price_inc_gst")
    def validate_pair(cls, inc, values):
        ex = values.get("unit_price_ex_gst")
        if inc is None and ex is None:
            raise ValueError("unit_price_inc_gst or unit_price_ex_gst required")
        return inc


class PricebookItemResponse(PricebookItemBase, AuditResponse):
    id: str
    pricebook_id: str


class SalesTagBase(BaseModel):
    slug: str = Field(..., max_length=100)
    label: str = Field(..., max_length=120)
    description: Optional[str] = None


class SalesTagCreate(SalesTagBase):
    pass


class SalesTagUpdate(BaseModel):
    label: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None


class SalesTagResponse(SalesTagBase, AuditResponse):
    id: str


class CustomerSiteBase(BaseModel):
    customer_id: str
    site_name: str = Field(..., max_length=120)
    state: str = Field(..., max_length=8)
    suburb: Optional[str] = Field(None, max_length=120)
    postcode: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class CustomerSiteCreate(CustomerSiteBase):
    pass


class CustomerSiteUpdate(BaseModel):
    site_name: Optional[str] = Field(None, max_length=120)
    state: Optional[str] = Field(None, max_length=8)
    suburb: Optional[str] = Field(None, max_length=120)
    postcode: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class CustomerSiteResponse(CustomerSiteBase, AuditResponse):
    id: str


class SalesOrderLineInput(BaseModel):
    product_id: str
    qty: Decimal
    unit_price_ex_gst: Decimal
    unit_price_inc_gst: Optional[Decimal] = None
    discount_ex_gst: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    uom: Optional[str] = "unit"


class SalesOrderCreate(BaseModel):
    customer_id: str
    channel_id: Optional[str] = None
    customer_site_id: Optional[str] = None
    pricebook_id: Optional[str] = None
    order_ref: Optional[str] = Field(None, max_length=50)
    po_number: Optional[str] = Field(None, max_length=50)
    order_date: datetime
    status: Optional[SalesOrderStatus] = SalesOrderStatus.CONFIRMED
    source: Optional[SalesOrderSource] = SalesOrderSource.MANUAL
    entered_by: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    order_discount_ex_gst: Optional[Decimal] = None
    lines: List[SalesOrderLineInput]


class SalesOrderUpdate(BaseModel):
    channel_id: Optional[str] = None
    customer_site_id: Optional[str] = None
    pricebook_id: Optional[str] = None
    order_ref: Optional[str] = Field(None, max_length=50)
    po_number: Optional[str] = Field(None, max_length=50)
    order_date: Optional[datetime] = None
    status: Optional[SalesOrderStatus] = None
    source: Optional[SalesOrderSource] = None
    entered_by: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    order_discount_ex_gst: Optional[Decimal] = None
    lines: Optional[List[SalesOrderLineInput]] = None


class SalesOrderLineResponse(AuditResponse):
    id: str
    product_id: str
    product_sku: Optional[str] = None
    product_name: Optional[str] = None
    qty: Decimal
    uom: str
    unit_price_ex_gst: Decimal
    unit_price_inc_gst: Optional[Decimal]
    discount_ex_gst: Optional[Decimal]
    line_total_ex_gst: Decimal
    line_total_inc_gst: Decimal
    tax_rate: Optional[Decimal]

    class Config:
        from_attributes = True


class SalesOrderResponse(AuditResponse):
    id: str
    customer_id: str
    channel_id: Optional[str]
    customer_site_id: Optional[str]
    pricebook_id: Optional[str]
    order_ref: Optional[str]
    po_number: Optional[str]
    order_date: datetime
    status: str
    source: str
    entered_by: Optional[str]
    notes: Optional[str]
    order_discount_ex_gst: Optional[Decimal] = None
    total_ex_gst: Decimal
    total_inc_gst: Decimal
    total_alcohol_volume_litres: Optional[Decimal] = None
    lines: List[SalesOrderLineResponse]
    delivery_docket_id: Optional[str] = None
    delivery_docket_number: Optional[str] = None
    delivery_date: Optional[datetime] = None
    invoice_id: Optional[str] = None
    invoice_number: Optional[str] = None
    paid: Optional[bool] = None
    # Linked generated files (when created): id and path for Open button
    delivery_docket_document: Optional[dict] = None  # { "id": str, "pdf_path": str }
    invoice_document: Optional[dict] = None
    picking_slip_document: Optional[dict] = None

    class Config:
        from_attributes = True


class SalesOrderListResponse(SalesOrderResponse):
    """Order with delivery/invoice flags for Current Orders list."""

    has_delivery: bool = False
    delivery_docket_number: Optional[str] = None
    delivery_date: Optional[datetime] = None
    delivery_docket_id: Optional[str] = None
    has_invoice: bool = False
    invoice_number: Optional[str] = None
    invoice_id: Optional[str] = None
    paid: Optional[bool] = None


# --------------------------------------------------------------------------- #
# Sales Channels CRUD
# --------------------------------------------------------------------------- #
@router.get("/channels", response_model=List[SalesChannelResponse])
def list_channels(
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    stmt = _apply_filters(
        select(SalesChannel).order_by(SalesChannel.code),
        include_deleted,
        include_archived,
        SalesChannel,
    )
    channels = db.execute(stmt).scalars().all()
    return [SalesChannelResponse.model_validate(ch) for ch in channels]


@router.post(
    "/channels",
    response_model=SalesChannelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_channel(data: SalesChannelCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(SalesChannel).where(SalesChannel.code == data.code)
    ).scalar_one_or_none()
    if existing and existing.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Sales channel '{data.code}' already exists",
        )
    channel = existing or SalesChannel(code=data.code)
    channel.name = data.name
    channel.description = data.description
    channel.deleted_at = None
    channel.archived_at = None
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return SalesChannelResponse.model_validate(channel)


def _get_channel(db: Session, channel_id: str, include_deleted: bool = False):
    channel = db.get(SalesChannel, channel_id)
    if not channel or (channel.deleted_at and not include_deleted):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sales channel not found"
        )
    return channel


@router.put("/channels/{channel_id}", response_model=SalesChannelResponse)
def update_channel(
    channel_id: str, data: SalesChannelUpdate, db: Session = Depends(get_db)
):
    channel = _get_channel(db, channel_id)
    if data.name is not None:
        channel.name = data.name
    if data.description is not None:
        channel.description = data.description
    db.commit()
    db.refresh(channel)
    return SalesChannelResponse.model_validate(channel)


@router.post("/channels/{channel_id}/archive", response_model=SalesChannelResponse)
def archive_channel(channel_id: str, db: Session = Depends(get_db)):
    channel = _get_channel(db, channel_id)
    _archive(channel)
    db.commit()
    return SalesChannelResponse.model_validate(channel)


@router.post("/channels/{channel_id}/unarchive", response_model=SalesChannelResponse)
def unarchive_channel(channel_id: str, db: Session = Depends(get_db)):
    channel = _get_channel(db, channel_id)
    _unarchive(channel)
    db.commit()
    return SalesChannelResponse.model_validate(channel)


@router.delete("/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(channel_id: str, db: Session = Depends(get_db)):
    channel = _get_channel(db, channel_id, include_deleted=True)
    _soft_delete(channel)
    db.commit()


@router.post("/channels/{channel_id}/restore", response_model=SalesChannelResponse)
def restore_channel(channel_id: str, db: Session = Depends(get_db)):
    channel = _get_channel(db, channel_id, include_deleted=True)
    _restore(channel)
    db.commit()
    return SalesChannelResponse.model_validate(channel)


# --------------------------------------------------------------------------- #
# Pricebooks & items
# --------------------------------------------------------------------------- #
def _pricebook_query(db: Session, pricebook_id: str, include_deleted: bool = False):
    pricebook = db.get(Pricebook, pricebook_id)
    if not pricebook or (pricebook.deleted_at and not include_deleted):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pricebook not found"
        )
    return pricebook


@router.get("/pricebooks", response_model=List[PricebookResponse])
def list_pricebooks(
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    stmt = _apply_filters(
        select(Pricebook).order_by(Pricebook.active_from.desc()),
        include_deleted,
        include_archived,
        Pricebook,
    )
    pricebooks = db.execute(stmt).scalars().all()
    return [PricebookResponse.model_validate(pb) for pb in pricebooks]


@router.post(
    "/pricebooks",
    response_model=PricebookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pricebook(data: PricebookCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(Pricebook).where(Pricebook.name == data.name)
    ).scalar_one_or_none()
    if existing and existing.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pricebook '{data.name}' already exists",
        )
    pricebook = Pricebook(
        name=data.name,
        currency=data.currency,
        active_from=data.active_from,
        active_to=data.active_to,
    )
    db.add(pricebook)
    db.commit()
    db.refresh(pricebook)
    return PricebookResponse.model_validate(pricebook)


@router.put("/pricebooks/{pricebook_id}", response_model=PricebookResponse)
def update_pricebook(
    pricebook_id: str, data: PricebookUpdate, db: Session = Depends(get_db)
):
    pricebook = _pricebook_query(db, pricebook_id)
    if data.name is not None:
        pricebook.name = data.name
    if data.currency is not None:
        pricebook.currency = data.currency
    if data.active_from is not None:
        pricebook.active_from = data.active_from
    if data.active_to is not None:
        pricebook.active_to = data.active_to
    db.commit()
    db.refresh(pricebook)
    return PricebookResponse.model_validate(pricebook)


@router.post("/pricebooks/{pricebook_id}/archive", response_model=PricebookResponse)
def archive_pricebook(pricebook_id: str, db: Session = Depends(get_db)):
    pricebook = _pricebook_query(db, pricebook_id)
    _archive(pricebook)
    db.commit()
    return PricebookResponse.model_validate(pricebook)


@router.post("/pricebooks/{pricebook_id}/unarchive", response_model=PricebookResponse)
def unarchive_pricebook(pricebook_id: str, db: Session = Depends(get_db)):
    pricebook = _pricebook_query(db, pricebook_id)
    _unarchive(pricebook)
    db.commit()
    return PricebookResponse.model_validate(pricebook)


@router.delete("/pricebooks/{pricebook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pricebook(pricebook_id: str, db: Session = Depends(get_db)):
    pricebook = _pricebook_query(db, pricebook_id, include_deleted=True)
    _soft_delete(pricebook)
    db.commit()


@router.post("/pricebooks/{pricebook_id}/restore", response_model=PricebookResponse)
def restore_pricebook(pricebook_id: str, db: Session = Depends(get_db)):
    pricebook = _pricebook_query(db, pricebook_id, include_deleted=True)
    _restore(pricebook)
    db.commit()
    return PricebookResponse.model_validate(pricebook)


def _get_pricebook_item(db: Session, pricebook_id: str, item_id: str):
    pricebook = _pricebook_query(db, pricebook_id, include_deleted=True)
    item = db.get(PricebookItem, item_id)
    if not item or item.pricebook_id != pricebook.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pricebook item not found"
        )
    return pricebook, item


@router.get(
    "/pricebooks/{pricebook_id}/items",
    response_model=List[PricebookItemResponse],
)
def list_pricebook_items(
    pricebook_id: str,
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    pricebook = _pricebook_query(db, pricebook_id, include_deleted=True)
    stmt = select(PricebookItem).where(PricebookItem.pricebook_id == pricebook.id)
    stmt = _apply_filters(stmt, include_deleted, include_archived, PricebookItem)
    items = db.execute(stmt.order_by(PricebookItem.product_id)).scalars().all()
    return [PricebookItemResponse.model_validate(item) for item in items]


@router.post(
    "/pricebooks/{pricebook_id}/items",
    response_model=PricebookItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pricebook_item(
    pricebook_id: str,
    data: PricebookItemCreate,
    db: Session = Depends(get_db),
):
    pricebook = _pricebook_query(db, pricebook_id)
    existing = db.execute(
        select(PricebookItem).where(
            PricebookItem.pricebook_id == pricebook.id,
            PricebookItem.product_id == data.product_id,
            PricebookItem.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already exists in pricebook",
        )
    item = PricebookItem(
        pricebook_id=pricebook.id,
        product_id=data.product_id,
        sku_code=data.sku_code,
        unit_price_ex_gst=data.unit_price_ex_gst,
        unit_price_inc_gst=data.unit_price_inc_gst,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return PricebookItemResponse.model_validate(item)


@router.put(
    "/pricebooks/{pricebook_id}/items/{item_id}",
    response_model=PricebookItemResponse,
)
def update_pricebook_item(
    pricebook_id: str,
    item_id: str,
    data: PricebookItemUpdate,
    db: Session = Depends(get_db),
):
    _, item = _get_pricebook_item(db, pricebook_id, item_id)
    _ensure_active(item, "Pricebook item not found")
    if data.unit_price_ex_gst is not None:
        item.unit_price_ex_gst = data.unit_price_ex_gst
    if data.unit_price_inc_gst is not None:
        item.unit_price_inc_gst = data.unit_price_inc_gst
    if data.sku_code is not None:
        item.sku_code = data.sku_code
    db.commit()
    db.refresh(item)
    return PricebookItemResponse.model_validate(item)


@router.delete(
    "/pricebooks/{pricebook_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pricebook_item(
    pricebook_id: str, item_id: str, db: Session = Depends(get_db)
):
    _, item = _get_pricebook_item(db, pricebook_id, item_id)
    _soft_delete(item)
    db.commit()


@router.post(
    "/pricebooks/{pricebook_id}/items/{item_id}/restore",
    response_model=PricebookItemResponse,
)
def restore_pricebook_item(
    pricebook_id: str, item_id: str, db: Session = Depends(get_db)
):
    _, item = _get_pricebook_item(db, pricebook_id, item_id)
    _restore(item)
    db.commit()
    return PricebookItemResponse.model_validate(item)


@router.post(
    "/pricebooks/{pricebook_id}/items/{item_id}/archive",
    response_model=PricebookItemResponse,
)
def archive_pricebook_item(
    pricebook_id: str, item_id: str, db: Session = Depends(get_db)
):
    _, item = _get_pricebook_item(db, pricebook_id, item_id)
    _archive(item)
    db.commit()
    return PricebookItemResponse.model_validate(item)


@router.post(
    "/pricebooks/{pricebook_id}/items/{item_id}/unarchive",
    response_model=PricebookItemResponse,
)
def unarchive_pricebook_item(
    pricebook_id: str, item_id: str, db: Session = Depends(get_db)
):
    _, item = _get_pricebook_item(db, pricebook_id, item_id)
    _unarchive(item)
    db.commit()
    return PricebookItemResponse.model_validate(item)


# --------------------------------------------------------------------------- #
# Sales Tags
# --------------------------------------------------------------------------- #
def _get_tag(db: Session, tag_id: str, include_deleted: bool = False):
    tag = db.get(SalesTag, tag_id)
    if not tag or (tag.deleted_at and not include_deleted):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sales tag not found"
        )
    return tag


@router.get("/tags", response_model=List[SalesTagResponse])
def list_tags(
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    stmt = _apply_filters(
        select(SalesTag).order_by(SalesTag.slug),
        include_deleted,
        include_archived,
        SalesTag,
    )
    tags = db.execute(stmt).scalars().all()
    return [SalesTagResponse.model_validate(tag) for tag in tags]


@router.post(
    "/tags", response_model=SalesTagResponse, status_code=status.HTTP_201_CREATED
)
def create_tag(data: SalesTagCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(SalesTag).where(SalesTag.slug == data.slug)
    ).scalar_one_or_none()
    if existing and existing.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Sales tag already exists"
        )
    tag = existing or SalesTag(slug=data.slug)
    tag.label = data.label
    tag.description = data.description
    tag.deleted_at = None
    tag.archived_at = None
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return SalesTagResponse.model_validate(tag)


@router.put("/tags/{tag_id}", response_model=SalesTagResponse)
def update_tag(tag_id: str, data: SalesTagUpdate, db: Session = Depends(get_db)):
    tag = _get_tag(db, tag_id)
    if data.label is not None:
        tag.label = data.label
    if data.description is not None:
        tag.description = data.description
    db.commit()
    db.refresh(tag)
    return SalesTagResponse.model_validate(tag)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: str, db: Session = Depends(get_db)):
    tag = _get_tag(db, tag_id, include_deleted=True)
    _soft_delete(tag)
    db.commit()


@router.post("/tags/{tag_id}/restore", response_model=SalesTagResponse)
def restore_tag(tag_id: str, db: Session = Depends(get_db)):
    tag = _get_tag(db, tag_id, include_deleted=True)
    _restore(tag)
    db.commit()
    return SalesTagResponse.model_validate(tag)


@router.post("/tags/{tag_id}/archive", response_model=SalesTagResponse)
def archive_tag(tag_id: str, db: Session = Depends(get_db)):
    tag = _get_tag(db, tag_id)
    _archive(tag)
    db.commit()
    return SalesTagResponse.model_validate(tag)


@router.post("/tags/{tag_id}/unarchive", response_model=SalesTagResponse)
def unarchive_tag(tag_id: str, db: Session = Depends(get_db)):
    tag = _get_tag(db, tag_id)
    _unarchive(tag)
    db.commit()
    return SalesTagResponse.model_validate(tag)


# --------------------------------------------------------------------------- #
# Customers (for sales context: order form, sites)
# --------------------------------------------------------------------------- #
class CustomerListResponse(BaseModel):
    id: str
    code: str
    name: str
    customer_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    payment_method: Optional[str] = None
    paramount_number: Optional[str] = None
    default_pricing_level: Optional[str] = None

    class Config:
        from_attributes = True


def _get_or_create_customer_for_contact(db: Session, contact: Contact) -> Customer:
    """Return existing Customer linked to this contact, or create one from contact data."""
    existing = db.execute(
        select(Customer).where(
            Customer.contact_id == str(contact.id),
            Customer.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing:
        return existing
    # Optional: link existing Customer with same code if it has no contact_id
    by_code = db.execute(
        select(Customer).where(
            Customer.code == contact.code,
            Customer.deleted_at.is_(None),
            Customer.contact_id.is_(None),
        )
    ).scalar_one_or_none()
    if by_code:
        by_code.contact_id = str(contact.id)
        db.flush()
        return by_code
    # Create new Customer from Contact
    import uuid

    cust = Customer(
        id=str(uuid.uuid4()),
        code=contact.code,
        name=contact.name,
        customer_type=CustomerType.OTHER.value,
        contact_person=contact.contact_person,
        contact_name=contact.contact_person or contact.name,
        email=contact.email,
        phone=contact.phone,
        address=contact.address,
        billing_address_line1=getattr(contact, "billing_address_line1", None),
        billing_address_line2=getattr(contact, "billing_address_line2", None),
        billing_suburb=getattr(contact, "billing_suburb", None),
        billing_state=getattr(contact, "billing_state", None),
        billing_postcode=getattr(contact, "billing_postcode", None),
        billing_country=getattr(contact, "billing_country", None),
        delivery_address_line1=getattr(contact, "delivery_address_line1", None),
        delivery_address_line2=getattr(contact, "delivery_address_line2", None),
        delivery_suburb=getattr(contact, "delivery_suburb", None),
        delivery_state=getattr(contact, "delivery_state", None),
        delivery_postcode=getattr(contact, "delivery_postcode", None),
        delivery_country=getattr(contact, "delivery_country", None),
        tax_rate=contact.tax_rate or 10.0,
        abn=getattr(contact, "abn", None),
        notes=getattr(contact, "notes", None),
        contact_id=str(contact.id),
        is_active=contact.is_active,
    )
    db.add(cust)
    db.flush()
    return cust


@router.get("/customers", response_model=List[CustomerListResponse])
def list_customers(
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    """List customers for orders/sales: driven by contacts with is_customer=True.
    Ensures each such contact has a linked Customer record (get-or-create) and returns
    those customers so the order form can use customer_id as before.
    """
    stmt = (
        select(Contact)
        .where(Contact.is_customer.is_(True), Contact.deleted_at.is_(None))
        .order_by(Contact.name)
    )
    contacts = db.execute(stmt).scalars().all()
    result = []
    for contact in contacts:
        customer = _get_or_create_customer_for_contact(db, contact)
        result.append(
            CustomerListResponse(
                id=str(customer.id),
                code=customer.code,
                name=customer.name,
                customer_type=customer.customer_type,
                email=customer.email,
                phone=customer.phone,
                payment_method=getattr(contact, "payment_method", None),
                paramount_number=getattr(contact, "paramount_number", None),
                default_pricing_level=getattr(contact, "default_pricing_level", None),
            )
        )
    db.commit()
    return result


# --------------------------------------------------------------------------- #
# Customer sites
# --------------------------------------------------------------------------- #
def _get_site(db: Session, site_id: str, include_deleted: bool = False):
    site = db.get(CustomerSite, site_id)
    if not site or (site.deleted_at and not include_deleted):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer site not found"
        )
    return site


@router.get("/customer-sites", response_model=List[CustomerSiteResponse])
def list_sites(
    customer_id: Optional[str] = None,
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    stmt = select(CustomerSite)
    if customer_id:
        stmt = stmt.where(CustomerSite.customer_id == customer_id)
    stmt = _apply_filters(stmt, include_deleted, include_archived, CustomerSite)
    sites = db.execute(stmt.order_by(CustomerSite.site_name)).scalars().all()
    return [CustomerSiteResponse.model_validate(site) for site in sites]


@router.post(
    "/customer-sites",
    response_model=CustomerSiteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_site(data: CustomerSiteCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(CustomerSite).where(
            CustomerSite.customer_id == data.customer_id,
            CustomerSite.site_name == data.site_name,
            CustomerSite.state == data.state,
            CustomerSite.suburb == data.suburb,
        )
    ).scalar_one_or_none()
    if existing and existing.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Customer site already exists"
        )
    site = existing or CustomerSite(customer_id=data.customer_id)
    site.site_name = data.site_name
    site.state = data.state
    site.suburb = data.suburb
    site.postcode = data.postcode
    site.latitude = data.latitude
    site.longitude = data.longitude
    site.deleted_at = None
    site.archived_at = None
    db.add(site)
    db.commit()
    db.refresh(site)
    return CustomerSiteResponse.model_validate(site)


@router.put("/customer-sites/{site_id}", response_model=CustomerSiteResponse)
def update_site(site_id: str, data: CustomerSiteUpdate, db: Session = Depends(get_db)):
    site = _get_site(db, site_id)
    if data.site_name is not None:
        site.site_name = data.site_name
    if data.state is not None:
        site.state = data.state
    if data.suburb is not None:
        site.suburb = data.suburb
    if data.postcode is not None:
        site.postcode = data.postcode
    if data.latitude is not None:
        site.latitude = data.latitude
    if data.longitude is not None:
        site.longitude = data.longitude
    db.commit()
    db.refresh(site)
    return CustomerSiteResponse.model_validate(site)


@router.delete("/customer-sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(site_id: str, db: Session = Depends(get_db)):
    site = _get_site(db, site_id, include_deleted=True)
    _soft_delete(site)
    db.commit()


# --------------------------------------------------------------------------- #
# Customer import aliases (CSV name mapping)
# --------------------------------------------------------------------------- #
class CustomerImportAliasCreate(BaseModel):
    alias: str = Field(..., min_length=1, max_length=200)
    customer_id: str
    notes: Optional[str] = None


class CustomerImportAliasResponse(BaseModel):
    id: str
    alias: str
    alias_key: str
    customer_id: str
    customer_name: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


@router.get(
    "/customer-import-aliases",
    response_model=List[CustomerImportAliasResponse],
)
def list_customer_import_aliases(db: Session = Depends(get_db)):
    service = CustomerMappingService(db)
    rows = service.list_aliases()
    return [
        CustomerImportAliasResponse(
            id=str(row.id),
            alias=row.alias_label,
            alias_key=row.alias_key,
            customer_id=str(row.customer_id),
            customer_name=row.customer.name if row.customer else "",
            notes=row.notes,
        )
        for row in rows
    ]


@router.post(
    "/customer-import-aliases",
    response_model=CustomerImportAliasResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_import_alias(
    data: CustomerImportAliasCreate,
    db: Session = Depends(get_db),
):
    service = CustomerMappingService(db)
    try:
        row = service.add_alias(data.alias, data.customer_id, notes=data.notes)
        db.commit()
        db.refresh(row)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return CustomerImportAliasResponse(
        id=str(row.id),
        alias=row.alias_label,
        alias_key=row.alias_key,
        customer_id=str(row.customer_id),
        customer_name=row.customer.name if row.customer else "",
        notes=row.notes,
    )


@router.delete(
    "/customer-import-aliases/{alias_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer_import_alias(alias_id: str, db: Session = Depends(get_db)):
    service = CustomerMappingService(db)
    try:
        service.remove_alias(alias_id)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


class CustomerSiteImportAliasCreate(BaseModel):
    alias: str = Field(..., min_length=1, max_length=200)
    customer_id: str
    site_name: str = Field(..., min_length=1, max_length=120)
    notes: Optional[str] = None


class CustomerSiteImportAliasResponse(BaseModel):
    id: str
    alias: str
    alias_key: str
    customer_id: str
    customer_name: str
    site_name: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


@router.get(
    "/customer-site-import-aliases",
    response_model=List[CustomerSiteImportAliasResponse],
)
def list_customer_site_import_aliases(db: Session = Depends(get_db)):
    service = CustomerMappingService(db)
    rows = service.list_site_aliases()
    return [
        CustomerSiteImportAliasResponse(
            id=str(row.id),
            alias=row.alias_label,
            alias_key=row.alias_key,
            customer_id=str(row.customer_id),
            customer_name=row.customer.name if row.customer else "",
            site_name=row.site_name,
            notes=row.notes,
        )
        for row in rows
    ]


@router.post(
    "/customer-site-import-aliases",
    response_model=CustomerSiteImportAliasResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_site_import_alias(
    data: CustomerSiteImportAliasCreate,
    db: Session = Depends(get_db),
):
    service = CustomerMappingService(db)
    try:
        row = service.add_site_alias(
            data.alias,
            data.customer_id,
            data.site_name,
            notes=data.notes,
        )
        db.commit()
        db.refresh(row)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return CustomerSiteImportAliasResponse(
        id=str(row.id),
        alias=row.alias_label,
        alias_key=row.alias_key,
        customer_id=str(row.customer_id),
        customer_name=row.customer.name if row.customer else "",
        site_name=row.site_name,
        notes=row.notes,
    )


@router.delete(
    "/customer-site-import-aliases/{alias_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer_site_import_alias(alias_id: str, db: Session = Depends(get_db)):
    service = CustomerMappingService(db)
    try:
        service.remove_site_alias(alias_id)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post("/customer-sites/{site_id}/restore", response_model=CustomerSiteResponse)
def restore_site(site_id: str, db: Session = Depends(get_db)):
    site = _get_site(db, site_id, include_deleted=True)
    _restore(site)
    db.commit()
    return CustomerSiteResponse.model_validate(site)


@router.post("/customer-sites/{site_id}/archive", response_model=CustomerSiteResponse)
def archive_site(site_id: str, db: Session = Depends(get_db)):
    site = _get_site(db, site_id)
    _archive(site)
    db.commit()
    return CustomerSiteResponse.model_validate(site)


@router.post("/customer-sites/{site_id}/unarchive", response_model=CustomerSiteResponse)
def unarchive_site(site_id: str, db: Session = Depends(get_db)):
    site = _get_site(db, site_id)
    _unarchive(site)
    db.commit()
    return CustomerSiteResponse.model_validate(site)


# --------------------------------------------------------------------------- #
# Sales Orders
# --------------------------------------------------------------------------- #
def _order_query(db: Session, order_id: str, include_deleted: bool = False):
    order = db.get(SalesOrder, order_id)
    if not order or (order.deleted_at and not include_deleted):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found"
        )
    return order


def _build_order_response(order: SalesOrder) -> SalesOrderResponse:
    return SalesOrderResponse.model_validate(
        {
            **order.__dict__,
            "lines": [
                SalesOrderLineResponse.model_validate(line) for line in order.lines
            ],
        }
    )


def _build_order_list_response(order: SalesOrder) -> SalesOrderListResponse:
    """Build list item with delivery/invoice flags from first linked docket and invoice."""
    dockets = list(order.delivery_dockets) if order.delivery_dockets else []
    invoices = list(order.invoices) if order.invoices else []
    first_docket = dockets[0] if dockets else None
    first_invoice = invoices[0] if invoices else None
    return SalesOrderListResponse.model_validate(
        {
            **order.__dict__,
            "lines": [
                SalesOrderLineResponse.model_validate(line) for line in order.lines
            ],
            "has_delivery": first_docket is not None,
            "delivery_docket_number": first_docket.docket_number
            if first_docket
            else None,
            "delivery_date": first_docket.delivery_date if first_docket else None,
            "delivery_docket_id": str(first_docket.id) if first_docket else None,
            "has_invoice": first_invoice is not None,
            "invoice_number": first_invoice.invoice_number if first_invoice else None,
            "invoice_id": str(first_invoice.id) if first_invoice else None,
            "paid": getattr(first_invoice, "paid", None) if first_invoice else None,
        }
    )


def _apply_order_lines(
    order: SalesOrder, line_inputs: List[SalesOrderLineInput], db: Session
):
    order.lines.clear()
    totals_service = TotalsService(db)
    sequence = 1
    for line_input in line_inputs:
        totals = totals_service.compute_line_totals(
            qty=line_input.qty,
            unit_price_ex_gst=line_input.unit_price_ex_gst,
            unit_price_inc_gst=line_input.unit_price_inc_gst,
            discount_ex_gst=line_input.discount_ex_gst,
        )
        order.lines.append(
            SalesOrderLine(
                product_id=line_input.product_id,
                qty=line_input.qty,
                uom=line_input.uom or "unit",
                unit_price_ex_gst=line_input.unit_price_ex_gst,
                unit_price_inc_gst=totals.line_total_inc_gst / line_input.qty
                if line_input.qty
                else line_input.unit_price_inc_gst,
                discount_ex_gst=line_input.discount_ex_gst,
                line_total_ex_gst=totals.line_total_ex_gst,
                line_total_inc_gst=totals.line_total_inc_gst,
                sequence=sequence,
                tax_rate=line_input.tax_rate,
            )
        )
        sequence += 1
    totals_service.refresh_order_totals(order)


@router.get("/orders", response_model=List[SalesOrderListResponse])
def list_orders(
    customer_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    status_filter: Optional[SalesOrderStatus] = None,
    has_delivery: Optional[bool] = Query(
        None, description="Filter by has delivery docket"
    ),
    has_invoice: Optional[bool] = Query(None, description="Filter by has invoice"),
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    stmt = select(SalesOrder)
    if customer_id:
        stmt = stmt.where(SalesOrder.customer_id == customer_id)
    if channel_id:
        stmt = stmt.where(SalesOrder.channel_id == channel_id)
    if status_filter:
        stmt = stmt.where(SalesOrder.status == status_filter.value)
    stmt = _apply_filters(stmt, include_deleted, include_archived, SalesOrder)
    orders = (
        db.execute(stmt.order_by(SalesOrder.order_date.desc())).scalars().unique().all()
    )
    if has_delivery is not None or has_invoice is not None:
        filtered = []
        for order in orders:
            dockets = list(order.delivery_dockets) if order.delivery_dockets else []
            invoices = list(order.invoices) if order.invoices else []
            if has_delivery is not None and (len(dockets) > 0) != has_delivery:
                continue
            if has_invoice is not None and (len(invoices) > 0) != has_invoice:
                continue
            filtered.append(order)
        orders = filtered
    result = []
    for order in orders:
        d = _build_order_list_response(order).model_dump()
        dockets = list(order.delivery_dockets) if order.delivery_dockets else []
        invoices = list(order.invoices) if order.invoices else []
        first_docket = dockets[0] if dockets else None
        first_invoice = invoices[0] if invoices else None
        if first_docket and getattr(first_docket, "generated_document_id", None):
            gd = db.get(GeneratedDocument, first_docket.generated_document_id)
            if (
                gd
                and getattr(gd, "status", None) == "completed"
                and getattr(gd, "pdf_path", None)
                and Path(gd.pdf_path).exists()
            ):
                d["delivery_docket_document"] = {
                    "id": str(gd.id),
                    "pdf_path": gd.pdf_path,
                }
            else:
                d["delivery_docket_document"] = None
        else:
            d["delivery_docket_document"] = None
        if first_invoice and getattr(first_invoice, "generated_document_id", None):
            gd = db.get(GeneratedDocument, first_invoice.generated_document_id)
            if (
                gd
                and getattr(gd, "status", None) == "completed"
                and getattr(gd, "pdf_path", None)
                and Path(gd.pdf_path).exists()
            ):
                d["invoice_document"] = {"id": str(gd.id), "pdf_path": gd.pdf_path}
            else:
                d["invoice_document"] = None
        else:
            d["invoice_document"] = None
        d["picking_slip_document"] = None
        result.append(SalesOrderListResponse.model_validate(d))
    return result


@router.get("/orders/{order_id}", response_model=SalesOrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = _order_query(db, order_id)
    lines_data = []
    for line in order.lines:
        line_dict = SalesOrderLineResponse.model_validate(line).model_dump()
        if getattr(line, "product", None):
            line_dict["product_sku"] = getattr(line.product, "sku", None)
            line_dict["product_name"] = getattr(line.product, "name", None)
        lines_data.append(line_dict)
    d = {
        **order.__dict__,
        "lines": lines_data,
    }
    dockets = list(order.delivery_dockets) if order.delivery_dockets else []
    invoices = list(order.invoices) if order.invoices else []
    first_docket = dockets[0] if dockets else None
    first_invoice = invoices[0] if invoices else None
    d["delivery_docket_id"] = str(first_docket.id) if first_docket else None
    d["delivery_docket_number"] = first_docket.docket_number if first_docket else None
    d["delivery_date"] = first_docket.delivery_date if first_docket else None
    d["invoice_id"] = str(first_invoice.id) if first_invoice else None
    d["invoice_number"] = first_invoice.invoice_number if first_invoice else None
    d["paid"] = getattr(first_invoice, "paid", None) if first_invoice else None
    # Linked generated documents (for Open vs Create in UI); only include when file exists
    if first_docket and getattr(first_docket, "generated_document_id", None):
        gd = db.get(GeneratedDocument, first_docket.generated_document_id)
        if (
            gd
            and getattr(gd, "status", None) == "completed"
            and getattr(gd, "pdf_path", None)
            and Path(gd.pdf_path).exists()
        ):
            d["delivery_docket_document"] = {"id": str(gd.id), "pdf_path": gd.pdf_path}
        else:
            d["delivery_docket_document"] = None
    else:
        d["delivery_docket_document"] = None
    if first_invoice and getattr(first_invoice, "generated_document_id", None):
        gd = db.get(GeneratedDocument, first_invoice.generated_document_id)
        if (
            gd
            and getattr(gd, "status", None) == "completed"
            and getattr(gd, "pdf_path", None)
            and Path(gd.pdf_path).exists()
        ):
            d["invoice_document"] = {"id": str(gd.id), "pdf_path": gd.pdf_path}
        else:
            d["invoice_document"] = None
    else:
        d["invoice_document"] = None
    d["picking_slip_document"] = None  # TODO when picking slip generation exists
    return SalesOrderResponse.model_validate(d)


@router.post(
    "/orders",
    response_model=SalesOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(data: SalesOrderCreate, db: Session = Depends(get_db)):
    order = SalesOrder(
        customer_id=data.customer_id,
        channel_id=data.channel_id,
        customer_site_id=data.customer_site_id,
        pricebook_id=data.pricebook_id,
        order_ref=data.order_ref,
        po_number=data.po_number,
        order_discount_ex_gst=data.order_discount_ex_gst or Decimal("0"),
        order_date=data.order_date,
        status=data.status.value if data.status else SalesOrderStatus.CONFIRMED.value,
        source=data.source.value if data.source else SalesOrderSource.MANUAL.value,
        entered_by=data.entered_by,
        notes=data.notes,
    )
    db.add(order)
    db.flush()
    _apply_order_lines(order, data.lines, db)
    db.commit()
    db.refresh(order)
    return _build_order_response(order)


@router.put("/orders/{order_id}", response_model=SalesOrderResponse)
def update_order(order_id: str, data: SalesOrderUpdate, db: Session = Depends(get_db)):
    order = _order_query(db, order_id)
    # Once converted to delivery, order is fixed (no line edits)
    if (
        data.lines is not None
        and order.delivery_dockets
        and any(d.deleted_at is None for d in order.delivery_dockets)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order has been converted to delivery and can no longer be edited",
        )
    if data.channel_id is not None:
        order.channel_id = data.channel_id
    if data.customer_site_id is not None:
        order.customer_site_id = data.customer_site_id
    if data.pricebook_id is not None:
        order.pricebook_id = data.pricebook_id
    if data.order_ref is not None:
        order.order_ref = data.order_ref
    if data.po_number is not None:
        order.po_number = data.po_number
    if data.order_discount_ex_gst is not None:
        order.order_discount_ex_gst = data.order_discount_ex_gst
    if data.order_date is not None:
        order.order_date = data.order_date
    if data.status is not None:
        order.status = data.status.value
    if data.source is not None:
        order.source = data.source.value
    if data.entered_by is not None:
        order.entered_by = data.entered_by
    if data.notes is not None:
        order.notes = data.notes
    if data.lines is not None:
        _apply_order_lines(order, data.lines, db)
    else:
        TotalsService(db).refresh_order_totals(order)
    db.commit()
    db.refresh(order)
    return _build_order_response(order)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: str, db: Session = Depends(get_db)):
    # Use explicit transaction so we always have an active one (avoids "cannot commit -
    # no transaction is active" when the session/connection was reused after an error).
    with db.begin():
        order = _order_query(db, order_id, include_deleted=True)
        _soft_delete(order)


@router.post("/orders/{order_id}/restore", response_model=SalesOrderResponse)
def restore_order(order_id: str, db: Session = Depends(get_db)):
    order = _order_query(db, order_id, include_deleted=True)
    _restore(order)
    db.commit()
    db.refresh(order)
    return _build_order_response(order)


@router.post("/orders/{order_id}/archive", response_model=SalesOrderResponse)
def archive_order(order_id: str, db: Session = Depends(get_db)):
    order = _order_query(db, order_id)
    _archive(order)
    db.commit()
    db.refresh(order)
    return _build_order_response(order)


@router.post("/orders/{order_id}/unarchive", response_model=SalesOrderResponse)
def unarchive_order(order_id: str, db: Session = Depends(get_db)):
    order = _order_query(db, order_id)
    _unarchive(order)
    db.commit()
    db.refresh(order)
    return _build_order_response(order)


def _next_docket_number(db: Session) -> str:
    """Generate unique delivery docket number DD-YYYYMMDD-XXXX."""
    from datetime import date

    prefix = f"DD-{date.today().strftime('%Y%m%d')}-"
    existing = (
        db.execute(
            select(DeliveryDocket.docket_number).where(
                DeliveryDocket.docket_number.like(f"{prefix}%"),
                DeliveryDocket.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )
    used = {
        int(n.split("-")[-1])
        for n in (x[0] for x in existing)
        if n.split("-")[-1].isdigit()
    }
    n = 1
    while n in used:
        n += 1
    return f"{prefix}{n:04d}"


def _next_invoice_number(db: Session) -> str:
    """Generate unique invoice number INV-YYYYMMDD-XXXX."""
    from datetime import date

    prefix = f"INV-{date.today().strftime('%Y%m%d')}-"
    existing = (
        db.execute(
            select(Invoice.invoice_number).where(
                Invoice.invoice_number.like(f"{prefix}%"),
            )
        )
        .scalars()
        .all()
    )
    used = {
        int(n.split("-")[-1])
        for n in (x[0] for x in existing)
        if len(n.split("-")) == 3 and n.split("-")[-1].isdigit()
    }
    n = 1
    while n in used:
        n += 1
    return f"{prefix}{n:04d}"


class ConvertToDeliveryRequest(BaseModel):
    delivery_date: Optional[datetime] = None


class DeliveryDocketLineUpdate(BaseModel):
    line_id: str
    quantity: Decimal  # dqty, must be <= ordered_quantity


class DeliveryDocketLinesUpdateRequest(BaseModel):
    lines: List[DeliveryDocketLineUpdate]


class BackorderLineInput(BaseModel):
    product_id: str
    backorder_qty: Decimal


class BackorderRequest(BaseModel):
    lines: List[BackorderLineInput]


@router.get("/delivery-dockets/{docket_id}")
def get_delivery_docket(docket_id: str, db: Session = Depends(get_db)):
    """Get delivery docket with lines (oqty, dqty, product) for delivery-quantities step."""
    docket = db.get(DeliveryDocket, docket_id)
    if not docket or getattr(docket, "deleted_at", None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery docket not found"
        )
    lines_out = []
    for line in sorted(docket.lines or [], key=lambda ln: (ln.sequence, ln.id)):
        if getattr(line, "deleted_at", None):
            continue
        product = line.product
        lines_out.append(
            {
                "id": str(line.id),
                "product_id": str(line.product_id),
                "product_sku": product.sku if product else None,
                "product_name": product.name if product else None,
                "ordered_quantity": float(line.ordered_quantity)
                if line.ordered_quantity is not None
                else float(line.quantity),
                "quantity": float(line.quantity),
                "unit_price": float(line.unit_price)
                if line.unit_price is not None
                else None,
                "uom": line.uom or "unit",
            }
        )
    return {
        "id": str(docket.id),
        "docket_number": docket.docket_number,
        "delivery_date": docket.delivery_date.isoformat()
        if docket.delivery_date
        else None,
        "lines": lines_out,
    }


@router.patch("/delivery-dockets/{docket_id}/lines")
def update_delivery_docket_lines(
    docket_id: str,
    body: DeliveryDocketLinesUpdateRequest,
    db: Session = Depends(get_db),
):
    """Set delivery quantity (dqty) per line. dqty must be <= ordered_quantity."""
    docket = db.get(DeliveryDocket, docket_id)
    if not docket or getattr(docket, "deleted_at", None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery docket not found"
        )
    line_ids = {
        str(ln.id): ln
        for ln in (docket.lines or [])
        if not getattr(ln, "deleted_at", None)
    }
    for item in body.lines:
        line = line_ids.get(item.line_id)
        if not line:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Line {item.line_id} not found",
            )
        oqty = (
            line.ordered_quantity
            if line.ordered_quantity is not None
            else line.quantity
        )
        if item.quantity > oqty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Delivery quantity cannot exceed ordered quantity (max {oqty})",
            )
        if item.quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity cannot be negative",
            )
        line.quantity = item.quantity
    db.commit()
    db.refresh(docket)
    return {"delivery_docket_id": docket_id, "updated": len(body.lines)}


@router.post("/orders/{order_id}/convert-to-delivery")
def convert_order_to_delivery(
    order_id: str,
    body: Optional[ConvertToDeliveryRequest] = None,
    db: Session = Depends(get_db),
):
    """Create a delivery docket from this order; add docket number and delivery date."""
    order = _order_query(db, order_id)
    if order.delivery_dockets and any(
        d.deleted_at is None for d in order.delivery_dockets
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order already has a delivery docket",
        )
    docket_number = _next_docket_number(db)
    docket = DeliveryDocket(
        customer_id=order.customer_id,
        sales_order_id=order.id,
        docket_number=docket_number,
        docket_date=datetime.utcnow(),
        delivery_date=(body.delivery_date if body else None) or datetime.utcnow(),
        status="PENDING",
        notes=order.notes,
    )
    db.add(docket)
    db.flush()
    for seq, line in enumerate(order.lines, 1):
        db.add(
            DeliveryDocketLine(
                docket_id=docket.id,
                product_id=line.product_id,
                quantity=line.qty,
                ordered_quantity=line.qty,
                unit_price=getattr(line, "unit_price_ex_gst", None),
                uom=line.uom or "unit",
                sequence=seq,
            )
        )
    db.commit()
    db.refresh(docket)
    return {
        "delivery_docket_id": docket.id,
        "docket_number": docket.docket_number,
        "delivery_date": docket.delivery_date.isoformat()
        if docket.delivery_date
        else None,
    }


class ConvertToInvoiceRequest(BaseModel):
    delivery_docket_id: Optional[str] = None


@router.post("/orders/{order_id}/convert-to-invoice")
def convert_order_to_invoice(
    order_id: str,
    body: Optional[ConvertToInvoiceRequest] = None,
    db: Session = Depends(get_db),
):
    """Create an invoice from this order (and optionally link delivery docket). Sets paid=False."""
    order = _order_query(db, order_id)
    if order.invoices and any(i.deleted_at is None for i in order.invoices):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order already has an invoice",
        )
    invoice_number = _next_invoice_number(db)
    subtotal_ex = order.total_ex_gst
    total_inc = order.total_inc_gst
    total_tax = total_inc - subtotal_ex
    inv = Invoice(
        customer_id=order.customer_id,
        sales_order_id=order.id,
        delivery_docket_id=body.delivery_docket_id if body else None,
        invoice_number=invoice_number,
        invoice_date=datetime.utcnow(),
        status="SENT",
        paid=False,
        subtotal_ex_tax=subtotal_ex,
        total_tax=total_tax,
        total_inc_tax=total_inc,
        notes=order.notes,
    )
    db.add(inv)
    db.flush()
    for seq, line in enumerate(order.lines, 1):
        db.add(
            InvoiceLine(
                invoice_id=inv.id,
                product_id=line.product_id,
                quantity_kg=line.qty,
                unit_price_ex_tax=line.unit_price_ex_gst,
                tax_rate=line.tax_rate or Decimal("10"),
                line_total_ex_tax=line.line_total_ex_gst,
                line_total_inc_tax=line.line_total_inc_gst,
                sequence=seq,
            )
        )
    db.commit()
    db.refresh(inv)
    return {
        "invoice_id": inv.id,
        "invoice_number": inv.invoice_number,
        "paid": inv.paid,
    }


@router.post("/orders/{order_id}/backorder", response_model=SalesOrderResponse)
def create_backorder_order(
    order_id: str,
    body: BackorderRequest,
    db: Session = Depends(get_db),
):
    """Create a new order with remaining (backorder) quantities for the same customer, PO and order date."""
    order = _order_query(db, order_id)
    order_lines_by_product = {
        str(line.product_id): line for line in (order.lines or [])
    }
    line_inputs = []
    for item in body.lines:
        if item.backorder_qty <= 0:
            continue
        orig = order_lines_by_product.get(item.product_id)
        if not orig:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item.product_id} not on order",
            )
        line_inputs.append(
            SalesOrderLineInput(
                product_id=item.product_id,
                qty=item.backorder_qty,
                unit_price_ex_gst=orig.unit_price_ex_gst,
                unit_price_inc_gst=getattr(orig, "unit_price_inc_gst", None),
                discount_ex_gst=orig.discount_ex_gst,
                tax_rate=getattr(orig, "tax_rate", None),
                uom=orig.uom or "unit",
            )
        )
    if not line_inputs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No backorder lines with positive quantity",
        )
    new_order = SalesOrder(
        customer_id=order.customer_id,
        channel_id=order.channel_id,
        customer_site_id=order.customer_site_id,
        pricebook_id=order.pricebook_id,
        order_ref=None,
        po_number=order.po_number,
        order_date=order.order_date,
        status=SalesOrderStatus.CONFIRMED.value,
        source=order.source or SalesOrderSource.MANUAL.value,
        entered_by=order.entered_by,
        notes=f"Backorder from order {order.order_ref or order.id}",
        order_discount_ex_gst=Decimal("0"),
    )
    db.add(new_order)
    db.flush()
    _apply_order_lines(new_order, line_inputs, db)
    db.commit()
    db.refresh(new_order)
    return _build_order_response(new_order)


@router.patch("/invoices/{invoice_id}/paid", status_code=status.HTTP_200_OK)
def mark_invoice_paid(invoice_id: str, db: Session = Depends(get_db)):
    """Set invoice paid flag to True when payment is received."""
    inv = db.get(Invoice, invoice_id)
    if not inv or getattr(inv, "deleted_at", None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )
    setattr(inv, "paid", True)
    inv.status = "PAID"
    db.commit()
    return {"invoice_id": invoice_id, "paid": True}


class SalesImportCSVResponse(BaseModel):
    format: str
    orders_inserted: int
    orders_updated: int
    dockets_created: int = 0
    lines_processed: int
    errors: List[str] = Field(default_factory=list)
    order_results: List[dict] = Field(default_factory=list)


class SalesAnalyticsOverviewResponse(BaseModel):
    total_orders: int
    revenue_inc_gst: float
    average_order_value: float
    repeat_rate_pct: float
    new_customers: int
    repeat_customers: int
    inactive_customers: int
    trend: List[dict] = Field(default_factory=list)
    top_skus: List[dict] = Field(default_factory=list)
    top_customers: List[dict] = Field(default_factory=list)


class SalesAnalyticsProductRow(BaseModel):
    sku: str
    name: str
    units: float
    revenue_ex_gst: float
    revenue_inc_gst: float
    inventory: float
    channel_mix: str


class SalesAnalyticsProductsResponse(BaseModel):
    rows: List[SalesAnalyticsProductRow]
    total_units: float
    total_revenue_inc_gst: float
    total_revenue_ex_gst: float


class SalesAnalyticsFilterOptionsResponse(BaseModel):
    channels: List[dict] = Field(default_factory=list)
    pricebooks: List[dict] = Field(default_factory=list)
    default_start_date: str
    default_end_date: str


@router.get(
    "/analytics/filter-options", response_model=SalesAnalyticsFilterOptionsResponse
)
def analytics_filter_options(db: Session = Depends(get_db)):
    start, end = default_period()
    opts = SalesAnalyticsService(db).filter_options()
    return SalesAnalyticsFilterOptionsResponse(
        **opts,
        default_start_date=start.isoformat(),
        default_end_date=end.isoformat(),
    )


@router.get("/analytics/overview", response_model=SalesAnalyticsOverviewResponse)
def analytics_overview(
    start_date: date = Query(..., description="Period start (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Period end (YYYY-MM-DD)"),
    channel_id: Optional[str] = Query(None),
    pricebook_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be on or before end_date",
        )
    metrics = SalesAnalyticsService(db).get_overview(
        start_date=start_date,
        end_date=end_date,
        channel_id=channel_id,
        pricebook_id=pricebook_id,
    )
    return SalesAnalyticsOverviewResponse(
        total_orders=metrics.total_orders,
        revenue_inc_gst=float(metrics.revenue_inc_gst),
        average_order_value=float(metrics.average_order_value),
        repeat_rate_pct=metrics.repeat_rate_pct,
        new_customers=metrics.new_customers,
        repeat_customers=metrics.repeat_customers,
        inactive_customers=metrics.inactive_customers,
        trend=metrics.trend,
        top_skus=metrics.top_skus,
        top_customers=metrics.top_customers,
    )


@router.get("/analytics/products", response_model=SalesAnalyticsProductsResponse)
def analytics_products(
    start_date: date = Query(..., description="Period start (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Period end (YYYY-MM-DD)"),
    channel_id: Optional[str] = Query(None),
    pricebook_id: Optional[str] = Query(None),
    segment: Optional[str] = Query(None, description="top, slow, or new"),
    db: Session = Depends(get_db),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be on or before end_date",
        )
    summary = SalesAnalyticsService(db).get_products_sold(
        start_date=start_date,
        end_date=end_date,
        channel_id=channel_id,
        pricebook_id=pricebook_id,
        segment=segment,
    )
    return SalesAnalyticsProductsResponse(
        rows=[
            SalesAnalyticsProductRow(
                sku=r.sku,
                name=r.name,
                units=float(r.units),
                revenue_ex_gst=float(r.revenue_ex_gst),
                revenue_inc_gst=float(r.revenue_inc_gst),
                inventory=float(r.inventory_qty),
                channel_mix=r.channel_mix,
            )
            for r in summary.rows
        ],
        total_units=float(summary.total_units),
        total_revenue_inc_gst=float(summary.total_revenue_inc_gst),
        total_revenue_ex_gst=float(summary.total_revenue_ex_gst),
    )


@router.post("/import/csv", response_model=SalesImportCSVResponse)
async def import_sales_csv(
    file: UploadFile = File(...),
    allow_create: bool = Form(False),
    create_delivery_docket: bool = Form(True),
    pricebook_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Import sales orders from a CSV file (standard sales or delivery docket layout)."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload a .csv file",
        )
    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV must be UTF-8 encoded",
        ) from exc

    importer = SalesCSVImporter(db)
    try:
        summary = importer.import_text(
            text,
            allow_create=allow_create,
            pricebook_id=pricebook_id,
            create_delivery_docket=create_delivery_docket,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {exc}",
        ) from exc

    return SalesImportCSVResponse(**summary.to_dict())
