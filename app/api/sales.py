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
from pydantic import BaseModel, Field, model_validator, validator
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import (
    Contact,
    CustomerPrice,
    DeliveryDocket,
    DeliveryDocketLine,
    GeneratedDocument,
    Invoice,
    InvoiceLine,
    Product,
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
from apps.vndmanuf_sales.services.analytics import (
    SalesAnalyticsService,
    _as_datetime_end,
    _as_datetime_start,
    default_period,
)
from apps.vndmanuf_sales.services.customer_location_enrichment import (
    CustomerLocationEnrichmentService,
)
from apps.vndmanuf_sales.services.customer_map import CustomerMapService
from apps.vndmanuf_sales.services.customer_mapping import CustomerMappingService
from apps.vndmanuf_sales.services.customer_pricing import (
    PRICING_LEVELS,
    count_active_special_prices_for_customers,
    get_customer_pricing_level,
    is_special_price_active,
    list_tier_prices_for_customer,
    list_tier_prices_for_level,
    resolve_customer_product_price,
)
from apps.vndmanuf_sales.services.import_sales_csv import SalesCSVImporter
from apps.vndmanuf_sales.services.pricing import PriceComputationError, PricingService
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
    freight_ex_gst: Optional[Decimal] = None
    freight_gst: Optional[Decimal] = None
    freight_inc_gst: Optional[Decimal] = None
    commission_amount: Optional[Decimal] = None
    distributor: Optional[str] = Field(None, max_length=50)
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
    freight_ex_gst: Optional[Decimal] = None
    freight_gst: Optional[Decimal] = None
    freight_inc_gst: Optional[Decimal] = None
    commission_amount: Optional[Decimal] = None
    distributor: Optional[str] = Field(None, max_length=50)
    payment_date: Optional[datetime] = None
    payment_reference: Optional[str] = Field(None, max_length=100)
    invoice_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    paid: Optional[bool] = None
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
    freight_ex_gst: Optional[Decimal] = None
    freight_gst: Optional[Decimal] = None
    freight_inc_gst: Optional[Decimal] = None
    commission_amount: Optional[Decimal] = None
    distributor: Optional[str] = None
    payment_date: Optional[datetime] = None
    payment_reference: Optional[str] = None
    invoice_date: Optional[datetime] = None
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


class OrderSummaryRow(BaseModel):
    order_id: str
    order_date: str
    order_ref: str
    po_number: str
    status: str
    total_ex_gst: float
    total_inc_gst: float


class OrderProductSummaryRow(BaseModel):
    product_id: str
    sku: str
    name: str
    total_qty: float
    order_count: int
    total_ex_gst: float
    total_inc_gst: float


class OrderProductSummaryResponse(BaseModel):
    orders: List[OrderSummaryRow]
    rows: List[OrderProductSummaryRow]
    order_count: int
    total_qty: float
    total_ex_gst: float
    total_inc_gst: float


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
    active_special_prices: int = 0
    created_at: Optional[datetime] = None
    order_count: int = 0
    revenue_inc_gst: float = 0.0
    last_order_date: Optional[str] = None
    days_since_last_order: Optional[int] = None

    class Config:
        from_attributes = True


class CustomerDashboardSummary(BaseModel):
    active_customers: int
    new_this_month: int
    avg_lifetime_value: float
    days_since_last_order: Optional[int] = None


class CustomerDashboardResponse(BaseModel):
    summary: CustomerDashboardSummary
    customers: List[CustomerListResponse]


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
                name=contact.name or customer.name,
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


@router.get("/customers/dashboard", response_model=CustomerDashboardResponse)
def customer_dashboard(db: Session = Depends(get_db)):
    """Customers tab: KPI summary plus per-customer order stats."""
    contacts = (
        db.execute(
            select(Contact)
            .where(Contact.is_customer.is_(True), Contact.deleted_at.is_(None))
            .order_by(Contact.name)
        )
        .scalars()
        .all()
    )

    order_stats = SalesAnalyticsService(db).get_customer_order_stats()
    customers: List[CustomerListResponse] = []
    customer_ids: List[str] = []

    for contact in contacts:
        customer = _get_or_create_customer_for_contact(db, contact)
        customer_ids.append(str(customer.id))
        stats = order_stats.get(str(customer.id), {})
        last_order_dt = stats.get("last_order_date")
        days_since: Optional[int] = None
        if last_order_dt:
            days_since = (date.today() - last_order_dt.date()).days
        created_at = customer.created_at
        customers.append(
            CustomerListResponse(
                id=str(customer.id),
                code=customer.code,
                name=contact.name or customer.name,
                customer_type=customer.customer_type,
                email=customer.email,
                phone=customer.phone,
                payment_method=getattr(contact, "payment_method", None),
                paramount_number=getattr(contact, "paramount_number", None),
                default_pricing_level=getattr(contact, "default_pricing_level", None),
                created_at=created_at,
                order_count=int(stats.get("order_count", 0)),
                revenue_inc_gst=float(stats.get("revenue_inc_gst", 0)),
                last_order_date=last_order_dt.date().isoformat()
                if last_order_dt
                else None,
                days_since_last_order=days_since,
            )
        )

    active_special_counts = count_active_special_prices_for_customers(
        db, customer_ids, datetime.utcnow()
    )
    customers = [
        c.model_copy(
            update={
                "active_special_prices": active_special_counts.get(c.id, 0),
            }
        )
        for c in customers
    ]

    summary_data = SalesAnalyticsService(db).get_customer_dashboard_summary(
        active_customer_count=len(customers),
        order_stats=order_stats,
    )
    db.commit()
    return CustomerDashboardResponse(
        summary=CustomerDashboardSummary(**summary_data),
        customers=customers,
    )


# --------------------------------------------------------------------------- #
# Customer pricing (default tier + special product prices)
# --------------------------------------------------------------------------- #
class CustomerPricingLevelUpdate(BaseModel):
    default_pricing_level: Optional[str] = Field(None, max_length=50)


class CustomerSpecialPriceCreate(BaseModel):
    product_id: str
    unit_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    unit_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)

    @model_validator(mode="after")
    def require_unit_price(self):
        if self.unit_price_ex_gst is None and self.unit_price_inc_gst is None:
            raise ValueError("Provide unit_price_ex_gst or unit_price_inc_gst")
        return self


