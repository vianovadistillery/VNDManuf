# Complete Legacy Data Preservation

## Overview

This document explains how **ALL** fields and data from the original QuickBASIC `acstk` file are preserved in the modern TPManuf system.

## Solution Architecture

The solution uses a **dual-approach**:

1. **Normalized Modern Schema** - For active operations (products, inventory, pricing)
2. **Legacy Preservation Table** - Stores 100% of original legacy data for reference

## Legacy Data Preservation Table

### Table: `legacy_acstk_data`

This table stores **every single field** from the original acstk file:

#### Product Description Fields (13 fields)
- `legacy_no` - Original record number
- `legacy_search` - Product code/SKU (search field)
- `ean13` - EAN-13 barcode
- `desc1` - Primary description
- `desc2` - Secondary description
- `legacy_suplr` - Supplier code
- `size` - Size information
- `legacy_unit` - Unit code
- `pack` - Package quantity
- `dgflag` - Dangerous goods flag
- `form` - Form code
- `pkge` - Package type
- `label` - Label type
- `manu` - Manufacturer code
- `legacy_active` - Active status ('Y'/'N')

#### Financial Description Fields (7 fields)
- `taxinc` - Tax included flag
- `salestaxcde` - Sales tax code
- `purcost` - Purchase cost
- `purtax` - Purchase tax
- `wholesalecost` - Wholesale cost
- `disccdeone` - Discount code 1
- `disccdetwo` - Discount code 2

#### Customer Price Codes (7 fields)
- `wholesalecde`, `retailcde`, `countercde`, `tradecde`, `contractcde`, `industrialcde`, `distributorcde` - Pricing tier codes

#### Customer Prices (6 fields)
- `retail`, `counter`, `trade`, `contract`, `industrial`, `distributor` - Actual price values

#### Stock Holding Fields (10 fields)
- `cogs` - Cost of goods sold
- `gpc` - Gross profit cost
- `rmc` - Raw material cost
- `gpr` - Gross profit ratio
- `soh` - Stock on hand
- `sohv` - Stock on hand value
- `sip` - Stock in progress
- `soo` - Stock on order
- `sold` - Quantity sold
- `legacy_date` - Last transaction date (YYYYMMDD)

#### Additional Fields (7 fields)
- `bulk` - Bulk quantity
- `lid` - Lid type
- `pbox` - Per box quantity
- `boxlbl` - Box label type
- `suplr4stdcost`, `search4stdcost` - Standard cost references

#### Metadata (2 fields)
- `imported_at` - When data was imported
- `notes` - Import notes

**Total: 53 fields preserved** - Every single field from the original 256-byte record!

## How It Works

### 1. Dual Storage

When legacy data is imported:

```python
# Create normalized product
product = Product(sku=record.search, name=record.product_name, ...)

# Store EVERY field in legacy table
legacy_data = LegacyAcstkData(
    product_id=product.id,
    legacy_no=record.no,
    legacy_search=record.search,
    ean13=record.ean13,
    desc1=record.desc1,
    # ... ALL 53 fields preserved
)
```

### 2. Complete Preservation

- **Original record number**: `legacy_no`
- **All descriptions**: `desc1`, `desc2`
- **All financials**: `purcost`, `purtax`, `wholesalecost`
- **All price tiers**: 6 different customer prices preserved
- **All stock metrics**: `soh`, `sip`, `soo`, `sohv`, `cogs`, etc.
- **All codes**: Price codes, discount codes, tax codes
- **All metadata**: Date, bulk, pack, form, size, etc.

### 3. Bidirectional Access

You can:
- Query modern normalized data for operations
- Query legacy data for historical reference
- Join them together for complete migration tracking

```sql
-- Get modern product
SELECT * FROM products WHERE sku = 'NWG-200';

-- Get ALL original fields
SELECT * FROM legacy_acstk_data WHERE legacy_search = 'NWG-200';

-- Join for complete view
SELECT p.*, l.*
FROM products p
JOIN legacy_acstk_data l ON p.id = l.product_id
WHERE p.sku = 'NWG-200';
```

## Migration Script

### Usage

