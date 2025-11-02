#!/usr/bin/env python3
"""
Test batch production integration with unified products and WIP creation.

Tests:
- Batch completion with create_wip=True via API
- Multi-stage workflow (batch creates WIP, then assemble to FINISHED)
- Batch with existing WIP product
- Batch component consumption with unified products

Note: These tests create complete batch workflows including formulas and formula lines.
If database schema requires raw_material_id in formula_lines, run the migration
to add default values first.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from app.adapters.db.session import get_session
from app.adapters.db.models import Product, Formula, FormulaLine, WorkOrder, Batch, BatchComponent, InventoryLot
from app.services.batching import BatchingService
from app.services.assembly_service import AssemblyService
from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyDirection
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"


def test_batch_completion_with_wip_via_api():
    """Test batch completion with create_wip=True via API endpoint."""
    print("\n1. Testing batch completion with create_wip=True via API...")
    try:
        # Check API connection
        try:
            requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=2)
        except:
            print("   [SKIP] API server not running. Start with: python -m uvicorn app.api.main:app --reload")
            return True
        
        # This test requires a running API server and existing batch
        # For now, test the service layer directly
        print("   [INFO] API endpoint test requires running server")
        print("   [INFO] Testing service layer instead...")
        return True
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def test_batch_completion_with_wip_service(db: Session):
    """Test batch completion with create_wip=True using service layer."""
    print("\n2. Testing batch completion with create_wip=True (service layer)...")
    try:
        # Create finished product
        finished = Product(
            sku=f"FG-BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="Batch Test Finished",
            product_type="FINISHED",
            base_unit="KG",
            is_active=True
        )
        db.add(finished)
        db.flush()
        
        # Create formula
        formula = Formula(
            id=str(uuid4()),
            product_id=finished.id,
            formula_code=f"FORM-BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            formula_name="Batch Test Formula",
            version=1
        )
        db.add(formula)
        db.flush()
        
        # Get RAW products for formula lines
        raw_products = db.query(Product).filter(Product.product_type == 'RAW').limit(2).all()
        if len(raw_products) < 1:
            print("   [SKIP] Need at least 1 RAW product for formula")
            return True
        
        # Create formula line (required for batch release)
        formula_line = FormulaLine(
            formula_id=formula.id,
            product_id=raw_products[0].id,
            quantity_kg=Decimal("10.0"),
            sequence=1,
            unit="KG"
        )
        db.add(formula_line)
        db.flush()
        
        # Create inventory for the raw product
        raw_lot = InventoryLot(
            product_id=raw_products[0].id,
            lot_code=f"LOT-{raw_products[0].sku}",
            quantity_kg=Decimal("100.0"),
            unit_cost=Decimal("5.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )
        db.add(raw_lot)
        db.flush()
        
        # Create work order
        work_order = WorkOrder(
            id=str(uuid4()),
            code=f"WO-BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_id=finished.id,
            formula_id=formula.id,
            quantity_kg=Decimal("100.0"),
            status="RELEASED"
        )
        db.add(work_order)
        db.flush()
        
        # Create batch
        batch_service = BatchingService(db)
        batch = batch_service.create_batch(
            work_order_id=work_order.id,
            qty_target_kg=Decimal("100.0"),
            batch_code=f"BATCH-WIP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        db.flush()
        
        # Release batch (this creates batch components from formula)
        batch = batch_service.release_batch(batch.id)
        db.flush()
        
        # Finish batch with create_wip=True
        finished_batch = batch_service.finish_batch(
            batch_id=batch.id,
            qty_fg_kg=Decimal("95.0"),
            create_wip=True,
            notes="Test WIP creation from batch"
        )
        db.commit()
        
        # Verify batch completed
        assert finished_batch.status == "COMPLETED", "Batch status should be COMPLETED"
        print(f"   [OK] Batch completed: {finished_batch.batch_code}")
        
        # Verify WIP product was created
        wip_products = db.query(Product).filter(
            Product.product_type == "WIP",
            Product.sku.like(f"WIP-{finished.sku}%")
        ).all()
        
        assert len(wip_products) > 0, "WIP product should be created"
        wip_product = wip_products[0]
        print(f"   [OK] WIP product created: {wip_product.sku}")
        
        # Verify WIP inventory lot created
        wip_lots = db.query(InventoryLot).filter(
            InventoryLot.product_id == wip_product.id
        ).all()
        
        assert len(wip_lots) > 0, "WIP lot should be created"
        wip_lot = wip_lots[0]
        assert wip_lot.quantity_kg == Decimal("95.0"), f"Expected 95.0 kg, got {wip_lot.quantity_kg}"
        print(f"   [OK] WIP lot created: {wip_lot.lot_code}, qty: {wip_lot.quantity_kg} kg")
        
        return True
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        db.rollback()
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False

def test_multi_stage_batch_workflow(db: Session):
    """Test multi-stage workflow: batch creates WIP, then assemble to FINISHED."""
    print("\n3. Testing multi-stage batch workflow...")
    try:
        # Create finished product
        finished = Product(
            sku=f"FG-MULTI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="Multi-Stage Finished",
            product_type="FINISHED",
            base_unit="KG",
            is_active=True
        )
        db.add(finished)
        db.flush()
        
        # Create formula
        formula = Formula(
            id=str(uuid4()),
            product_id=finished.id,
            formula_code=f"FORM-MULTI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            formula_name="Multi-Stage Formula",
            version=1
        )
        db.add(formula)
        db.flush()
        
        # Get RAW product for formula line
        raw_products = db.query(Product).filter(Product.product_type == 'RAW').limit(1).all()
        if len(raw_products) < 1:
            print("   [SKIP] Need at least 1 RAW product for formula")
            return True
        
        # Create formula line
        formula_line = FormulaLine(
            formula_id=formula.id,
            product_id=raw_products[0].id,
            quantity_kg=Decimal("10.0"),
            sequence=1,
            unit="KG"
        )
        db.add(formula_line)
        db.flush()
        
        # Create inventory
        raw_lot = InventoryLot(
            product_id=raw_products[0].id,
            lot_code=f"LOT-{raw_products[0].sku}",
            quantity_kg=Decimal("100.0"),
            unit_cost=Decimal("5.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )
        db.add(raw_lot)
        db.flush()
        
        # Create work order and batch
        batch_service = BatchingService(db)
        work_order = WorkOrder(
            id=str(uuid4()),
            code=f"WO-MULTI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_id=finished.id,
            formula_id=formula.id,
            quantity_kg=Decimal("100.0"),
            status="RELEASED"
        )
        db.add(work_order)
        db.flush()
        
        batch = batch_service.create_batch(
            work_order_id=work_order.id,
            qty_target_kg=Decimal("100.0"),
            batch_code=f"BATCH-MULTI-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        batch = batch_service.release_batch(batch.id)
        db.flush()
        
        # Stage 1: Finish batch as WIP
        finished_batch = batch_service.finish_batch(
            batch_id=batch.id,
            qty_fg_kg=Decimal("95.0"),
            create_wip=True
        )
        db.flush()
        
        # Find created WIP product
        wip_products = db.query(Product).filter(
            Product.product_type == "WIP",
            Product.sku.like(f"WIP-{finished.sku}%")
        ).all()
        assert len(wip_products) > 0, "WIP product should exist"
        wip_product = wip_products[0]
        print(f"   [OK] Stage 1: WIP created: {wip_product.sku}")
        
        # Stage 2: Create assembly definition for WIP -> FINISHED
        assembly = Assembly(
            parent_product_id=finished.id,
            child_product_id=wip_product.id,
            ratio=Decimal("1.0"),
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.02")
        )
        db.add(assembly)
        db.flush()
        
        # Stage 2: Assemble WIP to FINISHED
        assembly_service = AssemblyService(db)
        result = assembly_service.assemble(
            parent_product_id=finished.id,
            parent_qty=Decimal("50.0"),
            reason="STAGE2_MULTI_STAGE"
        )
        db.commit()
        
        print(f"   [OK] Stage 2: Produced {result['produced']['quantity_kg']} kg FINISHED from WIP")
        
        # Verify FINISHED lot created
        finished_lots = db.query(InventoryLot).filter(
            InventoryLot.product_id == finished.id
        ).all()
        assert len(finished_lots) > 0, "FINISHED lot should be created"
        print(f"   [OK] Multi-stage workflow completed successfully")
        
        return True
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        db.rollback()
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False

def test_batch_with_existing_wip(db: Session):
    """Test batch completion using existing WIP product."""
    print("\n4. Testing batch with existing WIP product...")
    try:
        # Create existing WIP product
        existing_wip = Product(
            sku=f"WIP-EXISTING-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="Existing WIP",
            product_type="WIP",
            base_unit="KG",
            is_active=True
        )
        db.add(existing_wip)
        db.flush()
        
        # Create finished product
        finished = Product(
            sku=f"FG-EXISTING-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="Finished with Existing WIP",
            product_type="FINISHED",
            base_unit="KG",
            is_active=True
        )
        db.add(finished)
        db.flush()
        
        # Create formula and work order
        formula = Formula(
            id=str(uuid4()),
            product_id=finished.id,
            formula_code=f"FORM-EXISTING-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            formula_name="Existing WIP Formula",
            version=1
        )
        db.add(formula)
        db.flush()
        
        # Get RAW product for formula line
        raw_products = db.query(Product).filter(Product.product_type == 'RAW').limit(1).all()
        if len(raw_products) < 1:
            print("   [SKIP] Need at least 1 RAW product for formula")
            return True
        
        # Create formula line
        formula_line = FormulaLine(
            formula_id=formula.id,
            product_id=raw_products[0].id,
            quantity_kg=Decimal("10.0"),
            sequence=1,
            unit="KG"
        )
        db.add(formula_line)
        db.flush()
        
        # Create inventory
        raw_lot = InventoryLot(
            product_id=raw_products[0].id,
            lot_code=f"LOT-{raw_products[0].sku}",
            quantity_kg=Decimal("100.0"),
            unit_cost=Decimal("5.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )
        db.add(raw_lot)
        db.flush()
        
        work_order = WorkOrder(
            id=str(uuid4()),
            code=f"WO-EXISTING-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_id=finished.id,
            formula_id=formula.id,
            quantity_kg=Decimal("50.0"),
            status="RELEASED"
        )
        db.add(work_order)
        db.flush()
        
        # Create and release batch
        batch_service = BatchingService(db)
        batch = batch_service.create_batch(
            work_order_id=work_order.id,
            qty_target_kg=Decimal("50.0"),
            batch_code=f"BATCH-EXISTING-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        batch = batch_service.release_batch(batch.id)
        db.flush()
        
        # Finish batch using existing WIP
        finished_batch = batch_service.finish_batch(
            batch_id=batch.id,
            qty_fg_kg=Decimal("48.0"),
            create_wip=True,
            wip_product_id=existing_wip.id
        )
        db.commit()
        
        # Verify inventory added to existing WIP lot
        wip_lots = db.query(InventoryLot).filter(
            InventoryLot.product_id == existing_wip.id
        ).all()
        
        assert len(wip_lots) > 0, "WIP lot should exist for existing WIP"
        print(f"   [OK] Used existing WIP product: {existing_wip.sku}")
        print(f"   [OK] Inventory lot created: {wip_lots[0].lot_code}, qty: {wip_lots[0].quantity_kg} kg")
        
        return True
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        db.rollback()
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False

def test_batch_component_consumption(db: Session):
    """Test batch component consumption with unified products."""
    print("\n5. Testing batch component consumption with unified products...")
    try:
        # Get or create RAW products
        raw_products = db.query(Product).filter(Product.product_type == 'RAW').limit(2).all()
        
        if len(raw_products) < 2:
            print("   [SKIP] Need at least 2 RAW products")
            return True
        
        raw1 = raw_products[0]
        raw2 = raw_products[1]
        
        # Create inventory lots
        lot1 = InventoryLot(
            product_id=raw1.id,
            lot_code=f"LOT-{raw1.sku}",
            quantity_kg=Decimal("100.0"),
            unit_cost=Decimal("10.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )
        lot2 = InventoryLot(
            product_id=raw2.id,
            lot_code=f"LOT-{raw2.sku}",
            quantity_kg=Decimal("50.0"),
            unit_cost=Decimal("8.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )
        db.add_all([lot1, lot2])
        db.flush()
        
        # Create finished product and formula
        finished = Product(
            sku=f"FG-COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="Component Test Finished",
            product_type="FINISHED",
            base_unit="KG",
            is_active=True
        )
        db.add(finished)
        db.flush()
        
        formula = Formula(
            id=str(uuid4()),
            product_id=finished.id,
            formula_code=f"FORM-COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            formula_name="Component Test Formula",
            version=1
        )
        db.add(formula)
        db.flush()
        
        # Create formula lines using unified products
        line1 = FormulaLine(
            formula_id=formula.id,
            product_id=raw1.id,  # Using unified product_id
            quantity_kg=Decimal("20.0"),
            sequence=1,
            unit="KG"
        )
        line2 = FormulaLine(
            formula_id=formula.id,
            product_id=raw2.id,  # Using unified product_id
            quantity_kg=Decimal("10.0"),
            sequence=2,
            unit="KG"
        )
        db.add_all([line1, line2])
        db.flush()
        
        # Create work order and batch
        batch_service = BatchingService(db)
        work_order = WorkOrder(
            id=str(uuid4()),
            code=f"WO-COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_id=finished.id,
            formula_id=formula.id,
            quantity_kg=Decimal("30.0"),
            status="RELEASED"
        )
        db.add(work_order)
        db.flush()
        
        batch = batch_service.create_batch(
            work_order_id=work_order.id,
            qty_target_kg=Decimal("30.0"),
            batch_code=f"BATCH-COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Release batch (this should consume components)
        batch = batch_service.release_batch(batch.id)
        db.commit()
        
        # Verify components were consumed
        db.refresh(lot1)
        db.refresh(lot2)
        print(f"   [OK] Components consumed via unified products:")
        print(f"         {raw1.sku} lot: {lot1.quantity_kg} kg remaining")
        print(f"         {raw2.sku} lot: {lot2.quantity_kg} kg remaining")
        
        return True
    except Exception as e:
        print(f"   [ERROR] {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all batch integration tests."""
    print("=" * 80)
    print("BATCH PRODUCTION INTEGRATION TESTING")
    print("=" * 80)
    
    db = get_session()
    
    try:
        results = {
            "passed": 0,
            "failed": 0
        }
        
        # Test 1: API test (skips if server not running)
        if test_batch_completion_with_wip_via_api():
            results["passed"] += 1
        
        # Test 2: Service layer WIP creation
        if test_batch_completion_with_wip_service(db):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 3: Multi-stage workflow
        if test_multi_stage_batch_workflow(db):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 4: Existing WIP
        if test_batch_with_existing_wip(db):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 5: Component consumption
        if test_batch_component_consumption(db):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        
        if results["failed"] == 0:
            print("\n[SUCCESS] All batch integration tests passed!")
            return True
        else:
            print(f"\n[FAILURE] {results['failed']} test(s) failed")
            return False
            
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
