# Distillation Run Logging Specification

## 1. Current Manufacturing Capabilities

- `WorkOrderService` already orchestrates issuing inputs, creating outputs, booking inventory movements, and calculating actual cost using `InventoryService` and `InventoryMovement` rows.
- Work order inputs (`WorkOrderLine`) distinguish **material**, **overhead**, and timers (`WoTimer`) for labour; outputs (`WorkOrderOutput`) are tied to `Batch` records for downstream genealogy.
- Inventory adjustments always flow through `InventoryService.add_lot` or `InventoryService.move_inventory`, which ensures FIFO cost capture and links back to a `reference_type`/`reference_id` pair for audit.
- Assemblies (`Assembly`, `AssemblyLine`) and products (`Product`) already define relationships for BOM-style explosions; botanical blends and feed liquids can reuse these structures without schema changes.
- Costing and reporting expect discrete work orders with start/end timestamps; distillation must appear similar from accounting’s perspective so existing dashboards, cost rollups, and ledger exports remain valid.

## 2. Data Model & Persistence

### 2.1 Core Entities

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `distillation_runs` | Top-level record for each continuous still operation. | `id`, `code`, `status` (`open`, `running`, `paused`, `closed`), `still_id` (work center), `product_id` (intended product assembly), `open_at`, `close_at`, `notes`. |
| `distillation_periods` | Segment between botanical swaps; anchors DAQ summaries (duration, rates). | `id`, `run_id`, `botanical_product_id`, `started_at`, `ended_at`, `avg_feed_rate_lph`, `avg_product_rate_lph`, `record_source` (`manual`, `daq`). |
| `distillation_events` | Append-only log of operational events (feed additions, product draws, parameter snapshots). | `id`, `run_id`, `period_id` (nullable for pre-period events), `event_type`, `timestamp`, `payload_json`. |
| `distillation_materials` | Junction table tracking inventory impacts per run/period. | `id`, `run_id`, `period_id`, `product_id`, `direction` (`input`, `output`), `inventory_movement_id`, `qty_kg`, `uom`, `unit_cost`. |
| `distillation_parameters` (optional if event payloads suffice) | Pre-aggregated time-series for rapid UI queries. | `id`, `run_id`, `period_id`, `parameter_name`, `timestamp`, `value`. |

### 2.2 Migration Strategy

- Create migrations using Alembic batch mode with SQLite guards (per `scripts/run_migrations.ps1` workflow).
- Guard table creation and indexes with inspector checks before executing `op.create_table` / `op.create_index`.
- Index suggestions:
  - `ix_distillation_runs_status` on `(status, still_id)`.
  - `ix_distillation_events_run_ts` on `(run_id, timestamp)`.
  - `ix_distillation_materials_movement` on `inventory_movement_id`.
- Enforce constraint naming conventions (e.g., `pk_distillation_runs`, `fk_distillation_periods__run_id__distillation_runs`).
- Avoid schema overlap with existing work order tables to keep migrations isolated; reuse `Product.id` and `Batch.id` as foreign keys with inline definitions.

### 2.3 Domain Models / DTOs

- Add Pydantic schemas in `app/api/dto.py` mirroring work order DTOs:
  - `DistillationRunCreate`, `DistillationRunResponse`, `DistillationEventCreate`, `DistillationPeriodSummary`.
- SQLAlchemy models mirror the tables above, inheriting `AuditMixin` for `created_at`/`updated_at`.
- Provide enumerations for `DistillationEventType` (`feed_charge`, `product_draw`, `botanical_swap`, `parameter_snapshot`, `run_open`, `run_close`, `note`) to keep API stable.

## 3. Service Layer Workflows

- Introduce `DistillationService` in `app/services/distillation.py` leveraging `InventoryService` for all stock movements.
- **Open Run**
  - Validate still/work-center availability and ensure no other `open` run on the same still.
  - Optionally seed an initial botanical charge, generating a `distillation_event` and issuing inventory via `InventoryService.issue_material`.
  - Generate a run code using `BatchCodeGenerator` with a distinct prefix (e.g., `DST-YYYYMMDD-###`).
- **Record Feed Addition**
  - Accept feed product ID, quantity, source batch, location.
  - Create `InventoryMovement` (negative) tied to `distillation_materials` row (`direction=input`).
  - Append `distillation_event` with DAQ packet or manual entry metadata.
- **Record Product Draw / Vessel Change**
  - Optionally create or select a `Batch` representing the draw or downstream holding tank.
  - Use `InventoryService.add_lot` to receive output and tie cost to the run; store link in `distillation_materials` with `direction=output`.
  - Support incremental draws across the run; closing run aggregates totals via `distillation_materials`.