class CustomerSpecialPriceResponse(BaseModel):
    id: str
    customer_id: str
    customer_name: Optional[str] = None
    product_id: str
    product_sku: Optional[str] = None
    product_name: Optional[str] = None
    unit_price_ex_gst: Decimal
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: bool = False


class CustomerPricingResponse(BaseModel):
    customer_id: str
    customer_name: str
    default_pricing_level: Optional[str] = None
    pricing_levels: List[str] = Field(default_factory=lambda: list(PRICING_LEVELS))
    special_prices: List[CustomerSpecialPriceResponse]


class PriceResolveResponse(BaseModel):
    unit_price_ex_gst: float
    unit_price_inc_gst: float
    pricing_level: str
    source: str
    special_price_id: Optional[str] = None


class TierPriceCatalogRow(BaseModel):
    product_id: str
    product: str
    sku: Optional[str] = None
    unit_price_ex_gst: Optional[float] = None
    unit_price_inc_gst: Optional[float] = None
    has_active_special: bool = False
    special_price_ex_gst: Optional[float] = None
    special_price_inc_gst: Optional[float] = None


class CustomerSpecialPriceUpdate(BaseModel):
    unit_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    unit_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)


def _customer_display_name(
    customer: Customer, contact: Optional[Contact] = None
) -> str:
    """Prefer contact name; avoid showing raw UUIDs as the customer label."""
    import re

    uuid_re = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    def _ok(value: Optional[str]) -> bool:
        if not value or not str(value).strip():
            return False
        return not uuid_re.match(str(value).strip())

    for candidate in (
        getattr(contact, "name", None) if contact else None,
        customer.name,
        customer.code,
    ):
        if _ok(candidate):
            return str(candidate).strip()
    return customer.code or "Customer"


