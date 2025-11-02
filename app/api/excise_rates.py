# app/api/excise_rates.py
"""Excise rates API router."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.adapters.db import get_db
from app.adapters.db.models import ExciseRate
from app.api.dto import ErrorResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/excise-rates", tags=["excise-rates"])


class ExciseRateCreate(BaseModel):
    """Excise rate creation request."""
    date_active_from: datetime = Field(..., description="Date from which this rate is active")
    rate_per_l_abv: Decimal = Field(..., gt=0, description="Excise rate in $/L ABV")
    description: Optional[str] = None


class ExciseRateUpdate(BaseModel):
    """Excise rate update request."""
    date_active_from: Optional[datetime] = None
    rate_per_l_abv: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None


class ExciseRateResponse(BaseModel):
    """Excise rate response."""
    id: str
    date_active_from: datetime
    rate_per_l_abv: Decimal
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


def excise_rate_to_response(rate: ExciseRate) -> ExciseRateResponse:
    """Convert ExciseRate model to response DTO."""
    return ExciseRateResponse(
        id=str(rate.id),
        date_active_from=rate.date_active_from,
        rate_per_l_abv=rate.rate_per_l_abv,
        description=rate.description,
        created_at=rate.created_at,
        updated_at=rate.updated_at
    )


@router.get("/", response_model=List[ExciseRateResponse])
async def list_excise_rates(
    skip: int = 0,
    limit: int = 100,
    as_of_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    List excise rates with optional filtering by date.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        as_of_date: Optional date to filter rates active on or before this date
        db: Database session
        
    Returns:
        List of excise rates
    """
    stmt = select(ExciseRate)
    
    if as_of_date:
        stmt = stmt.where(ExciseRate.date_active_from <= as_of_date)
    
    stmt = stmt.order_by(desc(ExciseRate.date_active_from)).offset(skip).limit(limit)
    rates = db.execute(stmt).scalars().all()
    
    return [excise_rate_to_response(r) for r in rates]


@router.get("/current", response_model=ExciseRateResponse)
async def get_current_excise_rate(
    as_of_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get the current excise rate effective on a given date.
    
    Args:
        as_of_date: Date to get rate for (defaults to now)
        db: Database session
        
    Returns:
        Current excise rate
        
    Raises:
        HTTPException: If no rate found
    """
    if as_of_date is None:
        as_of_date = datetime.utcnow()
    
    stmt = (
        select(ExciseRate)
        .where(ExciseRate.date_active_from <= as_of_date)
        .order_by(desc(ExciseRate.date_active_from))
        .limit(1)
    )
    rate = db.execute(stmt).scalar_one_or_none()
    
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No excise rate found for date {as_of_date.isoformat()}"
        )
    
    return excise_rate_to_response(rate)


@router.get("/{rate_id}", response_model=ExciseRateResponse)
async def get_excise_rate(rate_id: str, db: Session = Depends(get_db)):
    """Get excise rate by ID."""
    rate = db.get(ExciseRate, rate_id)
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excise rate not found"
        )
    
    return excise_rate_to_response(rate)


@router.post("/", response_model=ExciseRateResponse, status_code=status.HTTP_201_CREATED)
async def create_excise_rate(
    data: ExciseRateCreate,
    db: Session = Depends(get_db)
):
    """Create a new excise rate."""
    rate = ExciseRate(
        date_active_from=data.date_active_from,
        rate_per_l_abv=data.rate_per_l_abv,
        description=data.description
    )
    
    db.add(rate)
    db.commit()
    db.refresh(rate)
    
    return excise_rate_to_response(rate)


@router.put("/{rate_id}", response_model=ExciseRateResponse)
async def update_excise_rate(
    rate_id: str,
    data: ExciseRateUpdate,
    db: Session = Depends(get_db)
):
    """Update an excise rate."""
    rate = db.get(ExciseRate, rate_id)
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excise rate not found"
        )
    
    if data.date_active_from is not None:
        rate.date_active_from = data.date_active_from
    if data.rate_per_l_abv is not None:
        rate.rate_per_l_abv = data.rate_per_l_abv
    if data.description is not None:
        rate.description = data.description
    
    db.commit()
    db.refresh(rate)
    
    return excise_rate_to_response(rate)


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_excise_rate(
    rate_id: str,
    db: Session = Depends(get_db)
):
    """Delete an excise rate."""
    rate = db.get(ExciseRate, rate_id)
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excise rate not found"
        )
    
    db.delete(rate)
    db.commit()
    
    return None

