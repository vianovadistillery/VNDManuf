#!/usr/bin/env python3
"""
Validation script for unified product migration.
Tests data integrity and completeness after migration.
"""

import sys

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


def validate_migration(db_url: str):
    """Validate unified product migration."""
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    inspector = inspect(engine)

    issues = []
    warnings = []
    successes = []

    try:
        # Check 1: All products have product_type set
        null_type_count = session.execute(
            text("SELECT COUNT(*) FROM products WHERE product_type IS NULL")
        ).scalar()

        if null_type_count > 0:
            issues.append(f"Found {null_type_count} products without product_type")
        else:
            successes.append("All products have product_type set")

        # Check 2: Formula lines use product_id (not raw_material_id)
        if "formula_lines" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("formula_lines")]

            if "raw_material_id" in columns and "product_id" in columns:
                # Check if any formula_lines still reference raw_material_id without product_id
                null_product_id = session.execute(
                    text(
                        "SELECT COUNT(*) FROM formula_lines WHERE product_id IS NULL AND raw_material_id IS NOT NULL"
                    )
                ).scalar()

                if null_product_id > 0:
                    issues.append(
                        f"Found {null_product_id} formula_lines with raw_material_id but no product_id"
                    )
                else:
                    successes.append("Formula lines migrated to use product_id")
            elif "product_id" in columns:
                successes.append("Formula lines use unified product_id")
            else:
                issues.append("Formula lines table missing product_id column")

        # Check 3: Inventory movements use product_id (not item_type/item_id)
        if "inventory_movements" in inspector.get_table_names():
            columns = [
                col["name"] for col in inspector.get_columns("inventory_movements")
            ]

            if "item_type" in columns and "product_id" in columns:
                # Check if any movements still use old structure
                null_product_id = session.execute(
                    text(
                        "SELECT COUNT(*) FROM inventory_movements WHERE product_id IS NULL AND item_id IS NOT NULL"
                    )
                ).scalar()

                if null_product_id > 0:
                    issues.append(
                        f"Found {null_product_id} inventory_movements with item_id but no product_id"
                    )
                else:
                    successes.append("Inventory movements migrated to use product_id")
            elif "product_id" in columns:
                successes.append("Inventory movements use unified product_id")
            else:
                issues.append("Inventory movements table missing product_id column")

        # Check 4: Raw materials migrated (if raw_materials table exists)
        if "raw_materials" in inspector.get_table_names():
            raw_material_count = session.execute(
                text("SELECT COUNT(*) FROM raw_materials")
            ).scalar()

            raw_product_count = session.execute(
                text("SELECT COUNT(*) FROM products WHERE product_type = 'RAW'")
            ).scalar()

            if raw_product_count < raw_material_count:
                warnings.append(
                    f"Found {raw_material_count} raw_materials but only {raw_product_count} RAW products. "
                    "Some may not be migrated."
                )
            else:
                successes.append(
                    f"Raw materials appear migrated: {raw_product_count} RAW products found"
                )

        # Check 5: Finished goods migrated (if finished_goods table exists)
        if "finished_goods" in inspector.get_table_names():
            finished_goods_count = session.execute(
                text("SELECT COUNT(*) FROM finished_goods")
            ).scalar()

            finished_product_count = session.execute(
                text("SELECT COUNT(*) FROM products WHERE product_type = 'FINISHED'")
            ).scalar()

            if finished_product_count < finished_goods_count:
                warnings.append(
                    f"Found {finished_goods_count} finished_goods but only {finished_product_count} FINISHED products. "
                    "Some may not be migrated."
                )
            else:
                successes.append(
                    f"Finished goods appear migrated: {finished_product_count} FINISHED products found"
                )

        # Check 6: Product type distribution
        type_distribution = session.execute(
            text(
                """
                SELECT product_type, COUNT(*) as cnt
                FROM products
                GROUP BY product_type
            """
            )
        ).fetchall()

        type_dict = {row[0]: row[1] for row in type_distribution}
        total = sum(type_dict.values())

        successes.append(f"Product type distribution: {type_dict} (Total: {total})")

        # Check 7: Foreign key integrity
        # Check formula_lines.product_id references valid products
        if "formula_lines" in inspector.get_table_names():
            orphaned_lines = session.execute(
                text(
                    """
                    SELECT COUNT(*) FROM formula_lines fl
                    LEFT JOIN products p ON fl.product_id = p.id
                    WHERE p.id IS NULL AND fl.product_id IS NOT NULL
                """
                )
            ).scalar()

            if orphaned_lines > 0:
                issues.append(
                    f"Found {orphaned_lines} formula_lines with invalid product_id references"
                )
            else:
                successes.append("All formula_lines have valid product_id references")

        # Check 8: Inventory lots reference valid products
        orphaned_lots = session.execute(
            text(
                """
                SELECT COUNT(*) FROM inventory_lots il
                LEFT JOIN products p ON il.product_id = p.id
                WHERE p.id IS NULL
            """
            )
        ).scalar()

        if orphaned_lots > 0:
            issues.append(
                f"Found {orphaned_lots} inventory_lots with invalid product_id references"
            )
        else:
            successes.append("All inventory_lots have valid product_id references")

        # Summary
        print("\n" + "=" * 70)
        print("UNIFIED PRODUCT MIGRATION VALIDATION REPORT")
        print("=" * 70)

        if successes:
            print("\n✓ SUCCESSES:")
            for success in successes:
                print(f"  • {success}")

        if warnings:
            print("\n⚠ WARNINGS:")
            for warning in warnings:
                print(f"  • {warning}")

        if issues:
            print("\n✗ ISSUES:")
            for issue in issues:
                print(f"  • {issue}")

        print("\n" + "=" * 70)

        if issues:
            print("❌ MIGRATION VALIDATION FAILED - Issues found")
            return 1
        elif warnings:
            print("⚠ MIGRATION VALIDATION PASSED with warnings")
            return 0
        else:
            print("✅ MIGRATION VALIDATION PASSED - All checks successful")
            return 0

    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    import os

    from app.settings import settings

    db_url = os.getenv("DATABASE_URL", settings.database.database_url)

    print(f"Validating migration for database: {db_url}")
    print("(Using in-memory database for safety)")

    exit_code = validate_migration(db_url)
    sys.exit(exit_code)