- **Botanical Swap / Period Close**
  - End current `distillation_period` with timestamps; freeze KPI metrics (yield, rates, ABV if provided).
  - Start a new `distillation_period` referencing the new botanical assembly.
  - Optionally auto-calculate consumption for the prior period by summing feed inputs minus product draws.
- **Parameter Capture**
  - Accept either high-frequency event stream (written to `distillation_events` as `parameter_snapshot`) or aggregated metrics (written to `distillation_parameters`).
  - Flag records with `record_source` to distinguish human vs DAQ entries.
- **Close Run**
  - Finalize all open periods, ensure inventory movements balance (inputs vs outputs).
  - Run costing rollup similar to `_recalculate_actual_cost`, summing `distillation_materials` cost to compute run-level actual cost, storing on `distillation_runs.actual_cost`.
  - Emit summary `InventoryMovement` if a final packaged batch should be created (e.g., transfer to holding tank).
  - Update status to `closed`, set `close_at`, and optionally trigger downstream reporting jobs.

## 4. DAQ Integration Contract

### 4.1 Transport Options

- **Direct API**: DAQ posts JSON packets to new endpoints:
  - `POST /distillation/runs/{run_id}/events` for streaming updates.
  - `POST /distillation/runs` to open/close runs if DAQ controls lifecycle.
- **File Drop**: DAQ exports JSONL/CSV to watched directory; scheduled job ingests and calls the same service functions.
- Start with API-first, retain file import as fallback for offline uploads.

### 4.2 Event Payload Schema (JSON)

```json
{
  "event_type": "feed_charge",
  "timestamp": "2025-11-10T09:15:04Z",
  "external_id": "DAQ12345",        // optional
  "period_ref": "PERIOD-3",        // optional period identifier
  "metrics": {
    "volume_l": 120.5,
    "mass_kg": 105.4,
    "feed_rate_lph": 60.2,
    "boiler_voltage_v": 230,
    "liquid_hex_temp_c": 78.4,
    "vapour_hex_temp_c": 89.1
  },
  "inventory": {
    "product_id": "feed-product-id",
    "batch_id": "optional-source-batch",
    "location_id": "feed-tank-1"
  },
  "notes": "operator annotated text"
}
```

Supported `event_type` values: `run_open`, `feed_charge`, `botanical_swap`, `parameter_snapshot`, `product_draw`, `run_close`, `note`. DAQ must send a `run_id` or include stable `external_run_code` so VNDManuf can correlate; ingestion maps to internal IDs.

### 4.3 Validation & Error Handling

- Reject events that would overdraw inventory unless flagged `allow_negative_inventory`.
- If a `period_ref` is new on `botanical_swap`, automatically create a `distillation_period`.
- Queue events in a staging table if inventory validation fails; expose reconciliation UI for operators.
- Provide idempotency via `external_id` to deduplicate retries.

## 5. UI & Reporting Requirements

- Add Dash layout (e.g., `apps/distillation/ui/run_monitor.py`) with:
  - Active run table (status, still, botanical, elapsed time, cumulative input/output, net yield).
  - Event timeline graphing feed/product rates and temperature traces.
  - Operator controls for manual event entry when DAQ is offline.
- Extend genealogy/product history screens to include distillation runs producing each batch (reusing work order genealogy view).
- Provide period-level summary report:
  - Duration, total feed mass/volume, total product, average rates, efficiency (% of theoretical yield).
  - Downloadable as CSV for compliance.
- Notifications: highlight runs exceeding expected parameter ranges or with missing close events.

## 6. Costing & Accounting Alignment

- Treat each `distillation_run` as a virtual work order for costing; when closed, generate a synthetic `WorkOrder` record (or reuse cost report pipeline) so downstream reports remain consistent.
- Inventory moves executed during the run immediately affect stock on hand; the run’s actual cost is the sum of issued materials plus overhead allocations configured per still/hour.
- For partial draws pushed to holding tanks, ensure the receiving lot references the distillation run for traceability (`reference_type="distillation_run"`).

## 7. Next Steps

1. Create Alembic migration scaffolding for the new tables following SQLite-safe patterns.
2. Implement service layer and API endpoints with unit tests covering event ingestion and cost reconciliation.
3. Collaborate with DAQ vendor to finalise payload schema and authentication (API key or mutual TLS).
4. Build Dash UI components and register callbacks after verifying component IDs.
5. Pilot with one still, gather operator feedback, iterate on KPIs and alerting thresholds.
