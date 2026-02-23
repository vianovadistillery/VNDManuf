# Distillation DAQ → VNDManuf Integration Specification

## Overview

This document defines the contract between the distillation DAQ system and VNDManuf after the distillation run logging feature has been implemented. It covers lifecycle sequencing, payload formats, authentication, retry semantics, and validation expectations so the DAQ-side agent can implement automated exports with minimal ambiguity.

Key design principles:

- **Event-driven**: Every material or telemetry change is posted as an event; VNDManuf reconstructs inventory movements and KPIs server-side.
- **Idempotent**: All POSTs accept an `external_id` to deduplicate retries.
- **Traceable**: Inventory movements link back to runs; DAQ must supply batch/product identifiers for reconciliation.
- **Resilient**: Offline fallback via file export is preserved with the same schema.

## API Endpoints

| Operation | Method & Path | Purpose |
|-----------|---------------|---------|
| Open Run | `POST /api/v1/distillation/runs` | Create/open a run and optionally seed initial botanicals. |
| List Runs | `GET /api/v1/distillation/runs?status=<status>&limit=<n>` | Retrieve recent runs for monitoring/debug. |
| Record Event | `POST /api/v1/distillation/runs/{run_id}/events` | Append feed/product/botanical/telemetry events. |
| Close Run | `POST /api/v1/distillation/runs/{run_id}/close` or `PATCH /api/v1/distillation/runs/{run_id}` with `status=closed` | Finalise a run, locking cost rollups. |
| Get Run | `GET /api/v1/distillation/runs/{run_id}` | Return full run including events/materials. |

### Authentication

- API key header `x-api-key: <token>` (configurable in VNDManuf `.env`).
- Keys managed in `settings.api.auth_tokens`. DAQ service must store securely.
- Optional mutual TLS for on-prem deployments (coordinate certificate exchange if required).

### Common Headers

```
Content-Type: application/json
Accept: application/json
x-api-key: <shared-secret>
```

## Payload Schemas

### 1. Open Run

```json
{
  "still_code": "Still-01",
  "product_id": "finished-gin-id",
  "code": "DST-B250123",        // optional override (else auto-generated)
  "external_run_code": "DAQ-RUN-20251111-01",
  "notes": "Morning run",
  "initial_botanical_product_id": "botanical-mix-a",
  "started_at": "2025-11-11T07:30:00Z"
}
```

Response includes `id` (UUID) which must be stored for subsequent events. If DAQ cannot persist IDs, it may query by `external_run_code` to resolve the run.

### 2. Event Stream

```
POST /api/v1/distillation/runs/{run_id}/events
```

```json
{
  "event_type": "feed_charge",
  "timestamp": "2025-11-11T09:15:04Z",
  "period_id": null,
  "period_ref": "BOT-SESSION-3",
  "botanical_product_id": "botanical-mix-a",
  "metrics": {
    "feed_rate_lph": 58.4,
    "boiler_voltage_v": 228.0,
    "liquid_hex_temp_c": 79.6,
    "vapour_hex_temp_c": 88.9
  },
  "notes": "Operator override",
  "external_id": "EVENT-000123",
  "source": "daq",
  "inventory": {
    "product_id": "wash-feed-id",
    "qty_kg": 120.5,
    "uom": "KG",
    "batch_id": "wash-lot-20251110",
    "location_id": "FeedTank-01",
    "unit_cost": 8.45,
    "direction": "input",
    "note": "Charged from FeedTank-01"
  }
}
```

`event_type` values:
- `run_open`, `feed_charge`, `botanical_swap`, `parameter_snapshot`, `product_draw`, `run_close`, `note`.

Direction defaults: feeds → `input`, product draws → `output`. Supply explicitly if diverging from defaults.

`metrics` supports arbitrary numeric/string values; VNDManuf stores them JSON plus normalises `parameter_snapshot` values into the `distillation_parameters` table.

### 3. Close Run

```
POST /api/v1/distillation/runs/{run_id}/close
```

or

