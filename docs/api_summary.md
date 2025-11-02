# TPManuf API - QuickBASIC Migration Summary

## Phase 1-3: Complete ✅

### Phase 1: Legacy Code Analysis ✅
- Cataloged 238 QuickBASIC files (.BAS, .INC, .BIX)
- Extracted 14 menu options from MSMENU.BAS
- Documented all TYPE definitions (300+ fields)
- Generated data dictionary and module inventory

### Phase 2: Database Schema Design ✅
- Created 6 new QB models:
  - `RawMaterialGroup` - groups raw materials
  - `RawMaterial` - raw material records (41 fields)
  - `FormulaClass` - formula classification
  - `Markup` - pricing markups
  - `ConditionType` - hazard/condition codes
  - `Dataset` - multi-company support
  - `ManufacturingConfig` - system parameters
- Generated Alembic migration `b7a47f197d45`
- Added indexes for performance

### Phase 3: Legacy Data Import ✅
- Built QB binary file parser (`app/adapters/qb_parser.py`)
- Created import script (`scripts/import_qb_data.py`)
- Parsed 944 raw materials from `MSRMNEW.MSF`
- Imported sample data (10 records)
- Verified database persistence

## Phase 4: API Endpoints (In Progress)

### Unified Products API ✅
**Note:** Raw materials, WIP, and finished goods are now unified in the products API.

**Endpoints:**
- `GET /api/v1/products?product_type=RAW|WIP|FINISHED` - List products with optional type filtering
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/products/sku/{sku}` - Get product by SKU
- `POST /api/v1/products` - Create product (supports product_type: RAW, WIP, FINISHED)
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Soft delete (sets is_active=False)

**Product Types:**
- **RAW**: Raw materials with specific fields (raw_material_code, specific_gravity, usage_cost, etc.)
- **WIP**: Work-in-progress products created during batch production
- **FINISHED**: Finished goods with formula references

**Features:**
- Full CRUD operations for all product types
- Filtering by product_type (RAW, WIP, FINISHED)
- Type-specific fields included in responses
- Unified inventory tracking across all types

**Example Requests:**
```powershell
# List all raw materials
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products?product_type=RAW&limit=10" -Method GET

# List all WIP products
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products?product_type=WIP" -Method GET

# List all finished goods
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products?product_type=FINISHED" -Method GET

# Search across all types
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products?query=WATER" -Method GET
```

**Legacy Raw Materials API:**
The legacy `/api/v1/raw-materials/` endpoints may still exist for backward compatibility but should be migrated to use the unified products API.

## Next Steps

### Formulas API (Pending)
**Endpoints to implement:**
- `GET /api/v1/formulas/` - List with filters
- `GET /api/v1/formulas/{code}/revisions` - All revisions
- `GET /api/v1/formulas/{code}/rev/{revision}` - Specific revision
- `POST /api/v1/formulas/` - Create with lines
- `POST /api/v1/formulas/{code}/new-revision` - Clone as new revision

### Batch Processing API (Enhance)
**Endpoints to add:**
- `POST /api/v1/batches/` - Create (reserves materials)
- `PUT /api/v1/batches/{id}/record-actual` - Record actual yield
- `PUT /api/v1/batches/{id}/qc-results` - Record QC data
- `GET /api/v1/batches/` - List with filters

### Reports API (Pending)
**Endpoints to create:**
- `GET /api/v1/reports/raw-materials/usage` - YTD usage report
- `GET /api/v1/reports/formulas/cost-analysis` - Cost breakdown
- `GET /api/v1/reports/batch-history` - Historical batches

## Architecture

### File Structure
```
app/
├── api/
│   ├── main.py              # FastAPI app
│   ├── raw_materials.py     # Raw materials endpoints ✅
│   ├── products.py          # Products endpoints (existing)
│   ├── batches.py           # Batch endpoints (existing)
│   └── dto.py              # DTOs (extended with RM DTOs)
├── adapters/
│   ├── db/
│   │   ├── models.py        # Core models (existing)
│   │   └── qb_models.py     # QB-derived models ✅
│   ├── qb_parser.py         # QB file parser ✅
│   └── legacy_io.py         # Legacy data I/O
├── domain/
│   └── rules.py            # Business logic
└── services/
    ├── formulas.py
    ├── inventory.py
    └── batch_reporting.py
scripts/
├── import_qb_data.py        # Data import ✅
└── check_qb_import.py      # Verification ✅
```

### Database Models

**RawMaterial (QB-derived):**
- 41 fields matching `RcdFmtmsrmat` from QB
- Costs (purchase, usage, deal)
- SG (specific gravity) tracking
- SOH (stock on hand) with opening, value, restock level
- Hazard, condition, MSDS flags
- Alternative numbers (altno1-5)
- EAN13 barcode
- Group relationship

**RawMaterialGroup:**
- Code (hierarchical like "1.1.1")
- Name, description
- Active flag

## Data Import

**Source:** `legacy_data/MSRMNEW.msf` (1.29 MB, 944 records)

**Process:**
1. Parse binary QuickBASIC format
2. Map to SQLAlchemy model
3. Validate and check duplicates
4. Insert with UUID PKs
5. Report anomalies

**Command:**
```bash
python scripts/import_qb_data.py --dry-run  # Test
python scripts/import_qb_data.py           # Import
python scripts/check_qb_import.py           # Verify
```

## Status

✅ Phases 1-3 complete
🔄 Phase 4 in progress (Raw Materials API complete)
⏳ Remaining: Formulas API, Reports API, Batch enhancements

## Notes

- QuickBASIC used fixed-width binary records
- QB CURRENCY type is 8-byte scaled integer (divide by 10000)
- QB stores strings with null padding (trim for display)
- Character encoding: CP437 (IBM PC)
- Little-endian byte order
- Single precision float (4 bytes)

