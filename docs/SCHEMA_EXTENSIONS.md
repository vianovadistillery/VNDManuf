# TPManuf Schema Extensions - Finished Goods & Inventory Movements

**Date: 26 Oct 2025**

This document describes the new schema extensions for finished goods tracking, batch line snapshots, and inventory movements ledger.

## Summary of New Entities

### 1. `finished_goods` — Sellable Products
Master table for finished goods (products ready to sell).

**Fields:**
- `id` - UUID primary key
- `code` - Unique code (e.g., "FG-100", "TP-ACR-001")
- `description` - Product description
- `base_unit` - Default unit (LT or KG)
- `formula_id` - Optional link to default formula
- `formula_revision` - Formula revision number
- `is_active` - Active status
- `created_at`, `updated_at` - Timestamps

### 2. `finished_goods_inventory` — Stock on Hand
Tracks stock on hand for each finished good.

**Fields:**
- `fg_id` - Foreign key to finished_goods (primary key)
- `soh` - Stock on hand quantity

**Relationship:** One-to-one with `finished_goods`

### 3. `batch_lines` — Component Snapshots
Snapshot of materials used in each batch (captures theoretical vs actual).

**Fields:**
- `id` - UUID primary key
- `batch_id` - Foreign key to batches
- `material_id` - Foreign key to products (raw materials)
- `role` - Material role (resin/solvent/additive/etc)
- `qty_theoretical` - Expected quantity from formula (scaled by yield)
- `qty_actual` - Actual quantity used (operator adjustable)
- `unit` - Unit of measure (KG/LT/EA)
- `cost_at_time` - Cost capture

**Constraint:** Unique on (`batch_id`, `material_id`)

### 4. `inventory_movements` — Single Source of Truth Ledger
Complete audit trail for ALL stock changes (both raw materials and finished goods).

**Fields:**
- `id` - UUID primary key
- `ts` - UTC timestamp
- `date` - Business date (YYYY-MM-DD)
- `item_type` - 'RAW' or 'FG'
- `item_id` - Points to products.id (RAW) or finished_goods.id (FG)
- `qty` - Positive magnitude
- `unit` - Unit of measure
- `direction` - 'IN' or 'OUT'
- `source_batch_id` - Foreign key to batches (if movement from batch)
- `note` - Optional notes

**Indexes:**
- `ix_movements_item` - For fast lookups by item
- `ix_movements_date` - For date range queries
- `ix_movements_batch` - For batch traceability

### 5. Batch Status Extension
Added `batch_status` to `batches` table:
- `planned` - Batch is planned but not started
- `in_process` - Batch is currently being processed
- `closed` - Batch is completed and movements posted

## Data Flow

### Batch Commit Flow

When committing a batch:

```
1. Operator creates/updates batch
   ↓
2. Computes theoretical quantities from formula
   ↓
3. Upserts batch_lines (saves snapshot)
   ↓
4. For each batch_line:
   → Posts RAW OUT movement to inventory_movements
   ↓
5. Posts FG IN movement to inventory_movements
   ↓
6. Updates batch_status to 'closed'
```

### Stock Updates

Stock on hand is maintained via triggers (described in DDL section) that:
- Update `raw_materials.soh` for RAW movements
- Update `finished_goods_inventory.soh` for FG movements

## Usage Patterns

### Creating Finished Goods

```python
from app.adapters.db.models import FinishedGood, FinishedGoodInventory
from app.adapters.db import get_session

with get_session() as db:
    fg = FinishedGood(
        code="FG-100",
        description="Acrylic White Base",
        base_unit="LT",
        formula_id=formula.id,
        formula_revision=2,
        is_active=True
    )
    db.add(fg)
    db.flush()

    # Create inventory record
    fg_inv = FinishedGoodInventory(fg_id=fg.id, soh=Decimal("0"))
    db.add(fg_inv)
    db.commit()
```

### Posting Inventory Movements

