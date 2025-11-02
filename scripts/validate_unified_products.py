"""Validation script for unified products migration."""

import sys
from sqlalchemy import text
from app.adapters.db import get_db
from app.adapters.db.models import Product, FormulaLine, InventoryMovement, InventoryLot


def validate_product_types(db):
    """Validate all products have product_type set."""
    print("Validating product types...")
    
    # Check for products without product_type
    null_type_query = text("SELECT COUNT(*) FROM products WHERE product_type IS NULL")
    null_count = db.execute(null_type_query).scalar()
    
    if null_count > 0:
        print(f"ERROR: {null_count} products have NULL product_type")
        return False
    
    # Check distribution
    type_query = text("""
        SELECT product_type, COUNT(*) as count
        FROM products
        GROUP BY product_type
    """)
    results = db.execute(type_query).fetchall()
    
    print("Product type distribution:")
    for row in results:
        print(f"  {row.product_type}: {row.count}")
    
    return True


def validate_formula_lines(db):
    """Validate formula_lines reference products."""
    print("\nValidating formula_lines...")
    
    # Check for formula_lines with NULL product_id
    null_product_query = text("SELECT COUNT(*) FROM formula_lines WHERE product_id IS NULL")
    null_count = db.execute(null_product_query).scalar()
    
    if null_count > 0:
        print(f"ERROR: {null_count} formula_lines have NULL product_id")
        return False
    
    # Check for formula_lines referencing non-existent products
    invalid_product_query = text("""
        SELECT COUNT(*) 
        FROM formula_lines fl
        LEFT JOIN products p ON fl.product_id = p.id
        WHERE p.id IS NULL
    """)
    invalid_count = db.execute(invalid_product_query).scalar()
    
    if invalid_count > 0:
        print(f"ERROR: {invalid_count} formula_lines reference non-existent products")
        return False
    
    # Check for formula_lines still referencing raw_materials table
    try:
        raw_material_query = text("""
            SELECT COUNT(*) 
            FROM formula_lines 
            WHERE raw_material_id IS NOT NULL
        """)
        raw_material_count = db.execute(raw_material_query).scalar()
        
        if raw_material_count > 0:
            print(f"WARNING: {raw_material_count} formula_lines still have raw_material_id (legacy column)")
        else:
            print("All formula_lines use product_id ✓")
    except Exception:
        # raw_material_id column may not exist
        print("formula_lines table structure verified ✓")
    
    return True


def validate_inventory_movements(db):
    """Validate inventory_movements reference products."""
    print("\nValidating inventory_movements...")
    
    # Check for movements with NULL product_id
    null_product_query = text("SELECT COUNT(*) FROM inventory_movements WHERE product_id IS NULL")
    null_count = db.execute(null_product_query).scalar()
    
    if null_count > 0:
        print(f"ERROR: {null_count} inventory_movements have NULL product_id")
        return False
    
    # Check for movements referencing non-existent products
    invalid_product_query = text("""
        SELECT COUNT(*) 
        FROM inventory_movements im
        LEFT JOIN products p ON im.product_id = p.id
        WHERE p.id IS NULL
    """)
    invalid_count = db.execute(invalid_product_query).scalar()
    
    if invalid_count > 0:
        print(f"ERROR: {invalid_count} inventory_movements reference non-existent products")
        return False
    
    # Check for legacy item_type/item_id columns
    try:
        legacy_query = text("""
            SELECT COUNT(*) 
            FROM inventory_movements 
            WHERE item_type IS NOT NULL OR item_id IS NOT NULL
        """)
        legacy_count = db.execute(legacy_query).scalar()
        
        if legacy_count > 0:
            print(f"WARNING: {legacy_count} inventory_movements still have item_type/item_id (legacy columns)")
        else:
            print("All inventory_movements use product_id ✓")
    except Exception:
        # Columns may not exist
        print("inventory_movements table structure verified ✓")
    
    return True


def validate_inventory_lots(db):
    """Validate inventory_lots reference products."""
    print("\nValidating inventory_lots...")
    
    # Check for lots with NULL product_id
    null_product_query = text("SELECT COUNT(*) FROM inventory_lots WHERE product_id IS NULL")
    null_count = db.execute(null_product_query).scalar()
    
    if null_count > 0:
        print(f"ERROR: {null_count} inventory_lots have NULL product_id")
        return False
    
    # Check for lots referencing non-existent products
    invalid_product_query = text("""
        SELECT COUNT(*) 
        FROM inventory_lots il
        LEFT JOIN products p ON il.product_id = p.id
        WHERE p.id IS NULL
    """)
    invalid_count = db.execute(invalid_product_query).scalar()
    
    if invalid_count > 0:
        print(f"ERROR: {invalid_count} inventory_lots reference non-existent products")
        return False
    
    print("All inventory_lots reference valid products ✓")
    return True


def validate_migration_mapping(db):
    """Validate migration mapping table exists and has data."""
    print("\nValidating migration mapping...")
    
    try:
        map_query = text("""
            SELECT legacy_table, COUNT(*) as count
            FROM product_migration_map
            GROUP BY legacy_table
        """)
        results = db.execute(map_query).fetchall()
        
        if len(results) == 0:
            print("WARNING: No migration mappings found (may be pre-migration)")
        else:
            print("Migration mapping summary:")
            for row in results:
                print(f"  {row.legacy_table}: {row.count} records migrated")
        
        return True
    except Exception as e:
        print(f"WARNING: Could not access migration mapping table: {e}")
        return True  # Not critical if table doesn't exist yet


def validate_data_integrity(db):
    """Run overall data integrity checks."""
    print("\n" + "="*50)
    print("DATA INTEGRITY VALIDATION")
    print("="*50)
    
    all_valid = True
    
    all_valid &= validate_product_types(db)
    all_valid &= validate_formula_lines(db)
    all_valid &= validate_inventory_movements(db)
    all_valid &= validate_inventory_lots(db)
    all_valid &= validate_migration_mapping(db)
    
    print("\n" + "="*50)
    if all_valid:
        print("✓ All validations passed!")
    else:
        print("✗ Some validations failed. Please review errors above.")
    print("="*50)
    
    return all_valid


def main():
    """Main validation function."""
    db = next(get_db())
    try:
        success = validate_data_integrity(db)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: Validation failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

