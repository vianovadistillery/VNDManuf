# Mail Merge Document Generator — Implementation Plan

## Architecture Overview

- **Data**: SQLAlchemy + SQLite (existing). Use existing `Contact`/`Customer`, `Product`, `SalesOrder`/`SalesOrderLine`, `DeliveryDocket`/`DeliveryDocketLine`. Add `GeneratedDocument` for output metadata.
- **Templating**: Admin-authored `.docx` with **docxtpl** (Jinja2 placeholders). Template is the source of truth for layout.
- **Conversion**: **docx2pdf** (Microsoft Word on Windows) primary; **LibreOffice headless** fallback.
- **API**: FastAPI — generate (sync or job), get metadata, download PDF.
- **Concurrency**: Single conversion worker (RQ + Redis) to avoid Word fragility; API enqueues jobs, worker runs conversion and updates DB.

---

## Phased Implementation

### Phase 1: POC (Proof of Concept)

**Goal**: Single-threaded, in-process generation and conversion; no queue.

1. Add `DocumentGeneratorSettings` to app settings (template dir, output dir, keep_docx, conversion backend).
2. Add `GeneratedDocument` SQLAlchemy model and migration.
3. Define **data contract**: Python dict schema for docxtpl (contact, document header, `line_items` list, overrides).
4. Implement **context builder**: Load Customer/Contact + Product from DB; support input as `quote_id` (SalesOrder/DeliveryDocket) or explicit `product_id`+`qty` list; apply overrides (quote_date, discount, notes, shipping, payment_terms).
5. Implement **renderer**: Load template from path, render with docxtpl, write DOCX to temp dir.
6. Implement **converter**: docx2pdf with timeout; on failure try LibreOffice; return path to PDF (and optional DOCX).
7. **Service**: Orchestrate build context → render DOCX → convert to PDF → save to `/generated` → insert/update `GeneratedDocument`; return paths.
8. **FastAPI**: `POST /documents/generate` (sync), `GET /documents/{id}`, `GET /documents/{id}/download`; serve generated files via static mount.

**Risks**: Word not installed; file locks. **Mitigations**: Fallback to LibreOffice; configurable timeout; retry with backoff; optional cleanup of temp DOCX.

**Deliverables**: Runnable prototype; deterministic naming `{doc_type}_{customer_slug}_{doc_number}_{YYYYMMDD}.pdf`.

---

### Phase 2: Queue and Robustness

1. Add **RQ** (Redis): `enqueue_generation_job(payload)`; worker runs in separate process, uses same service, updates `GeneratedDocument.status` and `error_message`.
2. **API**: `POST /documents/generate` with `async=true` returns `job_id`; `GET /documents/jobs/{job_id}` returns status and `document_id` when ready.
3. **Robustness**:
   - Structured logging (request_id, document_id, job_id, conversion backend).
   - Timeouts for conversion (e.g. 60s Word, 120s LibreOffice).
   - Retries with exponential backoff (e.g. 2 retries).
   - Handle orphan WINWORD.EXE (optional: kill stale processes before convert; document in runbook).
   - Configurable `keep_docx` for debugging.

**Risks**: Redis unavailable; Word still locks. **Mitigations**: Document Redis requirement; single worker; timeout + retry; runbook for killing WINWORD.

---

### Phase 3: Production Hardening

1. **Template versioning**: Either filename convention (`Delivery_Docket_v2.docx`) or optional DB table `document_templates` (id, name, path, version, is_active).
2. **Auth**: Protect download and generate endpoints (existing JWT or API key).
3. **Rate limiting**: Per-user or per-tenant limits on generation.
4. **Monitoring**: Metrics for conversion success/failure, latency; alerts on fallback usage or repeated failures.
5. **Cleanup**: Scheduled job to remove old temp files and optionally archive or delete old generated PDFs by policy.

---

## Windows + Word–Specific Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Word not installed | Use docx2pdf first; fallback to LibreOffice; clear error in `GeneratedDocument.error_message`. |
| WINWORD.EXE file locks | Single RQ worker; timeout; optional pre-convert kill of stale WINWORD (runbook). |
| COM/timeout on convert | Configurable timeout (e.g. 60s); retry with backoff; then LibreOffice. |
| Path length / special chars | Safe slug for customer and doc number (alphanumeric + underscore); pathlib throughout. |
| Temp dir on network drive | Use local temp dir for DOCX during conversion; move to output dir after success. |

