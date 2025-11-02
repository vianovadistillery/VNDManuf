# app/api/inventory.py
"""Inventory API router for stock on hand queries and adjustments."""

from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.adapters.db import get_db
from app.adapters.db.models import InventoryLot, Product, InventoryTxn
from app.api.dto import (
    InventorySummaryResponse,
    InventoryAdjustmentRequest,
    InventoryAdjustmentResponse
)
from app.services.inventory import InventoryService
from app.domain.rules import round_quantity, round_money

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/product/{product_id}/soh")
async def get_product_soh(product_id: str, db: Session = Depends(get_db)):
    """
    Get stock on hand for a product in kg.
    
    Returns the sum of all active inventory lots for the product.
    """
    # Validate product exists
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Calculate SOH from active lots
    soh_stmt = (
        select(func.sum(InventoryLot.quantity_kg))
        .where(InventoryLot.product_id == product_id)
        .where(InventoryLot.is_active == True)
    )
    result = db.execute(soh_stmt).scalar()
    soh = result if result is not None else Decimal("0")
    
    return {
        "product_id": product_id,
        "product_sku": product.sku,
        "product_name": product.name,
        "stock_on_hand_kg": float(soh)
    }


@router.get("/products/soh")
async def get_products_soh(
    product_ids: str = Query(..., description="Comma-separated product IDs"),
    db: Session = Depends(get_db)
):
    """
    Get stock on hand for multiple products.
    
    Returns SOH for each product in kg.
    """
    # Parse product IDs
    product_id_list = [pid.strip() for pid in product_ids.split(",")]
    
    if not product_id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No product IDs provided"
        )
    
    # Calculate SOH for each product
    soh_results = []
    for product_id in product_id_list:
        # Validate product exists
        product = db.get(Product, product_id)
        if not product:
            soh_results.append({
                "product_id": product_id,
                "product_sku": None,
                "product_name": None,
                "stock_on_hand_kg": 0.0,
                "error": "Product not found"
            })
            continue
        
        # Calculate SOH
        soh_stmt = (
            select(func.sum(InventoryLot.quantity_kg))
            .where(InventoryLot.product_id == product_id)
            .where(InventoryLot.is_active == True)
        )
        result = db.execute(soh_stmt).scalar()
        soh = result if result is not None else Decimal("0")
        
        soh_results.append({
            "product_id": product_id,
            "product_sku": product.sku,
            "product_name": product.name,
            "stock_on_hand_kg": float(soh)
        })
    
    return {"results": soh_results}


