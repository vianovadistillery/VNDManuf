# app/api/contacts.py
"""Contacts API router for unified customer/supplier/other management."""

import random
import string
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import Contact


# DTOs
class ContactCreate(BaseModel):
    """Create contact request."""

    code: Optional[str] = None  # Optional - will be auto-generated if not provided
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_customer: bool = False
    is_supplier: bool = False
    is_other: bool = False
    tax_rate: Optional[float] = None
    xero_contact_id: Optional[str] = None
    is_active: bool = True


class ContactUpdate(BaseModel):
    """Update contact request."""

    code: Optional[str] = None  # Can update code if needed
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_customer: Optional[bool] = None
    is_supplier: Optional[bool] = None
    is_other: Optional[bool] = None
    tax_rate: Optional[float] = None
    xero_contact_id: Optional[str] = None
    is_active: Optional[bool] = None


class ContactResponse(BaseModel):
    """Contact response."""

    id: str
    code: str
    name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    is_customer: bool
    is_supplier: bool
    is_other: bool
    tax_rate: Optional[float]
    xero_contact_id: Optional[str]
    is_active: bool
    created_at: str


router = APIRouter(prefix="/contacts", tags=["contacts"])


def generate_contact_code(db: Session, length: int = 5) -> str:
    """Generate a unique 5-character alphanumeric code for contacts."""
    max_attempts = 1000
    for _ in range(max_attempts):
        # Generate code using uppercase letters and digits
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

        # Check if code is already in use
        existing = db.execute(
            select(Contact).where(Contact.code == code)
        ).scalar_one_or_none()
        if not existing:
            return code

    # Fallback if we can't generate a unique code (shouldn't happen)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unable to generate unique contact code",
    )


def contact_to_response(c: Contact) -> ContactResponse:
    """Convert Contact model to response DTO."""
    return ContactResponse(
        id=str(c.id),
        code=c.code,
        name=c.name,
        contact_person=c.contact_person,
        email=c.email,
        phone=c.phone,
        address=c.address,
        is_customer=c.is_customer,
        is_supplier=c.is_supplier,
        is_other=c.is_other,
        tax_rate=float(c.tax_rate) if c.tax_rate else None,
        xero_contact_id=c.xero_contact_id,
        is_active=c.is_active,
        created_at=c.created_at.isoformat() if c.created_at else "",
    )


@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    code: Optional[str] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_customer: Optional[bool] = None,
    is_supplier: Optional[bool] = None,
    is_other: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List contacts with optional filtering by type."""
    stmt = select(Contact)

    # Filter by code (UUID search)
    if code:
        stmt = stmt.where(Contact.id.contains(code))

    # Filter by name
    if name:
        stmt = stmt.where(Contact.name.contains(name))

    # Filter by active status
    if is_active is not None:
        stmt = stmt.where(Contact.is_active == is_active)

    # Filter by contact type
    if is_customer is not None:
        stmt = stmt.where(Contact.is_customer == is_customer)
    if is_supplier is not None:
        stmt = stmt.where(Contact.is_supplier == is_supplier)
    if is_other is not None:
        stmt = stmt.where(Contact.is_other == is_other)

    stmt = stmt.order_by(Contact.name).offset(skip).limit(limit)
    contacts = db.execute(stmt).scalars().all()

    return [contact_to_response(c) for c in contacts]


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: str, db: Session = Depends(get_db)):
    """Get contact by ID."""
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    return contact_to_response(contact)


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact_data: ContactCreate, db: Session = Depends(get_db)):
    """Create a new contact."""
    import uuid

    # Generate code if not provided
    if contact_data.code:
        # Validate provided code is unique
        existing = db.execute(
            select(Contact).where(Contact.code == contact_data.code)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Contact code '{contact_data.code}' already exists",
            )
        code = contact_data.code
    else:
        # Auto-generate 5-character code
        code = generate_contact_code(db)

    contact = Contact(
        id=str(uuid.uuid4()),
        code=code,
        name=contact_data.name,
        contact_person=contact_data.contact_person,
        email=contact_data.email,
        phone=contact_data.phone,
        address=contact_data.address,
        is_customer=contact_data.is_customer,
        is_supplier=contact_data.is_supplier,
        is_other=contact_data.is_other,
        tax_rate=contact_data.tax_rate,
        xero_contact_id=contact_data.xero_contact_id,
        is_active=contact_data.is_active,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact_to_response(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str, contact_data: ContactUpdate, db: Session = Depends(get_db)
):
    """Update contact."""
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    # Update fields
    if contact_data.code is not None:
        # Validate new code is unique (if changed)
        if contact_data.code != contact.code:
            existing = db.execute(
                select(Contact).where(Contact.code == contact_data.code)
            ).scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Contact code '{contact_data.code}' already exists",
                )
            contact.code = contact_data.code
    if contact_data.name is not None:
        contact.name = contact_data.name
    if contact_data.contact_person is not None:
        contact.contact_person = contact_data.contact_person
    if contact_data.email is not None:
        contact.email = contact_data.email
    if contact_data.phone is not None:
        contact.phone = contact_data.phone
    if contact_data.address is not None:
        contact.address = contact_data.address
    if contact_data.is_customer is not None:
        contact.is_customer = contact_data.is_customer
    if contact_data.is_supplier is not None:
        contact.is_supplier = contact_data.is_supplier
    if contact_data.is_other is not None:
        contact.is_other = contact_data.is_other
    if contact_data.tax_rate is not None:
        contact.tax_rate = contact_data.tax_rate
    if contact_data.xero_contact_id is not None:
        contact.xero_contact_id = contact_data.xero_contact_id
    if contact_data.is_active is not None:
        contact.is_active = contact_data.is_active

    db.commit()
    db.refresh(contact)

    return contact_to_response(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: str, db: Session = Depends(get_db)):
    """Delete contact."""
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    db.delete(contact)
    db.commit()
