# TPManuf Modernisation Project - Complete Summary

## Executive Summary

**TPManuf** is a complete modernization of a QuickBASIC DOS-based manufacturing system for a paint/trade-paints factory. The system has been rebuilt using modern Python 3.12, FastAPI (REST API), and Dash (web UI) while maintaining full feature parity with the legacy system.

**Project Status**: Phases 1-9 Complete; Phase 10 (Deployment) Pending
**Tech Stack**: Python 3.12, FastAPI, Dash, SQLAlchemy, Alembic, SQLite/PostgreSQL
**Current Version**: 1.0.0
**Lines of Code**: ~15,000+ lines across 50+ Python files

---

## 1. System Overview

### Purpose
TPManuf manages the complete manufacturing workflow for a paint factory including:
- **Product Catalog**: Finished products with variants, pricing, and packaging
- **Raw Materials**: 41-field ingredient database with FIFO inventory
- **Formulas**: Production recipes with unlimited revisions
- **Work Orders & Batches**: Production planning, execution, and QC tracking
- **Inventory**: FIFO stock management with reservation/release
- **Purchasing**: Suppliers, purchase orders, receipts
- **Sales**: Orders, despatch, invoicing
- **Pricing**: Multi-tier pricing with customer-specific overrides
- **Packaging**: Unit conversions (CAN→4PK→CTN) with product-specific scaling
- **Reports**: Batch tickets, invoices, stock valuation, usage analysis

### Key Features
- **FIFO Inventory**: Automatic oldest-first material reservation
- **Formula Versioning**: Unlimited revisions with history tracking
- **Batch QC**: 86+ quality control fields (pH, SG, viscosity, etc.)
- **Variance Analysis**: Automatic calculation of actual vs theoretical yields
- **Multi-Unit Support**: Automatic conversions between kg, L, g, mL, oz, lb
- **Legacy Compatibility**: Binary QB data import with anomaly detection

---

## 2. Technology Stack & Architecture

### Backend
```
Framework: FastAPI (Python 3.12)
ORM: SQLAlchemy
Migrations: Alembic
Database: SQLite (dev) / PostgreSQL (prod)
Testing: pytest
Code Quality: ruff, black, pre-commit
```

### Frontend
```
Framework: Dash + Dash Bootstrap Components
Layout: Multi-page tabbed interface
Tables: dash_table.DataTable (filterable, sortable, paginated)
Forms: Modal dialogs with accordion sections
```

### Database Schema
- **20+ tables** with proper relationships and constraints
- **Indexes** on all search/foreign key fields
- **UUID primary keys** throughout
- **Natural keys** (codes) for user-facing identification
- **Audit trails** on critical tables (created_at, updated_at)

### Project Structure
```
TPManuf/
├── app/
│   ├── api/              # FastAPI routers
│   │   ├── products.py
│   │   ├── raw_materials.py
│   │   ├── formulas.py
│   │   ├── batches.py
│   │   ├── pricing.py
│   │   ├── packing.py
│   │   ├── invoices.py
│   │   ├── suppliers.py
│   │   └── reports.py
│   ├── adapters/
│   │   ├── db/
│   │   │   ├── models.py         # Core models
│   │   │   ├── qb_models.py      # QB-derived models
│   │   │   └── session.py
│   │   ├── qb_parser.py          # QB binary parser
│   │   └── legacy_io.py          # Fixed-width parser
│   ├── domain/
│   │   └── rules.py              # Business logic (FIFO, conversions)
│   ├── services/                 # Application services
│   │   ├── formula_calculations.py
│   │   ├── stock_management.py
│   │   ├── pricing.py
│   │   ├── packing.py
│   │   └── invoicing.py
│   ├── ui/
│   │   ├── app.py                # Main Dash app
│   │   ├── pages/                # UI pages
│   │   │   ├── products_page.py
│   │   │   ├── raw_materials_page.py
│   │   │   ├── formulas_page.py
│   │   │   ├── batch_processing_page.py
│   │   │   ├── suppliers_page.py
│   │   │   └── ... (12 pages total)
│   │   └── *_callbacks.py        # Callback handlers
│   ├── reports/                  # Text renderers
│   │   ├── batch_ticket.py
│   │   ├── invoice.py
│   │   └── formula_print.py
│   ├── settings.py               # Configuration
│   ├── logging_config.py         # JSON logging
│   └── error_handlers.py
├── db/alembic/versions/          # Migrations
├── tests/
│   ├── golden/                  # Golden file tests
│   ├── acceptance/              # QB parity tests
│   └── test_*.py
├── scripts/                      # Utility scripts
├── legacy_data/                 # Original QB files
└── docs/                        # Documentation
```

