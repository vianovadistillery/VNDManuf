# QuickBASIC to TPManuf Migration Guide

## Overview

This guide documents the migration process from the legacy QuickBASIC TPManuf system to the modern Python-based application.

## Prerequisites

1. **Legacy QB Files**: Ensure all QB data files are backed up
2. **Python Environment**: Python 3.12+ with virtual environment
3. **Database**: SQLite (dev) or PostgreSQL (prod)
4. **QB Data Files**: Located in `legacy_data/` folder

## Migration Process

### Phase 1: Data Export

**No action required** - QB files are already in binary format compatible with the parser.

**Required files**:
- `MSRMNEW.MSF` - Raw materials
- `MSBATCH.MSF` or `MSBATCH*.HST` - Batch history
- `FORHED.ASF` or dataset-specific (`BRIhed.asf`, etc.) - Formula headers
- `FORDET.ASF` - Formula detail lines
- `MSMISC.MSF` - Configuration data

**Location**: `legacy_data/` folder

### Phase 2: Data Import

#### Step 1: Setup Environment

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create database tables
.\scripts\dev.ps1 db
```

#### Step 2: Dry Run Import

Preview the import without writing to database:

```powershell
python scripts\import_qb_data.py --dry-run
```

This will:
- Parse all QB files
- Display summary statistics
- Generate `out/audit.csv`
- Report anomalies in `out/anomalies/*.csv`
- **NOT write to database**

#### Step 3: Review Anomalies

Check `out/anomalies/*.csv` for:
- Missing referenced records (formulas → raw materials)
- Invalid data types
- Out-of-range values
- Duplicate codes

**Common issues**:
- Raw material codes missing from MSRMNEW.MSF
- Formula lines referencing non-existent materials
- Batch references to invalid formulas

**Fix options**:
1. Update QB data files and re-import
2. Use `--allow-anomalies` to skip errors
3. Manually correct in new system after import

#### Step 4: Full Import

Run the actual import:

```powershell
python scripts\import_qb_data.py
```

**Without `--allow-anomalies`**: Import stops at first error
**With `--allow-anomalies`**: Logs errors but continues

```powershell
python scripts\import_qb_data.py --allow-anomalies
```

**Output**:
- `out/audit.csv` - Summary of imported records
- `out/anomalies/*.csv` - Error details

#### Step 5: Validate Import

Check imported data:

```powershell
python scripts\check_qb_import.py
```

This queries the database and displays:
- Raw material count
- Formula count
- Batch count
- Sample records

### Phase 3: Data Validation

#### Compare Record Counts

**QB System** (manual count):
- Raw materials: X
- Formulas: Y
- Batches: Z

**New System**:
```sql
SELECT COUNT(*) FROM raw_materials;
SELECT COUNT(*) FROM formulas;
SELECT COUNT(*) FROM batches;
```

**Expected**: Slight differences due to:
- QB inactive/deleted records
- Invalid references excluded
- Duplicate codes (first one kept)

#### Validate Calculations

**Test Scenarios**:

1. **Formula cost calculation**
   - Select a formula in UI
   - Compare theoretical cost to QB calculation
   - Tolerance: ±0.01%

2. **SG conversions**
   - Create a batch
   - Check kg ↔ litres conversion
   - Verify matches QB logic

3. **FIFO stock issue**
   - Check material reservations for batch
   - Verify oldest lots consumed first
   - Compare to QB FIFO behavior

4. **Batch variance**
   - Record actual production
   - Compare variance % to QB
   - Tolerance: ±0.1%

#### Generate Reports

**Batch tickets**:
1. Navigate to Batch Reports
2. Select a batch
3. Click "Print Batch Ticket"
4. Compare to `.PRN` file from QB

**Formula cards**:
1. Navigate to Formulas
2. Select a formula
3. Click "Print Formula Card"
4. Compare to QB formula print

**Stock reports**:
1. Navigate to RM Reports
2. Generate usage report (YTD)
3. Compare to QB usage report
4. Verify totals match

### Phase 4: User Acceptance

#### Test Workflows

**1. Create Raw Material**
- Add new material via UI
- Verify SOH tracking
- Check restock alerts

**2. Create Formula**
- Enter formula with 5+ ingredients
- Verify cost calculation
- Check line sequencing

**3. Process Batch**
- Create batch from formula
- Record actual production
- Enter QC results
- Verify variance calculation
- Check material SOH updated

**4. Stocktake**
- Enter physical counts
- Review variances
- Approve changes
- Verify SOH updated

**5. Generate Reports**
- Batch history report
- RM usage report
- Stock valuation report
- Export to CSV
- Print batch ticket

#### Parallel Run (Optional)

Run both systems concurrently for 1-2 weeks:
- Process real batches in both systems
- Compare outputs daily
- Document any discrepancies
- Fix issues in new system
- Build user confidence

### Phase 5: Cutover

#### Pre-Cutover Checklist

- [ ] All data validated
- [ ] User training completed
- [ ] Reports match QB output
- [ ] Backup of QB data created
- [ ] Backup of new database created
- [ ] Production environment configured
- [ ] Go-live date scheduled

#### Cutover Steps

1. **Final Data Import**
   ```powershell
   # Backup current database
   copy app.db app.db.backup

   # Import latest QB data
   python scripts\import_qb_data.py

   # Validate
   python scripts\check_qb_import.py
   ```

2. **Start Production Servers**
   ```powershell
   # Start API (background)
   .\scripts\dev.ps1 api

   # Start UI (background)
   .\scripts\dev.ps1 ui
   ```

3. **Verify System Ready**
   - API health check: `http://127.0.0.1:8000/health`
   - UI access: `http://127.0.0.1:8050`
   - Test login (if auth enabled)
   - Check all tabs load

4. **Announce Go-Live**
   - Notify all users
   - Provide access credentials
   - Share user guide

5. **Monitor First Day**
   - Monitor for errors
   - Answer user questions
   - Fix critical issues immediately
   - Document non-critical issues

#### Post-Cutover

**Week 1**:
- Daily check-ins with users
- Address reported issues
- Review log files for errors
- Compare batches to expected

**Week 2**:
- User feedback survey
- Performance review
- Finalize documentation
- Decommission QB system

## Rollback Plan

### If Critical Issues Arise

1. **Immediate Rollback**:
   - Stop new system servers
   - Restore QB system
   - Notify users to continue on QB

2. **Data Recovery**:
   - Export recent batches from new system
   - Manual entry into QB system
   - Or re-import after fixing issues

3. **Investigation**:
   - Identify root cause
   - Fix issue in new system
   - Test thoroughly
   - Re-attempt cutover

### Rollback Timing

**First 24 hours**: Immediate rollback available
**First week**: QB system remains on standby
**After week 1**: Cutover considered permanent

## Data Mapping Reference

### QB to SQLAlchemy Models

**Raw Materials** (`MSRMNEW.MSF` → `raw_materials`):
- `no` → `code`
- `Desc1` → `desc1`
- `Desc2` → `desc2`
- `Search` → `search_key`
- `Sg` → `sg`
- `PurCost` → `purchase_cost`
- `PurUnit` → `purchase_unit`
- `UseCost` → `usage_cost`
- `UseUnit` → `usage_unit`
- (see full mapping in `docs/legacy/qb_data_dictionary.csv`)

**Formulas** (`FORHED.ASF` → `formulas`):
- Formula code + revision + dataset
- Yield, type (S/W), class
- Related formulas table

**Formula Lines** (`FORDET.ASF` → `formula_lines`):
- Sequence, raw material code, quantity
- Comments, special instructions

**Batches** (`MSBATCH.MSF` → `batches`):
- Batch number (year + sequence)
- Formula reference, dates
- Yield (theoretical, actual)
- QC results (86+ fields)
- Material consumption

## Field Calculations

### Specific Gravity (SG)

**QB Formula**: `vol_solid × (solid_sg - 1) + 1`

**New System**: Stored as-is, used for conversions

**Conversion**:
```python
# Mass to volume
volume_l = mass_kg / sg

# Volume to mass
mass_kg = volume_l × sg
```

### Yield Variance

**QB Formula**: `(actual - theoretical) / theoretical × 100`

**New System**: Same calculation

**Tolerance**: ±5% (configurable)

### FIFO Issue

**QB Logic**: Oldest lot first, consume until qty satisfied

**New System**: Same logic
```python
lots = sorted_by_received_date()
for lot in lots:
    if required_qty <= 0:
        break
    qty_from_lot = min(lot.quantity, required_qty)
    issue_lot(qty_from_lot)
    required_qty -= qty_from_lot
```

## Troubleshooting

### Common Import Errors

**"Record contains duplicate key"**
- Solution: Use `upsert=True` or skip duplicates

**"Material code X not found"**
- Cause: Formula line references non-existent material
- Solution: Add material to QB data or use `--allow-anomalies`

**"Invalid SG value"**
- Cause: SG < 0 or > 10 (unreasonable)
- Solution: Validate QB data or use default SG = 1.0

**"Out of range quantity"**
- Cause: Negative or zero quantities
- Solution: Skip invalid records or use `--allow-anomalies`

### Performance Issues

**Slow import** (>5 minutes)
- Cause: Large files (>100MB)
- Solution: Use batch inserts (already implemented)

**Memory errors**
- Cause: Very large files (>500MB)
- Solution: Process in chunks

## Support

**Technical Issues**: See `docs/architecture.md`
**User Questions**: See `docs/user_guide.md`
**API Reference**: `http://127.0.0.1:8000/docs`

## Appendix: QB File Formats

### MSRMNEW.MSF (Raw Materials)

- Record size: ~300 bytes
- Number of records: Varies by installation
- Encoding: CP437 (DOS)
- Endianness: Little-endian

**Key Fields** (offset, type, length):
- 0-1: `no` (INTEGER)
- 2-26: `Desc1` (STRING * 25)
- 27-51: `Desc2` (STRING * 25)
- 52-53: `purqty` (INTEGER)
- 54-58: `Search` (STRING * 5)
- 59-62: `Sg` (SINGLE)
- ... (see `app/adapters/qb_parser.py`)

### MSBATCH.MSF (Batches)

- Record size: 512 bytes
- Number of records: Historical batches
- Contains: Production data, QC results

**Key Fields**:
- `bno` (INTEGER)
- `year` (STRING * 2)
- `formula_code` (STRING * 4)
- `revision` (INTEGER)
- `yield_theoretical` (SINGLE)
- `yield_actual` (SINGLE)
- QC fields (SG, viscosity, pH, etc.)
