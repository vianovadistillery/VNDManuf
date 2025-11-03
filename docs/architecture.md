# TPManuf Architecture Documentation

## System Overview

TPManuf is a FastAPI + Dash application for paint manufacturing, replacing the legacy QuickBASIC system. It maintains feature parity with 14 QB menu options while modernizing the tech stack.

**Technology Stack**:
- Python 3.12
- FastAPI (REST API)
- Dash + Dash Bootstrap Components (Web UI)
- SQLAlchemy (ORM)
- Alembic (Migrations)
- SQLite (Development) / PostgreSQL (Production)

## Database Schema

### Core Tables

**Products** (`products`)
- Primary product catalog
- Fields: `id`, `sku`, `name`, `description`, `category`
- Related: `ProductVariant` (packaging)

**Raw Materials** (`raw_materials`)
- Ingredients for production
- 41 fields mapping to QB `RcdFmtmsrmat`
- Key fields: `code`, `desc1`, `desc2`, `sg`, `purchase_cost`, `usage_cost`, `soh`, `restock_level`
- Indexed on: `code`, `desc1`, `active_flag`

**Formulas** (`formulas`)
- Production formulas with revisions
- Fields: `formula_code`, `version`, `quantity_kg`, `type` (S/W), `class_id`
- Related: `FormulaLine` (ingredients), `FormulaClass`

**Formula Lines** (`formula_lines`)
- Ingredient list for formulas
- Fields: `formula_id`, `sequence`, `ingredient_product_id`, `quantity_kg`, `unit_cost`
- Order matters (sequence)

**Batches** (`batches`)
- Production batches
- 86+ fields mapping to QB `RcdFmtbatch`
- Key fields: `batch_code`, `formula_code`, `quantity_kg`, `yield_actual`, `variance_percent`
- QC fields: `filter_flag`, `grind`, `ph`, `sg`, `vsol`, `wsol`, `gln`, `flow`
- Related: `BatchComponent` (consumed materials)

**Inventory** (`inventory_lots`, `inventory_txn`)
- Stock management
- FIFO tracking via `received_at`
- Transaction history for audit

### Relationships

```
Product ──┬── ProductVariant (packaging)
          │
          ├── Formula (one-to-many)
          │   └── FormulaLine
          │        └── RawMaterial (ingredient)
          │
          └── Batch
               └── BatchComponent (raw material consumption)
```

## API Architecture

### Endpoints

**Products API** (`/api/v1/products`)
- `GET /products/` - List products
- `POST /products/` - Create product
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product

**Raw Materials API** (`/api/v1/raw-materials`)
- `GET /raw-materials/` - List raw materials (filtered)
- `POST /raw-materials/` - Create raw material
- `GET /raw-materials/{id}` - Get raw material details
- `PUT /raw-materials/{id}` - Update raw material
- `GET /raw-materials/{id}/stock-movements` - Historical SOH changes

**Formulas API** (`/api/v1/formulas`)
- `GET /formulas/` - List formulas
- `GET /formulas/code/{code}/revisions` - All revisions of formula
- `GET /formulas/code/{code}/version/{rev}` - Specific revision
- `POST /formulas/` - Create new formula
- `POST /formulas/code/{code}/new-revision` - Clone to new revision

**Batches API** (`/api/v1/batches`)
- `POST /batches/` - Create batch (reserves materials)
- `PUT /batches/{id}/record-actual` - Record actual yield
- `PUT /batches/{id}/qc-results` - Record QC data
- `GET /batches/` - List batches (filtered)
- `GET /batches/{id}` - Get batch details

**Reports API** (`/api/v1/reports`)
- `GET /reports/raw-materials/usage` - YTD usage report
- `GET /reports/formulas/cost-analysis` - Formula cost breakdown
- `GET /reports/batch-history` - Batch history with variance

### Error Handling

**422 Validation Error**: Invalid input data
```json
{
  "error": "Validation Error",
  "message": "Field 'sg' must be > 0",
  "details": {...}
}
```

**409 Conflict Error**: Business rule violation
```json
{
  "error": "Conflict",
  "message": "Insufficient stock for material RM-001"
}
```

**404 Not Found**: Resource not found
```json
{
  "error": "Not Found",
  "message": "Formula code 'XYZ' not found"
}
```

## UI Architecture

### Dash Application

**Main App** (`app/ui/app.py`)
- Multi-page layout with tabs
- Tab content rendered dynamically
- API integration via `requests`

**Page Components** (`app/ui/pages/*.py`)
- Raw Materials: Master-detail CRUD
- Formulas: Formula list + lines editor
- Batch Processing: Plan/Execute/QC/History tabs
- Batch Reports: Variance analysis
- RM Reports: Usage, valuation, reorder
- Stocktake: Physical count entry
- Condition Types: Hazard code management

**Callbacks**
- Data loading on tab switch
- Form submission for CRUD
- Export/import handlers
- API error handling

## Business Logic

### Formula Calculations

**File**: `app/services/formula_calculations.py`

**Functions**:
- `calculate_theoretical_cost(formula_id)` - Sum of (qty × unit_cost)
- `calculate_theoretical_yield(formula_id, batch_size_kg)` - Total with SG correction
- `calculate_batch_variance(batch_id)` - Actual vs theoretical

**SG Conversion**:
```python
# Volume to mass
mass_kg = volume_litres × SG

# Mass to volume
volume_litres = mass_kg / SG
```

### Stock Management

**File**: `app/services/stock_management.py`

**Functions**:
- `reserve_materials(batch_id)` - FIFO issue, decrement SOH
- `release_materials(batch_id)` - Return materials (cancelled batch)
- `perform_stocktake(counts)` - Physical vs system variance

