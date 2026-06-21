"""
Stock management services for FIFO, reservations, and stocktake.
Per Phase 6.2 of tpmanu.plan.md
"""

import uuid
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.adapters.db.models import (
    Batch,
    BatchComponent,
    InventoryLot,
    InventoryTxn,
    Product,
)
from app.domain.inventory_uom import inventory_uom_for_product
from app.domain.rules import round_quantity
from app.services.inventory import InventoryService


def reserve_materials(batch_id: str, db: Session) -> Dict[str, any]:
    """
    Reserve raw materials for a batch (decrement SOH).
    Returns reservation summary.
    """

    batch = db.get(Batch, batch_id)
    if not batch:
        raise ValueError(f"Batch {batch_id} not found")

    # Get batch components
    stmt = select(BatchComponent).where(BatchComponent.batch_id == batch_id)
    components = db.execute(stmt).scalars().all()

    reservations = []
    issues = []
    inventory_service = InventoryService(db)

    for component in components:
        # Get product
        product = db.get(Product, component.ingredient_product_id)
        if not product:
            issues.append(f"Product {component.ingredient_product_id} not found")
            continue

        allow_negative = bool(getattr(product, "allow_negative_inventory", False))

        try:
            fifo_issues = inventory_service.consume_lots_fifo(
                product_id=product.id,
                qty_kg=component.quantity_kg,
                reason=f"Batch {batch.batch_code}",
                ref_type="BATCH",
                ref_id=batch.id,
                notes=f"Batch {batch.batch_code}",
                allow_negative=allow_negative,
            )
        except ValueError as e:
            issues.append(str(e))
            db.rollback()
            return {"success": False, "issues": issues}

        for issue in fifo_issues:
            reservations.append(
                {
                    "lot_id": issue.lot_id,
                    "material_id": product.sku,
                    "qty_issued": issue.quantity_kg,
                }
            )

    db.commit()

    return {"success": True, "reservations": reservations, "issues": issues}


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
                InventoryTxn.quantity_kg < 0,  # Negative for consumption
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
                    notes=f"{reason}: Batch {batch.batch_code}",
                )
                db.add(reversal)

                releases.append(
                    {"lot_id": lot.id, "qty_restored": abs(txn.quantity_kg)}
                )

    db.commit()

    return {"success": True, "releases": releases}


def perform_stocktake(
    counts: List[Dict],
    db: Session,
    reference: Optional[str] = None,
    counter: Optional[str] = None,
    stocktake_date: Optional[str] = None,
) -> Dict[str, any]:
    """
    Perform stocktake: compare physical vs system SOH.
    When update_soh is true, sets product SOH to the physical count.
    """
    inventory_service = InventoryService(db)
    variances = []
    total_system_value = Decimal("0.00")
    total_physical_value = Decimal("0.00")
    items_adjusted = 0

    ref_note_parts = []
    if reference:
        ref_note_parts.append(f"Ref: {reference}")
    if counter:
        ref_note_parts.append(f"By: {counter}")
    if stocktake_date:
        ref_note_parts.append(f"Date: {stocktake_date}")
    ref_suffix = " | ".join(ref_note_parts)

    for count in counts:
        product_id = count.get("product_id") or count.get("material_id")
        if not product_id:
            continue

        physical_count = round_quantity(Decimal(str(count.get("physical_count", 0))))

        product = db.get(Product, product_id)
        if not product:
            continue

        system_soh = inventory_service.get_stock_on_hand(product_id)
        variance = round_quantity(physical_count - system_soh)
        variance_pct = (
            (variance / system_soh * 100) if system_soh > 0 else Decimal("0.00")
        )

        usage_cost = (
            product.usage_cost_ex_gst
            or product.purchase_cost_ex_gst
            or product.usage_cost
            or Decimal("0")
        )
        system_value = system_soh * usage_cost
        physical_value = physical_count * usage_cost

        total_system_value += system_value
        total_physical_value += physical_value

        line_notes = count.get("notes") or ""
        if ref_suffix:
            line_notes = f"{line_notes} | {ref_suffix}".strip(" |")

        inv_unit = inventory_uom_for_product(product)

        variances.append(
            {
                "product_id": product_id,
                "material_id": product_id,
                "material_code": product.raw_material_code or product.sku,
                "material_desc": product.name,
                "inventory_unit": inv_unit,
                "system_soh": float(system_soh),
                "physical_count": float(physical_count),
                "variance": float(variance),
                "variance_pct": float(variance_pct),
                "system_value": float(system_value),
                "physical_value": float(physical_value),
                "adjusted": False,
            }
        )

        if count.get("update_soh", False):
            inventory_service.set_product_count(
                product_id=product_id,
                target_qty_kg=physical_count,
                ref_type="STOCKTAKE",
                ref_id=reference,
                notes=line_notes or "Stocktake adjustment",
                unit_cost=usage_cost if usage_cost else None,
                allow_negative=bool(
                    getattr(product, "allow_negative_inventory", False)
                ),
            )
            variances[-1]["adjusted"] = True
            items_adjusted += 1

    db.commit()

    return {
        "variances": variances,
        "total_system_value": float(total_system_value),
        "total_physical_value": float(total_physical_value),
        "total_variance_value": float(total_physical_value - total_system_value),
        "item_count": len(variances),
        "items_adjusted": items_adjusted,
        "reference": reference,
        "counter": counter,
        "stocktake_date": stocktake_date,
    }
