#!/usr/bin/env python3
"""
Migration script to backfill costing fields for existing data.

This script:
1. Sets is_tracked and sellable flags based on product_type
2. Backfills standard_cost from purcost where available
3. Sets original_unit_cost and current_unit_cost from existing unit_cost
4. Backfills cost_source and extended_cost for existing transactions
5. Builds assembly_cost_dependencies for existing batches/components
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime

from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import (
    AssemblyCostDependency,
    Batch,
    InventoryLot,
    InventoryTxn,
    Product,
)
from app.domain.rules import CostSource, round_money


def backfill_product_costing_fields(db: Session, dry_run: bool = True):
    """Backfill costing fields on products."""
    products = db.query(Product).all()

    updated_count = 0

    for product in products:
        updates = {}

        # Set is_tracked: default True for RAW, True for WIP/FINISHED (can be overridden)
        if product.is_tracked is None:
            updates["is_tracked"] = True  # Default to tracked

        # Set sellable: only FINISHED products are sellable by default
        if product.sellable is None:
            updates["sellable"] = product.product_type == "FINISHED"

        # Backfill standard_cost from purcost if available
        if product.standard_cost is None and product.purcost is not None:
            updates["standard_cost"] = product.purcost

        if updates:
            if not dry_run:
                for key, value in updates.items():
                    setattr(product, key, value)
                updated_count += 1
            else:
                print(f"Would update {product.sku}: {updates}")
                updated_count += 1

    if not dry_run:
        db.commit()

    print(f"{'Would update' if dry_run else 'Updated'} {updated_count} products")
    return updated_count


def backfill_lot_costing_fields(db: Session, dry_run: bool = True):
    """Backfill costing fields on inventory lots."""
    lots = db.query(InventoryLot).all()

    updated_count = 0

    for lot in lots:
        updates = {}

        # Set original_unit_cost and current_unit_cost from existing unit_cost
        if lot.unit_cost is not None:
            if lot.original_unit_cost is None:
                updates["original_unit_cost"] = lot.unit_cost
            if lot.current_unit_cost is None:
                updates["current_unit_cost"] = lot.unit_cost

        if updates:
            if not dry_run:
                for key, value in updates.items():
                    setattr(lot, key, value)
                updated_count += 1
            else:
                print(f"Would update lot {lot.lot_code}: {updates}")
                updated_count += 1

    if not dry_run:
        db.commit()

    print(f"{'Would update' if dry_run else 'Updated'} {updated_count} lots")
    return updated_count


def backfill_transaction_costing_fields(db: Session, dry_run: bool = True):
    """Backfill costing fields on inventory transactions."""
    txns = db.query(InventoryTxn).all()

    updated_count = 0

    for txn in txns:
        updates = {}

        # Calculate extended_cost
        if (
            txn.extended_cost is None
            and txn.unit_cost is not None
            and txn.quantity_kg is not None
        ):
            extended = round_money(abs(txn.quantity_kg) * txn.unit_cost)
            if txn.quantity_kg < 0:  # Negative for issues
                extended = -extended
            updates["extended_cost"] = extended

        # Set cost_source based on transaction type
        if txn.cost_source is None:
            if txn.transaction_type == "RECEIPT":
                updates["cost_source"] = CostSource.SUPPLIER_INVOICE.value
            elif txn.transaction_type == "ISSUE":
                # Default to fifo_actual if lot has cost, otherwise unknown
                lot = txn.lot
                if lot and (lot.current_unit_cost or lot.unit_cost):
                    updates["cost_source"] = CostSource.FIFO_ACTUAL.value
                else:
                    updates["cost_source"] = CostSource.UNKNOWN.value
            elif txn.transaction_type == "PRODUCE":
                updates[
                    "cost_source"
                ] = CostSource.FIFO_ACTUAL.value  # Assembly-produced items
            else:
                updates["cost_source"] = CostSource.UNKNOWN.value

        if updates:
            if not dry_run:
                for key, value in updates.items():
                    setattr(txn, key, value)
                updated_count += 1
            else:
                print(f"Would update txn {txn.id[:8]}...: {updates}")
                updated_count += 1

    if not dry_run:
        db.commit()

    print(f"{'Would update' if dry_run else 'Updated'} {updated_count} transactions")
    return updated_count


def build_assembly_cost_dependencies(db: Session, dry_run: bool = True):
    """Build assembly_cost_dependencies from existing batches/components."""
    # Get completed batches with components
    batches = db.query(Batch).filter(Batch.status == "COMPLETED").all()

    created_count = 0

    for batch in batches:
        # Find produced lot for this batch (created around batch completion time)
        produced_lots = (
            db.query(InventoryLot)
            .filter(
                InventoryLot.product_id == batch.work_order.product_id,
                InventoryLot.received_at >= batch.completed_at
                if batch.completed_at
                else True,
            )
            .order_by(InventoryLot.received_at.desc())
            .limit(1)
            .all()
        )

        if not produced_lots:
            continue

        produced_lot = produced_lots[0]

        # Find PRODUCE transaction for this lot
        produce_txns = (
            db.query(InventoryTxn)
            .filter(
                InventoryTxn.lot_id == produced_lot.id,
                InventoryTxn.transaction_type == "PRODUCE",
            )
            .all()
        )

        if not produce_txns:
            continue

        produce_txn = produce_txns[0]

        # Process batch components
        for component in batch.components:
            if not component.lot_id:
                continue

            # Find ISSUE transaction for this component lot around batch time
            issue_txns = (
                db.query(InventoryTxn)
                .filter(
                    InventoryTxn.lot_id == component.lot_id,
                    InventoryTxn.transaction_type == "ISSUE",
                    InventoryTxn.created_at
                    <= (batch.completed_at or datetime.utcnow()),
                )
                .order_by(InventoryTxn.created_at.desc())
                .limit(1)
                .all()
            )

            if not issue_txns:
                continue

            issue_txn = issue_txns[0]

            # Check if dependency already exists
            existing = (
                db.query(AssemblyCostDependency)
                .filter(
                    AssemblyCostDependency.consumed_lot_id == component.lot_id,
                    AssemblyCostDependency.produced_lot_id == produced_lot.id,
                    AssemblyCostDependency.consumed_txn_id == issue_txn.id,
                    AssemblyCostDependency.produced_txn_id == produce_txn.id,
                )
                .first()
            )

            if existing:
                continue

            # Create dependency
            if not dry_run:
                dep = AssemblyCostDependency(
                    consumed_lot_id=component.lot_id,
                    produced_lot_id=produced_lot.id,
                    consumed_txn_id=issue_txn.id,
                    produced_txn_id=produce_txn.id,
                    dependency_ts=batch.completed_at or datetime.utcnow(),
                )
                db.add(dep)
                created_count += 1
            else:
                print(
                    f"Would create dependency: {component.lot_id} -> {produced_lot.id}"
                )
                created_count += 1

    if not dry_run:
        db.commit()

    print(
        f"{'Would create' if dry_run else 'Created'} {created_count} assembly cost dependencies"
    )
    return created_count


def main():
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate costing data for existing records"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the migration (default is dry-run)",
    )
    args = parser.parse_args()

    dry_run = not args.execute

    print("=" * 60)
    print("Costing Data Migration Script")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print()

    db_gen = get_db()
    db = next(db_gen)

    try:
        # Step 1: Backfill product fields
        print("\n1. Backfilling product costing fields...")
        backfill_product_costing_fields(db, dry_run)

        # Step 2: Backfill lot fields
        print("\n2. Backfilling inventory lot costing fields...")
        backfill_lot_costing_fields(db, dry_run)

        # Step 3: Backfill transaction fields
        print("\n3. Backfilling transaction costing fields...")
        backfill_transaction_costing_fields(db, dry_run)

        # Step 4: Build assembly dependencies
        print("\n4. Building assembly cost dependencies...")
        build_assembly_cost_dependencies(db, dry_run)

        if not dry_run:
            db.commit()
            print("\n" + "=" * 60)
            print("MIGRATION COMPLETE")
        else:
            db.rollback()
            print("\n" + "=" * 60)
            print("DRY RUN COMPLETE")
            print("Run with --execute to apply changes")
    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        db.close()
        print("=" * 60)


if __name__ == "__main__":
    main()