```bash
python scripts/migrate_acstk.py legacy_data/acstk.acf
```

### What It Does

1. **Parses** the 256-byte random access file
2. **Creates** modern products in normalized schema
3. **Preserves** every field in `legacy_acstk_data` table
4. **Creates** inventory lots from `soh`
5. **Creates** price list items from pricing tiers
6. **Creates** initial inventory transactions
7. **Tracks** supplier relationships
8. **Creates** pack units and conversions

### Output

- ✅ All products migrated
- ✅ All inventory preserved as lots
- ✅ All pricing tiers created
- ✅ Complete legacy data stored
- ✅ Zero data loss

## Data Integrity

### Foreign Key Relationships

```python
legacy_acstk_data.product_id → products.id
```

Each legacy record is linked to its modern product, ensuring:
- ✅ No orphaned data
- ✅ Bidirectional access
- ✅ Complete audit trail

### Data Types

- **Strings**: Preserved with original lengths
- **Numbers**: Converted to appropriate `Numeric`/`Integer` types
- **Dates**: Preserved as strings (YYYYMMDD) in `legacy_date`
- **Currency**: Stored as `Numeric(18, 4)` to match QuickBASIC CURRENCY
- **Singles**: Stored as `Numeric(10, 2)` for monetary values

## Benefits

### 1. Zero Data Loss
- Every single field preserved
- Complete historical record
- Reference for business rules

### 2. Dual System
- Modern normalized system for operations
- Legacy data for reference and migration validation

### 3. Audit Trail
- `imported_at` timestamp
- Links to original product
- Migration notes

### 4. Query Flexibility
```sql
-- Query by modern SKU
SELECT p.* FROM products p
JOIN legacy_acstk_data l ON p.id = l.product_id
WHERE p.sku = 'NWG-200';

-- Query by legacy SKU
SELECT p.* FROM products p
JOIN legacy_acstk_data l ON p.id = l.product_id
WHERE l.legacy_search = 'NWG-200';

-- Get all stock metrics
SELECT
    l.legacy_search as legacy_sku,
    p.sku as modern_sku,
    l.soh as legacy_stock_on_hand,
    l.sohv as legacy_stock_value,
    l.sip as legacy_stock_in_progress,
    l.soo as legacy_stock_on_order,
    l.cogs as legacy_cogs,
    l.gpr as legacy_gross_profit_ratio,
    SUM(inv.quantity_kg) as modern_stock_on_hand
FROM legacy_acstk_data l
JOIN products p ON l.product_id = p.id
LEFT JOIN inventory_lots inv ON p.id = inv.product_id AND inv.is_active = TRUE
GROUP BY l.legacy_search, p.sku, l.soh, l.sohv, l.sip, l.soo, l.cogs, l.gpr;
```

## Examples

### Get Complete Product Data

```python
from app.adapters.db.models import Product, LegacyAcstkData
from app.adapters.db import get_db

def get_complete_product_data(sku: str):
    db = next(get_db())

    # Get modern product
    product = db.query(Product).filter(Product.sku == sku).first()

    # Get ALL legacy fields
    legacy = db.query(LegacyAcstkData).filter(
        LegacyAcstkData.product_id == product.id
    ).first()

    return {
        "modern": product,
        "legacy": legacy,
        "original_soh": legacy.soh,
        "original_purcost": legacy.purcost,
        "original_gpr": legacy.gpr,
        # ... all fields accessible
    }
```

## Migration Checklist

- [x] Create `legacy_acstk_data` table
- [x] Generate Alembic migration
- [x] Apply migration to database
- [x] Create parser for 256-byte format
- [x] Create migration script
- [x] Preserve all 53 fields
- [x] Link to modern products
- [x] Maintain referential integrity
- [x] Document solution

## Summary

✅ **ALL fields preserved** - Every single field from the original 256-byte record
✅ **Zero data loss** - Complete historical record maintained
✅ **Dual system** - Modern operations + legacy reference
✅ **Query flexibility** - Access by modern or legacy identifiers
✅ **Complete migration** - Products, inventory, pricing, all tiers

**Result**: You now have a complete, lossless migration preserving every piece of data from your original QuickBASIC system.
