# Unified Products Migration Guide

## Overview

The TPManuf system has been migrated from separate `raw_materials` and `finished_goods` tables to a unified `products` table with a `product_type` field. This enables seamless assembly operations throughout the manufacturing process (RAW → WIP → FINISHED).

## Migration Status

**Migration Script**: `db/alembic/versions/9472b39d71be_unified_products_migration.py`

**Status**: Ready for production deployment after testing on backup database.

## Schema Changes

### Product Table Extensions

The `products` table now includes:

1. **product_type** (String, indexed, default: 'RAW')
   - Values: `RAW`, `WIP`, `FINISHED`
   - Required field after migration

2. **Raw Material Fields** (nullable, for RAW type products):
   - `raw_material_code`: Legacy QB material code
   - `raw_material_group_id`: FK to raw_material_groups
   - `specific_gravity`, `vol_solid`, `solid_sg`, `wt_solid`
   - `usage_cost`, `usage_unit`
   - `restock_level`, `used_ytd`
   - `hazard`, `condition`, `msds_flag`
   - `altno1-5`: Alternative material codes
   - `last_movement_date`, `last_purchase_date`
   - `ean13_raw`: Legacy EAN
   - `xero_account`

3. **Finished Good Fields** (nullable, for FINISHED type products):
   - `formula_id`: FK to formulas
   - `formula_revision`: Formula revision number

### Foreign Key Changes

1. **FormulaLine**
   - Changed: `raw_material_id` → `product_id` (FK to `products.id`)
   - Backward compatibility: `raw_material` property returns `product`

2. **InventoryMovement**
   - Changed: `item_type` + `item_id` → `product_id` (FK to `products.id`)
   - Removed: `item_type` column (after migration)

## Migration Process

### Pre-Migration Checklist

1. **Backup Database**
   ```bash
   # SQLite
   cp tpmanuf.db tpmanuf.db.backup
   
   # PostgreSQL
   pg_dump tpmanuf > tpmanuf_backup.sql
   ```

2. **Verify Current State**
   ```bash
   alembic current
   ```

3. **Check for Existing Data**
   ```bash
   # Verify raw_materials and finished_goods tables exist
   python scripts/check_db.py
   ```

### Running the Migration

1. **Run Migration**
   ```bash
   alembic upgrade head
   ```

2. **Validate Migration**
   ```bash
   python scripts/validate_migration.py
   ```

3. **Verify Data Integrity**
   - Check product_type distribution
   - Verify formula_lines.product_id is set
   - Verify inventory_movements.product_id is set
   - Check migration mapping table

### Post-Migration Validation

1. **Data Checks**
   - All raw_materials migrated with product_type='RAW'
   - All finished_goods migrated with product_type='FINISHED'
   - No NULL product_type values
   - All foreign key references valid

2. **Functional Tests**
   ```bash
   pytest tests/test_unified_products.py -v
   pytest tests/test_wip_batching.py -v
   pytest tests/test_assembly_service.py -v
   ```

3. **API Tests**
   - Test product_type filtering
   - Test creating products with different types
   - Test assembly operations

## API Usage

### Listing Products by Type

```python
# List raw materials
GET /api/v1/products?product_type=RAW

# List WIP products
GET /api/v1/products?product_type=WIP

# List finished goods
GET /api/v1/products?product_type=FINISHED

# List all products
GET /api/v1/products
```

### Creating Products

```python
# Create raw material
POST /api/v1/products
{
  "sku": "RM-001",
  "name": "Raw Material",
  "product_type": "RAW",
  "raw_material_code": 1001,
  "specific_gravity": 1.2,
  "usage_cost": 5.50
}

# Create finished good
POST /api/v1/products
{
  "sku": "FG-001",
  "name": "Finished Good",
  "product_type": "FINISHED",
  "formula_id": "formula-uuid"
}
```

## Assembly Operations

### Multi-Stage Assembly

The unified structure supports multi-stage assembly:

1. **RAW → WIP**: Assemble raw materials into work-in-progress
   ```python
   POST /api/v1/assemblies/assemble
   {
     "parent_product_id": "wip-product-id",
     "parent_qty": 100.0,
     "reason": "BATCH_PRODUCTION"
   }
   ```

2. **WIP → FINISHED**: Assemble WIP into finished goods
   ```python
   POST /api/v1/assemblies/assemble
   {
     "parent_product_id": "finished-product-id",
     "parent_qty": 50.0,
     "reason": "FINAL_ASSEMBLY"
   }
   ```

3. **RAW → FINISHED**: Direct assembly (bypassing WIP)
   ```python
   POST /api/v1/assemblies/assemble
   {
     "parent_product_id": "finished-product-id",
     "parent_qty": 75.0,
     "reason": "DIRECT_PRODUCTION"
   }
   ```

### Batch Completion with WIP

```python
POST /api/v1/batches/{batch_id}/finish
{
  "qty_fg_kg": 95.0,
  "create_wip": true,  # Creates WIP product
  "notes": "First stage production"
}
```

## Rollback Plan

If migration issues occur:

1. **Restore Backup**
   ```bash
   # SQLite
   cp tpmanuf.db.backup tpmanuf.db
   
   # PostgreSQL
   psql tpmanuf < tpmanuf_backup.sql
   ```

2. **Rollback Migration**
   ```bash
   alembic downgrade -1
   ```

3. **Verify Rollback**
   - Check raw_materials and finished_goods tables restored
   - Verify original foreign key structure
   - Run tests

## Troubleshooting

### Common Issues

1. **NULL product_type after migration**
   - Run: `UPDATE products SET product_type='RAW' WHERE product_type IS NULL`
   - Re-validate migration

2. **Orphaned formula_lines**
   - Check migration mapping table
   - Manually update via SQL if needed

3. **Missing inventory_movements.product_id**
   - Migration script should handle this
   - Check for items not in migration map

## Benefits

1. **Simplified Schema**: Single products table for all material types
2. **Unified Assembly**: Support for multi-stage workflows (RAW→WIP→FINISHED)
3. **Consistent API**: Single product endpoint with filtering
4. **Better Traceability**: Unified inventory tracking
5. **Future-Proof**: Easier to add new product types if needed

## Support

For migration issues or questions:
- Check `scripts/validate_migration.py` output
- Review `db/alembic/versions/9472b39d71be_unified_products_migration.py`
- Check `product_migration_map` table for ID mappings


