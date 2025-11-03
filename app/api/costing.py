# app/api/costing.py
"""Costing API router for COGS inspection and revaluation."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import Product
from app.services.costing import CostingService

router = APIRouter(prefix="/costing", tags=["costing"])


# Request/Response Models
class RevaluationRequest(BaseModel):
    """Request to revalue a lot."""

    lot_id: str = Field(..., description="Lot ID to revalue")
    new_unit_cost: Decimal = Field(..., description="New unit cost")
    reason: str = Field(..., description="Reason for revaluation")
    revalued_by: str = Field(..., description="User performing revaluation")
    propagate: bool = Field(
        True, description="Whether to propagate to downstream assemblies"
    )


class RevaluationResponse(BaseModel):
    """Response from revaluation."""

    id: str
    item_id: str
    lot_id: Optional[str]
    old_unit_cost: Decimal
    new_unit_cost: Decimal
    delta_extended_cost: Decimal
    reason: str
    revalued_by: str
    revalued_at: datetime
    propagated_to_assemblies: bool


class COGSBreakdownItem(BaseModel):
    """Single item in COGS breakdown tree."""

    level: int
    sku: str
    name: str
    product_type: str  # Derived from capabilities (RAW/WIP/FINISHED) for compatibility
    qty_per_parent: Decimal
    unit_cost: Decimal
    extended_cost: Decimal
    cost_source: str
    has_estimate: bool
    estimate_reason: Optional[str] = None
    children: List["COGSBreakdownItem"] = []


class COGSInspectionResponse(BaseModel):
    """Response from COGS inspection."""

    item_id: str
    sku: str
    name: str
    product_type: str  # Derived from capabilities (RAW/WIP/FINISHED) for compatibility
    unit_cost: Decimal
    cost_source: str
    has_estimate: bool
    estimate_reason: Optional[str] = None
    breakdown: COGSBreakdownItem


# Allow forward references
COGSBreakdownItem.model_rebuild()


@router.get("/inspect/{item_id}", response_model=COGSInspectionResponse)
async def inspect_cogs(
    item_id: str,
    as_of_date: Optional[datetime] = Query(
        None, description="Point-in-time date for historical costing"
    ),
    include_estimates: bool = Query(
        True, description="Whether to include items with estimated costs"
    ),
    db: Session = Depends(get_db),
):
    """
    Inspect cost of goods (COGS) for a product with multi-level breakdown.

    Returns:
        COGS inspection with breakdown tree showing cost contributions and estimate flags
    """
    # Validate product exists
    product = db.get(Product, item_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item_id} not found"
        )

    try:
        service = CostingService(db)
        cogs_data = service.inspect_cogs(
            item_id=item_id, as_of_date=as_of_date, include_estimates=include_estimates
        )

        return COGSInspectionResponse(**cogs_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to inspect COGS: {str(e)}",
        )


@router.get("/breakdown/{item_id}", response_model=COGSBreakdownItem)
async def get_cogs_breakdown(
    item_id: str,
    as_of_date: Optional[datetime] = Query(
        None, description="Point-in-time date for historical costing"
    ),
    include_estimates: bool = Query(
        True, description="Whether to include items with estimated costs"
    ),
    db: Session = Depends(get_db),
):
    """
    Get COGS breakdown tree for a product.

    Returns:
        Breakdown tree showing cost contributions at each level
    """
    # Validate product exists
    product = db.get(Product, item_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item_id} not found"
        )

    try:
        service = CostingService(db)
        cogs_data = service.inspect_cogs(
            item_id=item_id, as_of_date=as_of_date, include_estimates=include_estimates
        )

        return COGSBreakdownItem(**cogs_data["breakdown"])

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get COGS breakdown: {str(e)}",
        )


@router.post(
    "/revalue", response_model=RevaluationResponse, status_code=status.HTTP_201_CREATED
)
async def revalue_lot(request: RevaluationRequest, db: Session = Depends(get_db)):
    """
    Revalue a lot and optionally propagate to downstream assemblies.

    Returns:
        Revaluation record with propagation status
    """
    try:
        service = CostingService(db)
        reval = service.revalue_lot(
            lot_id=request.lot_id,
            new_unit_cost=request.new_unit_cost,
            reason=request.reason,
            revalued_by=request.revalued_by,
            propagate=request.propagate,
        )

        db.commit()
        db.refresh(reval)

        return RevaluationResponse(
            id=reval.id,
            item_id=reval.item_id,
            lot_id=reval.lot_id,
            old_unit_cost=reval.old_unit_cost,
            new_unit_cost=reval.new_unit_cost,
            delta_extended_cost=reval.delta_extended_cost,
            reason=reval.reason,
            revalued_by=reval.revalued_by,
            revalued_at=reval.revalued_at,
            propagated_to_assemblies=reval.propagated_to_assemblies,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revalue lot: {str(e)}",
        )


@router.get("/current/{item_id}")
async def get_current_cost(item_id: str, db: Session = Depends(get_db)):
    """
    Get current cost for a product.

    Returns:
        Dictionary with unit_cost, cost_source, has_estimate, estimate_reason
    """
    # Validate product exists
    product = db.get(Product, item_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item_id} not found"
        )

    try:
        service = CostingService(db)
        cost_data = service.get_current_cost(item_id)
        return cost_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current cost: {str(e)}",
        )


@router.get("/historical/{item_id}")
async def get_historical_cost(
    item_id: str,
    as_of_date: datetime = Query(
        ..., description="Point-in-time date for historical costing"
    ),
    db: Session = Depends(get_db),
):
    """
    Get historical cost for a product as of a specific date.

    Returns:
        Dictionary with unit_cost, cost_source, has_estimate, estimate_reason
    """
    # Validate product exists
    product = db.get(Product, item_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item_id} not found"
        )

    try:
        service = CostingService(db)
        cost_data = service.get_historical_cost(item_id, as_of_date)
        return cost_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get historical cost: {str(e)}",
        )


@router.get("/tree/{item_id}")
async def print_cogs_tree(
    item_id: str,
    as_of_date: Optional[datetime] = Query(
        None, description="Point-in-time date for historical costing"
    ),
    include_estimates: bool = Query(
        True, description="Whether to include items with estimated costs"
    ),
    db: Session = Depends(get_db),
):
    """
    Get formatted COGS tree as text.

    Returns:
        Plain text formatted COGS breakdown tree
    """
    # Validate product exists
    product = db.get(Product, item_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item_id} not found"
        )

    try:
        service = CostingService(db)
        cogs_data = service.inspect_cogs(
            item_id=item_id, as_of_date=as_of_date, include_estimates=include_estimates
        )

        tree_text = service.print_cogs_tree(cogs_data)

        return {"tree": tree_text}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to print COGS tree: {str(e)}",
        )
