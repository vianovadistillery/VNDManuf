"""
Stock management services for FIFO, reservations, and stocktake.
Per Phase 6.2 of tpmanu.plan.md
"""

import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.adapters.db import get_db
from app.adapters.db.models import (
    InventoryLot, InventoryTxn, Batch, BatchComponent, Product
)


def reserve_materials(batch_id: str, db: Session) -> Dict[str, any]:
    """
    Reserve raw materials for a batch (decrement SOH).
    Returns reservation summary.
    """
    from app.domain.rules import fifo_issue, validate_non_negative_lot
    
    batch = db.get(Batch, batch_id)
    if not batch:
        raise ValueError(f"Batch {batch_id} not found")
    
    # Get batch components
    stmt = select(BatchComponent).where(BatchComponent.batch_id == batch_id)
    components = db.execute(stmt).scalars().all()
    
    reservations = []
    issues = []
    
    for component in components:
        # Get product
        product = db.get(Product, component.ingredient_product_id)
        if not product:
            issues.append(f"Product {component.ingredient_product_id} not found")
            continue
        
        # Get available lots
        lots_stmt = select(InventoryLot).where(
            and_(
                InventoryLot.product_id == component.ingredient_product_id,
                InventoryLot.is_active == True,
                InventoryLot.quantity_kg > 0
            )
        ).order_by(InventoryLot.received_at)
        
        lots = db.execute(lots_stmt).scalars().all()
        
        # Use FIFO to issue materials
        remaining_qty = component.quantity_kg
        for lot in lots:
            if remaining_qty <= 0:
                break
            
            qty_to_issue = min(remaining_qty, lot.quantity_kg)
            
            # Decrement lot
            lot.quantity_kg -= qty_to_issue
            
            # Validate non-negative
            if lot.quantity_kg < 0:
                issues.append(f"Lot {lot.lot_code} would go negative")
                db.rollback()
                return {'success': False, 'issues': issues}
            
            # Create transaction record
            txn = InventoryTxn(
                id=str(uuid.uuid4()),
                lot_id=lot.id,
                transaction_type="BATCH_CONSUMPTION",
                quantity_kg=-qty_to_issue,
                unit_cost=lot.unit_cost,
                notes=f"Batch {batch.batch_code}"
            )
            db.add(txn)
            
            reservations.append({
                'lot_id': lot.id,
                'material_id': material.code,
                'qty_issued': qty_to_issue
            })
            
            remaining_qty -= qty_to_issue
        
        if remaining_qty > 0:
            issues.append(f"Insufficient stock for {material.desc1}: need {remaining_qty} kg more")
            db.rollback()
            return {'success': False, 'issues': issues}
    
    db.commit()
    
    return {
        'success': True,
        'reservations': reservations,
        'issues': issues
    }


def release_materials(batch_id: str, db: Session, reason: str = "Batch cancelled"):
    """
    Return materials to SOH (for cancelled batches).
    """
    batch = db.get(Batch, batch_id)
    if not batch:
        raise ValueError(f"Batch {batch_id} not found")
    
    # Get batch components
    stmt = select(BatchComponent).where(BatchComponent.batch_id == batch_id)
    components = db.execute(stmt).scalars().all()
    
    releases = []
    
    for component in components:
        # Get the lots used
        txn_stmt = select(InventoryTxn).where(
            and_(
                InventoryTxn.notes.contains(batch.batch_code),
                InventoryTxn.transaction_type == "BATCH_CONSUMPTION",
                InventoryTxn.quantity_kg < 0  # Negative for consumption
            )
        )
        
        txns = db.execute(txn_stmt).scalars().all()
        
        for txn in txns:
            lot = db.get(InventoryLot, txn.lot_id)
            if lot:
                # Restore quantity
                lot.quantity_kg += abs(txn.quantity_kg)
                
                # Create reversal transaction
                reversal = InventoryTxn(
                    id=str(uuid.uuid4()),
                    lot_id=lot.id,
                    transaction_type="BATCH_REVERSAL",
                    quantity_kg=abs(txn.quantity_kg),
                    unit_cost=txn.unit_cost,
                    notes=f"{reason}: Batch {batch.batch_code}"
                )
                db.add(reversal)
                
                releases.append({
                    'lot_id': lot.id,
                    'qty_restored': abs(txn.quantity_kg)
                })
    
    db.commit()
    
    return {'success': True, 'releases': releases}


def perform_stocktake(counts: List[Dict], db: Session) -> Dict[str, any]:
    """
    Perform stocktake: compare physical vs system SOH.
    Returns variance report and updates SOH.
    """
    
    variances = []
    total_system_value = Decimal('0.00')
    total_physical_value = Decimal('0.00')
    
    for count in counts:
        material_id = count.get('material_id')
        physical_count = Decimal(str(count.get('physical_count', 0)))
        
        # Get system SOH from inventory lots
        product = db.get(Product, material_id)
        if not product:
            continue
        
        # Calculate system SOH from inventory lots
        lots_stmt = select(InventoryLot).where(
            and_(
                InventoryLot.product_id == material_id,
                InventoryLot.is_active == True
            )
        )
        lots = db.execute(lots_stmt).scalars().all()
        system_soh = sum(lot.quantity_kg for lot in lots) if lots else Decimal('0')
        
        # Calculate variance
        variance = physical_count - system_soh
        variance_pct = (variance / system_soh * 100) if system_soh > 0 else Decimal('0.00')
        
        # Calculate values
        usage_cost = product.usage_cost or Decimal('0')
        system_value = system_soh * usage_cost
        physical_value = physical_count * usage_cost
        
        total_system_value += system_value
        total_physical_value += physical_value
        
        variances.append({
            'material_id': material_id,
            'material_code': product.raw_material_code or product.sku,
            'material_desc': product.name,
            'system_soh': float(system_soh),
            'physical_count': float(physical_count),
            'variance': float(variance),
            'variance_pct': float(variance_pct),
            'system_value': float(system_value),
            'physical_value': float(physical_value)
        })
        
        # Update SOH if flagged - create/adjust inventory lot
        if count.get('update_soh', False):
            # Adjust inventory lot or create new one
            if lots:
                # Update existing lot
                lots[0].quantity_kg = physical_count
            else:
                # Create new lot for stocktake adjustment
                from app.adapters.db.models import InventoryLot
                lot = InventoryLot(
                    id=str(uuid.uuid4()),
                    product_id=material_id,
                    lot_code=f"STOCKTAKE-{datetime.now().strftime('%Y%m%d')}",
                    quantity_kg=physical_count,
                    unit_cost=usage_cost,
                    received_at=datetime.utcnow(),
                    is_active=True
                )
                db.add(lot)
            
            # Create transaction record
            txn = InventoryTxn(
                id=str(uuid.uuid4()),
                lot_id=lots[0].id if lots else None,
                transaction_type="STOCKTAKE",
                quantity_kg=variance,
                unit_cost=usage_cost,
                notes=f"Stocktake: {count.get('notes', '')}"
            )
            db.add(txn)
    
    db.commit()
    
    return {
        'variances': variances,
        'total_system_value': float(total_system_value),
        'total_physical_value': float(total_physical_value),
        'total_variance_value': float(total_physical_value - total_system_value),
        'item_count': len(variances)
    }

