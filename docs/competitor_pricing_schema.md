# Competitor Pricing Schema Reference

This guide summarises the standalone schema that powers the `apps/competitor_intel` Dash application. Use it to craft prompts (e.g. for ChatGPT) when you need structured competitor pricing data or want to populate CSV templates automatically.

---

## Entity Overview

| Table | Purpose |
| --- | --- |
| `brands` | Master list of spirit brands. |
| `products` | Brand-specific products (gin bottles or RTD cans). |
| `package_specs` | Canonical bottle/can specifications (size, can form factor). |
| `pack_specs` | Pack-level configurations (e.g. 4-pack of 250 mL cans). |
| `carton_specs` | Carton-level configurations tied to either units or packs. |
| `skus` | Sellable item that links a product to a package spec. |
| `sku_packs` | Optional one-to-one mapping from SKU to a pack spec. |
| `sku_cartons` | Links SKUs to one or more carton specs. |
| `manufacturing_costs` | Known/estimated manufacturing costs per SKU. |
| `companies` | Retailers, distributors or venues that capture observations. |
| `locations` | Physical or online presence for a company. |
| `price_observations` | Normalised competitor price captures (unit/pack/carton). |
| `attachments` | Supporting evidence files for a price observation. |

---

## Table Dictionary

### `brands`

- **Primary key**: `id` (UUID string)
- **Columns**
  - `name` (`String(255)`, required) – brand name (unique).
  - `owner_company` (`String(255)`, optional) – owning organisation.
- **Relationships**
  - One-to-many with `products`.
- **Constraints**
  - `uq_brands_name`, `ix_brands_name`.

### `products`

- **Primary key**: `id`
- **Columns**
  - `brand_id` (FK → `brands.id`, required).
  - `name` (`String(255)`, required) – product label (unique per brand).
  - `category` (`String(32)`, required) – must be `gin_bottle` or `rtd_can`.
  - `abv_percent` (`Numeric(5,2)`, required) – alcohol by volume.
  - `notes` (`Text`, optional).
- **Relationships**
  - Many-to-one with `brands`.
  - One-to-many with `skus`.
- **Constraints**
  - `uq_products_brand_name`, `ck_products_category`.

### `package_specs`

- **Primary key**: `id`
- **Columns**
  - `type` (`String(32)`, required) – `bottle` or `can`.
  - `container_ml` (`Integer`, required) – volume per primary unit.
  - `can_form_factor` (`String(32)`, optional) – `slim`, `sleek`, `classic`; must be set only for cans.
- **Relationships**
  - One-to-many with `skus`, `pack_specs`, and `carton_specs`.
- **Constraints**
  - `uq_package_specs_unique`, `ck_package_specs_type`, `ck_package_specs_can_form_factor`, `ck_package_specs_can_form_factor_values`.

### `pack_specs`

- **Primary key**: `id`
- **Columns**
  - `package_spec_id` (FK → `package_specs.id`, required).
  - `units_per_pack` (`Integer`, required).
  - `gtin` (`String(32)`, optional, unique) – pack-level GTIN.
  - `notes` (`Text`, optional).
- **Relationships**
  - Many-to-one with `package_specs`.
  - One-to-many with `sku_packs`.
  - Optional link to `carton_specs` (via `carton_specs.pack_spec_id`).
- **Constraints**
  - `uq_pack_specs_package_units`.

### `carton_specs`

- **Primary key**: `id`
- **Columns**
  - `units_per_carton` (`Integer`, required).
  - `pack_count` (`Integer`, optional) – number of packs in the carton.
  - `package_spec_id` (FK, optional) – used for unit-based cartons.
  - `pack_spec_id` (FK, optional) – used for pack-based cartons; mutually exclusive with `package_spec_id`.
  - `gtin` (`String(32)`, optional, unique) – carton-level GTIN.
  - `notes` (`Text`, optional).
- **Relationships**
  - One-to-many with `sku_cartons`.
  - Optional many-to-one with `package_specs` or `pack_specs`.
- **Constraints**
  - `ck_carton_specs_pack_or_unit` (exactly one of `package_spec_id` or `pack_spec_id`).
  - `uq_carton_specs_gtin`.

### `skus`

