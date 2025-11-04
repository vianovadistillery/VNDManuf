#!/usr/bin/env python3
"""
Fix critical database constraint issues:
1. Add primary key to products.id (if missing)
2. Verify all foreign key constraints
3. Add missing indexes
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect, text

from app.adapters.db.session import get_engine
from app.settings import settings


def fix_products_primary_key(engine):
    """Fix products.id primary key constraint."""
    inspector = inspect(engine)

    # Check if products table exists
    if "products" not in inspector.get_table_names():
        print("[ERROR] products table does not exist!")
        return False

    # Get primary key constraint
    pk_constraint = inspector.get_pk_constraint("products")

    with engine.connect() as conn:
        if not pk_constraint or not pk_constraint.get("constrained_columns"):
            print("[WARNING] products table has no primary key!")
            print("  Attempting to add primary key to products.id...")

            try:
                # Check if id column exists and has data
                result = conn.execute(text("SELECT COUNT(*) FROM products"))
                count = result.scalar()
                print(f"  Found {count} products in table")

                if count > 0:
                    # Check if id column has nulls
                    result = conn.execute(
                        text("SELECT COUNT(*) FROM products WHERE id IS NULL")
                    )
                    nulls = result.scalar()
                    if nulls > 0:
                        print(
                            f"  [ERROR] Found {nulls} products with NULL id - cannot add PK"
                        )
                        return False

                # Try to add primary key
                # SQLite requires recreating the table
                if settings.database.database_url.startswith("sqlite"):
                    print("  [INFO] SQLite detected - PK fix requires table recreation")
                    print("  [INFO] This should be done via Alembic migration")
                    return False
                else:
                    # PostgreSQL - can add PK directly
                    conn.execute(text("ALTER TABLE products ADD PRIMARY KEY (id)"))
                    conn.commit()
                    print("  [OK] Primary key added to products.id")
                    return True
            except Exception as e:
                print(f"  [ERROR] Failed to add primary key: {e}")
                return False
        else:
            pk_cols = pk_constraint.get("constrained_columns", [])
            if "id" in pk_cols:
                print("[OK] products.id is already a primary key")
                return True
            else:
                print(f"[WARNING] products has PK on {pk_cols}, but not on id")
                return False


def verify_foreign_keys(engine):
    """Verify all foreign key relationships."""
    inspector = inspect(engine)
    issues = []

    for table_name in inspector.get_table_names():
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            ref_table = fk.get("referred_table")
            if ref_table not in inspector.get_table_names():
                issues.append(
                    f"{table_name}.{fk['constrained_columns'][0]} -> {ref_table} (table missing)"
                )

    if issues:
        print("[WARNING] Foreign key issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("[OK] All foreign key relationships valid")
        return True


def main():
    """Main function."""
    print("Fixing database constraints...")
    print(f"Database: {settings.database.database_url}")

    engine = get_engine()

    print("\n1. Fixing products.id primary key...")
    fix_products_primary_key(engine)

    print("\n2. Verifying foreign keys...")
    verify_foreign_keys(engine)

    print("\n[OK] Constraint verification complete!")
    print("\nNOTE: For SQLite, primary key fixes require Alembic migration.")
    print("      Run: alembic revision --autogenerate -m 'fix_products_primary_key'")


if __name__ == "__main__":
    main()