---

## Proposed Project Structure

```
app/
  settings.py                    # + DocumentGeneratorSettings
  adapters/db/
    models.py                    # + GeneratedDocument
  documents/                     # NEW PACKAGE
    __init__.py
    contracts.py                 # Data contract (docxtpl context schema)
    context_builder.py           # Build context from DB (Customer, quote/line items)
    renderer.py                  # docxtpl render DOCX
    converter.py                 # docx2pdf + LibreOffice fallback
    service.py                   # Orchestration: context → render → convert → save → DB
    repository.py               # GeneratedDocument CRUD / lookup
  api/
    main.py                      # + documents router, static mount for /generated
    documents.py                 # NEW: POST generate, GET metadata, GET download, GET job status
db/alembic/versions/
  xxx_add_generated_documents.py # NEW
workers/
  document_worker.py             # RQ worker: run generation job, update DB
templates/                       # Admin-authored .docx (e.g. Delivery_Docket.docx)
generated/                       # Output PDFs (and optional DOCX)
docs/
  MAIL_MERGE_IMPLEMENTATION_PLAN.md  # This file
  MAIL_MERGE_TEMPLATE_CHECKLIST.md   # Template inspection checklist
```

---

## Data Contract (docxtpl Context)

See `app/documents/contracts.py` for the exact TypedDict/dataclass. Summary:

- **contact**: `name`, `code`, `contact_person`, `email`, `phone`, `address`, and optional billing/delivery address lines.
- **document**: `doc_type`, `doc_number`, `date`, `quote_date`, `delivery_date`, `notes`, `shipping`, `payment_terms`, `discount_percent`, `subtotal`, `tax`, `total`.
- **line_items**: list of `{ description, sku, quantity, uom, unit_price, line_total }` (and optional fields).
- **overrides**: any runtime overrides applied (for logging).

Template placeholders: e.g. `{{ contact.name }}`, `{{ document.doc_number }}`, `{% for item in line_items %}...{% endfor %}` in a table row.

---

## Template Versioning Strategy

- **POC**: Templates in `/templates` with naming `{doc_type}.docx` or `{doc_type}_v2.docx`; config or env specifies which file to use per doc_type.
- **Production option**: Table `document_templates` with `(id, name, doc_type, file_path, version, is_active)` and API to select by name or id; default to latest active per doc_type.

---

## Next Step: Attach the DOCX Template

After you attach the Word template (e.g. `DD-merge.docx`), the following **checklist** will be used to inspect it and propose minimal edits for docxtpl:

### Template inspection checklist

- [ ] **Tables**: Identify all tables; which one contains repeating line items (one row per product)?
- [ ] **Header/footer**: Any placeholders in header/footer (e.g. document number, date)?
- [ ] **Repeating rows**: Propose exact table row with `{% for item in line_items %}` and `{{ item.description }}`, `{{ item.quantity }}`, etc.
- [ ] **Single-value fields**: List all current merge fields or placeholders; map each to data contract (e.g. `{{ contact.name }}`, `{{ document.doc_number }}`, `{{ document.date }}`).
- [ ] **Totals**: Where are subtotal/tax/total; ensure they use `{{ document.subtotal }}`, `{{ document.total }}`, etc.
- [ ] **Notes / shipping / payment terms**: If present, map to `{{ document.notes }}`, `{{ document.shipping }}`, `{{ document.payment_terms }}`.
- [ ] **Date format**: Document uses which date format (DD/MM/YYYY vs YYYY-MM-DD); recommend filter in Jinja2 if needed (e.g. `{{ document.date | format_date }}`).
- [ ] **Empty line items**: If no line items, docxtpl needs a single empty row or conditional; propose `{% if line_items %}...{% else %}...{% endif %}` or ensure table has one data row.

Once the template is attached, we will output a short “Template guidance” section with the exact placeholder names and one example table row for line items.
