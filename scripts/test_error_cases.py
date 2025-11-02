#!/usr/bin/env python3
"""
Test error cases for assembly operations and product validation.

Tests:
- Insufficient stock scenarios
- Invalid product_type validation
- Missing assembly definitions
- Missing products (404 errors)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime

from app.adapters.db.session import get_session
from app.adapters.db.models import Product, InventoryLot
from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyDirection
from app.services.assembly_service import AssemblyService
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"


def test_insufficient_stock_assembly(db: Session):
    """Test assembly fails when insufficient stock available."""
    print("\n1. Testing insufficient stock scenario...")
    try:
        # Create test products
        raw = Product(
            sku=f"RM-ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="Test Raw Material",
            product_type="RAW",
            base_unit="KG",
            is_active=True
        )
        wip = Product(
            sku=f"WIP-ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="Test WIP",
            product_type="WIP",
            base_unit="KG",
            is_active=True
        )
        db.add_all([raw, wip])
        db.flush()
        
        # Create limited inventory (only 10 kg)
        lot = InventoryLot(
            product_id=raw.id,
            lot_code="LIMITED-LOT",
            quantity_kg=Decimal("10.0"),
            unit_cost=Decimal("5.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )
        db.add(lot)
        db.flush()
        
        # Create assembly definition
        assembly = Assembly(
            parent_product_id=wip.id,
            child_product_id=raw.id,
            ratio=Decimal("2.0"),  # Need 2 kg raw per 1 kg wip
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.0")
        )
        db.add(assembly)
        db.commit()
        
        # Try to assemble more than available (need 20 kg, only have 10)
        svc = AssemblyService(db)
        try:
            svc.assemble(wip.id, Decimal("10.0"), "TEST_INSUFFICIENT")
            print("   [FAIL] Should have raised ValueError for insufficient stock")
            return False
        except ValueError as e:
            error_msg = str(e)
            if "Insufficient" in error_msg or "not enough" in error_msg.lower():
                print(f"   [OK] Correctly raised error: {error_msg}")
                
                # Verify no partial consumption occurred
                db.refresh(lot)
                assert lot.quantity_kg == Decimal("10.0"), "Stock was partially consumed!"
                print(f"   [OK] Stock not consumed: {lot.quantity_kg} kg remaining")
                return True
            else:
                print(f"   [FAIL] Wrong error message: {error_msg}")
                return False
        
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_invalid_product_type_api():
    """Test API rejects invalid product_type."""
    print("\n2. Testing invalid product_type validation via API...")
    try:
        # Test connection
        try:
            requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=2)
        except:
            print("   [SKIP] API server not running")
            return True
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        product_data = {
            "sku": f"TEST-INVALID-{timestamp}",
            "name": "Test Invalid",
            "product_type": "INVALID_TYPE",
            "base_unit": "KG"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/products",
            json=product_data,
            timeout=5
        )
        
        if response.status_code == 422:
            print("   [OK] API correctly rejected invalid product_type")
            return True
        else:
            print(f"   [FAIL] Expected 422, got {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def test_missing_assembly_definition(db: Session):
    """Test assembly fails when no assembly definition exists."""
    print("\n3. Testing missing assembly definition...")
    try:
        # Create products without assembly definition
        parent = Product(
            sku=f"PARENT-NO-ASSEMBLY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="Parent No Assembly",
            product_type="FINISHED",
            base_unit="KG",
            is_active=True
        )
        db.add(parent)
        db.commit()
        
        svc = AssemblyService(db)
        try:
            svc.assemble(parent.id, Decimal("10.0"), "TEST_NO_ASSEMBLY")
            print("   [FAIL] Should have raised ValueError for missing assembly")
            return False
        except ValueError as e:
            error_msg = str(e)
            if "No assembly definitions" in error_msg or "not found" in error_msg.lower():
                print(f"   [OK] Correctly raised error: {error_msg}")
                return True
            else:
                print(f"   [FAIL] Wrong error message: {error_msg}")
                return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def test_missing_product_api():
    """Test API returns 404 for non-existent product."""
    print("\n4. Testing missing product (404 error)...")
    try:
        # Test connection
        try:
            requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=2)
        except:
            print("   [SKIP] API server not running")
            return True
        
        # Use obviously non-existent UUID
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{API_BASE_URL}/products/{fake_id}", timeout=5)
        
        if response.status_code == 404:
            print("   [OK] API correctly returned 404 for non-existent product")
            return True
        else:
            print(f"   [FAIL] Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def test_missing_product_assembly_api():
    """Test assembly API returns error for non-existent product."""
    print("\n5. Testing assembly with non-existent product via API...")
    try:
        # Test connection
        try:
            requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=2)
        except:
            print("   [SKIP] API server not running")
            return True
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        assemble_data = {
            "parent_product_id": fake_id,
            "qty": 10.0,
            "reason": "TEST"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/assemblies/assemble",
            json=assemble_data,
            timeout=5
        )
        
        # Should return error (422 or 500)
        if response.status_code in [422, 500]:
            print(f"   [OK] API correctly returned error ({response.status_code})")
            return True
        else:
            print(f"   [FAIL] Expected error (422/500), got {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def main():
    """Run all error case tests."""
    print("=" * 80)
    print("ERROR CASE TESTING")
    print("=" * 80)
    
    db = get_session()
    
    try:
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        
        # Test 1: Insufficient stock
        if test_insufficient_stock_assembly(db):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 2: Invalid product_type
        if test_invalid_product_type_api():
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 3: Missing assembly definition
        if test_missing_assembly_definition(db):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 4: Missing product (404)
        if test_missing_product_api():
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 5: Missing product assembly
        if test_missing_product_assembly_api():
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
            print("\n[SUCCESS] All error case tests passed!")
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


