#!/usr/bin/env python3
"""
Master verification script for post-migration testing.

Orchestrates all verification test scripts and reports results.
"""

import subprocess
import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Test scripts to run
TEST_SCRIPTS = [
    {
        "name": "API Product Type Filtering",
        "script": "scripts/test_api_product_type_filtering.py",
        "requires_api": True,
        "description": "Test API endpoints with product_type filtering",
    },
    {
        "name": "Real Migrated Data",
        "script": "scripts/test_with_real_migrated_data.py",
        "requires_api": False,
        "description": "Test operations with migrated products",
    },
    {
        "name": "Error Cases",
        "script": "scripts/test_error_cases.py",
        "requires_api": False,
        "description": "Test error handling and validation",
    },
    {
        "name": "Batch Production Integration",
        "script": "scripts/test_batch_production_integration.py",
        "requires_api": False,
        "description": "Test batch workflows with WIP creation",
    },
]


def check_api_server():
    """Check if API server is running."""
    try:
        import requests

        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_api_server():
    """Start API server in background."""
    print("\n[INFO] Starting API server...")
    try:
        # Use subprocess to start server
        # Note: In production, server should be managed separately
        print("   [INFO] Please start API server manually:")
        print("   python -m uvicorn app.api.main:app --reload")
        return False
    except Exception as e:
        print(f"   [ERROR] Failed to start server: {e}")
        return False


def run_test_script(script_path: str, name: str):
    """Run a test script and return success status."""
    print(f"\n{'=' * 80}")
    print(f"Running: {name}")
    print(f"{'=' * 80}")

    script_full_path = project_root / script_path

    if not script_full_path.exists():
        print(f"[ERROR] Script not found: {script_path}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_full_path)],
            cwd=str(project_root),
            capture_output=False,  # Show output in real-time
            timeout=300,  # 5 minute timeout per script
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Script timed out: {name}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to run script: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 80)
    print("POST-MIGRATION VERIFICATION TEST SUITE")
    print("=" * 80)
    print(f"Project Root: {project_root}")
    print(f"Python: {sys.executable}")
    print("=" * 80)

    results = {"passed": [], "failed": [], "skipped": []}

    # Check API server status
    api_running = check_api_server()
    if not api_running:
        print("\n[WARNING] API server not running")
        print("   Some tests may be skipped")
        print("   Start server with: python -m uvicorn app.api.main:app --reload")

    # Run each test script
    for test in TEST_SCRIPTS:
        # Check if API is required
        if test["requires_api"] and not api_running:
            print(f"\n[SKIP] {test['name']} - API server not running")
            results["skipped"].append(test["name"])
            continue

        print(f"\n[RUNNING] {test['name']}")
        print(f"          {test['description']}")

        success = run_test_script(test["script"], test["name"])

        if success:
            results["passed"].append(test["name"])
            print(f"\n[PASS] {test['name']}")
        else:
            results["failed"].append(test["name"])
            print(f"\n[FAIL] {test['name']}")

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Passed: {len(results['passed'])}/{len(TEST_SCRIPTS)}")
    print(f"Failed: {len(results['failed'])}/{len(TEST_SCRIPTS)}")
    print(f"Skipped: {len(results['skipped'])}/{len(TEST_SCRIPTS)}")

    if results["passed"]:
        print("\nPassed tests:")
        for name in results["passed"]:
            print(f"  [OK] {name}")

    if results["failed"]:
        print("\nFailed tests:")
        for name in results["failed"]:
            print(f"  [FAIL] {name}")

    if results["skipped"]:
        print("\nSkipped tests:")
        for name in results["skipped"]:
            print(f"  [SKIP] {name}")

    # Final status
    print("\n" + "=" * 80)
    if len(results["failed"]) == 0 and len(results["passed"]) > 0:
        print("[SUCCESS] All tests passed!")
        return True
    elif len(results["failed"]) > 0:
        print(f"[FAILURE] {len(results['failed'])} test(s) failed")
        return False
    else:
        print("[PARTIAL] Some tests skipped (API server not running)")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