def _get_sales_customer(db: Session, customer_id: str) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer or customer.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    return customer


def _special_price_to_response(
    db: Session, cp: CustomerPrice, as_of: Optional[datetime] = None
) -> CustomerSpecialPriceResponse:
    as_of = as_of or datetime.utcnow()
    customer = db.get(Customer, cp.customer_id)
    product = db.get(Product, cp.product_id)
    customer_name = customer.name if customer else None
    if customer and customer.contact_id:
        contact = db.get(Contact, customer.contact_id)
        if contact and contact.name:
            customer_name = contact.name
    return CustomerSpecialPriceResponse(
        id=str(cp.id),
        customer_id=str(cp.customer_id),
        customer_name=customer_name,
        product_id=str(cp.product_id),
        product_sku=getattr(product, "sku", None) if product else None,
        product_name=getattr(product, "name", None) if product else None,
        unit_price_ex_gst=cp.unit_price_ex_tax,
        effective_date=cp.effective_date,
        expiry_date=cp.expiry_date,
        notes=getattr(cp, "notes", None),
        is_active=is_special_price_active(cp, as_of),
    )


@router.get("/customers/{customer_id}/pricing", response_model=CustomerPricingResponse)
def get_customer_pricing(customer_id: str, db: Session = Depends(get_db)):
    customer = _get_sales_customer(db, customer_id)
    contact = None
    if customer.contact_id:
        contact = db.get(Contact, customer.contact_id)
    name = _customer_display_name(customer, contact)
    level = get_customer_pricing_level(db, customer_id)
    rows = (
        db.execute(
            select(CustomerPrice)
            .where(
                CustomerPrice.customer_id == customer_id,
                CustomerPrice.deleted_at.is_(None),
            )
            .order_by(
                CustomerPrice.product_id,
                CustomerPrice.effective_date.desc(),
            )
        )
        .scalars()
        .all()
    )
    return CustomerPricingResponse(
        customer_id=str(customer.id),
        customer_name=name,
        default_pricing_level=level,
        special_prices=[_special_price_to_response(db, r) for r in rows],
    )


@router.put(
    "/customers/{customer_id}/pricing-level", response_model=CustomerPricingResponse
)
def update_customer_pricing_level(
    customer_id: str, data: CustomerPricingLevelUpdate, db: Session = Depends(get_db)
):
    customer = _get_sales_customer(db, customer_id)
    if not customer.contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer has no linked contact; set pricing level on the contact first",
        )
    contact = db.get(Contact, customer.contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Linked contact not found"
        )
    level = (data.default_pricing_level or "").strip().lower() or None
    if level and level not in PRICING_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pricing level. Use one of: {', '.join(PRICING_LEVELS)}",
        )
    contact.default_pricing_level = level
    db.commit()
    return get_customer_pricing(customer_id, db)


