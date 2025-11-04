# Work Orders & Batch Manufacturing — Implementation Spec (VNDManuf)

**Owner:** Via Nova Distillery
**Scope:** Production Work Order (WO) system that bridges product definitions (Products/Assemblies/Recipes) with execution (materials issues, production, QC, costs, batch codes, inventory moves).
**Targets:** Python (SQLAlchemy), Alembic, SQLite (later Postgres), Dash UI

## 0. Principles

- **Definition vs Execution:** Products/Assemblies define "how to make it". Work Orders record "what was actually made".
- **Actuals Beat Standards:** Planned (from assemblies) → adjusted by actuals → cost roll-up uses FIFO costs + real overheads.
- **Traceability:** Every finished batch must be traceable to input batches (lot genealogy).
- **Idempotent Inventory Moves:** All increases/decreases flow through a single `inventory_movements` table.
- **Composable Costs:** Overheads (canning, energy, labor, fixed/variable) can be line items or captured at WO close.

## 1. Database Schema

### 1.1 work_orders

Extended with:
- `planned_qty` (Numeric) - From planned run size
- `uom` (Text) - Unit of measure (e.g., L, can, bottle)
- `work_center` (Text) - e.g., Still01, Canning01
- `start_time` (Timestamp) - Set on in_progress
- `end_time` (Timestamp) - Set on complete
- `batch_code` (Text, UNIQUE) - Generated batch code
- `status` - Updated to: `draft`, `released`, `in_progress`, `hold`, `complete`, `void`

### 1.2 work_order_lines (inputs)

Extended with:
- `component_product_id` (FK) - Component product
- `planned_qty` (Numeric) - From assembly explosion
- `actual_qty` (Numeric) - Set on issue/close
- `uom` (Text) - Unit of measure
- `source_batch_id` (FK → batches.id) - If batch-tracked input
- `unit_cost` (Numeric) - FIFO snapshot at issue
- `line_type` (Text) - `material` or `overhead`
- `note` (Text) - Optional note

### 1.3 work_order_outputs

New table:
- `id` (UUID, PK)
- `work_order_id` (FK)
- `product_id` (FK)
- `qty_produced` (Numeric)
- `uom` (Text)
- `batch_id` (FK → batches.id)
- `unit_cost` (Numeric) - Set at cost roll-up
- `scrap_qty` (Numeric) - Optional
- `note` (Text)

### 1.4 batches

Extended to support both work-order-specific and generalized batches:
- `product_id` (FK, nullable) - For generalized batches
- `work_order_id` (FK, nullable) - Made nullable
- `batch_code` (Text, UNIQUE) - Global unique constraint
- `mfg_date` (Date)
- `exp_date` (Date)
- `status` - Updated to: `open`, `quarantined`, `released`, `closed`
- `meta` (JSON) - e.g., ABV, genealogy

### 1.5 inventory_movements

Extended with:
- `batch_id` (FK → batches.id, nullable)
- `timestamp` (DateTime) - Alias for ts
- `uom` (Text) - Alias for unit
- `move_type` (Text) - `wo_issue`, `wo_completion`, `receipt`, etc.
- `ref_table` (Text) - e.g., 'work_orders'
- `ref_id` (Text) - Reference ID
- `unit_cost` (Numeric) - Cost at time of move

### 1.6 wo_qc_tests

New table:
- `id` (UUID, PK)
- `work_order_id` (FK)
- `test_type` (Text) - 'ABV', 'fill', etc.
- `result_value` (Numeric) - Numeric result
- `result_text` (Text) - Text result
- `unit` (Text) - %, pH, NTU
- `status` (Text) - `pending`, `pass`, `fail`
- `tested_at` (Timestamp)
- `tester` (Text)
- `note` (Text)

### 1.7 wo_timers

New table:
- `id` (UUID, PK)
- `work_order_id` (FK)
- `timer_type` (Text) - 'still_runtime', etc.
- `seconds` (Integer)
- `rate_per_hour` (Numeric)
- `cost` (Numeric) - Derived: seconds/3600*rate

### 1.8 product_cost_rates

