"""Buying groups API router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import BuyingGroup

router = APIRouter(prefix="/buying-groups", tags=["buying-groups"])


class BuyingGroupCreate(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    map_color: Optional[str] = Field(None, max_length=7)
    is_active: bool = True


class BuyingGroupUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    map_color: Optional[str] = Field(None, max_length=7)
    is_active: Optional[bool] = None


class BuyingGroupResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str] = None
    map_color: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


def _to_response(group: BuyingGroup) -> BuyingGroupResponse:
    return BuyingGroupResponse(
        id=str(group.id),
        code=group.code,
        name=group.name,
        description=group.description,
        map_color=group.map_color,
        is_active=group.is_active,
    )


@router.get("/", response_model=List[BuyingGroupResponse])
async def list_buying_groups(
    skip: int = 0,
    limit: int = 200,
    query: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    stmt = select(BuyingGroup).where(BuyingGroup.deleted_at.is_(None))
    if query:
        stmt = stmt.where(
            BuyingGroup.code.contains(query) | BuyingGroup.name.contains(query)
        )
    if is_active is not None:
        stmt = stmt.where(BuyingGroup.is_active == is_active)
    stmt = stmt.order_by(BuyingGroup.name).offset(skip).limit(limit)
    groups = db.execute(stmt).scalars().all()
    return [_to_response(g) for g in groups]


@router.get("/{group_id}", response_model=BuyingGroupResponse)
async def get_buying_group(group_id: str, db: Session = Depends(get_db)):
    group = db.get(BuyingGroup, group_id)
    if not group or group.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Buying group not found"
        )
    return _to_response(group)


@router.post(
    "/", response_model=BuyingGroupResponse, status_code=status.HTTP_201_CREATED
)
async def create_buying_group(data: BuyingGroupCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(BuyingGroup).where(
            BuyingGroup.code == data.code, BuyingGroup.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Buying group code '{data.code}' already exists",
        )
    group = BuyingGroup(
        code=data.code,
        name=data.name,
        description=data.description,
        map_color=data.map_color,
        is_active=data.is_active,
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return _to_response(group)


@router.put("/{group_id}", response_model=BuyingGroupResponse)
async def update_buying_group(
    group_id: str, data: BuyingGroupUpdate, db: Session = Depends(get_db)
):
    group = db.get(BuyingGroup, group_id)
    if not group or group.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Buying group not found"
        )
    if data.code and data.code != group.code:
        clash = db.execute(
            select(BuyingGroup).where(
                BuyingGroup.code == data.code,
                BuyingGroup.id != group_id,
                BuyingGroup.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if clash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Buying group code '{data.code}' already exists",
            )
        group.code = data.code
    if data.name is not None:
        group.name = data.name
    if data.description is not None:
        group.description = data.description
    if data.map_color is not None:
        group.map_color = data.map_color or None
    if data.is_active is not None:
        group.is_active = data.is_active
    db.commit()
    db.refresh(group)
    return _to_response(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_buying_group(group_id: str, db: Session = Depends(get_db)):
    from app.services.audit import soft_delete

    group = db.get(BuyingGroup, group_id)
    if not group or group.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Buying group not found"
        )
    soft_delete(db, group)
    db.commit()
    return None