```json
PATCH /api/v1/distillation/runs/{run_id}`
{
  "status": "closed",
  "close_at": "2025-11-11T17:45:00Z",
  "notes": "Run completed without incident."
}
```

VNDManuf will automatically end active periods, recalculate costs, and emit a closing event.

## Lifecycle Sequence

1. **Open Run** – DAQ calls `POST /runs` (captures still, botanical, start time).
2. **Botanical Swap** – send `botanical_swap` event to terminate prior period and start new period with `botanical_product_id`.
3. **Feed Additions** – `feed_charge` event with inventory payload; VNDManuf issues inventory and links `InventoryMovement`.
4. **Product Draws** – `product_draw` event with receiving batch info; VNDManuf receives into holding lot.
5. **Telemetry** – periodic `parameter_snapshot` events; DAQ may batch (per-minute, per-5min).
6. **Run Close** – call `POST /close` or patch status; optional final summary event.

## Validation & Error Handling

- **HTTP 2xx** – success (response body includes run/event objects).
- **HTTP 422** – validation errors (missing product, invalid quantities). DAQ must log and re-present to operators.
- **HTTP 409** – conflicting state (e.g., closing already closed run).
- **HTTP 5xx** – transient; queue for retry with exponential backoff (recommended schedule: 1m, 5m, 15m, 1h).

All requests should include an `external_id`; VNDManuf discards duplicates gracefully.

### Inventory Guardrails

- Negative inventory allowed only when product is flagged `allow_negative_inventory=True`. If movement would overdraw, API responds 422 with message `Insufficient stock`.
- Provide `batch_id` for outputs when possible; otherwise VNDManuf creates internal lot keyed to run.

## Offline File Export (Fallback)

- Format: JSON Lines (`.jsonl`), each line identical to POST payload.
- File naming: `distillation_run_<external-code>_<yyyymmddHHMM>.jsonl`.
- Drop location: shared network path `\\vnd-app\daq_exports`.
- VNDManuf ingestion job (cron) reads pending files, replays events using same API service layer, then moves files to `processed/` or `error/`.

## Testing Matrix

| Scenario | DAQ Action | Expected Outcome |
|----------|------------|------------------|
| Open run with initial botanicals | POST `/runs` | Run status `running`, period created, event `run_open`. |
| Feed addition | POST event `feed_charge` | InventoryMovement created (negative qty), distillation_material `input`. |
| Product draw | POST event `product_draw` | InventoryMovement created (positive qty), distillation_material `output`. |
| Botanical swap | POST event `botanical_swap` | Previous period `ended_at` set, new period created. |
| Parameter snapshot | POST event `parameter_snapshot` | Metrics stored JSON + individual rows in `distillation_parameters`. |
| Duplicate event (same `external_id`) | Retry POST | API returns 2xx with existing event, no duplicates. |
| Invalid stock | feed exceeding stock | HTTP 422 with message; event queued for operator resolution. |

QA should execute flows in staging using both direct HTTP (Postman) and DAQ export to ensure parity.

## DAQ Implementation Checklist

- [ ] Persist VNDManuf run UUID returned from `POST /runs` (or resolve by `external_run_code`).
- [ ] Map DAQ sensor channels to payload metrics and units.
- [ ] Convert tank mass/volume to kg before posting (shared density table).
- [ ] Handle API key rotation (reload from secure store without restart).
- [ ] Implement retry queue with idempotent `external_id`.
- [ ] Provide operator-visible error log for rejected events.
- [ ] Support offline JSONL export and reprocessing.
- [ ] Include automated integration test hitting VND staging API nightly.

## Appendix A – Sample JSONL Export

```
{"event_type":"run_open","timestamp":"2025-11-11T07:30:00Z","external_id":"RUN-START-01","source":"daq","metrics":{"operator":"Alice"}}
{"event_type":"feed_charge","timestamp":"2025-11-11T08:10:00Z","external_id":"EVENT-0001","inventory":{"product_id":"wash-feed-id","qty_kg":95.2,"batch_id":"wash-lot-20251110","uom":"KG","direction":"input"}}
{"event_type":"product_draw","timestamp":"2025-11-11T11:45:00Z","external_id":"EVENT-0002","inventory":{"product_id":"hearts-output","qty_kg":68.4,"batch_id":"hearts-lot-20251111","uom":"KG","direction":"output"}}
{"event_type":"botanical_swap","timestamp":"2025-11-11T12:00:00Z","external_id":"EVENT-0003","botanical_product_id":"botanical-mix-b"}
{"event_type":"parameter_snapshot","timestamp":"2025-11-11T12:05:00Z","external_id":"EVENT-0004","metrics":{"vapour_hex_temp_c":88.7,"boiler_voltage_v":229.1}}
{"event_type":"run_close","timestamp":"2025-11-11T17:40:00Z","external_id":"RUN-END-01"}
```

This sample can be replayed via API or ingested via the file watcher.
