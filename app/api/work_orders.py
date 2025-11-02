# app/api/work_orders.py
"""Work Orders API router."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.adapters.db import get_db
from app.adapters.db.models import WorkOrder, Batch, Product, Formula

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_work_order(
    product_id: str,
    formula_id: str,
    quantity_kg: Decimal,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Create a new work order.
    
    Work Order is auto-created when creating a batch.
    """
    # Validate product exists
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Validate formula exists
    formula = db.get(Formula, formula_id)
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formula not found"
        )
    
    # Generate work order code (date-based)
    from datetime import datetime
    now = datetime.utcnow()
    wo_code = f"WO{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"
    
    # Check for duplicate code
    existing = db.execute(
        select(WorkOrder).where(WorkOrder.code == wo_code)
    ).scalar_one_or_none()
    
    if existing:
        # Add a counter if duplicate
        counter = 1
        while existing:
            wo_code = f"WO{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}-{counter}"
            existing = db.execute(
                select(WorkOrder).where(WorkOrder.code == wo_code)
            ).scalar_one_or_none()
            counter += 1
    
    # Create work order
    work_order = WorkOrder(
        id=str(uuid4()),
        code=wo_code,
        product_id=product_id,
        formula_id=formula_id,
        quantity_kg=quantity_kg,
        status="DRAFT",
        notes=notes
    )
    
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    
    return {
        "id": work_order.id,
        "code": work_order.code,
        "product_id": work_order.product_id,
        "formula_id": work_order.formula_id,
        "quantity_kg": float(work_order.quantity_kg),
        "status": work_order.status,
        "created_at": work_order.created_at.isoformat() if work_order.created_at else None
    }