```python
from app.adapters.db.models import InventoryMovement
from datetime import datetime

def post_raw_consumption(session, date, batch_id, material_id, qty, unit, note=None):
    """Post raw material consumption to ledger."""
    movement = InventoryMovement(
        date=date,
        item_type="RAW",
        item_id=material_id,
        qty=qty,
        unit=unit,
        direction="OUT",
        source_batch_id=batch_id,
        note=note or "Batch consumption"
    )
    session.add(movement)

def post_fg_production(session, date, batch_id, fg_id, qty, unit, note=None):
    """Post finished goods production to ledger."""
    movement = InventoryMovement(
        date=date,
        item_type="FG",
        item_id=fg_id,
        qty=qty,
        unit=unit,
        direction="IN",
        source_batch_id=batch_id,
        note=note or "Batch production"
    )
    session.add(movement)
```

### Querying Stock from Ledger

```python
# Get current stock for a raw material
select(st.func.sum(
    case(
        (InventoryMovement.direction == "IN", InventoryMovement.qty),
        else_=-InventoryMovement.qty
    )
)).where(
    and_(
        InventoryMovement.item_type == "RAW",
        InventoryMovement.item_id == material_id
    )
)

# Get finished goods stock
select(st.func.sum(
    case(
        (InventoryMovement.direction == "IN", InventoryMovement.qty),
        else_=-InventoryMovement.qty
    )
)).where(
    and_(
        InventoryMovement.item_type == "FG",
        InventoryMovement.item_id == fg_id
    )
)
```

### Creating Batch Lines

```python
from app.adapters.db.models import BatchLine

def create_batch_line(session, batch_id, material_id, qty_theoretical, unit, qty_actual=None):
    """Create or update batch line."""
    batch_line = BatchLine(
        batch_id=batch_id,
        material_id=material_id,
        qty_theoretical=qty_theoretical,
        qty_actual=qty_actual or qty_theoretical,
        unit=unit,
        role="ingredient"  # or "resin", "solvent", etc.
    )
    session.add(batch_line)
```

## Integration with Existing Schema

The new tables integrate with existing models:

- **Products** remain as raw materials and finished goods can reference them for ingredients
- **Batches** extended with `batch_status` and relationship to `batch_lines`
- **Inventory Lots** track raw material inventory (existing)
- **Inventory Movements** provide ledger for both RAW and FG inventory

## Benefits

1. **Complete Audit Trail** - Every stock change recorded in one place
2. **Stock Traceability** - Know exactly which batch produced/consumed each item
3. **Flexible Reporting** - Query movements by date, batch, item type
4. **Data Integrity** - Single source of truth for stock
5. **Performance** - Mirrored SOH fields for fast queries, ledger for accuracy

## Next Steps

1. ✅ Schema created
2. ✅ Migration applied
3. ⏳ Implement batch commit logic in services
4. ⏳ Create Dash UI pages for finished goods management
5. ⏳ Add inventory movements log view
6. ⏳ Implement stock queries from ledger

## Database Views (Future Enhancement)

The spec mentioned views for derived stock. These can be implemented as SQLAlchemy models:

```python
# v_raw_stock_derived view
from sqlalchemy import text

def get_raw_stock_derived(session, material_id):
    """Get derived stock from ledger."""
    result = session.execute(text("""
        SELECT
            material_id,
            COALESCE(SUM(CASE WHEN direction='IN' THEN qty ELSE -qty END), 0) as qty_net
        FROM inventory_movements
        WHERE item_type='RAW' AND item_id = :material_id
        GROUP BY material_id
    """), {"material_id": material_id})
    return result.fetchone()

# v_fg_stock_derived view
def get_fg_stock_derived(session, fg_id):
    """Get derived stock from ledger."""
    result = session.execute(text("""
        SELECT
            fg_id,
            COALESCE(SUM(CASE WHEN direction='IN' THEN qty ELSE -qty END), 0) as qty_net
        FROM inventory_movements
        WHERE item_type='FG' AND item_id = :fg_id
        GROUP BY fg_id
    """), {"fg_id": fg_id})
    return result.fetchone()
```

## Notes

- All quantities stored as `Numeric(12, 3)` for precision
- Units are flexible (KG, LT, EA, etc.)
- `inventory_movements.item_id` is a string UUID that references either products or finished_goods based on `item_type`
- Batch status tracking separate from batch completion time
- Relationships use appropriate cascade deletes for data integrity