@router.post(
    "/customers/{customer_id}/special-prices",
    response_model=CustomerSpecialPriceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_special_price(
    customer_id: str, data: CustomerSpecialPriceCreate, db: Session = Depends(get_db)
):
    _get_sales_customer(db, customer_id)
    product = db.get(Product, data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    if data.expiry_date and data.expiry_date < data.effective_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after start date",
        )
    pricing_svc = PricingService(db)
    gst_rate = (
        pricing_svc._get_customer_tax_rate(customer_id)  # noqa: SLF001
        or pricing_svc.default_gst_rate
    )
    try:
        unit_ex, _ = pricing_svc._pair_prices(  # noqa: SLF001
            data.unit_price_ex_gst,
            data.unit_price_inc_gst,
            gst_rate,
        )
    except PriceComputationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    cp = CustomerPrice(
        customer_id=customer_id,
        product_id=data.product_id,
        unit_price_ex_tax=unit_ex,
        effective_date=data.effective_date,
        expiry_date=data.expiry_date,
        notes=(data.notes or "").strip() or None,
    )
    db.add(cp)
    db.commit()
    db.refresh(cp)
    return _special_price_to_response(db, cp)


def _get_customer_special_price(
    db: Session, customer_id: str, price_id: str
) -> CustomerPrice:
    cp = db.get(CustomerPrice, price_id)
    if not cp or cp.deleted_at or str(cp.customer_id) != str(customer_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer special price not found",
        )
    return cp


@router.put(
    "/customers/{customer_id}/special-prices/{price_id}",
    response_model=CustomerSpecialPriceResponse,
)
def update_customer_special_price(
    customer_id: str,
    price_id: str,
    data: CustomerSpecialPriceUpdate,
    db: Session = Depends(get_db),
):
    _get_sales_customer(db, customer_id)
    cp = _get_customer_special_price(db, customer_id, price_id)
    pricing_svc = PricingService(db)
    gst_rate = (
        pricing_svc._get_customer_tax_rate(customer_id)  # noqa: SLF001
        or pricing_svc.default_gst_rate
    )

    if data.unit_price_ex_gst is not None or data.unit_price_inc_gst is not None:
        try:
            unit_ex, _ = pricing_svc._pair_prices(  # noqa: SLF001
                data.unit_price_ex_gst,
                data.unit_price_inc_gst,
                gst_rate,
            )
        except PriceComputationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        cp.unit_price_ex_tax = unit_ex

    if data.effective_date is not None:
        cp.effective_date = data.effective_date
    updates = data.model_dump(exclude_unset=True)
    if "expiry_date" in updates:
        cp.expiry_date = data.expiry_date
    if data.notes is not None:
        cp.notes = (data.notes or "").strip() or None

    effective = cp.effective_date
    expiry = cp.expiry_date
    if expiry and effective and expiry < effective:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after start date",
        )

    db.commit()
    db.refresh(cp)
    return _special_price_to_response(db, cp)


@router.delete(
    "/customers/{customer_id}/special-prices/{price_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer_special_price(
    customer_id: str, price_id: str, db: Session = Depends(get_db)
):
    _get_sales_customer(db, customer_id)
    cp = _get_customer_special_price(db, customer_id, price_id)
    _soft_delete(cp)
    db.commit()


@router.get("/special-prices", response_model=List[CustomerSpecialPriceResponse])
def list_all_special_prices(
    customer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    active_only: bool = Query(False, description="Only offers active as of as_of date"),
    as_of: Optional[date] = Query(
        None, description="Active-as-of date (default today)"
    ),
    db: Session = Depends(get_db),
):
    """Global view of customer special pricing offers (full history unless active_only)."""
    as_of_dt = _as_datetime_start(as_of) if as_of else datetime.utcnow()
    stmt = select(CustomerPrice).where(CustomerPrice.deleted_at.is_(None))
    if customer_id:
        stmt = stmt.where(CustomerPrice.customer_id == customer_id)
    if product_id:
        stmt = stmt.where(CustomerPrice.product_id == product_id)
    rows = (
        db.execute(
            stmt.order_by(
                CustomerPrice.customer_id,
                CustomerPrice.product_id,
                CustomerPrice.effective_date.desc(),
            )
        )
        .scalars()
        .all()
    )
    out = [_special_price_to_response(db, r, as_of_dt) for r in rows]
    if active_only:
        out = [r for r in out if r.is_active]
    return out


@router.get("/pricing/resolve", response_model=PriceResolveResponse)
def resolve_order_line_price(
    customer_id: str = Query(...),
    product_id: str = Query(...),
    as_of: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Resolve unit price for an order line: tier default, special price override."""
    _get_sales_customer(db, customer_id)
    try:
        result = resolve_customer_product_price(
            db, customer_id, product_id, as_of or datetime.utcnow().date()
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return PriceResolveResponse(**result)


@router.get("/pricing/tier-catalog", response_model=List[TierPriceCatalogRow])
def get_tier_price_catalog(
    pricing_level: str = Query(..., min_length=1),
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Product list prices for a pricing tier (sellable products only)."""
    level = pricing_level.strip().lower()
    if level not in PRICING_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pricing level. Use one of: {', '.join(PRICING_LEVELS)}",
        )
    if customer_id:
        _get_sales_customer(db, customer_id)
        rows = list_tier_prices_for_customer(db, level, customer_id)
    else:
        rows = list_tier_prices_for_level(db, level)
    return [TierPriceCatalogRow(**row) for row in rows]


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


