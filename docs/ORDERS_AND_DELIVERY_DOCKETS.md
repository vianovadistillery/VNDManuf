# Orders and Delivery Dockets — Front End and Flow

## Intent

- **Order front end**: UI to manage orders/sales, populate delivery dockets, generate PDFs, and print.
- **Tracking**: Orders and delivery dockets are stored in the database; generated PDFs are tracked in `generated_documents`.

## Database

- **customers** — Customer master (code, name, address, etc.).
- **sales_orders** — Orders (optional; can create delivery dockets from orders or ad hoc).
- **delivery_dockets** — Delivery docket headers (customer, docket number, date, status).
- **delivery_docket_lines** — Line items (product, quantity, UOM).
- **generated_documents** — Generated PDF/DOCX (path, status, link to customer/docket/order).

## API (FastAPI)

Base prefix: `/api/v1`.

### Documents (mail-merge → PDF)

| Method | Endpoint | Purpose |
|--------|----------|--------|
| POST | `/documents/generate` | Generate PDF (and optional DOCX). Body: `template_name`, `doc_type`, `delivery_docket_id` or `quote_id` (sales_order_id) or `customer_id` + `line_specs`, optional `overrides`, `async_job`. |
| GET | `/documents/{document_id}` | Document metadata (status, paths, related ids). |
| GET | `/documents/{document_id}/download` | Stream the PDF. |
| GET | `/documents/jobs/{job_id}` | When `async_job=true`, poll for status and `document_id`. |

### Suggested order flow (front end)

1. **List/create orders or dockets** — Use existing sales/delivery APIs or add CRUD for `delivery_dockets` and `delivery_docket_lines`.
2. **Generate PDF** — `POST /documents/generate` with `delivery_docket_id` (or `quote_id`). Use `template_name: "delivery_docket.docx"`, `doc_type: "delivery_docket"`.
3. **Download / print** — `GET /documents/{document_id}/download` returns the PDF; front end can open in new tab or send to printer.
4. **Track** — `GET /documents/{document_id}` for metadata; list generated docs by customer/docket if you add a list endpoint.

## Templates

- **Path**: `templates/delivery_docket.docx` (or set `DOCGEN_TEMPLATE_DIR`).
- **Output**: `generated/` (or `DOCGEN_OUTPUT_DIR`). Naming: `{doc_type}_{customer_slug}_{doc_number}_{YYYYMMDD}.pdf`.

## Scripts (CLI)

- **Create template**: `python scripts/create_delivery_docket_template.py` — creates a minimal `templates/delivery_docket.docx` with docxtpl placeholders.
- **Sync generate**: `python scripts/run_sync_generate_delivery_docket.py [delivery_docket_id]` or `--quote <sales_order_id>`. Creates test customer/docket if none exist.

## Next steps for order front end

1. Add or reuse **delivery docket CRUD** (create docket + lines from basket/order).
2. Add **list documents** endpoint, e.g. `GET /documents?customer_id=...&delivery_docket_id=...`.
3. Build **orders UI** (e.g. Dash): select customer, add line items, save as delivery docket, then "Generate PDF" → call `POST /documents/generate` → "Download" / "Print" via `/documents/{id}/download`.
