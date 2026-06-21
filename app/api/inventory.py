# app/api/inventory.py
"""Inventory API router for stock on hand queries and adjustments."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import InventoryLot, Product
from app.api.dto import (
    InventoryAdjustmentRequest,
    InventoryAdjustmentResponse,
    InventoryLotResponse,
    InventorySummaryResponse,
    StocktakeRequest,
    StocktakeResponse,
    StocktakeVarianceLine,
    WriteOffRequest,
    WriteOffResponse,
)
from app.domain.inventory_uom import inventory_uom_for_product
from app.services.inventory import WRITE_OFF_REASONS, InventoryService
from app.services.stock_management import perform_stocktake

router = APIRouter(prefix="/inventory", tags=["inventory"])


def _lot_to_response(
    lot: InventoryLot, product: Optional[Product] = None
) -> InventoryLotResponse:
    product = product or lot.product
    inv_unit = inventory_uom_for_product(product) if product else None
    return InventoryLotResponse(
        id=lot.id,
        product_id=lot.product_id,
        product_sku=product.sku if product else None,
        product_name=product.name if product else None,
        lot_code=lot.lot_code,
        quantity_kg=lot.quantity_kg,
        inventory_unit=inv_unit,
        unit_cost=lot.unit_cost,
        received_at=lot.received_at,
        expires_at=lot.expires_at,
        is_active=bool(lot.is_active),
    )


def _adjustment_response(
    result: dict, adjustment_type: str, created_at: Optional[datetime] = None
) -> InventoryAdjustmentResponse:
    return InventoryAdjustmentResponse(
        transaction_id=result.get("transaction_id"),
        product_id=result["product_id"],
        lot_id=result.get("lot_id"),
        adjustment_type=adjustment_type,
        quantity_delta_kg=result["quantity_delta_kg"],
        new_quantity_kg=result["new_quantity_kg"],
        inventory_unit=result.get("inventory_unit"),
        unit_cost=result.get("unit_cost"),
        notes=result.get("notes"),
        reference_type=result.get("reference_type"),
        reference_id=result.get("reference_id"),
        created_at=created_at or datetime.utcnow(),
    )


@router.get("/lots", response_model=List[InventoryLotResponse])
async def list_inventory_lots(
    product_id: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """List inventory lots, optionally filtered by product."""
    stmt = select(InventoryLot).order_by(InventoryLot.received_at.desc())
    if product_id:
        stmt = stmt.where(InventoryLot.product_id == product_id)
    if active_only:
        stmt = stmt.where(InventoryLot.is_active.is_(True))

    lots = db.execute(stmt).scalars().all()
    responses = []
    for lot in lots:
        product = db.get(Product, lot.product_id)
        responses.append(_lot_to_response(lot, product))
    return responses


@router.get("/product/{product_id}/lots", response_model=List[InventoryLotResponse])
async def get_product_lots(product_id: str, db: Session = Depends(get_db)):
    """List active lots for a single product (FIFO order)."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    inventory_service = InventoryService(db)
    lots = inventory_service.get_lots_fifo(product_id)
    return [_lot_to_response(lot, product) for lot in lots]


@router.get("/product/{product_id}/soh")
async def get_product_soh(product_id: str, db: Session = Depends(get_db)):
    """Get stock on hand in the product's inventory unit."""
    inventory_service = InventoryService(db)
    try:
        return inventory_service.stock_on_hand_payload(product_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/products/soh")
async def get_products_soh(
    product_ids: str = Query(..., description="Comma-separated product IDs"),
    db: Session = Depends(get_db),
):
    """Get stock on hand for multiple products."""
    product_id_list = [pid.strip() for pid in product_ids.split(",") if pid.strip()]

    if not product_id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No product IDs provided"
        )

    inventory_service = InventoryService(db)
    soh_results = []
    for product_id in product_id_list:
        product = db.get(Product, product_id)
        if not product:
            soh_results.append(
                {
                    "product_id": product_id,
                    "product_sku": None,
                    "product_name": None,
                    "stock_on_hand_kg": 0.0,
                    "error": "Product not found",
                }
            )
            continue

        soh = inventory_service.get_stock_on_hand(product_id)
        inv_unit = inventory_uom_for_product(product)
        soh_results.append(
            {
                "product_id": product_id,
                "product_sku": product.sku,
                "product_name": product.name,
                "stock_on_hand": float(soh),
                "inventory_unit": inv_unit,
                "stock_on_hand_kg": float(soh),
            }
        )

    return {"results": soh_results}


