# Nova U — ChatGPT Population Guide

**Via Nova Distillery | NU | Nova University**
*Use this document as context when asking ChatGPT to draft or expand training articles for the in-house Nova U system in VNDManuf.*

---

## 1. What Nova U is

Nova U is Via Nova’s internal training and SOP knowledge base, embedded in **VNDManuf** (Dash UI → **Nova U** tab).

- **Brand:** Greek letter **ν** (nu) — “new,” tied to **Via Nova**
- **Tagline:** *Learn the New Way.*
- **Goal:** Practical, always-current training for production, finance, sales, and systems
- **Audience:** Distillery operators, office staff, sales, compliance
- **Systems referenced:** VNDManuf, VND-DAQ, Xero, Shopify, SharePoint, Loom

Articles support structured SOP fields, rich HTML, tags, systems, and LLM corpus export (`/api/v1/training/corpus`).

---

## 2. Category taxonomy (SharePoint-aligned)

Use these **codes and slugs** when assigning articles. Parent → child hierarchy:

| Code | Slug | Name |
|------|------|------|
| **01** | `company-induction` | Company Induction |
| 01.01 | `welcome` | Welcome |
| 01.02 | `safety-hr` | Safety & HR |
| 01.03 | `code-of-conduct` | Code of Conduct |
| **02** | `distillery-operations` | Distillery Operations |
| 02.01 | `distillation` | Distillation |
| 02.02 | `vndaq-training` | VND-DAQ System Training |
| 02.03 | `trip-logic-safety` | Trip Logic & Safety |
| 02.04 | `cleaning-sanitising` | Cleaning & Sanitising |
| 02.05 | `packaging-bottling` | Packaging & Bottling |
| **03** | `finance-xero` | Finance & Xero |
| 03.01 | `daily-tasks` | Daily Tasks |
| 03.02 | `bank-reconciliation` | Bank Reconciliation |
| 03.03 | `inventory-excise` | Inventory & Excise |
| 03.04 | `reporting` | Reporting |
| **04** | `sales-distribution` | Sales & Distribution |
| 04.01 | `price-lists-policies` | Price Lists & Policies |
| 04.02 | `retailer-setup` | Retailer Setup |
| 04.03 | `shopify-local-delivery` | Shopify & Local Delivery |
| **05** | `product-knowledge` | Product Knowledge |
| **06** | `quality-compliance` | Quality & Compliance |
| **07** | `systems-tools` | Systems & Tools |
| 07.01 | `loom-library` | Loom Library |
| 07.02 | `vndaq` | VND-DAQ |
| 07.03 | `vndmanuf` | VNDManuf |
| 07.04 | `shopify` | Shopify |
| 07.05 | `sharepoint-guides` | SharePoint Guides |

**UI behaviour:** Left sidebar lists categories; clicking one filters articles. Articles also appear in search across all fields.

---

## 3. Article JSON schema (API)

**Create:** `POST /api/v1/training/articles`
**Update:** `PUT /api/v1/training/articles/{id_or_slug}`

```json
{
  "title": "How to conduct a stocktake",
  "slug": "how-to-conduct-a-stocktake",
  "category_id": "<uuid from GET /api/v1/training/categories>",
  "content_type": "sop",
  "status": "published",
  "summary": "One-line description for search cards.",
  "purpose": "Why this procedure exists.",
  "prerequisites": "What the operator needs before starting.",
  "safety_notes": "PPE, hazards, legal requirements.",
  "steps": [
    {"title": "Step name", "body": "Detailed instruction."}
  ],
  "risks": [
    {"issue": "What goes wrong", "prevention": "How to avoid it."}
  ],
  "troubleshooting": "If X happens, do Y.",
  "body_markdown": "Extra notes in Markdown.",
  "rich_content_html": "<p>Optional rich HTML with images/video embeds.</p>",
  "tags": ["stocktake", "inventory"],
  "systems": ["vndmanuf"],
  "loom_url": "https://www.loom.com/share/...",
  "sharepoint_url": "https://...",
  "video_embed_url": "https://www.loom.com/embed/..."
}
```

**content_type:** `sop` | `guide` | `checklist` | `reference`
**status:** `draft` | `published` | `archived`
**systems:** use slugs `vndmanuf`, `vndaq`, `xero`, `shopify` (comma-separated in DB; array in API)

---

## 4. VNDManuf module map (for accurate articles)

When writing steps, reference real app areas:

| Business area | VNDManuf location | Topics |
|---------------|-------------------|--------|
| Raw materials & FG | Manufacturing → **Products** | SKUs, formulas, assemblies, costing, inventory |
| Recipes | Manufacturing → **Assemblies / Formulas** | BOM, yield, revisions |
| Production jobs | Manufacturing → **Work Orders** | Plan, release, issue materials, complete batch |
| Stock count | Manufacturing → **Stocktake** | Physical counts, variances |
| Suppliers & customers | **Contacts** | Unified contacts, addresses, ABN |
| Orders & invoicing | **Sales** | Customers, orders, delivery dockets, invoices |
| CRM visits | **CRM** | Customer visits, scheduled activities |
| Training | **Nova U** | This system |
| Settings | **Settings** | Units, excise rates, work areas, QC types |

**FastAPI** runs on port **8000**; Dash UI calls `/api/v1/...`.

---

## 5. Pre-drafted articles (expand these)

ChatGPT task: **Turn each stub into a full published article** with 4–8 steps, 2–3 risks, safety where relevant, and Australian English. Add Loom placeholder links where video would help.

### 5.1 Company Induction

#### Full site walkthrough (`welcome`, guide, published)
- **Summary:** Orientation tour of Via Nova — receival, still, packaging, bond store, office.
- **Steps:** Receival/raw store → Still & VND-DAQ → Blending/packaging → Finished goods/excise → Office systems (VNDManuf, Xero, Shopify, SharePoint NU).
- **Tags:** induction, site-tour

#### Safety briefing (`safety-hr`, guide)
- Cover: ethanol fire risk, confined spaces, manual handling, PPE, emergency exits, incident reporting.
- Reference WorkSafe SA / distillery-specific hazards.

#### How to navigate NU training directory (`welcome`, guide)
- Nova U tab → categories → search → edit articles → LLM corpus links in header.

---

### 5.2 Distillery Operations

#### How to dilute Gin60 to Gin42 (`distillation`, sop)
- **Systems:** vndmanuf, vndaq
- **Purpose:** Standardise proof reduction before bottling.
- **Steps:** Verify source batch QC → calculate water addition from formula → add water under supervision → sample and test ABV → record in work order / batch notes.
- **Risks:** Over-dilution; unrecorded batch traceability loss.

#### How to mix feedstock (`packaging-bottling`, sop)
- Blending vessel prep, component weighing, agitation, QC sample.

#### How to bottle product (`packaging-bottling`, sop)
- Filler setup, fill height, cap torque, line clearance.

#### How to apply shrink seals / label bottles (`packaging-bottling`, sop)
- Equipment settings, visual inspection, rework procedure.

#### Cleaning & sanitising still lines (`cleaning-sanitising`, sop)
- CIP sequence, chemical concentrations, rinse verification.

---

### 5.3 VND-DAQ

#### How to start and stop the DAQ system (`vndaq`, sop, **sample enriched**)
- Pre-checks: cooling, levels, permissives → start sequence → controlled shutdown.

#### How to navigate the Live tab (`vndaq`, sop)
- Trends, PV/SP, valve states, pump status.

#### How to read alarms (`vndaq`, sop)
- Priority levels, acknowledge vs action required.

#### How to acknowledge and reset trips (`trip-logic-safety`, sop)
- Trip causes, reset preconditions, never bypass interlocks.

#### How to use permissives and interlocks (`trip-logic-safety`, sop)
- Boiler heat, condenser flow, level switches.

#### How to configure channels and scales (`vndaq`, sop)
- Engineering units, tare, calibration records.

#### How to operate the PID controller (`vndaq`, sop)
- Auto/manual, tuning basics, operator limits.

---

### 5.4 Finance & Xero

#### Daily bank reconciliation (`bank-reconciliation`, sop, **sample enriched**)
- Xero reconcile workflow, matching, exception coding.

#### Creating and sending invoices (`daily-tasks`, sop)
- From VNDManuf sales invoice → Xero sync → email PDF.

#### How to prepare EX46 excise return (`inventory-excise`, sop)
- Bond records, volume accounting, reconciliation to production logs.

---

### 5.5 Sales & Distribution

#### How to set up a new customer (`retailer-setup`, sop, **sample enriched**)
- Contacts → Sales customer → channel, terms, price list.

#### How to deliver product and complete ID checks (`retailer-setup`, sop)
- RSA requirements, delivery docket, signature.

#### How to record the sale (`retailer-setup`, sop)
- Order → delivery → invoice → Xero.

