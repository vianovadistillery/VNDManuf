# app/api/work_areas.py
"""Work Areas API router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import WorkArea  # noqa: F401

router = APIRouter(prefix="/work-areas", tags=["work-areas"])


class WorkAreaCreate(BaseModel):
    """Work area creation request."""

    code: str = Field(
        ..., max_length=20, description="Work area code (e.g., 'Still01')"
    )
    name: str = Field(..., max_length=100, description="Work area name")
    description: Optional[str] = None
    is_active: bool = True


class WorkAreaUpdate(BaseModel):
    """Work area update request."""

    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WorkAreaResponse(BaseModel):
    """Work area response."""

    id: str
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


def work_area_to_response(work_area: WorkArea) -> WorkAreaResponse:
    """Convert WorkArea model to response DTO."""
    return WorkAreaResponse(
        id=str(work_area.id),
        code=work_area.code,
        name=work_area.name,
        description=work_area.description,
        is_active=work_area.is_active,
    )


@router.get("/", response_model=List[WorkAreaResponse])
async def list_work_areas(
    skip: int = 0,
    limit: int = 100,
    query: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List work areas with optional filtering."""
    stmt = select(WorkArea).where(WorkArea.deleted_at.is_(None))

    if query:
        stmt = stmt.where(WorkArea.code.contains(query) | WorkArea.name.contains(query))

    if is_active is not None:
        stmt = stmt.where(WorkArea.is_active == is_active)

    stmt = stmt.order_by(WorkArea.code).offset(skip).limit(limit)
    work_areas = db.execute(stmt).scalars().all()

    return [work_area_to_response(wa) for wa in work_areas]


@router.get("/{work_area_id}", response_model=WorkAreaResponse)
async def get_work_area(work_area_id: str, db: Session = Depends(get_db)):
    """Get a work area by ID."""
    work_area = db.get(WorkArea, work_area_id)
    if not work_area or work_area.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work area not found"
        )
    return work_area_to_response(work_area)


@router.post("/", response_model=WorkAreaResponse, status_code=status.HTTP_201_CREATED)
async def create_work_area(
    work_area_data: WorkAreaCreate, db: Session = Depends(get_db)
):
    """Create a new work area."""
    # Check if code already exists (excluding soft-deleted)
    existing = db.execute(
        select(WorkArea).where(
            WorkArea.code == work_area_data.code, WorkArea.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Work area with code '{work_area_data.code}' already exists",
        )

    work_area = WorkArea(
        code=work_area_data.code,
        name=work_area_data.name,
        description=work_area_data.description,
        is_active=work_area_data.is_active,
    )
    db.add(work_area)
    db.commit()
    db.refresh(work_area)
    return work_area_to_response(work_area)


@router.put("/{work_area_id}", response_model=WorkAreaResponse)
async def update_work_area(
    work_area_id: str, work_area_data: WorkAreaUpdate, db: Session = Depends(get_db)
):
    """Update a work area."""
    work_area = db.get(WorkArea, work_area_id)
    if not work_area or work_area.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work area not found"
        )

    # Check if code is being changed and if new code already exists
    if work_area_data.code and work_area_data.code != work_area.code:
        existing = db.execute(
            select(WorkArea).where(
                WorkArea.code == work_area_data.code,
                WorkArea.id != work_area_id,
                WorkArea.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Work area with code '{work_area_data.code}' already exists",
            )

    if work_area_data.code is not None:
        work_area.code = work_area_data.code
    if work_area_data.name is not None:
        work_area.name = work_area_data.name
    if work_area_data.description is not None:
        work_area.description = work_area_data.description
    if work_area_data.is_active is not None:
        work_area.is_active = work_area_data.is_active

    db.commit()
    db.refresh(work_area)
    return work_area_to_response(work_area)


@router.delete("/{work_area_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_area(work_area_id: str, db: Session = Depends(get_db)):
    """Soft delete a work area."""
    from app.services.audit import soft_delete

    work_area = db.get(WorkArea, work_area_id)
    if not work_area or work_area.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work area not found"
        )

    soft_delete(db, work_area)
    db.commit()
    return None
