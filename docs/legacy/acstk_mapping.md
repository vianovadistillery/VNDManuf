# Legacy ACSTK (Accessory Stock File) Schema Mapping

## Overview
This document maps the legacy QuickBASIC `acstk.acf` file schema to the modern TPManuf system.

## Legacy File Structure
- **File**: `acstk.acf` (or `acstk.new`, `acstk.pre`)
- **Record Length**: 256 bytes
- **Type**: Random Access File with TYPE definition

## Field Mapping

### Product Identification Fields

| Legacy Field | Type | Size | Modern Field | Notes |
|-------------|------|------|-------------|-------|
| `no` | INTEGER | 2 | Not mapped | Internal record number |
| `search` | STRING | 10 | `products.sku` | Product code/SKU |
| `ean13` | CURRENCY | 8 | Not mapped | EAN-13 barcode (can store as metadata) |
| `desc1` | STRING | 25 | `products.name` | Primary product name |
| `desc2` | STRING | 10 | `products.description` (partial) | Secondary description |
| `suplr` | STRING | 5 | To `suppliers` table | Supplier code |
| `size` | STRING | 3 | `products.description` | Size information |
| `unit` | STRING | 2 | Not mapped | Unit code (handled via UOM tables) |
| `pack` | INTEGER | 2 | `pack_units` table | Package quantity |
| `dgflag` | STRING | 1 | Not mapped | Dangerous goods flag |
| `form` | STRING | 4 | Not mapped | Form code |
| `pkge` | INTEGER | 2 | `pack_conversions` table | Package type |
| `label` | INTEGER | 2 | Not mapped | Label type |
| `manu` | INTEGER | 2 | Not mapped | Manufacturer code |
| `active` | STRING | 1 | `products.is_active` | Active status ('Y'/'N' to boolean) |

### Financial Fields

| Legacy Field | Type | Size | Modern Field | Notes |
|-------------|------|------|-------------|-------|
| `taxinc` | STRING | 1 | Not mapped | Tax included flag |
| `salestaxcde` | STRING | 1 | Not mapped | Sales tax code |
| `purcost` | SINGLE | 4 | `inventory_lots.unit_cost` | Purchase cost |
| `purtax` | SINGLE | 4 | Not mapped | Purchase tax (calculated) |
| `wholesalecost` | SINGLE | 4 | `price_list_items` | Wholesale price |

#### Discount Codes
- `disccdeone` | STRING | 1 | To pricing rules | Discount code 1
- `disccdetwo` | STRING | 1 | To pricing rules | Discount code 2

#### Customer Price Codes
- `wholesalecde` | STRING | 1 | `price_list_items` | Wholesale pricing code
- `retailcde` | STRING | 1 | `price_list_items` | Retail pricing code
- `countercde` | STRING | 1 | `price_list_items` | Counter pricing code
- `tradecde` | STRING | 1 | `price_list_items` | Trade pricing code
- `contractcde` | STRING | 1 | `price_list_items` | Contract pricing code
- `industrialcde` | STRING | 1 | `price_list_items` | Industrial pricing code
- `distributorcde` | STRING | 1 | `price_list_items` | Distributor pricing code

#### Customer Prices
- `retail` | SINGLE | 4 | `price_list_items.unit_price_ex_tax` | Retail price
- `counter` | SINGLE | 4 | `price_list_items.unit_price_ex_tax` | Counter price
- `trade` | SINGLE | 4 | `price_list_items.unit_price_ex_tax` | Trade price
- `contract` | SINGLE | 4 | `price_list_items.unit_price_ex_tax` | Contract price
- `industrial` | SINGLE | 4 | `price_list_items.unit_price_ex_tax` | Industrial price
- `distributor` | SINGLE | 4 | `price_list_items.unit_price_ex_tax` | Distributor price

**Note**: These prices map to different `price_list_items` entries based on customer type.

#### Standard Cost References
- `suplr4stdcost` | STRING | 5 | `inventory_lots.supplier_id` | Supplier for standard cost
- `search4stdcost` | STRING | 10 | Not mapped | Product code for standard cost

### Stock Holding Fields

| Legacy Field | Type | Size | Modern Field | Notes |
|-------------|------|------|-------------|-------|
| `cogs` | SINGLE | 4 | `inventory_lots` | Cost of goods sold |
| `gpc` | SINGLE | 4 | Not mapped | Gross profit cost |
| `rmc` | SINGLE | 4 | Not mapped | Raw material cost |
| `gpr` | SINGLE | 4 | Not mapped | Gross profit ratio |
| `soh` | INTEGER | 2 | `inventory_lots.quantity_kg` | Stock on hand |
| `sohv` | SINGLE | 4 | `inventory_lots` (calculated) | Stock on hand value |
| `sip` | INTEGER | 2 | To work orders | Stock in progress |
| `soo` | INTEGER | 2 | To purchase orders | Stock on order |
| `sold` | INTEGER | 2 | Historical data only | Quantity sold |
| `date` | STRING | 8 | Not mapped | Last transaction date |

### Additional Fields
- `bulk` | SINGLE | 4 | Not mapped | Bulk quantity
- `lid` | INTEGER | 2 | Not mapped | Lid type
- `pbox` | INTEGER | 2 | Not mapped | Per box quantity
- `boxlbl` | INTEGER | 2 | Not mapped | Box label type
- `filler` | STRING | 69 | Not mapped | Reserved/padding

## Migration Strategy

### 1. Core Product Creation
```python
Product(
    sku=legacy.search,
    name=legacy.desc1 + " " + legacy.desc2,
    description=f"Size: {legacy.size}, Form: {legacy.form}",
    is_active=(legacy.active == 'Y')
)
```

### 2. Inventory Lots
```python
InventoryLot(
    lot_code=f"LEGACY-{legacy.no}",
    product_id=product.id,
    quantity_kg=legacy.soh,  # If 'unit' is 'kg'
    unit_cost=legacy.purcost,
    received_at=parse_date(legacy.date)
)
```

### 3. Price Lists
Create price list items for each price tier:
- Retail, Counter, Trade, Contract, Industrial, Distributor

### 4. Pack Units
```python
PackUnit(
    code=legacy.unit,
    name=f"Unit {legacy.unit}",
    description=f"Package: {legacy.pack}, Pkg: {legacy.pkge}"
)
```

## Data Type Conversions

- `STRING * N`: Truncate/pad to length N
- `INTEGER`: 2-byte signed integer
- `SINGLE`: 4-byte floating point (map to DECIMAL/NUMERIC)
- `CURRENCY`: 8-byte fixed-point (map to NUMERIC(18,4))
- Empty strings ("") map to NULL

## Notes

1. The legacy system has a flat pricing structure. Modern system uses separate price lists.
2. Stock quantities need to be converted based on unit codes.
3. Multiple price fields should create separate price list items.
4. Date fields are stored as "YYYYMMDD" strings.
5. The `active` field uses 'Y'/'N' instead of boolean.
6. Some fields are specific to the legacy business logic and don't map to modern schema.
