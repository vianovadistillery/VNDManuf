# TPManuf User Guide

## Overview

TPManuf is a modern manufacturing system for paint production, replacing the legacy QuickBASIC TPManuf system. This guide covers core workflows and features.

## Getting Started

### Accessing the System

1. Start the API server:
   ```powershell
   .\scripts\dev.ps1 api
   ```

2. Start the Dash UI:
   ```powershell
   .\scripts\dev.ps1 ui
   ```

3. Open your browser to `http://127.0.0.1:8050`

### Dashboard

The main dashboard shows:
- Recent batches
- Stock alerts (materials below reorder level)
- Quick actions (create batch, stocktake, etc.)

## Core Workflows

### 1. Managing Raw Materials

**Purpose**: Maintain inventory of ingredients for paint production.

**Steps**:

1. Navigate to **Raw Materials** tab.
2. Use filters to find materials (status, group, search).
3. To add a material:
   - Click **"Add Raw Material"**
   - Enter code, descriptions, SG, costs
   - Set restock level and hazard codes
   - Save
4. To edit: Select a material from the table and click **"Edit"**.
5. To import/export: Use the **Import/Export** sub-tab for CSV operations.

**Fields**:
- Code: Material identifier (integer)
- Desc1/Desc2: Primary and secondary descriptions
- SG: Specific gravity for conversions
- Purchase/Usage Cost: Cost tracking
- SOH: Stock on Hand (auto-updated during production)
- Restock Level: Alert threshold
- Hazard/Condition: Safety codes

### 2. Formulating Products

**Purpose**: Define formulas for paint products.

**Steps**:

1. Navigate to **Formulas** tab.
2. Left panel: Browse formulas by code/name.
3. Right panel: View formula details and lines.
4. To create formula:
   - Click **"New Formula"**
   - Enter formula code, name, yield
   - Add lines (ingredients) with quantities
   - System calculates theoretical cost
   - Save
5. To create revision: Select formula → **"New Revision"**.

**Formula Lines**:
- Sequence: Order of addition
- Material: Raw material code/description
- Quantity: Amount (kg) per batch
- Unit Cost: Automatic from raw material
- Line Cost: Calculated (qty × unit cost)

### 3. Batch Processing

**Purpose**: Execute production batches.

**Workflow**:

1. Navigate to **Batch Processing** tab.
2. **Plan Tab**:
   - Select formula
   - Enter target yield (kg)
   - System reserves materials (updates SOH)
   - Click **"Create Batch"** → generates batch number
3. **Execute Tab**:
   - Record actual production
   - Enter actual yield (kg, litres)
   - Record processing times
   - System calculates variance
4. **QC Testing Tab**:
   - Enter QC results (SG, viscosity, pH, etc.)
   - Set filter flags
   - Record drying times
5. **History Tab**:
   - View past batches
   - Filter by year, formula, operator
   - Export reports

**Batch Number Format**: `YYNNNN` (year + sequence)

**Material Reservation**: System uses FIFO (First-In-First-Out) to consume oldest stock first.

### 4. Inventory Management

**Purpose**: Monitor stock levels and perform stocktake.

**Features**:

- **Stock Valuation**: View total inventory value.
- **Reorder Analysis**: Materials below reorder level (RM Reports tab).
- **Slow Moving Stock**: Identify materials with no movement for 180+ days.
- **Stocktake**:
  1. Navigate to **Stocktake** tab
  2. Enter physical counts
  3. System calculates variances
  4. Review and approve
  5. Update SOH

### 5. Reports

**Available Reports**:

1. **Batch Reports**: Variance analysis, history, cost summaries
2. **RM Reports**: Usage analysis, stock valuation, reorder lists
3. **Formula Cards**: Printable formula with cost breakdown
4. **Batch Tickets**: Production instructions with component list

**Printing**:
- Click **"Print"** on any report
- Format: Text or PDF (text for production tickets)
- Batch tickets match legacy `.PRN` format

## Keyboard Shortcuts

- `Ctrl+F`: Search/filter
- `Ctrl+N`: New record
- `Ctrl+S`: Save
- `Esc`: Close modal/cancel

## CSV Import/Export

### Raw Materials Import Format

```csv
code,desc1,desc2,sg,purchase_cost,usage_cost,soh,restock_level,hazard,condition
1,WATER.........,    ,1.000,0.00,0.00,1000.00,500.00,,
2,TOLUOL........,     ,0.867,5.00,5.00,500.00,250.00,R,
```

**Required Fields**: `code`, `desc1`

**Optional Fields**: All other fields (defaults applied)

### Export Format

Exports include all fields for backup or migration.

## Common Tasks

### Creating a Production Batch

1. Go to **Batch Processing** → **Plan** tab
2. Select formula (e.g., "850D" Rev. 1)
3. Enter target yield: 370 Lt
4. Review reserved materials
5. Click **"Create Batch"** → System generates batch number (e.g., "24149")
6. Print batch ticket (PDF/text)
7. Execute production
8. Record actuals in **Execute** tab
9. Enter QC results in **QC Testing** tab
10. Complete batch → System updates material SOH

### Performing a Stocktake

1. Go to **Stocktake** tab
2. Click **"Start Stocktake"**
3. For each material:
   - Enter physical count
   - Review variance (system - physical)
   - Approve or adjust
4. Click **"Update SOH"** → System saves changes
5. Generate variance report

### Adding a New Formula

1. Go to **Formulas** tab
2. Click **"New Formula"**
3. Enter formula code (e.g., "850D")
4. Enter formula name and yield
5. Add ingredients (from raw materials list)
   - Select material
   - Enter quantity (kg)
   - Repeat for all ingredients
6. Review theoretical cost (auto-calculated)
7. Save → Formula is ready for batch creation

### Importing QB Data

1. Ensure QB data files are in `legacy_data/` folder
2. Run import script:
   ```powershell
   python scripts\import_qb_data.py --dry-run  # Preview
   python scripts\import_qb_data.py           # Import
   ```
3. Review `out/audit.csv` for summary
4. Check `out/anomalies/` for errors

## Troubleshooting

### API Server Not Running

**Symptom**: "Demo Mode" banner in UI

**Solution**: Start API server with `.\scripts\dev.ps1 api`

### Materials Not Found Error

**Cause**: Raw material code doesn't exist

**Solution**: Add material first in Raw Materials tab

### Insufficient Stock Error

**Cause**: SOH < required quantity for batch

**Solution**: Adjust restock level or reorder materials

### Batch Creation Failed

**Cause**: Formula or product not found

**Solution**: Ensure formula is created and active

## Additional Resources

- **API Documentation**: `http://127.0.0.1:8000/docs` (Swagger UI)
- **Database Schema**: `docs/architecture.md`
- **Migration Guide**: `docs/qb_migration.md`