New table:
- `id` (UUID, PK)
- `rate_code` (Text, UNIQUE) - e.g., CANNING_LINE_STD_HOURLY
- `rate_type` (Text) - 'hourly', 'per_unit', 'fixed'
- `rate_value` (Numeric)
- `uom` (Text) - e.g., AUD/hour
- `effective_from` (Date)
- `effective_to` (Date, nullable)

### 1.9 batch_seq

New table (sequence for batch codes):
- `id` (UUID, PK)
- `product_id` (FK)
- `date` (Text) - YYYYMMDD
- `seq` (Integer)
- Unique constraint: (product_id, date)

## 2. Status Machine

```
draft → released → in_progress → complete
             |             |
            hold         hold
```

- **draft:** Planned qty, batch template, can delete.
- **released:** Inputs reserved (optional), no inventory movement yet.
- **in_progress:** Material issues allowed; timers, QC running.
- **hold:** Block moves; used when QC/permit fails.
- **complete:** All movements posted, costed, batch released; immutable except admin reversal.
- **void:** Cancelled before any postings.

## 3. Core Workflows

### 3.1 Create & Plan WO

User selects `product_id`, `planned_qty`. System explodes assembly to `work_order_lines` (planned_qty). Pre-generate `batch_code` (placeholder). Status = `draft`.

### 3.2 Release WO

Validate ingredients available (optional hard/soft constraint). Lock recipe revision used. Status = `released`.

### 3.3 Start Production

Set `start_time`, status = `in_progress`. Start `wo_timers` if used.

### 3.4 Issue Materials (Actuals)

For each input line:
- Operator records `actual_qty` by batch (scan/select).
- System posts `inventory_movements` negatives with `move_type='wo_issue'`.
- Unit cost from FIFO at draw time is stored on the move and on `work_order_lines.unit_cost`.

### 3.5 Record QC

Insert `wo_qc_tests` rows; gate complete on required tests pass. ABV/fill checks feed `batches.meta`.

### 3.6 Complete WO (Post Outputs & Cost Roll-Up)

Validate required QC pass, required inputs issued, and permissives.

**Cost Roll-Up:**
- `material_cost = Σ(|issue_qty| × issue_unit_cost)`
- `overhead_cost = Σ(wo_input lines with line_type='overhead') + Σ(timer.cost)`
- `total_cost = material_cost + overhead_cost`
- `unit_cost = total_cost / qty_produced`

Write `work_order_outputs.unit_cost = unit_cost`, persist to positive move's `unit_cost`. Status = `complete`, stamp `end_time`, mark `batch.status = released`.

## 4. Batch, Codes & Genealogy

### 4.1 Batch Code Format

`{SITE}-{PROD}-{YYYYMMDD}-{SEQ}`

Example: `VND-GIN42-20251104-03`

Deterministic per day + product; maintain sequence table (`batch_seq`).

### 4.2 Genealogy View

From `inventory_movements` for a given `work_order_outputs.batch_id`, collect all `wo_issue` moves and their `batch_ids`. Store aggregated JSON in `batches.meta["genealogy"]` on close for fast display.

### 4.3 Compliance Flags

`batches.status = quarantined` until QC pass. Prevent `wo_completion` posting if `wo_qc_tests` required rows not pass.

## 5. Costing Rules

- FIFO for materials (already in system).
- Overheads:
  - Option A: Model as pseudo-components (`work_order_lines.line_type='overhead'`) with `actual_qty` (e.g., hours, litres of steam) × rate.
  - Option B: Derive from `wo_timers` with `rate_code`.
- Byproducts/Scrap: Model a negative overhead line (credit) or a secondary output line in `work_order_outputs` (multi-output supported).
- Unit Cost Freezing: Once WO complete, the `unit_cost` on the completion move is the canonical cost for that batch.

## 6. API Endpoints

