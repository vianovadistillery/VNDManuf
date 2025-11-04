# Model-to-Database Alignment Report

Generated comparison of SQLAlchemy models against database schema.

## Summary

- Tables in database: 48
- Tables in models: 50
- Tables only in database: 1
- Tables only in models: 3
- Tables with differences: 1

## Tables in Database but NOT in Models

- `alembic_version`

## Tables in Models but NOT in Database

- `finished_goods`
- `raw_materials`
- `units`

## Table Differences

### `products`

#### Missing Columns (in DB, not in models):

| Column | Type | Nullable |
|--------|------|----------|
| altno1 | INTEGER | True |
| altno2 | INTEGER | True |
| altno3 | INTEGER | True |
| altno4 | INTEGER | True |
| altno5 | INTEGER | True |
| archived_at | NUMERIC | True |
| condition | TEXT | True |
| contract_excise | NUMERIC | True |
| contract_price_ex_gst | NUMERIC | True |
| contract_price_inc_gst | NUMERIC | True |
| counter_excise | NUMERIC | True |
| counter_price_ex_gst | NUMERIC | True |
| counter_price_inc_gst | NUMERIC | True |
| distributor_excise | NUMERIC | True |
| distributor_price_ex_gst | NUMERIC | True |
| distributor_price_inc_gst | NUMERIC | True |
| ean13_raw | NUMERIC | True |
| estimate_reason | TEXT | True |
| estimated_at | NUMERIC | True |
| estimated_by | TEXT | True |
| estimated_cost | NUMERIC | True |
| formula_id | TEXT | True |
| formula_revision | INTEGER | True |
| hazard | TEXT | True |
| industrial_excise | NUMERIC | True |
| industrial_price_ex_gst | NUMERIC | True |
| industrial_price_inc_gst | NUMERIC | True |
| is_archived | NUMERIC | True |
| is_assemble | NUMERIC | True |
| is_purchase | NUMERIC | True |
| is_sell | NUMERIC | True |
| is_tracked | NUMERIC | True |
| last_movement_date | TEXT | True |
| last_purchase_date | TEXT | True |
| manufactured_cost_ex_gst | NUMERIC | True |
| manufactured_cost_inc_gst | NUMERIC | True |
| manufactured_tax_included | TEXT | True |
| msds_flag | TEXT | True |
| product_type | TEXT | True |
| purchase_cost_ex_gst | NUMERIC | True |
| purchase_cost_inc_gst | NUMERIC | True |
| purchase_tax_included | TEXT | True |
| purchase_tax_included_bool | NULL | True |
| purchase_unit_id | TEXT | True |
| purchase_volume | NUMERIC | True |
| raw_material_code | INTEGER | True |
| raw_material_group_id | TEXT | True |
| raw_material_search_ext | TEXT | True |
| raw_material_search_key | TEXT | True |
| restock_level | NUMERIC | True |
| retail_excise | NUMERIC | True |
| retail_price_ex_gst | NUMERIC | True |
| retail_price_inc_gst | NUMERIC | True |
| sellable | NUMERIC | True |
| solid_sg | NUMERIC | True |
| specific_gravity | NUMERIC | True |
| standard_cost | NUMERIC | True |
| trade_excise | NUMERIC | True |
| trade_price_ex_gst | NUMERIC | True |
| trade_price_inc_gst | NUMERIC | True |
| usage_cost | NUMERIC | True |
| usage_cost_ex_gst | NUMERIC | True |
| usage_cost_inc_gst | NUMERIC | True |
| usage_tax_included | TEXT | True |
| usage_unit | TEXT | True |
| used_ytd | NUMERIC | True |
| vol_solid | NUMERIC | True |
| wholesale_excise | NUMERIC | True |
| wholesale_price_ex_gst | NUMERIC | True |
| wholesale_price_inc_gst | NUMERIC | True |
| wt_solid | NUMERIC | True |
| xero_account | TEXT | True |

#### Column Property Differences:

**contractcde**:
- type: DB=NUMERIC, Model=VARCHAR(1)

**countercde**:
- type: DB=NUMERIC, Model=VARCHAR(1)

**created_at**:
- type: DB=NUMERIC, Model=DATETIME

**distributorcde**:
- type: DB=NUMERIC, Model=VARCHAR(1)

**id**:
- nullable: DB=True, Model=False
- primary_key: DB=False, Model=True

**industrialcde**:
- type: DB=NUMERIC, Model=VARCHAR(1)

**is_active**:
- type: DB=NUMERIC, Model=BOOLEAN

**last_sync**:
- type: DB=NUMERIC, Model=DATETIME

**name**:
- nullable: DB=True, Model=False

**retailcde**:
- type: DB=NUMERIC, Model=VARCHAR(1)

**sku**:
- nullable: DB=True, Model=False

**tradecde**:
- type: DB=NUMERIC, Model=VARCHAR(1)

**updated_at**:
- type: DB=NUMERIC, Model=DATETIME

**wholesalecde**:
- type: DB=NUMERIC, Model=VARCHAR(1)

#### Primary Key Differences:

- Database PKs:
- Model PKs: id

---