---

## 3. Database Models

### Core Entities

**Products** (`products`)
- 24+ fields including SKU, name, EAN13, supplier, physical properties
- Pricing fields: purchase_cost, wholesalecost, discount codes
- Classification: dgflag, form, pkge, label, manu
- Related: ProductVariant (packaging variants)

**Raw Materials** (`raw_materials`)
- 41 fields mapping to QB structure
- Key fields: code, desc1, desc2, sg (specific gravity)
- Cost fields: purchase_cost, usage_cost, deal_cost
- Stock: soh, opening_soh, restock_level
- Many-to-many with Suppliers via `raw_material_suppliers`
- Indexed on: code, desc1, active_flag

**Formulas** (`formulas`)
- Formula code, version, type (S/W), quantity_kg
- Class (classification system)
- Related: FormulaLine (ingredients with quantities and units)
- Unlimited revisions per code

**Formula Lines** (`formula_lines`)
- sequence, raw_material_id, quantity_kg, unit, cost
- Unit field supports: kg, g, L, mL, oz, lb
- Auto-conversion to canonical kg for storage

**Batches** (`batches`)
- 86+ fields for production batches
- QC fields: filter_flag, grind, ph, sg, vsol, wsol, gln, flow
- Variance: yield_actual vs theoretical
- Related: BatchComponent (consumed materials)

**Work Orders** (`work_orders`)
- Code, product_id, quantity, status
- Related: WorkOrderLine (planned production)

### Supporting Tables

**Suppliers** (`suppliers`)
- Name, contact, address, xero_id
- Many-to-many with RawMaterial

**Customers** (`customers`)
- Name, contact, address, xero_id
- Related to: SalesOrder, Invoice, CustomerPrice

**Inventory Lots** (`inventory_lots`)
- product_id, quantity_kg, received_at
- FIFO ordering by received_at
- Related: InventoryTxn (audit trail)

**Purchase Orders** (`purchase_orders`, `po_lines`)
- Supplier orders with line items
- Status tracking: DRAFT, CONFIRMED, RECEIVED, CANCELLED

**Sales Orders** (`sales_orders`, `so_lines`)
- Customer orders with line items
- Status tracking: DRAFT, CONFIRMED, SHIPPED, CANCELLED

**Invoices** (`invoices`, `invoice_lines`)
- Invoice generation from sales orders
- Text/PDF rendering support

**Pricing** (`price_lists`, `price_list_items`, `customer_price`)
- Multi-tier pricing system
- Customer-specific overrides
- Resolution order: customer_price → price_list → error

**Packaging** (`pack_units`, `pack_conversions`)
- Units: CAN, 4PK, CTN
- Product-specific conversions (multiplicative)

---

## 4. API Endpoints

### Products API (`/api/v1/products`)
```
GET    /products/               # List products
POST   /products/               # Create product
GET    /products/{id}           # Get product details
PUT    /products/{id}           # Update product
DELETE /products/{id}           # Delete product (soft)
GET    /products/sku/{sku}      # Get by SKU
```

