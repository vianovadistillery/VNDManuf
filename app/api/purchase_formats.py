# app/api/purchase_formats.py
"""Purchase formats API router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import PurchaseFormat

router = APIRouter(prefix="/purchase-formats", tags=["purchase-formats"])


class PurchaseFormatCreate(BaseModel):
    """Purchase format creation request."""

    code: str = Field(
        ..., max_length=20, description="Format code (e.g., 'IBC', 'BAG')"
    )
    name: str = Field(..., max_length=100, description="Format name")
    description: Optional[str] = None
    is_active: bool = True


class PurchaseFormatUpdate(BaseModel):
    """Purchase format update request."""

    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PurchaseFormatResponse(BaseModel):
    """Purchase format response."""

    id: str
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


def purchase_format_to_response(format: PurchaseFormat) -> PurchaseFormatResponse:
    """Convert PurchaseFormat model to response DTO."""
    return PurchaseFormatResponse(
        id=str(format.id),
        code=format.code,
        name=format.name,
        description=format.description,
        is_active=format.is_active,
    )


@router.get("/", response_model=List[PurchaseFormatResponse])
async def list_purchase_formats(
    skip: int = 0,
    limit: int = 100,
    query: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List purchase formats with optional filtering."""
    stmt = select(PurchaseFormat)

    if query:
        stmt = stmt.where(
            PurchaseFormat.code.contains(query) | PurchaseFormat.name.contains(query)
        )

    if is_active is not None:
        stmt = stmt.where(PurchaseFormat.is_active == is_active)

    stmt = stmt.order_by(PurchaseFormat.code).offset(skip).limit(limit)
    formats = db.execute(stmt).scalars().all()

    return [purchase_format_to_response(f) for f in formats]


@router.get("/{format_id}", response_model=PurchaseFormatResponse)
async def get_purchase_format(format_id: str, db: Session = Depends(get_db)):
    """Get a purchase format by ID."""
    format = db.get(PurchaseFormat, format_id)
    if not format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Purchase format not found"
        )
    return purchase_format_to_response(format)


@router.post(
    "/",
    response_model=PurchaseFormatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_purchase_format(
    format_data: PurchaseFormatCreate, db: Session = Depends(get_db)
):
    """Create a new purchase format."""
    # Check if code already exists
    existing = db.execute(
        select(PurchaseFormat).where(PurchaseFormat.code == format_data.code)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Purchase format with code '{format_data.code}' already exists",
        )

    purchase_format = PurchaseFormat(
        code=format_data.code,
        name=format_data.name,
        description=format_data.description,
        is_active=format_data.is_active,
    )
    db.add(purchase_format)
    db.commit()
    db.refresh(purchase_format)
    return purchase_format_to_response(purchase_format)


@router.put("/{format_id}", response_model=PurchaseFormatResponse)
async def update_purchase_format(
    format_id: str, format_data: PurchaseFormatUpdate, db: Session = Depends(get_db)
):
    """Update a purchase format."""
    purchase_format = db.get(PurchaseFormat, format_id)
    if not purchase_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Purchase format not found"
        )

    # Check if new code conflicts with existing format
    if format_data.code and format_data.code != purchase_format.code:
        existing = db.execute(
            select(PurchaseFormat).where(PurchaseFormat.code == format_data.code)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Purchase format with code '{format_data.code}' already exists",
            )

    # Update fields
    if format_data.code is not None:
        purchase_format.code = format_data.code
    if format_data.name is not None:
        purchase_format.name = format_data.name
    if format_data.description is not None:
        purchase_format.description = format_data.description
    if format_data.is_active is not None:
        purchase_format.is_active = format_data.is_active

    db.commit()
    db.refresh(purchase_format)
    return purchase_format_to_response(purchase_format)


@router.delete("/{format_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_format(format_id: str, db: Session = Depends(get_db)):
    """Delete a purchase format."""
    purchase_format = db.get(PurchaseFormat, format_id)
    if not purchase_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Purchase format not found"
        )

    db.delete(purchase_format)
    db.commit()
    return None
