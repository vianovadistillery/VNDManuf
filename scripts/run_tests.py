"""Run all tests and generate coverage report."""

import subprocess
import sys


def run_tests():
    """Run pytest with coverage and generate report."""

    print("Running TPManuf test suite...")
    print("=" * 60)

    # Run tests with coverage
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=60",  # 60% minimum coverage
        "-W",
        "ignore::UserWarning",  # Suppress warnings
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n[SUCCESS] All tests passed!")
        print("\nCoverage report: htmlcov/index.html")
    else:
        print("\n[FAILURE] Some tests failed. Check output above.")

    return result.returncode


def run_specific_tests(test_pattern: str):
    """Run specific test pattern."""
    print(f"Running tests matching: {test_pattern}")

    cmd = ["pytest", "tests/", "-v", "-k", test_pattern]
    result = subprocess.run(cmd)

    return result.returncode


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run TPManuf test suite")
    parser.add_argument(
        "--pattern", type=str, help="Run tests matching pattern (pytest -k)"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )

    args = parser.parse_args()

    if args.pattern:
        exit_code = run_specific_tests(args.pattern)
    else:
        exit_code = run_tests()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