def _get_filtered_orders(
    db: Session,
    *,
    customer_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    status_filter: Optional[SalesOrderStatus] = None,
    has_delivery: Optional[bool] = None,
    has_invoice: Optional[bool] = None,
    paid: Optional[bool] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    include_deleted: bool = False,
    include_archived: bool = False,
) -> List[SalesOrder]:
    """Shared order filters for list and product-summary endpoints."""
    stmt = select(SalesOrder)
    if customer_id:
        stmt = stmt.where(SalesOrder.customer_id == customer_id)
    if channel_id:
        stmt = stmt.where(SalesOrder.channel_id == channel_id)
    if status_filter:
        stmt = stmt.where(SalesOrder.status == status_filter.value)
    if start_date:
        stmt = stmt.where(SalesOrder.order_date >= _as_datetime_start(start_date))
    if end_date:
        stmt = stmt.where(SalesOrder.order_date <= _as_datetime_end(end_date))
    stmt = _apply_filters(stmt, include_deleted, include_archived, SalesOrder)
    orders = (
        db.execute(stmt.order_by(SalesOrder.order_date.desc())).scalars().unique().all()
    )
    if has_delivery is not None or has_invoice is not None or paid is not None:
        filtered = []
        for order in orders:
            dockets = [
                d
                for d in (order.delivery_dockets or [])
                if getattr(d, "deleted_at", None) is None
            ]
            invoices = [
                i
                for i in (order.invoices or [])
                if getattr(i, "deleted_at", None) is None
            ]
            if has_delivery is not None and (len(dockets) > 0) != has_delivery:
                continue
            if has_invoice is not None and (len(invoices) > 0) != has_invoice:
                continue
            if paid is not None:
                first_invoice = invoices[0] if invoices else None
                is_paid = bool(first_invoice and getattr(first_invoice, "paid", False))
                if is_paid != paid:
                    continue
            filtered.append(order)
        orders = filtered
    return orders


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
    paid: Optional[bool] = Query(None, description="Filter by invoice paid status"),
    start_date: Optional[date] = Query(None, description="Order date from (inclusive)"),
    end_date: Optional[date] = Query(None, description="Order date to (inclusive)"),
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    orders = _get_filtered_orders(
        db,
        customer_id=customer_id,
        channel_id=channel_id,
        status_filter=status_filter,
        has_delivery=has_delivery,
        has_invoice=has_invoice,
        paid=paid,
        start_date=start_date,
        end_date=end_date,
        include_deleted=include_deleted,
        include_archived=include_archived,
    )
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


