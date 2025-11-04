# app/api/suppliers.py
"""Suppliers API router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import Supplier


# DTOs
class SupplierCreate(BaseModel):
    """Create supplier request."""

    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    xero_id: Optional[str] = None
    is_active: bool = True


class SupplierUpdate(BaseModel):
    """Update supplier request."""

    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    xero_id: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseModel):
    """Supplier response."""

    id: str
    code: str
    name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    xero_id: Optional[str]
    is_active: bool
    created_at: str


router = APIRouter(prefix="/suppliers", tags=["suppliers"])


def supplier_to_response(s: Supplier) -> SupplierResponse:
    """Convert Supplier model to response DTO."""
    return SupplierResponse(
        id=str(s.id),
        code=s.code,
        name=s.name,
        contact_person=s.contact_person,
        email=s.email,
        phone=s.phone,
        address=s.address,
        xero_id=s.xero_id,
        is_active=s.is_active,
        created_at=s.created_at.isoformat() if s.created_at else "",
    )


@router.get("/", response_model=List[SupplierResponse])
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    code: Optional[str] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List suppliers with optional filtering."""
    stmt = select(Supplier)

    # Filter by code (UUID search)
    if code:
        stmt = stmt.where(Supplier.id.contains(code))

    # Filter by name
    if name:
        stmt = stmt.where(Supplier.name.contains(name))

    # Filter by active status
    if is_active is not None:
        stmt = stmt.where(Supplier.is_active == is_active)

    stmt = stmt.order_by(Supplier.name).offset(skip).limit(limit)
    suppliers = db.execute(stmt).scalars().all()

    return [supplier_to_response(s) for s in suppliers]


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    """Get supplier by ID."""
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )

    return supplier_to_response(supplier)


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(supplier_data: SupplierCreate, db: Session = Depends(get_db)):
    """Create a new supplier."""
    # Create supplier with auto-generated code
    import uuid

    supplier = Supplier(
        id=str(uuid.uuid4()),
        code=str(uuid.uuid4()),  # Auto-generate UUID code
        name=supplier_data.name,
        contact_person=supplier_data.contact_person,
        email=supplier_data.email,
        phone=supplier_data.phone,
        address=supplier_data.address,
        xero_id=supplier_data.xero_id,
        is_active=supplier_data.is_active,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier_to_response(supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str, supplier_data: SupplierUpdate, db: Session = Depends(get_db)
):
    """Update supplier."""
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )

    # Update fields
    if supplier_data.name is not None:
        supplier.name = supplier_data.name
    if supplier_data.contact_person is not None:
        supplier.contact_person = supplier_data.contact_person
    if supplier_data.email is not None:
        supplier.email = supplier_data.email
    if supplier_data.phone is not None:
        supplier.phone = supplier_data.phone
    if supplier_data.address is not None:
        supplier.address = supplier_data.address
    if supplier_data.xero_id is not None:
        supplier.xero_id = supplier_data.xero_id
    if supplier_data.is_active is not None:
        supplier.is_active = supplier_data.is_active

    db.commit()
    db.refresh(supplier)

    return supplier_to_response(supplier)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: str, db: Session = Depends(get_db)):
    """Soft delete supplier (marks as deleted, does not remove from database)."""
    from app.services.audit import soft_delete

    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )

    soft_delete(db, supplier)
    db.commit()
    return None
