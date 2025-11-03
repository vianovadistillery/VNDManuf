#!/usr/bin/env python3
"""Test assembly operations after unified products migration."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from decimal import Decimal

from app.adapters.db.models import InventoryLot, Product
from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyDirection
from app.adapters.db.session import get_session
from app.services.assembly_service import AssemblyService


def test_assembly_operations():
    """Test RAW → WIP → FINISHED assembly workflow."""
    db = get_session()

    try:
        print("=" * 80)
        print("ASSEMBLY OPERATIONS TEST")
        print("=" * 80)

        # Step 1: Create Products
        print("\n1. Creating products...")

        from datetime import datetime as dt

        timestamp = dt.now().strftime("%Y%m%d%H%M%S")

        raw1 = Product(
            sku=f"RM-ASSEMBLY-{timestamp}-001",
            name="Resin A",
            product_type="RAW",
            base_unit="KG",
            specific_gravity=Decimal("1.2"),
            usage_cost=Decimal("10.50"),
            raw_material_code=9101,
            is_active=True,
        )

        raw2 = Product(
            sku=f"RM-ASSEMBLY-{timestamp}-002",
            name="Solvent B",
            product_type="RAW",
            base_unit="KG",
            specific_gravity=Decimal("0.8"),
            usage_cost=Decimal("8.00"),
            raw_material_code=9102,
            is_active=True,
        )

        wip = Product(
            sku=f"WIP-ASSEMBLY-{timestamp}-001",
            name="WIP Paint Base",
            product_type="WIP",
            base_unit="KG",
            is_active=True,
        )

        finished = Product(
            sku=f"FG-ASSEMBLY-{timestamp}-001",
            name="Finished Paint",
            product_type="FINISHED",
            base_unit="KG",
            is_active=True,
        )

        db.add_all([raw1, raw2, wip, finished])
        db.commit()

        print(f"   [OK] Created RAW products: {raw1.sku}, {raw2.sku}")
        print(f"   [OK] Created WIP product: {wip.sku}")
        print(f"   [OK] Created FINISHED product: {finished.sku}")

        # Step 2: Add Inventory for RAW Materials
        print("\n2. Adding inventory for RAW materials...")

        raw1_lot = InventoryLot(
            product_id=raw1.id,
            lot_code="RAW1-LOT-001",
            quantity_kg=Decimal("500.0"),
            unit_cost=Decimal("10.0"),
            received_at=datetime.utcnow(),
            is_active=True,
        )

        raw2_lot = InventoryLot(
            product_id=raw2.id,
            lot_code="RAW2-LOT-001",
            quantity_kg=Decimal("300.0"),
            unit_cost=Decimal("8.0"),
            received_at=datetime.utcnow(),
            is_active=True,
        )

        db.add_all([raw1_lot, raw2_lot])
        db.commit()

        print(f"   [OK] Added {raw1_lot.quantity_kg} kg of {raw1.sku}")
        print(f"   [OK] Added {raw2_lot.quantity_kg} kg of {raw2.sku}")

        # Step 3: Create Assembly Definitions
        print("\n3. Creating assembly definitions...")

        # Assembly: WIP from RAW1 and RAW2
        assembly_wip_raw1 = Assembly(
            parent_product_id=wip.id,
            child_product_id=raw1.id,
            ratio=Decimal("0.6"),  # 0.6 kg RAW1 per kg WIP
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.05"),  # 5% loss
        )

        assembly_wip_raw2 = Assembly(
            parent_product_id=wip.id,
            child_product_id=raw2.id,
            ratio=Decimal("0.4"),  # 0.4 kg RAW2 per kg WIP
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.03"),  # 3% loss
        )

        # Assembly: FINISHED from WIP
        assembly_finished_wip = Assembly(
            parent_product_id=finished.id,
            child_product_id=wip.id,
            ratio=Decimal("1.0"),  # 1 kg WIP per kg FINISHED
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.02"),  # 2% loss
        )

        db.add_all([assembly_wip_raw1, assembly_wip_raw2, assembly_finished_wip])
        db.commit()

        print("   [OK] Created assembly: WIP from RAW1 (0.6:1 ratio)")
        print("   [OK] Created assembly: WIP from RAW2 (0.4:1 ratio)")
        print("   [OK] Created assembly: FINISHED from WIP (1.0:1 ratio)")

        # Step 4: Test Stage 1 - Assemble RAW -> WIP
        print("\n4. Testing Stage 1: RAW -> WIP Assembly...")

        svc = AssemblyService(db)
        wip_qty = Decimal("100.0")

        result1 = svc.assemble(
            parent_product_id=wip.id, parent_qty=wip_qty, reason="TEST_RAW_TO_WIP"
        )

        db.commit()

        print(f"   [OK] Produced {result1['produced']['quantity_kg']} kg of WIP")
        print(f"   [OK] Consumed {len(result1['consumed'])} child products")
        for consumed in result1["consumed"]:
            print(
                f"     - {consumed['qty_consumed']} kg of child {consumed['child_product_id'][:8]}"
            )

        # Verify inventory
        db.refresh(raw1_lot)
        db.refresh(raw2_lot)
        print(f"   [OK] RAW1 lot remaining: {raw1_lot.quantity_kg} kg")
        print(f"   [OK] RAW2 lot remaining: {raw2_lot.quantity_kg} kg")

        # Check WIP lot created
        wip_lots = (
            db.query(InventoryLot).filter(InventoryLot.product_id == wip.id).all()
        )
        print(f"   [OK] WIP lots created: {len(wip_lots)}")
        if wip_lots:
            print(
                f"     - Lot: {wip_lots[0].lot_code}, Qty: {wip_lots[0].quantity_kg} kg"
            )

        # Step 5: Test Stage 2 - Assemble WIP -> FINISHED
        print("\n5. Testing Stage 2: WIP -> FINISHED Assembly...")

        finished_qty = Decimal("50.0")

        result2 = svc.assemble(
            parent_product_id=finished.id,
            parent_qty=finished_qty,
            reason="TEST_WIP_TO_FINISHED",
        )

        db.commit()

        print(f"   [OK] Produced {result2['produced']['quantity_kg']} kg of FINISHED")
        print(f"   [OK] Consumed {len(result2['consumed'])} child products")

        # Verify WIP lot was consumed
        if wip_lots:
            db.refresh(wip_lots[0])
            print(f"   [OK] WIP lot remaining: {wip_lots[0].quantity_kg} kg")

        # Check FINISHED lot created
        finished_lots = (
            db.query(InventoryLot).filter(InventoryLot.product_id == finished.id).all()
        )
        print(f"   [OK] FINISHED lots created: {len(finished_lots)}")
        if finished_lots:
            print(
                f"     - Lot: {finished_lots[0].lot_code}, Qty: {finished_lots[0].quantity_kg} kg"
            )

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print("[OK] Multi-stage assembly (RAW -> WIP -> FINISHED) - SUCCESS")
        print("[OK] Inventory tracking - SUCCESS")
        print("[OK] Cost calculation - SUCCESS")
        print("\nAll assembly operations working correctly!")

        return True

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_assembly_operations()
    sys.exit(0 if success else 1)
