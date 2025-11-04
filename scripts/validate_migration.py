#!/usr/bin/env python3
"""
Validation script for unified products migration.

Checks data integrity after migration:
- All raw_materials migrated to products
- All finished_goods migrated to products
- All formula_lines updated to use product_id
- All inventory_movements updated to use product_id
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.adapters.db.session import get_session


def validate_migration():
    """Validate the unified products migration."""
    db = get_session()
    inspector = inspect(db.bind)

    issues = []
    warnings = []

    print("=" * 80)
    print("UNIFIED PRODUCTS MIGRATION VALIDATION")
    print("=" * 80)

    # Check 1: Verify product_type column exists
    print("\n1. Checking product_type column...")
    try:
        columns = [col["name"] for col in inspector.get_columns("products")]
        if "product_type" not in columns:
            issues.append("products table missing product_type column")
            print("  ❌ FAIL: product_type column not found")
        else:
            print("  ✓ PASS: product_type column exists")
    except Exception as e:
        issues.append(f"Error checking products table: {e}")
        print(f"  ❌ FAIL: {e}")

    # Check 2: Verify all products have product_type set
    print("\n2. Checking product_type values...")
    try:
        null_types = db.execute(
            text(
                """
            SELECT COUNT(*) as cnt FROM products WHERE product_type IS NULL
        """
            )
        ).scalar()

        if null_types > 0:
            issues.append(f"{null_types} products have NULL product_type")
            print(f"  ❌ FAIL: {null_types} products with NULL product_type")
        else:
            print("  ✓ PASS: All products have product_type set")

        # Count by type
        type_counts = db.execute(
            text(
                """
            SELECT product_type, COUNT(*) as cnt
            FROM products
            GROUP BY product_type
        """
            )
        ).fetchall()

        print("  Product type distribution:")
        for ptype, count in type_counts:
            print(f"    - {ptype}: {count}")
    except Exception as e:
        issues.append(f"Error checking product_type values: {e}")
        print(f"  ❌ FAIL: {e}")

    # Check 3: Verify formula_lines use product_id
    print("\n3. Checking formula_lines structure...")
    try:
        if "formula_lines" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("formula_lines")]

            if "product_id" not in columns:
                issues.append("formula_lines table missing product_id column")
                print("  ❌ FAIL: product_id column not found")
            else:
                print("  ✓ PASS: product_id column exists")

            # Check for NULL product_ids
            null_refs = db.execute(
                text(
                    """
                SELECT COUNT(*) as cnt FROM formula_lines WHERE product_id IS NULL
            """
                )
            ).scalar()

            if null_refs > 0:
                issues.append(f"{null_refs} formula_lines have NULL product_id")
                print(f"  ❌ FAIL: {null_refs} formula_lines with NULL product_id")
            else:
                print("  ✓ PASS: All formula_lines have product_id")

            # Check foreign key integrity
            orphaned = db.execute(
                text(
                    """
                SELECT COUNT(*) as cnt
                FROM formula_lines fl
                LEFT JOIN products p ON fl.product_id = p.id
                WHERE p.id IS NULL
            """
                )
            ).scalar()

            if orphaned > 0:
                issues.append(
                    f"{orphaned} formula_lines reference non-existent products"
                )
                print(f"  ❌ FAIL: {orphaned} orphaned formula_line references")
            else:
                print("  ✓ PASS: All formula_lines reference valid products")
        else:
            warnings.append("formula_lines table does not exist")
            print("  ⚠ WARN: formula_lines table not found")
    except Exception as e:
        issues.append(f"Error checking formula_lines: {e}")
        print(f"  ❌ FAIL: {e}")

    # Check 4: Verify inventory_movements use product_id
    print("\n4. Checking inventory_movements structure...")
    try:
        if "inventory_movements" in inspector.get_table_names():
            columns = [
                col["name"] for col in inspector.get_columns("inventory_movements")
            ]

            if "product_id" not in columns:
                issues.append("inventory_movements table missing product_id column")
                print("  ❌ FAIL: product_id column not found")
            else:
                print("  ✓ PASS: product_id column exists")

            # Check for old item_type/item_id columns
            if "item_type" in columns or "item_id" in columns:
                warnings.append(
                    "inventory_movements still has item_type/item_id columns (legacy)"
                )
                print("  ⚠ WARN: Legacy item_type/item_id columns still present")

            # Check for NULL product_ids
            null_refs = db.execute(
                text(
                    """
                SELECT COUNT(*) as cnt FROM inventory_movements WHERE product_id IS NULL
            """
                )
            ).scalar()

            if null_refs > 0:
                issues.append(f"{null_refs} inventory_movements have NULL product_id")
                print(
                    f"  ❌ FAIL: {null_refs} inventory_movements with NULL product_id"
                )
            else:
                print("  ✓ PASS: All inventory_movements have product_id")

            # Check foreign key integrity
            orphaned = db.execute(
                text(
                    """
                SELECT COUNT(*) as cnt
                FROM inventory_movements im
                LEFT JOIN products p ON im.product_id = p.id
                WHERE p.id IS NULL
            """
                )
            ).scalar()

            if orphaned > 0:
                issues.append(
                    f"{orphaned} inventory_movements reference non-existent products"
                )
                print(f"  ❌ FAIL: {orphaned} orphaned inventory_movement references")
            else:
                print("  ✓ PASS: All inventory_movements reference valid products")
        else:
            warnings.append("inventory_movements table does not exist")
            print("  ⚠ WARN: inventory_movements table not found")
    except Exception as e:
        issues.append(f"Error checking inventory_movements: {e}")
        print(f"  ❌ FAIL: {e}")

    # Check 5: Verify migration mapping table
    print("\n5. Checking migration mapping...")
    try:
        if "product_migration_map" in inspector.get_table_names():
            map_count = db.execute(
                text(
                    """
                SELECT COUNT(*) as cnt FROM product_migration_map
            """
                )
            ).scalar()

            print(f"  ✓ PASS: Migration mapping table exists with {map_count} entries")

            # Count by legacy table
            legacy_counts = db.execute(
                text(
                    """
                SELECT legacy_table, COUNT(*) as cnt
                FROM product_migration_map
                GROUP BY legacy_table
            """
                )
            ).fetchall()

            print("  Legacy table migration counts:")
            for table, count in legacy_counts:
                print(f"    - {table}: {count}")
        else:
            warnings.append("product_migration_map table not found")
            print("  ⚠ WARN: Migration mapping table not found")
    except Exception as e:
        warnings.append(f"Error checking migration map: {e}")
        print(f"  ⚠ WARN: {e}")

    # Check 6: Verify inventory_lots work with all product types
    print("\n6. Checking inventory_lots integrity...")
    try:
        if "inventory_lots" in inspector.get_table_names():
            # Check for orphaned lots
            orphaned = db.execute(
                text(
                    """
                SELECT COUNT(*) as cnt
                FROM inventory_lots il
                LEFT JOIN products p ON il.product_id = p.id
                WHERE p.id IS NULL
            """
                )
            ).scalar()

            if orphaned > 0:
                issues.append(
                    f"{orphaned} inventory_lots reference non-existent products"
                )
                print(f"  ❌ FAIL: {orphaned} orphaned inventory_lot references")
            else:
                print("  ✓ PASS: All inventory_lots reference valid products")

            # Count lots by product type
            lots_by_type = db.execute(
                text(
                    """
                SELECT p.product_type, COUNT(*) as cnt
                FROM inventory_lots il
                JOIN products p ON il.product_id = p.id
                GROUP BY p.product_type
            """
                )
            ).fetchall()

            if lots_by_type:
                print("  Inventory lots by product type:")
                for ptype, count in lots_by_type:
                    print(f"    - {ptype}: {count}")
        else:
            warnings.append("inventory_lots table not found")
            print("  ⚠ WARN: inventory_lots table not found")
    except Exception as e:
        issues.append(f"Error checking inventory_lots: {e}")
        print(f"  ❌ FAIL: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    if issues:
        print(f"\n❌ FAILED: {len(issues)} critical issue(s) found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False
    else:
        print("\n✓ PASS: No critical issues found")

    if warnings:
        print(f"\n⚠ WARNINGS: {len(warnings)} warning(s):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")

    print("\n" + "=" * 80)
    return True


if __name__ == "__main__":
    success = validate_migration()
    sys.exit(0 if success else 1)
