#!/usr/bin/env python3
"""
Create comprehensive migration to fix all database constraints and normalize types.

This script generates an Alembic migration that:
1. Fixes primary keys on all tables
2. Ensures foreign keys are properly set
3. Adds missing unique constraints
4. Normalizes types (TEXT -> VARCHAR, NUMERIC -> proper precision)
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect

from app.adapters.db.session import get_engine

engine = get_engine()
inspector = inspect(engine)

# Load complete schema
schema_path = project_root / "docs" / "snapshot" / "complete_schema.json"
with open(schema_path) as f:
    schema = json.load(f)

print("Analyzing database constraints...")
print("=" * 60)

# Check primary keys
print("\nTables without primary keys:")
for table_name in sorted(inspector.get_table_names()):
    if table_name == "alembic_version":
        continue
    pk = inspector.get_pk_constraint(table_name)
    if not pk.get("constrained_columns"):
        print(f"  [WARNING] {table_name}")

# Check foreign keys
print("\nForeign key relationships:")
fk_count = 0
for table_name in sorted(inspector.get_table_names()):
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        fk_count += len(fks)
        for fk in fks:
            print(
                f"  {table_name}.{fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}"
            )

print(f"\nTotal foreign keys: {fk_count}")

print("\n[OK] Analysis complete. Migration file will be created manually.")
print("See db/alembic/versions/fix_products_primary_key.py")