@router.get("/orders/product-summary", response_model=OrderProductSummaryResponse)
def order_product_summary(
    customer_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    status_filter: Optional[SalesOrderStatus] = None,
    has_delivery: Optional[bool] = Query(
        None, description="Filter by has delivery docket"
    ),
    has_invoice: Optional[bool] = Query(None, description="Filter by has invoice"),
    paid: Optional[bool] = Query(None, description="Filter by invoice paid status"),
    start_date: Optional[date] = Query(None, description="Order date from (inclusive)"),
    end_date: Optional[date] = Query(None, description="Order date to (inclusive)"),
    include_deleted: bool = Query(False),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    """Aggregate products purchased across orders matching the same filters as GET /orders."""
    orders = _get_filtered_orders(
        db,
        customer_id=customer_id,
        channel_id=channel_id,
        status_filter=status_filter,
        has_delivery=has_delivery,
        has_invoice=has_invoice,
        paid=paid,
        start_date=start_date,
        end_date=end_date,
        include_deleted=include_deleted,
        include_archived=include_archived,
    )
    order_ids = [o.id for o in orders]
    order_rows = [
        OrderSummaryRow(
            order_id=str(order.id),
            order_date=(
                order.order_date.date().isoformat()
                if order.order_date and hasattr(order.order_date, "date")
                else (str(order.order_date)[:10] if order.order_date else "")
            ),
            order_ref=order.order_ref or "—",
            po_number=order.po_number or "—",
            status=(order.status or "").title(),
            total_ex_gst=float(order.total_ex_gst or 0),
            total_inc_gst=float(order.total_inc_gst or 0),
        )
        for order in orders
    ]
    if not order_ids:
        return OrderProductSummaryResponse(
            orders=[],
            rows=[],
            order_count=0,
            total_qty=0.0,
            total_ex_gst=0.0,
            total_inc_gst=0.0,
        )

    summary_rows = db.execute(
        select(
            SalesOrderLine.product_id,
            Product.sku,
            Product.name,
            func.sum(SalesOrderLine.qty).label("total_qty"),
            func.count(func.distinct(SalesOrderLine.order_id)).label("order_count"),
            func.sum(SalesOrderLine.line_total_ex_gst).label("total_ex"),
            func.sum(SalesOrderLine.line_total_inc_gst).label("total_inc"),
        )
        .join(Product, Product.id == SalesOrderLine.product_id)
        .where(
            SalesOrderLine.order_id.in_(order_ids),
            SalesOrderLine.deleted_at.is_(None),
        )
        .group_by(SalesOrderLine.product_id, Product.sku, Product.name)
        .order_by(func.sum(SalesOrderLine.line_total_inc_gst).desc())
    ).all()

    rows = [
        OrderProductSummaryRow(
            product_id=str(row.product_id),
            sku=row.sku or "—",
            name=row.name or "—",
            total_qty=float(row.total_qty or 0),
            order_count=int(row.order_count or 0),
            total_ex_gst=float(row.total_ex or 0),
            total_inc_gst=float(row.total_inc or 0),
        )
        for row in summary_rows
    ]
    return OrderProductSummaryResponse(
        orders=order_rows,
        rows=rows,
        order_count=len(orders),
        total_qty=sum(r.total_qty for r in rows),
        total_ex_gst=sum(r.total_ex_gst for r in rows),
        total_inc_gst=sum(r.total_inc_gst for r in rows),
    )


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
    if first_invoice and first_invoice.invoice_date:
        d["invoice_date"] = first_invoice.invoice_date
    elif getattr(order, "invoice_date", None):
        d["invoice_date"] = order.invoice_date
    else:
        d["invoice_date"] = None
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
        freight_ex_gst=data.freight_ex_gst or Decimal("0"),
        freight_gst=data.freight_gst or Decimal("0"),
        freight_inc_gst=data.freight_inc_gst or Decimal("0"),
        commission_amount=data.commission_amount,
        distributor=data.distributor,
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
    fields_set = data.model_fields_set
    if "channel_id" in fields_set:
        order.channel_id = data.channel_id
    if data.customer_site_id is not None:
        order.customer_site_id = data.customer_site_id
    if data.pricebook_id is not None:
        order.pricebook_id = data.pricebook_id
    if "order_ref" in fields_set:
        order.order_ref = data.order_ref
    if "po_number" in fields_set:
        order.po_number = data.po_number
    if "order_discount_ex_gst" in fields_set and data.order_discount_ex_gst is not None:
        order.order_discount_ex_gst = data.order_discount_ex_gst
    if data.freight_ex_gst is not None:
        order.freight_ex_gst = data.freight_ex_gst
    if data.freight_gst is not None:
        order.freight_gst = data.freight_gst
    if data.freight_inc_gst is not None:
        order.freight_inc_gst = data.freight_inc_gst
    if "commission_amount" in fields_set:
        order.commission_amount = data.commission_amount
    if "distributor" in fields_set:
        order.distributor = data.distributor or None
    if "payment_date" in fields_set:
        order.payment_date = data.payment_date
    if "payment_reference" in fields_set:
        order.payment_reference = data.payment_reference or None
    if "invoice_date" in fields_set:
        order.invoice_date = data.invoice_date
        invoices = [
            i for i in (order.invoices or []) if getattr(i, "deleted_at", None) is None
        ]
        if invoices:
            invoices[0].invoice_date = data.invoice_date
    if "delivery_date" in fields_set:
        dockets = [
            d
            for d in (order.delivery_dockets or [])
            if getattr(d, "deleted_at", None) is None
        ]
        if dockets:
            dockets[0].delivery_date = data.delivery_date
    if "paid" in fields_set:
        invoices = [
            i for i in (order.invoices or []) if getattr(i, "deleted_at", None) is None
        ]
        if invoices:
            inv = invoices[0]
            inv.paid = bool(data.paid)
            if data.paid:
                inv.status = "PAID"
            elif inv.status == "PAID":
                inv.status = "SENT"
    if "order_date" in fields_set and data.order_date is not None:
        order.order_date = data.order_date
    if "status" in fields_set and data.status is not None:
        order.status = data.status.value
    if data.source is not None:
        order.source = data.source.value
    if "entered_by" in fields_set:
        order.entered_by = data.entered_by
    if "notes" in fields_set:
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
    invoice_number: Optional[str] = Field(None, max_length=50)
    invoice_date: Optional[datetime] = None


def _invoice_number_from_docket(docket_number: Optional[str]) -> Optional[str]:
    """ALM rule: DD260050 → A260050."""
    if not docket_number:
        return None
    dn = docket_number.strip().upper()
    if dn.startswith("DD"):
        return "A" + dn[2:]
    return None


def _suggest_invoice_number_for_order(order: SalesOrder, db: Session) -> Optional[str]:
    channel_code = None
    if order.channel_id:
        ch = db.get(SalesChannel, order.channel_id)
        if ch:
            channel_code = (ch.code or "").upper()
    if channel_code != "ALM":
        return None
    dockets = [
        d
        for d in (order.delivery_dockets or [])
        if getattr(d, "deleted_at", None) is None
    ]
    if not dockets:
        return None
    return _invoice_number_from_docket(dockets[0].docket_number)


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
    dockets = [
        d
        for d in (order.delivery_dockets or [])
        if getattr(d, "deleted_at", None) is None
    ]
    delivery_docket_id = (body.delivery_docket_id if body else None) or (
        str(dockets[0].id) if dockets else None
    )
    if body and body.invoice_number:
        invoice_number = body.invoice_number.strip()
        if not invoice_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice number cannot be empty",
            )
        existing = db.execute(
            select(Invoice.id).where(Invoice.invoice_number == invoice_number)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invoice number '{invoice_number}' already exists",
            )
    else:
        suggested = _suggest_invoice_number_for_order(order, db)
        invoice_number = suggested or _next_invoice_number(db)
    invoice_date = (body.invoice_date if body else None) or datetime.utcnow()
    subtotal_ex = order.total_ex_gst
    total_inc = order.total_inc_gst
    total_tax = total_inc - subtotal_ex
    inv = Invoice(
        customer_id=order.customer_id,
        sales_order_id=order.id,
        delivery_docket_id=delivery_docket_id,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        status="SENT",
        paid=False,
        subtotal_ex_tax=subtotal_ex,
        total_tax=total_tax,
        total_inc_tax=total_inc,
        notes=order.notes,
    )
    db.add(inv)
    db.flush()
    order.invoice_date = invoice_date
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