@router.get("/product/{product_id}/summary", response_model=InventorySummaryResponse)
async def get_product_inventory_summary(
    product_id: str,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive inventory summary for a product including FIFO and average costs.
    
    Returns:
    - Stock on hand (kg)
    - FIFO cost per kg and total value
    - Average cost per kg and total value
    - Cost source and estimate flags
    - Number of active lots
    """
    # Validate product exists
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get inventory summary using service
    inventory_service = InventoryService(db)
    try:
        summary = inventory_service.get_inventory_summary(product_id)
        return InventorySummaryResponse(**summary)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get inventory summary: {str(e)}"
        )


@router.post("/adjust", response_model=InventoryAdjustmentResponse, status_code=status.HTTP_201_CREATED)
async def adjust_inventory(
    adjustment: InventoryAdjustmentRequest,
    db: Session = Depends(get_db)
):
    """
    Adjust inventory for a product.
    
    Supports:
    - SET_COUNT: Set lot quantity to a specific value
    - INCREASE: Increase lot quantity by specified amount
    - DECREASE: Decrease lot quantity by specified amount
    
    If lot_id is provided, adjusts that lot. Otherwise creates a new lot.
    """
    # Validate product exists
    product = db.get(Product, adjustment.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    inventory_service = InventoryService(db)
    
    try:
        if adjustment.lot_id:
            # Adjust existing lot
            lot = db.get(InventoryLot, adjustment.lot_id)
            if not lot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Lot {adjustment.lot_id} not found"
                )
            
            if lot.product_id != adjustment.product_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Lot does not belong to specified product"
                )
            
            # Calculate delta based on adjustment type
            current_qty = lot.quantity_kg
            if adjustment.adjustment_type == "SET_COUNT":
                delta_kg = adjustment.quantity_kg - current_qty
                new_qty = adjustment.quantity_kg
            elif adjustment.adjustment_type == "INCREASE":
                delta_kg = adjustment.quantity_kg
                new_qty = current_qty + adjustment.quantity_kg
            elif adjustment.adjustment_type == "DECREASE":
                delta_kg = -adjustment.quantity_kg
                new_qty = current_qty - adjustment.quantity_kg
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid adjustment type: {adjustment.adjustment_type}"
                )
            
            # Update lot quantity
            lot.quantity_kg = round_quantity(new_qty)
            
            # Update cost if provided (revaluation)
            if adjustment.unit_cost is not None:
                if lot.original_unit_cost is None:
                    lot.original_unit_cost = lot.unit_cost or adjustment.unit_cost
                lot.current_unit_cost = adjustment.unit_cost
                lot.unit_cost = adjustment.unit_cost
            
            db.flush()
            
            # Create adjustment transaction
            cost_source = "override" if adjustment.unit_cost else None
            txn = inventory_service.write_inventory_txn(
                lot_id=lot.id,
                txn_type="ADJUSTMENT",
                qty_kg=delta_kg,
                unit_cost=adjustment.unit_cost or lot.unit_cost or lot.current_unit_cost,
                ref_type=adjustment.reference_type,
                ref_id=adjustment.reference_id,
                notes=adjustment.notes,
                cost_source=cost_source
            )
            
            db.flush()
            
            return InventoryAdjustmentResponse(
                transaction_id=str(txn.id),
                product_id=adjustment.product_id,
                lot_id=lot.id,
                adjustment_type=adjustment.adjustment_type,
                quantity_delta_kg=delta_kg,
                new_quantity_kg=new_qty,
                unit_cost=adjustment.unit_cost or lot.unit_cost or lot.current_unit_cost,
                notes=adjustment.notes,
                reference_type=adjustment.reference_type,
                reference_id=adjustment.reference_id,
                created_at=txn.created_at or datetime.utcnow()
            )
        
        else:
            # Create new lot
            if adjustment.adjustment_type != "INCREASE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New lots can only be created with INCREASE adjustment type"
                )
            
            if adjustment.unit_cost is None:
                # Try to get cost from product
                from app.services.costing import CostingService
                costing_service = CostingService(db)
                try:
                    cost_info = costing_service.get_current_cost(adjustment.product_id)
                    unit_cost = cost_info['unit_cost']
                except Exception:
                    unit_cost = product.standard_cost or Decimal("0")
            else:
                unit_cost = adjustment.unit_cost
            
            # Generate lot code
            lot_code = f"ADJ-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            
            # Create new lot
            lot = inventory_service.add_lot(
                product_id=adjustment.product_id,
                lot_code=lot_code,
                qty_kg=adjustment.quantity_kg,
                unit_cost=unit_cost
            )
            
            db.flush()
            
            # Create adjustment transaction with notes and reference
            txn = inventory_service.write_inventory_txn(
                lot_id=lot.id,
                txn_type="ADJUSTMENT",
                qty_kg=adjustment.quantity_kg,
                unit_cost=unit_cost,
                ref_type=adjustment.reference_type,
                ref_id=adjustment.reference_id,
                notes=adjustment.notes,
                cost_source="override" if adjustment.unit_cost else "standard"
            )
            
            db.flush()
            
            return InventoryAdjustmentResponse(
                transaction_id=str(txn.id),
                product_id=adjustment.product_id,
                lot_id=lot.id,
                adjustment_type=adjustment.adjustment_type,
                quantity_delta_kg=adjustment.quantity_kg,
                new_quantity_kg=lot.quantity_kg,
                unit_cost=unit_cost,
                notes=adjustment.notes,
                reference_type=adjustment.reference_type,
                reference_id=adjustment.reference_id,
                created_at=txn.created_at or datetime.utcnow()
            )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to adjust inventory: {str(e)}"
        )

