# Product Extension Summary

## Changes Made

### 1. Extended Product Model

Added comprehensive fields to match TPManuf legacy system:

#### Product Identification
- `ean13` - EAN-13 barcode
- `supplier_id` - Link to suppliers table

#### Physical Properties  
- `size` - Size information
- `base_unit` - Unit of measure (KG, LT, EA)
- `pack` - Package quantity
- `density_kg_per_l` - For L to kg conversions (existing)
- `abv_percent` - ABV as % v/v (existing)

#### Product Classifications
- `dgflag` - Dangerous goods flag
- `form` - Form code
- `pkge` - Package type
- `label` - Label type
- `manu` - Manufacturer code

#### Financial/Tax
- `taxinc` - Tax included flag
- `salestaxcde` - Sales tax code
- `purcost` - Purchase cost
- `purtax` - Purchase tax
- `wholesalecost` - Wholesale cost

#### Pricing Codes (8 codes)
- `disccdeone` - Discount code 1
- `disccdetwo` - Discount code 2
- `wholesalecde`, `retailcde`, `countercde`
- `tradecde`, `contractcde`, `industrialcde`, `distributorcde`

### 2. Migration

- Created: `db/alembic/versions/74980f3155d7_extend_product_with_all_fields.py`
- Note: Some columns may already exist in the database

### 3. Next Steps - Dash UI Full CRUD

To complete the implementation, update the Dash UI:

1. **Add Product Form** - Include all new fields in sections:
   - Basic Info (SKU, name, description)
   - Physical Properties (size, unit, pack, density)
   - Classifications (form, dgflag, etc.)
   - Financial (purchase cost, wholesale cost, tax codes)
   - Pricing Codes (all 8 codes)

2. **Edit Product** - Same form, but pre-populated with existing data

3. **Delete Product** - With confirmation modal

4. **Table Columns** - Update products table to show key fields

### 4. API Updates Needed

Update `app/api/products.py` to handle all new fields:

```python
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str]
    ean13: Optional[str]
    supplier_id: Optional[str]
    size: Optional[str]
    base_unit: Optional[str]
    pack: Optional[int]
    # ... all other fields
```

### 5. Model Fields Reference

See `app/adapters/db/models.py` lines 28-84 for complete Product model definition.

## Status

- ✅ Model extended with all fields
- ✅ Migration generated
- ⏳ Migration needs manual fix (handle existing columns)
- ⏳ Update Dash UI for full CRUD
- ⏳ Update API DTOs

## Manual Steps Required

Since some columns may already exist, you can either:

1. **Option A**: Drop database and recreate with all migrations
2. **Option B**: Manually add missing columns to existing database
3. **Option C**: Check which columns exist, modify migration to skip those

To check existing columns:
```python
from app.adapters.db import get_session
from sqlalchemy import inspect

session = next(get_session())
inspector = inspect(session)
columns = [col['name'] for col in inspector.get_columns('products')]
print("Existing columns:", columns)
```

Then modify the migration to only add missing columns.

