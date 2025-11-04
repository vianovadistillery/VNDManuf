#!/usr/bin/env python3
"""
Test API endpoints with product_type filtering.

Tests:
- GET /api/v1/products?product_type=RAW|WIP|FINISHED
- POST /api/v1/products with different product_type values
- PUT /api/v1/products/{id} with product_type changes
- Verify product_type field in all responses
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

# API base URL
API_BASE_URL = "http://127.0.0.1:8000/api/v1"


def test_api_connection():
    """Test if API server is running."""
    try:
        response = requests.get(
            f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=2
        )
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API server. Make sure it's running:")
        print("  python -m uvicorn app.api.main:app --reload")
        return False


def test_list_products_no_filter():
    """Test GET /api/v1/products returns all products."""
    print("\n1. Testing GET /api/v1/products (no filter)...")
    try:
        response = requests.get(f"{API_BASE_URL}/products", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        products = response.json()
        assert isinstance(products, list), "Response should be a list"
        print(f"   [OK] Retrieved {len(products)} products")

        # Verify all products have product_type field
        for product in products:
            assert "product_type" in product, "Product missing product_type field"
            assert product["product_type"] in [
                "RAW",
                "WIP",
                "FINISHED",
            ], f"Invalid product_type: {product['product_type']}"
        print("   [OK] All products have valid product_type field")
        return products
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        return []
    except Exception as e:
        print(f"   [ERROR] {e}")
        return []


def test_list_products_filter_raw():
    """Test GET /api/v1/products?product_type=RAW returns only RAW products."""
    print("\n2. Testing GET /api/v1/products?product_type=RAW...")
    try:
        response = requests.get(f"{API_BASE_URL}/products?product_type=RAW", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        products = response.json()
        assert isinstance(products, list), "Response should be a list"
        print(f"   [OK] Retrieved {len(products)} products")

        # Verify all are RAW
        for product in products:
            assert product["product_type"] == "RAW", (
                f"Expected RAW, got {product['product_type']} for {product.get('sku', 'unknown')}"
            )
        print("   [OK] All products are RAW type")
        return products
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        return []
    except Exception as e:
        print(f"   [ERROR] {e}")
        return []


def test_list_products_filter_wip():
    """Test GET /api/v1/products?product_type=WIP returns only WIP products."""
    print("\n3. Testing GET /api/v1/products?product_type=WIP...")
    try:
        response = requests.get(f"{API_BASE_URL}/products?product_type=WIP", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        products = response.json()
        assert isinstance(products, list), "Response should be a list"
        print(f"   [OK] Retrieved {len(products)} products")

        # Verify all are WIP
        for product in products:
            assert product["product_type"] == "WIP", (
                f"Expected WIP, got {product['product_type']} for {product.get('sku', 'unknown')}"
            )
        print("   [OK] All products are WIP type")
        return products
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        return []
    except Exception as e:
        print(f"   [ERROR] {e}")
        return []


def test_list_products_filter_finished():
    """Test GET /api/v1/products?product_type=FINISHED returns only FINISHED products."""
    print("\n4. Testing GET /api/v1/products?product_type=FINISHED...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/products?product_type=FINISHED", timeout=5
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        products = response.json()
        assert isinstance(products, list), "Response should be a list"
        print(f"   [OK] Retrieved {len(products)} products")

        # Verify all are FINISHED
        for product in products:
            assert product["product_type"] == "FINISHED", (
                f"Expected FINISHED, got {product['product_type']} for {product.get('sku', 'unknown')}"
            )
        print("   [OK] All products are FINISHED type")
        return products
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        return []
    except Exception as e:
        print(f"   [ERROR] {e}")
        return []


def test_create_product_with_type(product_type: str):
    """Test POST /api/v1/products with specific product_type."""
    print(f"\n5. Testing POST /api/v1/products with product_type={product_type}...")
    try:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        product_data = {
            "sku": f"TEST-{product_type}-{timestamp}",
            "name": f"Test {product_type} Product",
            "product_type": product_type,
            "base_unit": "KG",
            "is_active": True,
        }

        response = requests.post(
            f"{API_BASE_URL}/products", json=product_data, timeout=5
        )
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )
        product = response.json()
        assert product["product_type"] == product_type, (
            f"Expected {product_type}, got {product['product_type']}"
        )
        print(f"   [OK] Created {product_type} product: {product['sku']}")
        return product
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        return None
    except Exception as e:
        print(f"   [ERROR] {e}")
        return None


def test_update_product_type(product_id: str, new_type: str):
    """Test PUT /api/v1/products/{id} with product_type change."""
    print(
        f"\n6. Testing PUT /api/v1/products/{product_id} with product_type={new_type}..."
    )
    try:
        update_data = {"product_type": new_type}

        response = requests.put(
            f"{API_BASE_URL}/products/{product_id}", json=update_data, timeout=5
        )
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )
        product = response.json()
        assert product["product_type"] == new_type, (
            f"Expected {new_type}, got {product['product_type']}"
        )
        print(f"   [OK] Updated product type to {new_type}")
        return product
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        return None
    except Exception as e:
        print(f"   [ERROR] {e}")
        return None


def test_invalid_product_type():
    """Test POST /api/v1/products with invalid product_type."""
    print("\n7. Testing POST /api/v1/products with invalid product_type...")
    try:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        product_data = {
            "sku": f"TEST-INVALID-{timestamp}",
            "name": "Test Invalid Product",
            "product_type": "INVALID_TYPE",
            "base_unit": "KG",
        }

        response = requests.post(
            f"{API_BASE_URL}/products", json=product_data, timeout=5
        )
        # Should return validation error
        assert response.status_code == 422, (
            f"Expected 422 validation error, got {response.status_code}: {response.text}"
        )
        print("   [OK] Correctly rejected invalid product_type")
        return True
    except AssertionError as e:
        print(f"   [FAIL] {e}")
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False


def main():
    """Run all API verification tests."""
    print("=" * 80)
    print("API PRODUCT TYPE FILTERING VERIFICATION")
    print("=" * 80)

    # Test API connection
    if not test_api_connection():
        print("\n[ERROR] API server not available. Exiting.")
        return False

    results = {"passed": 0, "failed": 0}

    # Test list endpoints
    all_products = test_list_products_no_filter()
    if all_products:
        results["passed"] += 1
    else:
        results["failed"] += 1

    raw_products = test_list_products_filter_raw()
    if raw_products:
        results["passed"] += 1
    else:
        results["failed"] += 1

    wip_products = test_list_products_filter_wip()
    if wip_products:
        results["passed"] += 1
    else:
        results["failed"] += 1

    finished_products = test_list_products_filter_finished()
    if finished_products:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test create with different types
    test_raw = test_create_product_with_type("RAW")
    if test_raw:
        results["passed"] += 1
    else:
        results["failed"] += 1

    test_wip = test_create_product_with_type("WIP")
    if test_wip:
        results["passed"] += 1
    else:
        results["failed"] += 1

    test_finished = test_create_product_with_type("FINISHED")
    if test_finished:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test update product type
    if test_wip:
        updated = test_update_product_type(test_wip["id"], "FINISHED")
        if updated:
            results["passed"] += 1
        else:
            results["failed"] += 1

    # Test invalid product type
    if test_invalid_product_type():
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
        print("\n[SUCCESS] All API verification tests passed!")
        return True
    else:
        print(f"\n[FAILURE] {results['failed']} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
