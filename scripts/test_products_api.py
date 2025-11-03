"""Test products API endpoint."""

import json

import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

print("Testing Products API...")
print("=" * 50)

# Test 1: Get all products
try:
    response = requests.get(f"{API_BASE_URL}/products/", timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response type: {type(data)}")
        if isinstance(data, list):
            print(f"Got {len(data)} products")
            if len(data) > 0:
                print("\nFirst product:")
                print(json.dumps(data[0], indent=2, default=str))
        else:
            print(
                f"Response structure: {list(data.keys()) if isinstance(data, dict) else 'unknown'}"
            )
            print(json.dumps(data, indent=2, default=str)[:500])
    else:
        print(f"Error: {response.text}")
except requests.exceptions.ConnectionError:
    print(
        "API server is not running. Please start it with: uvicorn app.api.main:app --reload"
    )
except Exception as e:
    print(f"Error: {e}")

# Test 2: Get products by type
print("\n" + "=" * 50)
print("Testing filtered products (product_type=RAW)...")
try:
    response = requests.get(
        f"{API_BASE_URL}/products/", params={"product_type": "RAW"}, timeout=5
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Got {len(data)} RAW products")
except Exception as e:
    print(f"Error: {e}")
