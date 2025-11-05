# app/api/batches.py
"""Batches API router."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import (
    Batch,
    BatchComponent,
    InventoryLot,
    Product,
    WorkOrder,
)
from app.api.dto import (
    BatchComponentCreate,
    BatchComponentResponse,
    BatchCreate,
    BatchFinishRequest,
    BatchResponse,
    PrintResponse,
)
from app.reports.batch_ticket import generate_batch_ticket_text
from app.services.batch_codes import BatchCodeGenerator
from app.services.batching import BatchingService

router = APIRouter(prefix="/batches", tags=["batches"])


def batch_to_response(batch: Batch) -> BatchResponse:
    """Convert Batch model to response DTO."""
    return BatchResponse(
        id=batch.id,
        work_order_id=batch.work_order_id,
        batch_code=batch.batch_code,
        quantity_kg=batch.quantity_kg,
        status=batch.status,
        started_at=batch.started_at,
        completed_at=batch.completed_at,
        notes=batch.notes,
        components=[
            BatchComponentResponse(
                id=c.id,
                ingredient_product_id=c.ingredient_product_id,
                lot_id=c.lot_id,
                quantity_kg=c.quantity_kg,
                unit_cost=c.unit_cost,
            )
            for c in batch.components
        ],
    )


@router.post("/", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(batch_data: BatchCreate, db: Session = Depends(get_db)):
    """Create a new batch."""
    # Validate work order exists
    work_order = db.get(WorkOrder, batch_data.work_order_id)
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found"
        )

    # Auto-generate batch code if not provided
    batch_code = batch_data.batch_code
    if not batch_code:
        batch_code_gen = BatchCodeGenerator(db)
        batch_code = batch_code_gen.generate_batch_code()

    # Check if batch code already exists (globally unique)
    existing_stmt = select(Batch).where(Batch.batch_code == batch_code)
    existing = db.execute(existing_stmt).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch with code '{batch_code}' already exists",
        )

    # Create batch
    batch = Batch(
        id=str(uuid4()),
        work_order_id=batch_data.work_order_id,
        batch_code=batch_code,
        quantity_kg=batch_data.quantity_kg,
        status="DRAFT",
        notes=batch_data.notes,
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return batch_to_response(batch)


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(batch_id: str, db: Session = Depends(get_db)):
    """Get batch by ID."""
    batch = db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
        )

    return batch_to_response(batch)


@router.post(
    "/{batch_id}/components",
    response_model=BatchComponentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_batch_component(
    batch_id: str, component_data: BatchComponentCreate, db: Session = Depends(get_db)
):
    """Add a component to a batch."""
    # Validate batch exists
    batch = db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
        )

    if batch.status not in ["DRAFT", "IN_PROGRESS"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot add components to batch with status '{batch.status}'",
        )

    # Validate ingredient product exists
    ingredient_product = db.get(Product, component_data.ingredient_product_id)
    if not ingredient_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient product not found"
        )

    # Validate lot exists and has sufficient quantity
    lot = db.get(InventoryLot, component_data.lot_id)
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Inventory lot not found"
        )

    if lot.product_id != component_data.ingredient_product_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Lot does not belong to the specified ingredient product",
        )

    # Check if lot has sufficient quantity
    if lot.quantity_kg < component_data.quantity_kg:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient stock: lot {lot.lot_code} has {lot.quantity_kg} kg, requested {component_data.quantity_kg} kg",
        )

    # Create batch component
    component = BatchComponent(
        id=str(uuid4()),
        batch_id=batch_id,
        ingredient_product_id=component_data.ingredient_product_id,
        lot_id=component_data.lot_id,
        quantity_kg=component_data.quantity_kg,
        unit_cost=lot.unit_cost,
    )

    db.add(component)

    # Update batch status to IN_PROGRESS if it was DRAFT
    if batch.status == "DRAFT":
        batch.status = "IN_PROGRESS"
        batch.started_at = datetime.utcnow()

    db.commit()
    db.refresh(component)

    return BatchComponentResponse(
        id=component.id,
        ingredient_product_id=component.ingredient_product_id,
        lot_id=component.lot_id,
        quantity_kg=component.quantity_kg,
        unit_cost=component.unit_cost,
    )


@router.post("/{batch_id}/finish", response_model=BatchResponse)
async def finish_batch(
    batch_id: str, finish_data: BatchFinishRequest, db: Session = Depends(get_db)
):
    """Finish a batch (create FG or WIP lot and mark as COMPLETED)."""
    # Validate batch exists
    batch = db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
        )

    # Use BatchingService to finish the batch
    try:
        service = BatchingService(db)
        finished_batch = service.finish_batch(
            batch_id=batch_id,
            qty_fg_kg=finish_data.qty_fg_kg,
            notes=finish_data.notes,
            create_wip=finish_data.create_wip,
            wip_product_id=finish_data.wip_product_id,
        )
        db.commit()
        db.refresh(finished_batch)
        return batch_to_response(finished_batch)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to finish batch: {str(e)}",
        )


@router.get("/{batch_id}/print", response_model=PrintResponse)
async def print_batch(
    batch_id: str,
    format: str = Query("text", regex="^(text|pdf)$"),
    db: Session = Depends(get_db),
):
    """Print batch ticket in specified format."""
    batch = db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
        )

    if format == "text":
        content = generate_batch_ticket_text(batch.batch_code)
    else:
        # PDF not implemented yet
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF format not implemented yet",
        )

    return PrintResponse(content=content, format=format, generated_at=datetime.utcnow())


# Additional batch workflow endpoints per tpmanu.plan.md


@router.put("/{batch_id}/record-actual", response_model=BatchResponse)
async def record_actual_batch(
    batch_id: str, actual_data: dict, db: Session = Depends(get_db)
):
    """
    Record actual production data for a batch.
    Fields: yield_kg, yield_litres, variance, notes
    """
    batch = db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
        )

    # Update actual quantities
    if "yield_kg" in actual_data:
        batch.yield_actual = Decimal(str(actual_data["yield_kg"]))
    if "yield_litres" in actual_data:
        batch.yield_litres = Decimal(str(actual_data["yield_litres"]))
    if "variance" in actual_data:
        batch.variance_percent = Decimal(str(actual_data["variance"]))
    if "notes" in actual_data:
        batch.notes = (batch.notes or "") + f"\nActual: {actual_data['notes']}"

    batch.status = "EXECUTED"

    db.commit()
    db.refresh(batch)

    return batch_to_response(batch)


@router.put("/{batch_id}/qc-results", response_model=BatchResponse)
async def record_qc_results(
    batch_id: str, qc_data: dict, db: Session = Depends(get_db)
):
    """
    Record QC test results for a batch.
    Fields: sg, viscosity, ph, filter_flag, grind, vsol, wsol, gln, flow, etc.
    """
    batch = db.get(Batch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
        )

    # Record QC parameters from qc_data dict
    # These would be stored in batch.qc_results or separate QC table
    # For now, store as JSON in notes

    qc_notes = "\nQC Results:\n"
    for key, value in qc_data.items():
        if value is not None:
            qc_notes += f"{key}: {value}\n"

    batch.notes = (batch.notes or "") + qc_notes
    batch.status = "QC_COMPLETE"

    db.commit()
    db.refresh(batch)

    return batch_to_response(batch)


@router.get("/history/", response_model=List[BatchResponse])
async def get_batch_history(
    year: Optional[str] = None,
    formula_code: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get batch history with filters."""
    stmt = select(Batch)

    # Filter by year (batch_code format: YYNNNN)
    if year:
        stmt = stmt.where(Batch.batch_code.like(f"{year}%"))

    # Filter by status
    if status:
        stmt = stmt.where(Batch.status == status.upper())

    # Filter by formula (via work order)
    if formula_code:
        # Join with work_orders to filter by formula
        from app.adapters.db.models import WorkOrder

        stmt = stmt.join(WorkOrder).filter(
            # This would need to be extended based on actual schema
            # WorkOrder has product_id, which links to formulas
        )

    stmt = stmt.order_by(Batch.created_at.desc()).offset(skip).limit(limit)
    batches = db.execute(stmt).scalars().all()

    return [batch_to_response(b) for b in batches]