@router.get("/stocktake/sheet")
async def get_stocktake_sheet(
    is_purchase: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Return products with current system SOH for stocktake entry."""
    stmt = (
        select(Product)
        .where(Product.deleted_at.is_(None))
        .order_by(Product.sku.asc(), Product.name.asc())
    )
    products = db.execute(stmt).scalars().all()
    if is_purchase:
        products = [p for p in products if getattr(p, "is_purchase", False)]

    inventory_service = InventoryService(db)
    rows = []
    for product in products:
        soh = inventory_service.get_stock_on_hand(product.id)
        inv_unit = inventory_uom_for_product(product)
        rows.append(
            {
                "product_id": product.id,
                "code": product.raw_material_code or product.sku,
                "desc1": product.name,
                "inventory_unit": inv_unit,
                "system_soh": float(soh),
                "physical_count": float(soh),
                "variance": 0.0,
                "variance_pct": 0.0,
            }
        )
    return {"items": rows, "count": len(rows)}


@router.get("/product/{product_id}/summary", response_model=InventorySummaryResponse)
async def get_product_inventory_summary(product_id: str, db: Session = Depends(get_db)):
    """Get comprehensive inventory summary for a product."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    inventory_service = InventoryService(db)
    try:
        summary = inventory_service.get_inventory_summary(product_id)
        return InventorySummaryResponse(**summary)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get inventory summary: {str(e)}",
        )


@router.post(
    "/adjust",
    response_model=InventoryAdjustmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def adjust_inventory(
    adjustment: InventoryAdjustmentRequest, db: Session = Depends(get_db)
):
    """
    Adjust inventory for a product.

    - INCREASE: add stock (new lot if lot_id omitted)
    - DECREASE: remove stock (FIFO if lot_id omitted)
    - SET_COUNT: set total SOH (product-level if lot_id omitted)
    """
    product = db.get(Product, adjustment.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if adjustment.adjustment_type not in {"SET_COUNT", "INCREASE", "DECREASE"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid adjustment type: {adjustment.adjustment_type}",
        )

    inventory_service = InventoryService(db)

    try:
        result = inventory_service.adjust_inventory(
            product_id=adjustment.product_id,
            adjustment_type=adjustment.adjustment_type,
            quantity_kg=adjustment.quantity_kg,
            lot_id=adjustment.lot_id,
            lot_code=adjustment.lot_code,
            unit_cost=adjustment.unit_cost,
            reference_type=adjustment.reference_type,
            reference_id=adjustment.reference_id,
            notes=adjustment.notes,
            allow_negative=adjustment.allow_negative,
        )
        db.commit()
        return _adjustment_response(result, adjustment.adjustment_type)
    except HTTPException:
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to adjust inventory: {str(e)}",
        )


@router.post(
    "/write-off",
    response_model=WriteOffResponse,
    status_code=status.HTTP_201_CREATED,
)
async def write_off_inventory(payload: WriteOffRequest, db: Session = Depends(get_db)):
    """Write off damaged, lost, or shrinkage stock."""
    if payload.reason.upper() not in WRITE_OFF_REASONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"reason must be one of: {', '.join(sorted(WRITE_OFF_REASONS))}",
        )

    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    inventory_service = InventoryService(db)
    try:
        result = inventory_service.write_off(
            product_id=payload.product_id,
            quantity_kg=payload.quantity_kg,
            reason=payload.reason,
            lot_id=payload.lot_id,
            notes=payload.notes,
            reference_id=payload.reference_id,
            allow_negative=payload.allow_negative,
        )
        db.commit()
        return WriteOffResponse(
            transaction_id=result.get("transaction_id"),
            product_id=result["product_id"],
            lot_id=result.get("lot_id"),
            write_off_reason=result["write_off_reason"],
            quantity_delta_kg=result["quantity_delta_kg"],
            new_quantity_kg=result["new_quantity_kg"],
            notes=result.get("notes"),
            reference_type=result.get("reference_type"),
            reference_id=result.get("reference_id"),
            created_at=datetime.utcnow(),
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write off inventory: {str(e)}",
        )


@router.post(
    "/stocktake",
    response_model=StocktakeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def run_stocktake(payload: StocktakeRequest, db: Session = Depends(get_db)):
    """Calculate stocktake variances and optionally apply SOH updates."""
    if not payload.counts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No stocktake lines provided",
        )

    counts = []
    for line in payload.counts:
        counts.append(
            {
                "product_id": line.product_id,
                "physical_count": line.physical_count,
                "update_soh": payload.apply_adjustments and line.update_soh,
                "notes": line.notes,
            }
        )

    try:
        result = perform_stocktake(
            counts=counts,
            db=db,
            reference=payload.reference,
            counter=payload.counter,
            stocktake_date=payload.stocktake_date,
        )
        return StocktakeResponse(
            variances=[StocktakeVarianceLine(**v) for v in result["variances"]],
            total_system_value=result["total_system_value"],
            total_physical_value=result["total_physical_value"],
            total_variance_value=result["total_variance_value"],
            item_count=result["item_count"],
            items_adjusted=result["items_adjusted"],
            reference=result.get("reference"),
            counter=result.get("counter"),
            stocktake_date=result.get("stocktake_date"),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stocktake failed: {str(e)}",
        )