class CustomerMapPointResponse(BaseModel):
    customer_id: str
    name: str
    code: str
    lat: float
    lon: float
    buying_group_id: Optional[str] = None
    buying_group_name: str
    buying_group_color: str
    relationship_status: str
    price_level: str
    sales_rep_name: str
    period_revenue: float
    volume_band: str
    location_source: str
    location_label: str
    address_display: Optional[str] = None
    suburb: Optional[str] = None
    state: Optional[str] = None


class CustomerMapLegendItem(BaseModel):
    buying_group_id: Optional[str] = None
    name: str
    color: str


class CustomerMapResponse(BaseModel):
    points: List[CustomerMapPointResponse] = Field(default_factory=list)
    legend: List[CustomerMapLegendItem] = Field(default_factory=list)
    total_customers: int = 0
    mapped_customers: int = 0
    unmapped_customers: int = 0


class CustomerMapFilterOptionsResponse(BaseModel):
    sales_reps: List[dict] = Field(default_factory=list)
    buying_groups: List[dict] = Field(default_factory=list)
    price_levels: List[dict] = Field(default_factory=list)
    pricebooks: List[dict] = Field(default_factory=list)
    volume_bands: List[dict] = Field(default_factory=list)
    relationship_statuses: List[dict] = Field(default_factory=list)


