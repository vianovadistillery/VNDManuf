"""Sales reps API router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import SalesRep

router = APIRouter(prefix="/sales-reps", tags=["sales-reps"])


class SalesRepCreate(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class SalesRepUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class SalesRepResponse(BaseModel):
    id: str
    code: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


def _to_response(rep: SalesRep) -> SalesRepResponse:
    return SalesRepResponse(
        id=str(rep.id),
        code=rep.code,
        name=rep.name,
        email=rep.email,
        phone=rep.phone,
        is_active=rep.is_active,
    )


@router.get("/", response_model=List[SalesRepResponse])
async def list_sales_reps(
    skip: int = 0,
    limit: int = 200,
    query: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    stmt = select(SalesRep).where(SalesRep.deleted_at.is_(None))
    if query:
        stmt = stmt.where(SalesRep.code.contains(query) | SalesRep.name.contains(query))
    if is_active is not None:
        stmt = stmt.where(SalesRep.is_active == is_active)
    stmt = stmt.order_by(SalesRep.name).offset(skip).limit(limit)
    reps = db.execute(stmt).scalars().all()
    return [_to_response(r) for r in reps]


@router.get("/{rep_id}", response_model=SalesRepResponse)
async def get_sales_rep(rep_id: str, db: Session = Depends(get_db)):
    rep = db.get(SalesRep, rep_id)
    if not rep or rep.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rep not found"
        )
    return _to_response(rep)


@router.post("/", response_model=SalesRepResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_rep(data: SalesRepCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(SalesRep).where(
            SalesRep.code == data.code, SalesRep.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Sales rep code '{data.code}' already exists",
        )
    rep = SalesRep(
        code=data.code,
        name=data.name,
        email=data.email,
        phone=data.phone,
        is_active=data.is_active,
    )
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return _to_response(rep)


@router.put("/{rep_id}", response_model=SalesRepResponse)
async def update_sales_rep(
    rep_id: str, data: SalesRepUpdate, db: Session = Depends(get_db)
):
    rep = db.get(SalesRep, rep_id)
    if not rep or rep.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rep not found"
        )
    if data.code and data.code != rep.code:
        clash = db.execute(
            select(SalesRep).where(
                SalesRep.code == data.code,
                SalesRep.id != rep_id,
                SalesRep.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if clash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Sales rep code '{data.code}' already exists",
            )
        rep.code = data.code
    if data.name is not None:
        rep.name = data.name
    if data.email is not None:
        rep.email = data.email
    if data.phone is not None:
        rep.phone = data.phone
    if data.is_active is not None:
        rep.is_active = data.is_active
    db.commit()
    db.refresh(rep)
    return _to_response(rep)


@router.delete("/{rep_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_rep(rep_id: str, db: Session = Depends(get_db)):
    from app.services.audit import soft_delete

    rep = db.get(SalesRep, rep_id)
    if not rep or rep.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rep not found"
        )
    soft_delete(db, rep)
    db.commit()
    return None