---

### 5.6 Systems & Tools — VNDManuf

#### How to log raw materials (`vndmanuf`, sop, **sample enriched**)
- Products → receipt movement → cost → verify stock.

#### How to create a production order (`vndmanuf`, sop, **sample enriched**)
- Work Orders → formula → release.

#### How to record WIP (`vndmanuf`, sop)
- Issue to WO, partial completions, yield capture.

#### How to complete a production batch (`vndmanuf`, sop)
- QC hold/release, batch code, FG receipt.

#### How to conduct a stocktake (`vndmanuf`, sop, **sample enriched**)
- Stocktake page → variances → post.

#### How to manage recipes and costings (`vndmanuf`, sop)
- Formula revisions, standard cost, yield factor.

#### How to track packaging inventory (`vndmanuf`, sop)
- Cans, bottles, labels as products; movements on packaging orders.

---

### 5.7 Shopify

#### How to receive a Shopify order (`shopify`, sop)
- Notification → pick list → allocate stock.

#### How to mark an order as fulfilled (`shopify`, sop)
- Carrier, tracking, customer notification.

---

## 6. Articles still needed (gaps to fill)

ChatGPT: **draft new articles** for categories with little or no content:

| Category slug | Suggested new articles |
|---------------|-------------------------|
| `product-knowledge` | Gin42 tasting notes; Botanical sourcing; Shelf life & storage |
| `quality-compliance` | Excise record keeping; Sample retention; HACCP critical points |
| `price-lists-policies` | Wholesale price list updates; Promotional pricing rules |
| `shopify-local-delivery` | Local delivery run sheet; Same-day cutoff times |
| `code-of-conduct` | Workplace behaviour; Social media policy |
| `reporting` | Monthly management pack; Excise vs production reconciliation |
| `loom-library` | How to record a Loom; Naming conventions for NU videos |
| `sharepoint-guides` | NU folder structure; Version control for SOPs |

---

## 7. ChatGPT prompt template

Copy everything below into ChatGPT along with this file:

```
You are documenting Via Nova Distillery's internal training system (Nova U).

Using the category taxonomy and JSON schema in the attached guide:

1. For each article listed in section 5, output a complete JSON object ready for POST /api/v1/training/articles.
2. Use Australian English, imperative voice for steps, and realistic distillery terminology (gin, neutral spirit, excise, bond store).
3. Include 4–8 steps and 2–3 risks per SOP.
4. Set status to "published" for finished articles, "draft" if information is uncertain.
5. Set category_id to null but include "category_slug" so we can resolve IDs locally.
6. After all articles, output a CSV: title, category_slug, content_type, status, systems.

Do not invent hardware tag names for VND-DAQ unless marked [VERIFY WITH OPERATOR].
Prefer VNDManuf menu paths exactly as listed in section 4.
```

---

## 8. Local seed commands

```powershell
# Create category tree + stub articles (idempotent)
python scripts/seed_nu_training.py

# Add realistic sample content to 7 demo articles
python scripts/enrich_nu_sample_articles.py
```

After seeding, open VNDManuf → **Nova U**. Categories appear in the left sidebar; click **All categories** or a specific folder to filter articles.

**API check:**
```
GET http://127.0.0.1:8000/api/v1/training/categories
GET http://127.0.0.1:8000/api/v1/training/articles?status=all
```

---

## 9. Bulk import script (optional)

If ChatGPT returns a JSON array `articles.json`, import with:

```python
import json, requests
base = "http://127.0.0.1:8000/api/v1"
cats = {c["slug"]: c["id"] for c in requests.get(f"{base}/training/categories").json()}
for art in json.load(open("articles.json")):
    slug = art.pop("category_slug", None)
    if slug and slug in cats:
        art["category_id"] = cats[slug]
    requests.post(f"{base}/training/articles", json=art)
```

---

## 10. Quality checklist (per article)

- [ ] Title matches how staff actually ask (“How do I…?”)
- [ ] Category slug correct
- [ ] `systems` tags set for filtering
- [ ] Steps are actionable (verb first, one action per step)
- [ ] Safety notes for ethanol, heat, pressure, or RSA
- [ ] Risks cover common mistakes
- [ ] Loom or SharePoint link if video exists
- [ ] Status `published` only when reviewed by site owner

---

*Generated for Via Nova / VNDManuf Nova U — align with SharePoint NU library structure and in-house LLM corpus at `/api/v1/training/corpus`.*