@router.get(
    "/analytics/customer-map/filter-options",
    response_model=CustomerMapFilterOptionsResponse,
)
def customer_map_filter_options(db: Session = Depends(get_db)):
    return CustomerMapFilterOptionsResponse(**CustomerMapService(db).filter_options())


@router.get("/analytics/customer-map", response_model=CustomerMapResponse)
def customer_map(
    start_date: date = Query(..., description="Period start (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Period end (YYYY-MM-DD)"),
    sales_rep_id: Optional[str] = Query(None),
    buying_group_id: Optional[str] = Query(None),
    price_level: Optional[str] = Query(None),
    pricebook_id: Optional[str] = Query(None),
    volume_band: Optional[str] = Query(None),
    relationship_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be on or before end_date",
        )
    summary = CustomerMapService(db).get_map(
        start_date=start_date,
        end_date=end_date,
        sales_rep_id=sales_rep_id or None,
        buying_group_id=buying_group_id or None,
        price_level=price_level or None,
        pricebook_id=pricebook_id or None,
        volume_band=volume_band or None,
        relationship_status=relationship_status or None,
    )
    return CustomerMapResponse(
        points=[CustomerMapPointResponse(**p) for p in summary.points],
        legend=[CustomerMapLegendItem(**item) for item in summary.legend],
        total_customers=summary.total_customers,
        mapped_customers=summary.mapped_customers,
        unmapped_customers=summary.unmapped_customers,
    )


class CustomerLocationEnrichRequest(BaseModel):
    customer_ids: Optional[List[str]] = None
    limit: int = Field(default=15, ge=1, le=50)
    dry_run: bool = False
    min_confidence: float = Field(default=0.55, ge=0.0, le=1.0)
    use_llm: bool = False


class CustomerLocationEnrichRow(BaseModel):
    customer_id: str
    customer_name: str
    status: str
    query: Optional[str] = None
    message: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    display_name: Optional[str] = None


class CustomerLocationEnrichResponse(BaseModel):
    processed: int
    updated: int
    skipped: int
    not_found: int
    failed: int
    results: List[CustomerLocationEnrichRow] = Field(default_factory=list)


@router.post(
    "/customers/enrich-locations",
    response_model=CustomerLocationEnrichResponse,
)
def enrich_customer_locations(
    body: CustomerLocationEnrichRequest,
    db: Session = Depends(get_db),
):
    """Look up missing addresses/coordinates (OpenStreetMap; optional ChatGPT)."""
    summary = CustomerLocationEnrichmentService(db).enrich(
        customer_ids=body.customer_ids,
        limit=body.limit,
        dry_run=body.dry_run,
        min_confidence=body.min_confidence,
        use_llm=body.use_llm,
    )
    return CustomerLocationEnrichResponse(
        processed=summary.processed,
        updated=summary.updated,
        skipped=summary.skipped,
        not_found=summary.not_found,
        failed=summary.failed,
        results=[CustomerLocationEnrichRow(**row.__dict__) for row in summary.results],
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