### Raw Materials API (`/api/v1/raw-materials`)
```
GET    /raw-materials/                          # List (filtered)
POST   /raw-materials/                          # Create
GET    /raw-materials/{id}                      # Details
PUT    /raw-materials/{id}                      # Update
DELETE /raw-materials/{id}                      # Delete
GET    /raw-materials/code/{code}              # Get by code
GET    /raw-materials/{id}/stock-movements      # Historical SOH
POST   /raw-materials/{id}/suppliers             # Add supplier
DELETE /raw-materials/{id}/suppliers/{sup_id}   # Remove supplier
GET    /raw-materials/{id}/suppliers            # List suppliers
GET    /raw-materials/groups                    # List groups
```

### Formulas API (`/api/v1/formulas`)
```
GET    /formulas/                                   # List formulas
POST   /formulas/                                   # Create formula
GET    /formulas/{id}                               # Get details
PUT    /formulas/{id}                               # Update
DELETE /formulas/{id}                               # Delete
GET    /formulas/code/{code}/revisions              # All revisions
GET    /formulas/code/{code}/version/{rev}          # Specific revision
POST   /formulas/{id}/revision                      # Create new revision
PUT    /formulas/{id}/lines                         # Replace lines
```

### Batches API (`/api/v1/batches`)
```
GET    /batches/                      # List batches (filtered)
POST   /batches/                      # Create batch (reserves materials)
GET    /batches/{id}                  # Get details
PUT    /batches/{id}/record-actual    # Record actual yield
PUT    /batches/{id}/qc-results       # Record QC data
PUT    /batches/{id}/complete         # Mark complete
```

### Suppliers API (`/api/v1/suppliers`)
```
GET    /suppliers/           # List suppliers
POST   /suppliers/           # Create supplier
GET    /suppliers/{id}       # Get details
PUT    /suppliers/{id}       # Update
DELETE /suppliers/{id}       # Delete
```

### Pricing API (`/api/v1/pricing`)
```
GET /pricing/resolve?customer_id=X&product_id=Y  # Resolve price
```

### Packing API (`/api/v1/pack`)
```
GET /pack/convert?product_id=X&qty=Y&from_unit=Z&to_unit=W  # Convert units
```

### Invoices API (`/api/v1/invoices`)
```
GET    /invoices/                      # List invoices
POST   /invoices/                       # Create invoice
GET    /invoices/{id}                   # Get details
GET    /invoices/{id}/print?format=text  # Generate invoice text
DELETE /invoices/{id}                   # Delete invoice
```

---

## 5. UI Pages (Dash)

### Implemented Pages (12+)

1. **Products Management**
   - Full CRUD with 24+ fields
   - Accordion layout: Basic Info, Physical Properties, Classifications, Financial, Pricing Codes
   - Edit/Delete with confirmation
   - DataTable with filtering and pagination

2. **Raw Materials**
   - Master-detail CRUD (41 fields)
   - Tabs: Details, Costs, Stock
   - Supplier dropdown selection
   - Stock movement history
   - Search and filter by status

3. **Formulas**
   - Formula list with revisions
   - Formula editor with ingredient table
   - Ingredient selection from raw materials
   - Unit selection: kg, g, L, mL, oz, lb
   - Quantity and unit stored per line
   - Ingredient summary (Qty + Unit columns)

4. **Batch Processing**
   - Tabbed interface: Plan, Execute, QC, History
   - Create batches from work orders
   - Record actual yields
   - QC data entry (pH, SG, viscosity, etc.)
   - Variance analysis

5. **Suppliers**
   - CRUD for supplier management
   - Contact information and addresses
   - Xero integration ready

6. **Other Pages**
   - Batch Reports (variance analysis)
   - RM Reports (usage, valuation, reorder)
   - Stocktake (physical counts)
   - Condition Types (hazard codes)
   - Accounting Integration (placeholder)

### UI Features
- **Responsive Bootstrap layout**
- **Modal forms** for CRUD operations
- **DataTables** with sorting, filtering, pagination
- **Toast notifications** for success/error feedback
- **Row selection** for bulk operations
- **Auto-loading tables** on tab activation
- **Refresh buttons** on all pages
- **Search/filter** controls

