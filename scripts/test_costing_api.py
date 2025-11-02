#!/usr/bin/env python3
"""Test costing API endpoints."""
import requests
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.adapters.db import get_db
from app.adapters.db.models import Product

API_BASE = "http://127.0.0.1:8000/api/v1"

def test_api_connection():
    """Test if API server is running."""
    try:
        response = requests.get(f"{API_BASE}/products/", timeout=5)
        if response.status_code == 200:
            print(f"[OK] API server is running (Status: {response.status_code})")
            data = response.json()
            # Handle both dict and list responses
            if isinstance(data, dict):
                products = data.get("products", [])
            else:
                products = data if isinstance(data, list) else []
            print(f"[OK] Found {len(products)} products")
            return True
        else:
            print(f"[FAIL] API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] API server not running. Start with:")
        print("  python -m uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000")
        return False
    except Exception as e:
        print(f"[FAIL] Error connecting to API: {e}")
        return False

def test_costing_inspect():
    """Test COGS inspection endpoint."""
    print("\n" + "=" * 60)
    print("Testing COGS Inspection Endpoint")
    print("=" * 60)
    
    # Get a product from DB
    db_gen = get_db()
    db = next(db_gen)
    try:
        product = db.query(Product).filter(Product.is_active == True).first()
        if not product:
            print("[FAIL] No active products found in database")
            return False
        
        print(f"\nTesting with product: {product.sku} ({product.name})")
        print(f"Product ID: {product.id}")
        
        # Test inspect endpoint
        url = f"{API_BASE}/costing/inspect/{product.id}"
        print(f"\nGET {url}")
        
        response = requests.get(url, params={"include_estimates": True}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            breakdown = data.get("cogs_breakdown", {})
            
            print(f"[OK] Status: {response.status_code}")
            print(f"[OK] SKU: {breakdown.get('sku', 'N/A')}")
            print(f"[OK] Name: {breakdown.get('name', 'N/A')}")
            print(f"[OK] Unit Cost: ${breakdown.get('unit_cost', 0):.2f}")
            print(f"[OK] Cost Source: {breakdown.get('cost_source', 'unknown')}")
            print(f"[OK] Has Estimate: {breakdown.get('has_estimate', False)}")
            
            if breakdown.get('has_estimate'):
                print(f"  [WARN] Estimate Reason: {breakdown.get('estimate_reason', 'N/A')}")
            
            children = breakdown.get('children', [])
            if children:
                print(f"\n[OK] Found {len(children)} child components")
                for i, child in enumerate(children[:3]):  # Show first 3
                    print(f"  {i+1}. {child.get('sku')} - ${child.get('unit_cost', 0):.2f}")
            
            return True
        elif response.status_code == 404:
            print(f"[FAIL] Product not found (Status: {response.status_code})")
            error_data = response.json()
            print(f"  Detail: {error_data.get('detail', 'Unknown error')}")
            return False
        else:
            print(f"[FAIL] Error (Status: {response.status_code})")
            try:
                error_data = response.json()
                print(f"  Detail: {error_data.get('detail', error_data)}")
            except:
                print(f"  Response: {response.text[:200]}")
            return False
            
    finally:
        db.close()

def test_costing_current():
    """Test current cost endpoint."""
    print("\n" + "=" * 60)
    print("Testing Current Cost Endpoint")
    print("=" * 60)
    
    db_gen = get_db()
    db = next(db_gen)
    try:
        product = db.query(Product).filter(Product.is_active == True).first()
        if not product:
            print("[FAIL] No active products found")
            return False
        
        url = f"{API_BASE}/costing/current/{product.id}"
        print(f"\nGET {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Status: {response.status_code}")
            print(f"[OK] Unit Cost: ${data.get('unit_cost', 0):.2f}")
            print(f"[OK] Cost Source: {data.get('cost_source', 'unknown')}")
            return True
        else:
            print(f"[FAIL] Error (Status: {response.status_code})")
            return False
    finally:
        db.close()

def main():
    print("=" * 60)
    print("Costing API Test Suite")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    print("\nWaiting for API server...")
    time.sleep(2)
    
    if not test_api_connection():
        sys.exit(1)
    
    if not test_costing_inspect():
        print("\n[WARN] COGS inspection test failed, but API is running")
    
    if not test_costing_current():
        print("\n[WARN] Current cost test failed")
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()