- **Primary key**: `id`
- **Columns**
  - `product_id` (FK → `products.id`, required).
  - `package_spec_id` (FK → `package_specs.id`, required).
  - `gtin` (`String(32)`, optional, unique) – unit GTIN.
  - `is_active` (`Boolean`, default `True`).
- **Relationships**
  - Many-to-one with `products` and `package_specs`.
  - One-to-one (optional) with `sku_packs`.
  - One-to-many with `sku_cartons`, `price_observations`, `manufacturing_costs`.
- **Constraints**
  - `uq_skus_product_package`.

### `sku_packs`

- **Primary key**: `id`
- **Columns**
  - `sku_id` (FK → `skus.id`, required, cascades on delete).
  - `pack_spec_id` (FK → `pack_specs.id`, required).
  - `notes` (`Text`, optional).
- **Relationships**
  - Many-to-one with `skus` (one-to-one enforced via unique constraint).
  - Many-to-one with `pack_specs`.
- **Constraints**
  - `uq_sku_packs_sku`.

### `sku_cartons`

- **Primary key**: `id`
- **Columns**
  - `sku_id` (FK → `skus.id`, required, cascades on delete).
  - `carton_spec_id` (FK → `carton_specs.id`, required, cascades on delete).
- **Relationships**
  - Many-to-one with `skus` and `carton_specs`.
- **Constraints**
  - `uq_sku_cartons_parent` (prevents duplicate links).

### `manufacturing_costs`

- **Primary key**: `id`
- **Columns**
  - `sku_id` (FK → `skus.id`, required, cascades on delete).
  - `cost_type` (`String(16)`, required) – `estimated` or `known`.
  - `cost_currency` (`String(8)`, default `AUD`).
  - `cost_per_unit`, `cost_per_pack`, `cost_per_carton` (`Numeric(12,4)`, optional).
  - `effective_date` (`Date`, required).
  - `notes` (`Text`, optional).
- **Relationships**
  - Many-to-one with `skus`.
- **Constraints**
  - `ck_manufacturing_costs_type`, `uq_manufacturing_costs_sku_type_effective`.

### `companies`

- **Primary key**: `id`
- **Columns**
  - `name` (`String(255)`, required, unique).
  - `type` (`String(32)`, required, default `other`) – one of `distributor`, `retailer`, `venue`, `other`.
  - `parent_company_id` (self-referencing FK, optional).
- **Relationships**
  - Optional parent/child hierarchy.
  - One-to-many with `locations` and `price_observations`.
- **Constraints**
  - `uq_companies_name`, `ck_companies_type`.

### `locations`

- **Primary key**: `id`
- **Columns**
  - `company_id` (FK → `companies.id`, required, cascades on delete).
  - `store_name` (`String(255)`, optional).
  - `state` (`String(64)`, required).
  - `suburb` (`String(255)`, required).
  - `postcode` (`String(16)`, optional).
  - `lat`, `lon` (`Float`, optional).
- **Relationships**
  - Many-to-one with `companies`.
  - One-to-many with `price_observations`.
- **Constraints**
  - Composite uniqueness on `(company_id, store_name, state, suburb, postcode)`.

### `price_observations`

- **Primary key**: `id`
- **Columns (key fields)**
  - Foreign keys: `sku_id`, `company_id`, `location_id` (nullable).
  - Channel metadata: `channel` (required, choices listed below), `price_context` (default `shelf`), `promo_name`, `availability`.
  - Raw capture: `price_ex_gst_raw`, `price_inc_gst_raw`, `gst_rate`, `currency`, `is_carton_price`, `carton_units`.
  - Normalised prices (stored): `price_ex_gst_norm`, `price_inc_gst_norm`, `unit_price_inc_gst`, `carton_price_inc_gst`, `pack_price_inc_gst`, `price_basis`, `price_per_litre`, `price_per_unit_pure_alcohol`, `standard_drinks`.
  - Timing & provenance: `observation_dt`, `source_type`, `source_url`, `source_note`, `hash_key`.
  - Gross profit outputs: `gp_unit_abs`, `gp_unit_pct`, `gp_pack_abs`, `gp_pack_pct`, `gp_carton_abs`, `gp_carton_pct`.