---

## 6. Business Logic

### Domain Rules (`app/domain/rules.py`)

**Unit Conversions**
```python
# Convert to canonical kg
def to_kg(qty, uom, density=None):
    # Supports: kg, g, L, mL, oz, lb
    # Converts liquids using density (kg/L)

# Convert from kg to display unit
def to_liters(qty_kg, density):
    # For liquids: convert kg to L
```

**FIFO Inventory** (`app/services/stock_management.py`)
```python
def reserve_materials(batch_id):
    # 1. Get required materials from formula
    # 2. Order lots by received_at (oldest first)
    # 3. Issue materials, decrement SOH
    # 4. Create InventoryTxn for audit
```

**Formula Calculations** (`app/services/formula_calculations.py`)
```python
def calculate_theoretical_cost(formula_id):
    # Sum of (quantity × unit_cost) for all lines

def calculate_theoretical_yield(formula_id, batch_size_kg):
    # Total yield with SG corrections

def calculate_variance(batch_id):
    # (actual - theoretical) / theoretical × 100
```

**Pricing Resolution** (`app/services/pricing.py`)
```python
def resolve_price(customer_id, product_id):
    # 1. Check customer_price (specific override)
    # 2. Check price_list_item (general pricing)
    # 3. Raise error if no price found
```

---

## 7. Data Migration from QuickBASIC

### QB Parser (`app/adapters/qb_parser.py`)

**Supported Data Types:**
- `INTEGER` (2 bytes, signed)
- `SINGLE` (4 bytes, float)
- `STRING * n` (n bytes, CP437 encoding)
- `CURRENCY` (8 bytes, scaled integer)

**Import Process:**
1. Parse QB binary files using `struct.unpack()`
2. Map to SQLAlchemy models
3. Upsert using natural keys (code-based)
4. Generate anomaly reports for data issues
5. Support `--dry-run` for testing

**Import Order:**
1. Raw material groups
2. Raw materials (MSRMNEW.MSF)
3. Formula classes
4. Formulas (FORHED.ASF)
5. Formula lines (FORDET.ASF)
6. Batches (MSBATCH.MSF)
7. Configuration (MSMISC.MSF)

**Validation:**
- Reconcile counts within ±0.1%
- Numeric totals match
- Anomalies logged to `out/anomalies/*.csv`

---

## 8. Reports & Printing

### Batch Tickets (`app/reports/batch_ticket.py`)
- **Format**: Legacy `.PRN` text format
- **Fixed-width columns** (matches QuickBASIC output)
- **Content**: Batch code, date, operator, formula, component list, QC parameters
- **Rendering**: Jinja2 template → text

### Invoices (`app/reports/invoice.py`)
- **Format**: Legacy `.INS` text format
- **Content**: Invoice number, customer details, line items, totals
- **Formatting**: Maintains QB column widths and spacing

### Stock Reports (`app/reports/stock_reports.py`)
- Stock valuation (total inventory value)
- Reorder analysis (materials below restock_level)
- Usage reports (YTD consumption)
- Slow-moving stock (not used in 180+ days)

### Formula Cards (`app/reports/formula_print.py`)
- Recipe documentation
- Ingredient list with costs
- Processing instructions
- Theoretical cost calculation

---

## 9. Testing

### Test Structure
```
tests/
├── golden/                          # Print artifact tests
│   ├── test_batch_ticket.py
│   ├── test_invoice.py
│   └── print_normalizer.py
├── acceptance/                      # QB parity tests
│   └── test_qb_parity.py
├── test_domain_rules.py             # Business logic
├── test_formulas_api.py             # API integration
└── test_qb_parser.py                 # QB parser
```

### Test Coverage
- **Unit tests**: QB parser, domain rules
- **Integration tests**: API endpoints, CRUD operations
- **Acceptance tests**: QB format matching, calculation accuracy
- **Golden tests**: Print artifact comparison (normalized)