**FIFO Logic**:
```python
# Order lots by received_at (oldest first)
# Issue from lot until qty satisfied or lot exhausted
# Create InventoryTxn for audit trail
```

## Report Rendering

### Batch Tickets

**File**: `app/reports/batch_ticket.py`

**Format**: Legacy `.PRN` format
- Fixed-width columns
- Text only (no graphics)
- Component list with quantities
- QC parameters and instructions
- Printable on dot-matrix printers

**Fields**:
- Batch code, date, operator
- Formula code and revision
- Target yield
- Component list (seq, material, qty, hazard)
- QC checkboxes

### Formula Cards

**File**: `app/reports/formula_print.py`

**Format**: Printable formula document
- Header: Formula code, revision, product name
- Lines: Ingredient list with costs
- Totals: Theoretical cost
- Notes: Processing instructions
- Signature: Authorization

### Stock Reports

**File**: `app/reports/stock_reports.py`

**Reports**:
- `generate_stock_valuation_report()` - Total inventory value
- `generate_reorder_analysis_report()` - Materials below reorder level
- `generate_usage_report()` - YTD usage by material
- `generate_slow_moving_report()` - Stock not used in 180+ days

## Data Migration

### QB File Parsing

**File**: `app/adapters/qb_parser.py`

**QB Data Types**:
- `INTEGER`: 2 bytes, little-endian signed
- `SINGLE`: 4 bytes, float
- `STRING * n`: n bytes, null-padded, CP437 encoding
- `CURRENCY`: 8 bytes, scaled integer / 10000

**Parsing Process**:
1. Read fixed-size record
2. Use `struct.unpack()` to parse binary
3. Convert to Python types
4. Clean strings (strip nulls, decode)
5. Return dictionary

### Import Script

**File**: `scripts/import_qb_data.py`

**Import Sequence**:
1. Raw material groups
2. Raw materials (MSRMNEW.msf)
3. Formula classes
4. Formulas (FORHED.ASF)
5. Formula lines (FORDET.ASF)
6. Batches (MSBATCH.MSF)
7. Configuration (MSMISC.MSF)

**Features**:
- `--dry-run`: Preview without writes
- `--allow-anomalies`: Log errors but continue
- Natural key upserts (code-based)
- Anomaly reporting to `out/anomalies/*.csv`

## Deployment

### Development

```powershell
# Setup
.\scripts\dev.ps1 setup

# Database migrations
.\scripts\dev.ps1 db

# Run API
.\scripts\dev.ps1 api

# Run UI
.\scripts\dev.ps1 ui
```

### Production

**Database**: PostgreSQL recommended
**Hosting**: Docker containers or cloud platform
**Environment Variables**: See `env.example`

**Setup**:
1. Configure `.env` with production settings
2. Run migrations: `alembic upgrade head`
3. Import QB data
4. Start API server (Uvicorn)
5. Start Dash UI
6. Configure reverse proxy (nginx)

## Testing

### Unit Tests

**Files**: `tests/test_*.py`

**Coverage**: >60% (target)

**Test Files**:
- `test_qb_parser.py` - QB file parsing
- `test_formulas_api.py` - API integration
- `test_domain_rules.py` - Business logic

### Acceptance Tests

**File**: `tests/acceptance/test_qb_parity.py`

**Scenarios**:
- Import raw materials from QB files
- Batch ticket format matches legacy
- Formula print format matches legacy
- Calculations match QB system (±0.01% tolerance)
- SG conversions correct
- FIFO logic correct

### Running Tests

```powershell
# All tests
python scripts\run_tests.py

# Specific pattern
python scripts\run_tests.py --pattern "formulas"

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## Performance Considerations

### Database Indexes

- `products.sku`
- `raw_materials.code`, `raw_materials.desc1`, `raw_materials.active_flag`
- `formulas.formula_code`, `formulas.version`
- `batches.batch_code`, `batches.formula_code`
- `inventory_lots.product_id`, `inventory_lots.received_at`

### API Response Times

- List endpoints: <500ms (paginated)
- Detail endpoints: <200ms
- Report generation: <2s

### UI Load Times

- Initial page load: <1s
- Tab switch: <500ms
- API data fetch: <500ms

## Security

### Authentication

**Status**: Not yet implemented (local development)

**Planned**: JWT-based authentication
- Roles: Operator, Planner, Admin
- Admin: Stock adjustments, overrides
- Audit trail for sensitive operations

### Data Protection

- No secrets in logs
- PII scrubbing where applicable
- Database encryption at rest (PostgreSQL)

## Troubleshooting

### Common Issues

**1. API not responding**
- Check API server running: `Get-Process python | Where-Object {$_.CommandLine -like '*uvicorn*'}`
- Check logs in console

**2. UI blank tabs**
- Check API connectivity: Visit `http://127.0.0.1:8000/health`
- Check browser console for errors
- Verify database tables created: `.\scripts\dev.ps1 db`

**3. Migration errors**
- Check Alembic version: `alembic current`
- Drop and recreate: `alembic downgrade base && alembic upgrade head`

**4. Import errors**
- Run with `--dry-run` first
- Check `out/anomalies/*.csv` for details
- Verify QB file paths and formats

## References

- QuickBASIC source: `legacy_data/Src/`
- QB data dictionary: `docs/legacy/qb_data_dictionary.csv`
- API documentation: `http://127.0.0.1:8000/docs`
- User guide: `docs/user_guide.md`
- Migration guide: `docs/qb_migration.md`