- **Relationships**
  - Many-to-one with `skus`, `companies`, optional `locations`.
  - One-to-many with `attachments`.
- **Constraints & Indexes**
  - Extensive indexes on SKU, company, location, channel and hash.
  - Check constraints for enumerations (`channel`, `price_context`, `availability`, `source_type`, `price_basis`).

### `attachments`

- **Primary key**: `id`
- **Columns**
  - `price_observation_id` (FK → `price_observations.id`, required, cascades on delete).
  - `file_path` (`String(1024)`, required) – persisted evidence path.
  - `caption` (`String(255)`, optional).
- **Relationships**
  - Many-to-one with `price_observations`.

---

## Enumerations

- `products.category`: `gin_bottle`, `rtd_can`
- `package_specs.type`: `bottle`, `can`
- `package_specs.can_form_factor`: `slim`, `sleek`, `classic`
- `manufacturing_costs.cost_type`: `estimated`, `known`
- `companies.type`: `distributor`, `retailer`, `venue`, `other`
- `price_observations.channel`: `distributor_to_retailer`, `wholesale_to_venue`, `retail_instore`, `retail_online`, `direct_to_consumer`
- `price_observations.price_context`: `shelf`, `promo`, `member`, `online`, `quote`, `other`
- `price_observations.availability`: `in_stock`, `low_stock`, `out_of_stock`, `unknown`
- `price_observations.source_type`: `web`, `in_store`, `brochure`, `email`, `verbal`, `receipt`, `photo`
- `price_observations.price_basis`: `unit`, `pack`, `carton`

---

## Prompting Template (for ChatGPT or other LLMs)

Use the following JSON skeleton when asking an LLM to propose new data. Supply any locked values up front (e.g. brand or product) and let the model fill in the blanks consistent with the schema.

```json
{
  "brand": {
    "name": "",
    "owner_company": ""
  },
  "product": {
    "name": "",
    "category": "gin_bottle | rtd_can",
    "abv_percent": 0.0,
    "notes": ""
  },
  "package_spec": {
    "type": "bottle | can",
    "container_ml": 0,
    "can_form_factor": "slim | sleek | classic | null"
  },
  "pack_spec": {
    "units_per_pack": 0,
    "gtin": "",
    "notes": ""
  },
  "carton_spec": {
    "units_per_carton": 0,
    "pack_count": null,
    "gtin": "",
    "notes": ""
  },
  "sku": {
    "gtin": "",
    "is_active": true
  },
  "manufacturing_cost": {
    "cost_type": "estimated | known",
    "cost_currency": "AUD",
    "cost_per_unit": 0.0,
    "cost_per_pack": 0.0,
    "cost_per_carton": 0.0,
    "effective_date": "YYYY-MM-DD",
    "notes": ""
  },
  "observation": {
    "channel": "retail_online",
    "price_context": "shelf",
    "promo_name": "",
    "availability": "in_stock",
    "price_inc_gst_raw": 0.0,
    "price_ex_gst_raw": 0.0,
    "gst_rate": 0.10,
    "currency": "AUD",
    "is_carton_price": false,
    "carton_units": null,
    "price_basis": "unit",
    "observation_dt": "2025-01-01T12:00:00+00:00",
    "source_type": "web",
    "source_url": "",
    "source_note": "",
    "gp_unit_pct": null,
    "gp_unit_abs": null
  },
  "company": {
    "name": "",
    "type": "retailer | distributor | venue | other",
    "parent_company": ""
  },
  "location": {
    "store_name": "",
    "state": "",
    "suburb": "",
    "postcode": "",
    "lat": null,
    "lon": null
  },
  "attachments": [
    {
      "file_path": "",
      "caption": ""
    }
  ]
}
```

> Tip: When generating multiple observations, reuse reference entities (brand/product/SKU/company) and only vary the observation-specific fields (`channel`, prices, `observation_dt`, etc.). This keeps foreign keys consistent and avoids duplicate master data.

---

## Related Resources

- Models: `apps/competitor_intel/app/models/`
- CSV templates: `apps/competitor_intel/data_templates/`
- Sample data loader: `apps/competitor_intel/scripts/load_sample_data.py`

Use this guide as the canonical reference when enriching competitor pricing records or validating imported datasets.
