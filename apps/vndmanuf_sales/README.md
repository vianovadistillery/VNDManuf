# VNDManuf Sales Module

The Sales module extends VNDManuf with non-invoicing sales tracking: channels, customers, orders, analytics, and CSV import/export.

## Setup

1. Apply migrations (SQLite-safe):
   ```
   scripts/run_migrations.ps1
   ```
2. The Dash UI automatically mounts a `Sales` tab via `app/ui/app.py`.

## Database & Migrations

- Core revision: `db/alembic/versions/ae5d77380b60_create_sales_core.py`
- Key tables: `sales_channels`, `pricebooks`, `pricebook_items`, `sales_orders`, `sales_order_lines`, `sales_tags`, `sales_order_tags`, `customer_sites`.
- Existing `customers` and `sales_orders` are extended with enums/totals — all wrapped in batch mode for SQLite.
- Run drift checks:
  ```
  python scripts/alembic_check_safe.py
  ```

## Service Layer

Located in `apps/vndmanuf_sales/services/`:

- `pricing.py`: resolves unit prices (pricebooks, fallbacks, GST pairing).
- `totals.py`: recomputes order totals, aggregates sales vs. inventory.
- `import_sales_csv.py`: validates/loads CSV orders; see fixture below.

Unit tests live in `tests/test_sales_services.py`.

## Dash UI

- Top-level tab in `app/ui/app.py` renders via `apps/vndmanuf_sales/ui/sales_tab.py`.
- Sub-tabs under `apps/vndmanuf_sales/ui/pages/` (overview, orders, customers, products, analytics, import/export, settings).
- `tests/test_sales_ui_callbacks.py` smoke tests the layout.

## CSV Import Fixture

- `apps/vndmanuf_sales/data/sample_sales_orders.csv` provides 200 sample rows with required columns:
  ```
  order_date,channel,customer,site_name,product_code,qty,unit_price_ex_gst,unit_price_inc_gst,order_ref,notes
  ```

## Common Analytics Queries

Example SQL snippets:

- Monthly revenue (Inc GST):
  ```sql
  SELECT strftime('%Y-%m', order_date) as month,
         SUM(total_inc_gst) as revenue_inc_gst
  FROM sales_orders
  WHERE deleted_at IS NULL
  GROUP BY month
  ORDER BY month;
  ```
- Top customers by revenue:
  ```sql
  SELECT c.name, SUM(o.total_inc_gst) as revenue
  FROM sales_orders o
  JOIN customers c ON o.customer_id = c.id
  WHERE o.deleted_at IS NULL
  GROUP BY c.name
  ORDER BY revenue DESC
  LIMIT 10;
  ```

## End-to-End Smoke Flow

1. `alembic upgrade head`
2. Run services/UI tests:
   ```
   pytest tests/test_sales_services.py tests/test_sales_ui_callbacks.py
   ```
3. Import sample CSV via Dash Import/Export tab or programmatically with `SalesCSVImporter`.