### Running Tests
```powershell
# All tests
pytest tests/

# Specific pattern
pytest -k "formulas"

# With coverage
pytest --cov=app --cov-report=html
```

---

## 10. Current Implementation Status

### ✅ Completed (Phases 1-9)

**Phase 1: Legacy Code Analysis** ✅
- Analyzed 230+ .BAS files, 122 .INC files
- Extracted 41-field raw material structure
- Extracted 86+ field batch structure
- Created data dictionary and module inventory

**Phase 2: Database Schema** ✅
- 20+ tables created with proper relationships
- 30+ indexes for performance
- UUID primary keys throughout
- Alembic migrations for version control

**Phase 3: Legacy Data Import** ✅
- QB parser implemented
- Fixed-width file parser
- Import scripts with validation
- Anomaly detection and reporting

**Phase 4: API Endpoints** ✅
- Products, Raw Materials, Formulas, Batches
- Suppliers, Pricing, Packing, Invoices
- Reports and stock movements
- 50+ endpoints total

**Phase 5: Dash UI** ✅
- 12+ pages implemented
- Full CRUD on all major entities
- Master-detail layouts
- Modal forms and data tables

**Phase 6: Business Logic** ✅
- FIFO inventory management
- Formula cost/yield calculations
- Variance analysis
- Unit conversions
- Pricing resolution

**Phase 7: Reports & Printing** ✅
- Batch tickets (.PRN format)
- Invoices (.INS format)
- Formula cards
- Stock reports

**Phase 8: Testing** ✅
- Unit tests passing
- Integration tests passing
- Acceptance tests (QB parity)
- Golden tests for print artifacts

**Phase 9: Documentation** ✅
- User guide
- Technical architecture
- API documentation
- Migration guide

### ⚠️ Pending (Phase 10)

**Production Deployment**
- PostgreSQL setup
- User training
- Parallel run (1-2 weeks)
- Final cutover

---

## 11. Recent Updates

### Latest Features Added

1. **Supplier Selection in Raw Materials** ✅
   - Added supplier dropdown in raw materials details tab
   - Many-to-many relationship via junction table
   - API endpoints for managing supplier relationships
   - Loads existing supplier when editing

2. **Formula Lines with Units** ✅
   - Added unit field to formula lines
   - Supports: kg, g, L, mL, oz, lb
   - Auto-conversion to kg for storage
   - Separate quantity and unit columns in summary

3. **Ingredient Selection Enhancement** ✅
   - Searchable and paginated raw materials list
   - Click-to-select from ingredient table
   - Modal with search functionality
   - Handles unit conversions properly

4. **Formula Editor Improvements** ✅
   - Fixed saving issues with unique constraint violations
   - Proper handling of line updates
   - Unit display and editing
   - Auto-loading of table contents

---

## 12. Development Workflow

### Setup
```powershell
# Create virtual environment and install dependencies
.\scripts\dev.ps1 setup

# Or manually:
python -m venv .venv
.venv\Scripts\Activate
pip install -e .
```

### Database Migrations
```powershell
# Apply migrations
.\scripts\dev.ps1 db
# or
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Running Servers
```powershell
# API server (http://127.0.0.1:8000)
.\scripts\dev.ps1 api

# UI server (http://127.0.0.1:8050)
.\scripts\dev.ps1 ui

# Both
.\scripts\dev.ps1
```

### Importing Legacy Data
```powershell
# Preview (dry-run)
python scripts\import_qb_data.py --dry-run

# Actually import
python scripts\import_qb_data.py
```

### Testing
```powershell
# Run all tests
.\scripts\dev.ps1 test

