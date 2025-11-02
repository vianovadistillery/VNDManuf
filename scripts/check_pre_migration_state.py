#!/usr/bin/env python3
"""Check database state before unified products migration."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.settings import settings

engine = create_engine(settings.database.database_url)
inspector = inspect(engine)

print("=" * 80)
print("PRE-MIGRATION STATE CHECK")
print("=" * 80)

# Check tables
tables = inspector.get_table_names()
print(f"\n1. Tables exist:")
print(f"   - raw_materials: {'raw_materials' in tables}")
print(f"   - finished_goods: {'finished_goods' in tables}")
print(f"   - products: {'products' in tables}")
print(f"   - formula_lines: {'formula_lines' in tables}")
print(f"   - inventory_movements: {'inventory_movements' in tables}")

# Check data counts
with engine.connect() as conn:
    raw_count = conn.execute(text("SELECT COUNT(*) FROM raw_materials")).scalar()
    fg_count = conn.execute(text("SELECT COUNT(*) FROM finished_goods")).scalar()
    prod_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
    fl_count = conn.execute(text("SELECT COUNT(*) FROM formula_lines")).scalar()
    
    print(f"\n2. Data counts:")
    print(f"   - raw_materials: {raw_count}")
    print(f"   - finished_goods: {fg_count}")
    print(f"   - products: {prod_count}")
    print(f"   - formula_lines: {fl_count}")

# Check products table structure
prod_cols = [c['name'] for c in inspector.get_columns('products')]
print(f"\n3. Products table columns:")
print(f"   - product_type: {'product_type' in prod_cols}")
print(f"   - raw_material_code: {'raw_material_code' in prod_cols}")
print(f"   - formula_id: {'formula_id' in prod_cols}")

# Check formula_lines structure
fl_cols = [c['name'] for c in inspector.get_columns('formula_lines')]
print(f"\n4. Formula_lines table columns:")
print(f"   - product_id: {'product_id' in fl_cols}")
print(f"   - raw_material_id: {'raw_material_id' in fl_cols}")

# Check inventory_movements structure
if 'inventory_movements' in tables:
    im_cols = [c['name'] for c in inspector.get_columns('inventory_movements')]
    print(f"\n5. Inventory_movements table columns:")
    print(f"   - product_id: {'product_id' in im_cols}")
    print(f"   - item_type: {'item_type' in im_cols}")
    print(f"   - item_id: {'item_id' in im_cols}")

# Check current product types
with engine.connect() as conn:
    if 'product_type' in prod_cols:
        type_counts = conn.execute(text("""
            SELECT product_type, COUNT(*) 
            FROM products 
            GROUP BY product_type
        """)).fetchall()
        print(f"\n6. Product type distribution:")
        for ptype, count in type_counts:
            print(f"   - {ptype}: {count}")
        null_count = conn.execute(text("SELECT COUNT(*) FROM products WHERE product_type IS NULL")).scalar()
        if null_count > 0:
            print(f"   - NULL: {null_count}")

print("\n" + "=" * 80)
print("Migration ready to run: 9472b39d71be_unified_products_migration")
print("=" * 80)

