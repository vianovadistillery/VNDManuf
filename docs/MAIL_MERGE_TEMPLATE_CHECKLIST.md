# Mail Merge Template Inspection Checklist

Use this checklist when inspecting an admin-authored Word template (e.g. `DD-merge.docx`) to adapt it for **docxtpl** (Jinja2 placeholders). Do **not** use Word MERGEFIELD mail merge.

---

## 1. Tables

- [ ] List all tables in the document.
- [ ] Identify which table contains **repeating line items** (one row per product/quantity/price).
- [ ] Note the number of columns in the line-items table and their intended content (e.g. Description, SKU, Qty, UOM, Unit Price, Line Total).

---

## 2. Single-value placeholders (header / body)

Map each visible “merge” field or placeholder to the **data contract**:

| Placeholder in template | Data contract path | Example |
|-------------------------|--------------------|---------|
| Customer/contact name | `{{ contact.name }}` | |
| Contact code | `{{ contact.code }}` |
| Contact person | `{{ contact.contact_person }}` |
| Email / phone / address | `{{ contact.email }}`, `{{ contact.phone }}`, `{{ contact.address }}` |
| Document number | `{{ document.doc_number }}` |
| Document date | `{{ document.date }}` or `{{ document.quote_date }}` |
| Delivery date | `{{ document.delivery_date }}` |
| Notes | `{{ document.notes }}` |
| Shipping | `{{ document.shipping }}` |
| Payment terms | `{{ document.payment_terms }}` |
| Subtotal / Tax / Total | `{{ document.subtotal }}`, `{{ document.tax }}`, `{{ document.total }}` |

- [ ] List every current merge field or placeholder in the template.
- [ ] For each, write the exact docxtpl placeholder (e.g. `{{ document.doc_number }}`).

---

## 3. Repeating line items (table row loop)

docxtpl uses a **single table row** as the loop body; that row must contain the loop syntax.

- [ ] Locate the **data row** of the line-items table (the row that should repeat per item).
- [ ] Replace that row’s cell contents with Jinja2 loop and placeholders, for example:

  - In the first data row of the table, use:
    - `{% for item in line_items %}`
    - In the row: `{{ item.description }}`, `{{ item.sku }}`, `{{ item.quantity }}`, `{{ item.uom }}`, `{{ item.unit_price }}`, `{{ item.line_total }}`
    - After the row (or in the next row): `{% endfor %}`

- [ ] Ensure the **header row** of the table is **outside** the loop (no `{% for %}` in the header).
- [ ] If the template has **totals** in a row below the items, that row must be **after** `{% endfor %}`.

**Example (one row repeated):**

- Row 1: Table header (e.g. “Description”, “SKU”, “Qty”, “Price”, “Total”).
- Row 2: `{% for item in line_items %}` then in cells: `{{ item.description }}` | `{{ item.sku }}` | `{{ item.quantity }}` | `{{ item.unit_price }}` | `{{ item.line_total }}`
- Row 3 (or end of row 2): `{% endfor %}`
- Next row: Totals row with `{{ document.subtotal }}`, `{{ document.total }}`, etc.

- [ ] Confirm there is exactly one **data row** inside the loop (docxtpl duplicates that row per item).

---

## 4. Header and footer

- [ ] Check header and footer for any document number, date, or customer name.
- [ ] Replace with the same placeholders as in body (e.g. `{{ document.doc_number }}`, `{{ document.date }}`, `{{ contact.name }}`).

---

## 5. Date format

- [ ] Note the desired date format (e.g. DD/MM/YYYY vs YYYY-MM-DD).
- [ ] If you need a custom format, we can add a Jinja2 filter (e.g. `{{ document.date | format_date }}`) and implement it in the app.

---

## 6. Empty line items

- [ ] If the document can have **no line items**, decide:
  - Either show a single “No items” row, or
  - Use conditional: `{% if line_items %}...{% for item in line_items %}...{% endfor %}{% else %}No items{% endif %}`.

---

## 7. After inspection

- [ ] Produce a short **template guidance** note with:
  - Exact placeholder list (single-value and loop).
  - One example of the **line-items table row** (the row with `{% for item in line_items %}` and the `{{ item.* }}` cells).
  - Any header/footer placeholders and date format recommendation.

---

**Next step:** Attach the DOCX template (e.g. `DD-merge.docx`) so we can inspect it and fill this checklist with concrete placeholders and the exact table row for line items.