- `POST /api/v1/work-orders` - Create work order
- `GET /api/v1/work-orders` - List with filters (status, date, product)
- `GET /api/v1/work-orders/{id}` - Get detail
- `POST /api/v1/work-orders/{id}/release` - Release work order
- `POST /api/v1/work-orders/{id}/start` - Start production
- `POST /api/v1/work-orders/{id}/issues` - Issue material
- `POST /api/v1/work-orders/{id}/qc` - Record QC
- `POST /api/v1/work-orders/{id}/overheads` - Apply overhead
- `POST /api/v1/work-orders/{id}/complete` - Complete work order
- `POST /api/v1/work-orders/{id}/void` - Void work order (admin only)
- `GET /api/v1/work-orders/{id}/costs` - Cost breakdown
- `GET /api/v1/work-orders/{id}/genealogy` - Batch genealogy

## 7. Service Layer

Key functions in `app/services/work_orders.py`:

- `create_work_order(product_id, planned_qty, work_center)` → work_order
- `explode_assembly_to_inputs(work_order_id)` → None
- `release_work_order(work_order_id)` → None
- `start_work_order(work_order_id)` → None
- `issue_material(work_order_id, component_product_id, qty, source_batch_id)` → move_id
- `record_qc(work_order_id, test_type, result_value, status)` → None
- `apply_overhead(work_order_id, rate_code, basis_qty=None, seconds=None)` → input_line_id
- `complete_work_order(work_order_id, qty_produced, batch_attrs: dict)` → (output_move_id, batch_id)
- `void_work_order(work_order_id, reason)` → None

## 8. Domain Rules

### 8.1 FIFO Cost Peek

`fifo_peek_cost(lots, batch_id=None)` - Get FIFO unit cost without consuming inventory.

### 8.2 Batch Code Generation

`generate_batch_code(product_id, site_code='VND')` - Generates deterministic batch codes using `batch_seq` table.

### 8.3 Status Validation

`validate_wo_status_transition(from_status, to_status)` - Enforces valid status transitions.

## 9. Testing Checklist

- [ ] Create WO → inputs populated correctly from assembly (scale by planned qty).
- [ ] Issue partial materials, complete later; costs average correctly.
- [ ] Multi-batch issue of same component aggregates costs properly.
- [ ] QC fail blocks completion; pass enables.
- [ ] Overhead by timers vs fixed rate produce same totals when equivalent.
- [ ] Completion posts positive move with frozen unit_cost.
- [ ] Genealogy shows all input batch_ids.
- [ ] Reversal/void creates compensating moves and locks original.

## 10. Migration Strategy

1. Create Alembic migration with all schema changes
2. Data migration: existing `WorkOrderLine` → extend with new fields (copy data, add defaults)
3. Existing `Batch` records: add `product_id` from `work_order.product_id`
4. Existing `InventoryMovement`: migrate to new structure (map direction to move_type)
5. No data loss: all existing data preserved with new fields nullable where needed

## 11. Implementation Notes

- All inventory movements flow through `InventoryMovement` (extended)
- FIFO costs captured at issue time and stored on moves and input lines
- Cost roll-up: `material_cost + overhead_cost / qty_produced = unit_cost`
- Batch codes generated deterministically via `BatchSeq`
- Genealogy stored in `batches.meta["genealogy"]` JSON on completion
- Status machine enforced in service layer with validation
- QC tests gate completion (required tests must pass)
- All quantities stored in kg (canonical), UOM stored for display

## 12. Open Questions (assumptions we implemented)

- Canning costs: Supported both as pseudo-component overhead lines and timer-based rates.
- Multi-output WOs: Supported; `work_order_outputs` can have multiple rows (e.g., primary + byproduct).
- Reservations: Not implemented (soft validation only). Add `reserved_qty` in future if needed.
- Scrap/Rework: Use `scrap_qty` or secondary output + negative overhead.

## 13. Performance & Indexing

Frequent filters:
- `work_orders(status)`
- `inventory_movements(ref_table, ref_id)`
- `batches(product_id, status)`

Genealogy queries should use `(ref_table='work_orders' AND ref_id=:wo_id AND move_type='wo_issue')`.

## 14. Security/Permissions (minimal)

- Only users with role in ('operator','supervisor','admin') can `issue_material` or `complete_work_order`.
- `admin` required to `void_work_order` or edit costs post-completion.

---

**End of Spec** ✅