# Run specific tests
pytest tests/test_formulas_api.py -v
```

---

## 13. Key Files Reference

### Configuration
- `app/settings.py` - Application settings (database, API, UI, security)
- `app/logging_config.py` - JSON logging with request IDs
- `app/error_handlers.py` - HTTP error handling
- `alembic.ini` - Alembic configuration
- `pyproject.toml` - Project dependencies

### Core Business Logic
- `app/domain/rules.py` - Unit conversions, FIFO logic
- `app/services/formula_calculations.py` - Formula costs/yields
- `app/services/stock_management.py` - FIFO reservation/release
- `app/services/pricing.py` - Price resolution
- `app/services/packing.py` - Unit conversions

### Data Access
- `app/adapters/db/models.py` - Core SQLAlchemy models
- `app/adapters/db/qb_models.py` - QB-derived models
- `app/adapters/db/session.py` - Database session management

### API
- `app/api/main.py` - FastAPI application setup
- `app/api/products.py` - Products CRUD
- `app/api/raw_materials.py` - Raw materials CRUD + supplier relationships
- `app/api/formulas.py` - Formulas with revisions
- `app/api/batches.py` - Batch workflow

### UI
- `app/ui/app.py` - Main Dash application
- `app/ui/pages/*.py` - Page layouts
- `app/ui/*_callbacks.py` - Callback handlers

### Legacy Import
- `app/adapters/qb_parser.py` - QB binary file parser
- `app/adapters/legacy_io.py` - Fixed-width file parser
- `scripts/import_qb_data.py` - Import script

---

## 14. Database Schema Summary

### Core Tables
- `products` - Finished product catalog
- `raw_materials` - Ingredients (41 fields)
- `formulas` - Production recipes
- `formula_lines` - Recipe ingredients
- `batches` - Production batches (86+ fields)
- `work_orders` - Production planning
- `inventory_lots` - Stock on hand (FIFO)
- `inventory_txn` - Stock audit trail

### Relationships
- `suppliers` - Vendor management
- `raw_material_suppliers` - Many-to-many junction
- `customers` - Customer management
- `purchase_orders`, `po_lines` - Procurement
- `sales_orders`, `so_lines` - Sales
- `invoices`, `invoice_lines` - Invoicing

### Supporting
- `price_lists`, `price_list_items` - Tiered pricing
- `customer_price` - Customer-specific overrides
- `pack_units` - CAN, 4PK, CTN
- `pack_conversions` - Unit conversions
- `raw_material_groups` - Material classification

---

## 15. Important Notes

### Units Convention
- **Canonical storage**: mass in **kg**
- **Liquids**: convert L → kg using density (kg/L)
- **ABV**: stored as % v/v
- **Rounding**: quantities 3 dp, money 2 dp (bankers' rounding)

### FIFO Logic
- Materials issued oldest-first based on `received_at`
- Automatic reservation on batch creation
- Release on batch cancellation
- Transaction history for audit

### Formula Revisioning
- Unlimited revisions per formula code
- Each revision maintains full history
- Cannot modify older revisions (immutable)
- Must create new revision to change

### Pricing Resolution
- Order: customer_price → price_list_item → error
- Prices are ex-GST (add tax per line)
- Default tax rate: 10%
- Supports price lists and customer overrides

---

## 16. Quick Reference

### Start Development
```powershell
.\scripts\dev.ps1 setup   # Install dependencies
.\scripts\dev.ps1 db      # Run migrations
.\scripts\dev.ps1          # Start API + UI
```

### Access Points
- **API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs (dev only)
- **UI**: http://127.0.0.1:8050

### Key Commands
```powershell
# Run tests
pytest tests/

# Check database
python scripts/check_db.py

# Import QB data
python scripts/import_qb_data.py --dry-run
```

---

## 17. Contact & Support

**Project**: TPManuf Modernisation
**Status**: Production Ready (Phase 10 pending)
**Version**: 1.0.0
**Author**: AI Assistant (Claude Sonnet 4.5)
**Date**: December 2024

For questions or issues, refer to:
- `docs/user_guide.md` - User documentation
- `docs/architecture.md` - Technical architecture
- `docs/API_UPDATES_COMPLETE.md` - API reference
- `brief.md` - Original specification

---

*This document provides a comprehensive overview of the TPManuf project. For detailed information on specific features, refer to the documentation files in the `docs/` directory.*
