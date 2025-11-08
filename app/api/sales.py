"""Sales domain API router with soft delete and archive support."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, validator
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from apps.vndmanuf_sales.models import (
    CustomerSite,
    Pricebook,
    PricebookItem,
    SalesChannel,
    SalesOrder,
    SalesOrderLine,
    SalesOrderSource,
    SalesOrderStatus,
    SalesTag,
)
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
    order_date: datetime
    status: Optional[SalesOrderStatus] = SalesOrderStatus.CONFIRMED
    source: Optional[SalesOrderSource] = SalesOrderSource.MANUAL
    entered_by: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    lines: List[SalesOrderLineInput]


class SalesOrderUpdate(BaseModel):
    channel_id: Optional[str] = None
    customer_site_id: Optional[str] = None
    pricebook_id: Optional[str] = None
    order_ref: Optional[str] = Field(None, max_length=50)
    order_date: Optional[datetime] = None
    status: Optional[SalesOrderStatus] = None
    source: Optional[SalesOrderSource] = None
    entered_by: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    lines: Optional[List[SalesOrderLineInput]] = None


class SalesOrderLineResponse(AuditResponse):
    id: str
    product_id: str
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
    order_date: datetime
    status: str
    source: str
    entered_by: Optional[str]
    notes: Optional[str]
    total_ex_gst: Decimal
    total_inc_gst: Decimal
    lines: List[SalesOrderLineResponse]

    class Config:
        from_attributes = True


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


@router.get("/orders", response_model=List[SalesOrderResponse])
def list_orders(
    customer_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    status_filter: Optional[SalesOrderStatus] = None,
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
    return [_build_order_response(order) for order in orders]


@router.get("/orders/{order_id}", response_model=SalesOrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = _order_query(db, order_id)
    return _build_order_response(order)


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
        order_date=data.order_date,
        status=data.status.value if data.status else SalesOrderStatus.CONFIRMED.value,
        source=data.source.value if data.source else SalesOrderSource.MANUAL.value,
        entered_by=data.entered_by,
        notes=data.notes,
    )
    db.add(order)
    _apply_order_lines(order, data.lines, db)
    db.commit()
    db.refresh(order)
    return _build_order_response(order)


@router.put("/orders/{order_id}", response_model=SalesOrderResponse)
def update_order(order_id: str, data: SalesOrderUpdate, db: Session = Depends(get_db)):
    order = _order_query(db, order_id)
    if data.channel_id is not None:
        order.channel_id = data.channel_id
    if data.customer_site_id is not None:
        order.customer_site_id = data.customer_site_id
    if data.pricebook_id is not None:
        order.pricebook_id = data.pricebook_id
    if data.order_ref is not None:
        order.order_ref = data.order_ref
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
    order = _order_query(db, order_id, include_deleted=True)
    _soft_delete(order)
    db.commit()


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
