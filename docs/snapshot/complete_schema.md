# Complete Database Schema Documentation
Generated: 2025-11-03T12:40:49.748059+00:00
Database: sqlite:///./tpmanuf.db
Total Tables: 48

---

## Product Hierarchy

### Table: `product_channel_links`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  channel | VARCHAR(32) | No | 'shopify' | No |
|  shopify_product_id | VARCHAR(64) | Yes | NULL | No |
|  shopify_variant_id | VARCHAR(64) | Yes | NULL | No |
|  shopify_location_id | VARCHAR(64) | Yes | NULL | No |

#### Primary Keys

`id`

#### Unique Constraints

- uq_product_channel: (`product_id`, `channel`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_product_channel_links_product | No | product_id |

---

### Table: `product_migration_map`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  legacy_table | VARCHAR(50) | No | NULL | No |
|  legacy_id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  migrated_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_migration_map_legacy | No | legacy_table, legacy_id |

---

### Table: `product_variants`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  variant_code | VARCHAR(50) | No | NULL | No |
|  variant_name | VARCHAR(200) | No | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_product_variants__product_id__products | product_id | products(id) | N/A | N/A |

#### Unique Constraints

- uq_product_variant_code: (`product_id`, `variant_code`)

---

### Table: `products`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
|  id | TEXT | Yes | NULL | No |
|  sku | TEXT | Yes | NULL | No |
|  name | TEXT | Yes | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  density_kg_per_l | NUMERIC | Yes | NULL | No |
|  abv_percent | NUMERIC | Yes | NULL | No |
|  is_active | NUMERIC | Yes | NULL | No |
|  created_at | NUMERIC | Yes | NULL | No |
|  updated_at | NUMERIC | Yes | NULL | No |
|  ean13 | TEXT | Yes | NULL | No |
|  supplier_id | TEXT | Yes | NULL | No |
|  size | TEXT | Yes | NULL | No |
|  base_unit | TEXT | Yes | NULL | No |
|  pack | INTEGER | Yes | NULL | No |
|  dgflag | TEXT | Yes | NULL | No |
|  form | TEXT | Yes | NULL | No |
|  pkge | INTEGER | Yes | NULL | No |
|  label | INTEGER | Yes | NULL | No |
|  manu | INTEGER | Yes | NULL | No |
|  taxinc | TEXT | Yes | NULL | No |
|  salestaxcde | TEXT | Yes | NULL | No |
|  purcost | NUMERIC | Yes | NULL | No |
|  purtax | NUMERIC | Yes | NULL | No |
|  wholesalecost | NUMERIC | Yes | NULL | No |
|  disccdeone | TEXT | Yes | NULL | No |
|  disccdetwo | TEXT | Yes | NULL | No |
|  xero_item_id | TEXT | Yes | NULL | No |
|  last_sync | NUMERIC | Yes | NULL | No |
|  product_type | TEXT | Yes | NULL | No |
|  raw_material_group_id | TEXT | Yes | NULL | No |
|  raw_material_code | INTEGER | Yes | NULL | No |
|  raw_material_search_key | TEXT | Yes | NULL | No |
|  raw_material_search_ext | TEXT | Yes | NULL | No |
|  specific_gravity | NUMERIC | Yes | NULL | No |
|  vol_solid | NUMERIC | Yes | NULL | No |
|  solid_sg | NUMERIC | Yes | NULL | No |
|  wt_solid | NUMERIC | Yes | NULL | No |
|  usage_unit | TEXT | Yes | NULL | No |
|  usage_cost | NUMERIC | Yes | NULL | No |
|  restock_level | NUMERIC | Yes | NULL | No |
|  used_ytd | NUMERIC | Yes | NULL | No |
|  hazard | TEXT | Yes | NULL | No |
|  condition | TEXT | Yes | NULL | No |
|  msds_flag | TEXT | Yes | NULL | No |
|  altno1 | INTEGER | Yes | NULL | No |
|  altno2 | INTEGER | Yes | NULL | No |
|  altno3 | INTEGER | Yes | NULL | No |
|  altno4 | INTEGER | Yes | NULL | No |
|  altno5 | INTEGER | Yes | NULL | No |
|  last_movement_date | TEXT | Yes | NULL | No |
|  last_purchase_date | TEXT | Yes | NULL | No |
|  ean13_raw | NUMERIC | Yes | NULL | No |
|  xero_account | TEXT | Yes | NULL | No |
|  formula_id | TEXT | Yes | NULL | No |
|  formula_revision | INTEGER | Yes | NULL | No |
|  purchase_unit_id | TEXT | Yes | NULL | No |
|  purchase_volume | NUMERIC | Yes | NULL | No |
|  is_archived | NUMERIC | Yes | NULL | No |
|  archived_at | NUMERIC | Yes | NULL | No |
|  is_tracked | NUMERIC | Yes | NULL | No |
|  sellable | NUMERIC | Yes | NULL | No |
|  standard_cost | NUMERIC | Yes | NULL | No |
|  estimated_cost | NUMERIC | Yes | NULL | No |
|  estimate_reason | TEXT | Yes | NULL | No |
|  estimated_by | TEXT | Yes | NULL | No |
|  estimated_at | NUMERIC | Yes | NULL | No |
|  wholesalecde | NUMERIC | Yes | NULL | No |
|  retailcde | NUMERIC | Yes | NULL | No |
|  countercde | NUMERIC | Yes | NULL | No |
|  tradecde | NUMERIC | Yes | NULL | No |
|  contractcde | NUMERIC | Yes | NULL | No |
|  industrialcde | NUMERIC | Yes | NULL | No |
|  distributorcde | NUMERIC | Yes | NULL | No |
|  retail_price_inc_gst | NUMERIC | Yes | NULL | No |
|  retail_price_ex_gst | NUMERIC | Yes | NULL | No |
|  retail_excise | NUMERIC | Yes | NULL | No |
|  wholesale_price_inc_gst | NUMERIC | Yes | NULL | No |
|  wholesale_price_ex_gst | NUMERIC | Yes | NULL | No |
|  wholesale_excise | NUMERIC | Yes | NULL | No |
|  distributor_price_inc_gst | NUMERIC | Yes | NULL | No |
|  distributor_price_ex_gst | NUMERIC | Yes | NULL | No |
|  distributor_excise | NUMERIC | Yes | NULL | No |
|  counter_price_inc_gst | NUMERIC | Yes | NULL | No |
|  counter_price_ex_gst | NUMERIC | Yes | NULL | No |
|  counter_excise | NUMERIC | Yes | NULL | No |
|  trade_price_inc_gst | NUMERIC | Yes | NULL | No |
|  trade_price_ex_gst | NUMERIC | Yes | NULL | No |
|  trade_excise | NUMERIC | Yes | NULL | No |
|  contract_price_inc_gst | NUMERIC | Yes | NULL | No |
|  contract_price_ex_gst | NUMERIC | Yes | NULL | No |
|  contract_excise | NUMERIC | Yes | NULL | No |
|  industrial_price_inc_gst | NUMERIC | Yes | NULL | No |
|  industrial_price_ex_gst | NUMERIC | Yes | NULL | No |
|  industrial_excise | NUMERIC | Yes | NULL | No |
|  purchase_cost_inc_gst | NUMERIC | Yes | NULL | No |
|  purchase_cost_ex_gst | NUMERIC | Yes | NULL | No |
|  purchase_tax_included | TEXT | Yes | NULL | No |
|  usage_cost_inc_gst | NUMERIC | Yes | NULL | No |
|  usage_cost_ex_gst | NUMERIC | Yes | NULL | No |
|  usage_tax_included | TEXT | Yes | NULL | No |
|  is_purchase | NUMERIC | Yes | NULL | No |
|  is_sell | NUMERIC | Yes | NULL | No |
|  is_assemble | NUMERIC | Yes | NULL | No |
|  manufactured_cost_inc_gst | NUMERIC | Yes | NULL | No |
|  manufactured_cost_ex_gst | NUMERIC | Yes | NULL | No |
|  manufactured_tax_included | TEXT | Yes | NULL | No |
|  purchase_tax_included_bool | NULL | Yes | NULL | No |

#### Primary Keys

**WARNING**: No primary key defined!

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_products_is_assemble | No | is_assemble |
| ix_products_is_purchase | No | is_purchase |
| ix_products_is_sell | No | is_sell |

---

## Manufacturing Core

### Table: `batch_components`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  batch_id | VARCHAR(36) | No | NULL | No |
|  ingredient_product_id | VARCHAR(36) | No | NULL | No |
|  lot_id | VARCHAR(36) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  unit_cost | NUMERIC(10, 2) | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_batch_components__batch_id__batches | batch_id | batches(id) | N/A | N/A |
| fk_batch_components__ingredient_product_id__products | ingredient_product_id | products(id) | N/A | N/A |
| fk_batch_components__lot_id__inventory_lots | lot_id | inventory_lots(id) | N/A | N/A |

---

### Table: `batch_lines`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  batch_id | VARCHAR(36) | No | NULL | No |
|  material_id | VARCHAR(36) | No | NULL | No |
|  role | VARCHAR(50) | Yes | NULL | No |
|  qty_theoretical | NUMERIC(12, 3) | No | NULL | No |
|  qty_actual | NUMERIC(12, 3) | Yes | NULL | No |
|  unit | VARCHAR(10) | No | NULL | No |
|  cost_at_time | NUMERIC(10, 2) | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_batch_lines__batch_id__batches | batch_id | batches(id) | N/A | N/A |
| fk_batch_lines__material_id__products | material_id | products(id) | N/A | N/A |

#### Unique Constraints

- uq_batch_line: (`batch_id`, `material_id`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_batch_line_batch | No | batch_id |

---

### Table: `batches`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  work_order_id | VARCHAR(36) | No | NULL | No |
|  batch_code | VARCHAR(50) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  status | VARCHAR(20) | Yes | NULL | No |
|  started_at | DATETIME | Yes | NULL | No |
|  completed_at | DATETIME | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |
|  batch_status | VARCHAR(20) | Yes | NULL | No |
|  yield_actual | NUMERIC(12, 3) | Yes | NULL | No |
|  yield_litres | NUMERIC(12, 3) | Yes | NULL | No |
|  variance_percent | NUMERIC(5, 2) | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_batches__work_order_id__work_orders | work_order_id | work_orders(id) | N/A | N/A |

#### Unique Constraints

- uq_batch_code: (`work_order_id`, `batch_code`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_batch_wo_code | No | work_order_id, batch_code |

---

### Table: `formula_lines`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  formula_id | VARCHAR(36) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  sequence | INTEGER | No | NULL | No |
|  notes | TEXT | Yes | NULL | No |
|  unit | VARCHAR(10) | Yes | NULL | No |
|  product_id | VARCHAR(36) | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_formula_lines__formula_id__formulas | formula_id | formulas(id) | N/A | N/A |

#### Unique Constraints

- uq_formula_line_sequence: (`formula_id`, `sequence`)

---

### Table: `formulas`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  formula_code | VARCHAR(50) | No | NULL | No |
|  formula_name | VARCHAR(200) | No | NULL | No |
|  version | INTEGER | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  updated_at | DATETIME | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |
|  is_archived | BOOLEAN | No | '0' | No |
|  archived_at | DATETIME | Yes | NULL | No |
|  instructions | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_formulas__product_id__products | product_id | products(id) | N/A | N/A |

#### Unique Constraints

- uq_formula_version: (`product_id`, `formula_code`, `version`)

---

### Table: `qc_results`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  batch_id | VARCHAR(36) | No | NULL | No |
|  test_name | VARCHAR(100) | No | NULL | No |
|  test_value | NUMERIC(12, 3) | Yes | NULL | No |
|  test_unit | VARCHAR(20) | Yes | NULL | No |
|  pass_fail | BOOLEAN | Yes | NULL | No |
|  tested_at | DATETIME | Yes | NULL | No |
|  tested_by | VARCHAR(100) | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |
|  test_definition_id | VARCHAR(36) | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_qc_results__batch_id__batches | batch_id | batches(id) | N/A | N/A |

---

### Table: `work_order_lines`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  work_order_id | VARCHAR(36) | No | NULL | No |
|  ingredient_product_id | VARCHAR(36) | No | NULL | No |
|  required_quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  allocated_quantity_kg | NUMERIC(12, 3) | Yes | NULL | No |
|  sequence | INTEGER | No | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_work_order_lines__ingredient_product_id__products | ingredient_product_id | products(id) | N/A | N/A |
| fk_work_order_lines__work_order_id__work_orders | work_order_id | work_orders(id) | N/A | N/A |

---

### Table: `work_orders`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(50) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  formula_id | VARCHAR(36) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  status | VARCHAR(20) | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  released_at | DATETIME | Yes | NULL | No |
|  completed_at | DATETIME | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_work_orders__formula_id__formulas | formula_id | formulas(id) | N/A | N/A |
| fk_work_orders__product_id__products | product_id | products(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_work_order_code | No | code |
| ix_work_orders_code | Yes | code |

---

## Inventory Management

### Table: `inventory_lots`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  lot_code | VARCHAR(50) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  unit_cost | NUMERIC(10, 2) | Yes | NULL | No |
|  received_at | DATETIME | Yes | NULL | No |
|  expires_at | DATETIME | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  original_unit_cost | NUMERIC(10, 2) | Yes | NULL | No |
|  current_unit_cost | NUMERIC(10, 2) | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_inventory_lots__product_id__products | product_id | products(id) | N/A | N/A |

#### Unique Constraints

- uq_lot_code: (`product_id`, `lot_code`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_lot_product_code | No | product_id, lot_code |

---

### Table: `inventory_movements`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  ts | DATETIME | No | NULL | No |
|  date | VARCHAR(10) | No | NULL | No |
|  qty | NUMERIC(12, 3) | No | NULL | No |
|  unit | VARCHAR(10) | No | NULL | No |
|  direction | VARCHAR(10) | No | NULL | No |
|  source_batch_id | VARCHAR(36) | Yes | NULL | No |
|  note | TEXT | Yes | NULL | No |
|  product_id | VARCHAR(36) | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_inventory_movements__source_batch_id__batches | source_batch_id | batches(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_movements_batch | No | source_batch_id |
| ix_movements_date | No | date |

---

### Table: `inventory_reservations`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  qty_canonical | NUMERIC(18, 6) | No | NULL | No |
|  source | VARCHAR(16) | No | NULL | No |
|  reference_id | VARCHAR(128) | Yes | NULL | No |
|  status | VARCHAR(16) | No | 'ACTIVE' | No |
|  created_at | DATETIME | No | CURRENT_TIMESTAMP | No |
|  updated_at | DATETIME | No | CURRENT_TIMESTAMP | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_inventory_reservations_product | No | product_id |

---

### Table: `inventory_txns`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  lot_id | VARCHAR(36) | No | NULL | No |
|  transaction_type | VARCHAR(20) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  unit_cost | NUMERIC(10, 2) | Yes | NULL | No |
|  reference_type | VARCHAR(50) | Yes | NULL | No |
|  reference_id | VARCHAR(36) | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  created_by | VARCHAR(100) | Yes | NULL | No |
|  cost_source | VARCHAR(20) | Yes | NULL | No |
|  extended_cost | NUMERIC(12, 2) | Yes | NULL | No |
|  estimate_flag | BOOLEAN | Yes | '0' | No |
|  estimate_reason | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_inventory_txns__lot_id__inventory_lots | lot_id | inventory_lots(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_txn_lot_ts | No | lot_id, created_at |

---

## Assembly Operations

### Table: `assemblies`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  parent_product_id | VARCHAR(36) | No | NULL | No |
|  effective_from | DATETIME | Yes | NULL | No |
|  effective_to | DATETIME | Yes | NULL | No |
|  version | INTEGER | Yes | '1' | No |
|  is_active | BOOLEAN | Yes | '1' | No |
|  yield_factor | NUMERIC(6, 4) | Yes | '1.0' | No |
|  is_primary | BOOLEAN | No | '0' | No |
|  notes | VARCHAR(255) | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  updated_at | DATETIME | Yes | NULL | No |
|  assembly_code | VARCHAR(50) | No | NULL | No |
|  assembly_name | VARCHAR(200) | No | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_assemblies_parent | No | parent_product_id |

---

### Table: `assembly_cost_dependencies`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  consumed_lot_id | VARCHAR(36) | No | NULL | No |
|  produced_lot_id | VARCHAR(36) | No | NULL | No |
|  consumed_txn_id | VARCHAR(36) | No | NULL | No |
|  produced_txn_id | VARCHAR(36) | No | NULL | No |
|  dependency_ts | DATETIME | No | CURRENT_TIMESTAMP | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_dep_consumed_lot | consumed_lot_id | inventory_lots(id) | N/A | N/A |
| fk_dep_produced_lot | produced_lot_id | inventory_lots(id) | N/A | N/A |
| fk_dep_consumed_txn | consumed_txn_id | inventory_txns(id) | N/A | N/A |
| fk_dep_produced_txn | produced_txn_id | inventory_txns(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_dep_consumed | No | consumed_lot_id |
| ix_dep_consumed_txn | No | consumed_txn_id |
| ix_dep_produced | No | produced_lot_id |
| ix_dep_produced_txn | No | produced_txn_id |

---

### Table: `assembly_lines`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  assembly_id | VARCHAR(36) | No | NULL | No |
|  component_product_id | VARCHAR(36) | No | NULL | No |
|  quantity | NUMERIC(12, 3) | No | NULL | No |
|  sequence | INTEGER | No | NULL | No |
|  unit | VARCHAR(10) | Yes | NULL | No |
|  is_energy_or_overhead | BOOLEAN | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_assembly_lines__assembly_id__assemblies | assembly_id | assemblies(id) | N/A | N/A |
| fk_assembly_lines__component_product_id__products | component_product_id | products(id) | N/A | N/A |

#### Unique Constraints

- uq_assembly_line_sequence: (`assembly_id`, `sequence`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_assembly_line_assembly | No | assembly_id |

---

## Sales & Purchasing

### Table: `contacts`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(50) | No | NULL | No |
|  name | VARCHAR(200) | No | NULL | No |
|  contact_person | VARCHAR(100) | Yes | NULL | No |
|  email | VARCHAR(200) | Yes | NULL | No |
|  phone | VARCHAR(50) | Yes | NULL | No |
|  address | TEXT | Yes | NULL | No |
|  is_customer | BOOLEAN | No | '0' | No |
|  is_supplier | BOOLEAN | No | '0' | No |
|  is_other | BOOLEAN | No | '0' | No |
|  tax_rate | NUMERIC(5, 2) | Yes | NULL | No |
|  xero_contact_id | VARCHAR(100) | Yes | NULL | No |
|  last_sync | DATETIME | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | '1' | No |
|  created_at | DATETIME | Yes | NULL | No |
|  updated_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_contact_code | Yes | code |
| ix_contact_type | No | is_customer, is_supplier, is_other |
| ix_contacts_is_customer | No | is_customer |
| ix_contacts_is_supplier | No | is_supplier |

---

### Table: `customers`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(50) | No | NULL | No |
|  name | VARCHAR(200) | No | NULL | No |
|  contact_person | VARCHAR(100) | Yes | NULL | No |
|  email | VARCHAR(200) | Yes | NULL | No |
|  phone | VARCHAR(50) | Yes | NULL | No |
|  address | TEXT | Yes | NULL | No |
|  tax_rate | NUMERIC(5, 2) | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  xero_contact_id | VARCHAR(100) | Yes | NULL | No |
|  last_sync | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_customer_code | No | code |
| ix_customers_code | Yes | code |

---

### Table: `invoice_lines`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  invoice_id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  unit_price_ex_tax | NUMERIC(10, 2) | No | NULL | No |
|  tax_rate | NUMERIC(5, 2) | No | NULL | No |
|  line_total_ex_tax | NUMERIC(12, 2) | No | NULL | No |
|  line_total_inc_tax | NUMERIC(12, 2) | No | NULL | No |
|  sequence | INTEGER | No | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_invoice_lines__invoice_id__invoices | invoice_id | invoices(id) | N/A | N/A |
| fk_invoice_lines__product_id__products | product_id | products(id) | N/A | N/A |

---

### Table: `invoices`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  customer_id | VARCHAR(36) | No | NULL | No |
|  sales_order_id | VARCHAR(36) | Yes | NULL | No |
|  invoice_number | VARCHAR(50) | No | NULL | No |
|  invoice_date | DATETIME | Yes | NULL | No |
|  due_date | DATETIME | Yes | NULL | No |
|  status | VARCHAR(20) | Yes | NULL | No |
|  subtotal_ex_tax | NUMERIC(12, 2) | No | NULL | No |
|  total_tax | NUMERIC(12, 2) | No | NULL | No |
|  total_inc_tax | NUMERIC(12, 2) | No | NULL | No |
|  notes | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_invoices__customer_id__customers | customer_id | customers(id) | N/A | N/A |
| fk_invoices__sales_order_id__sales_orders | sales_order_id | sales_orders(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_invoice_code | No | invoice_number |
| ix_invoices_invoice_number | Yes | invoice_number |

---

### Table: `po_lines`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  purchase_order_id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  unit_price | NUMERIC(10, 2) | No | NULL | No |
|  line_total | NUMERIC(12, 2) | No | NULL | No |
|  sequence | INTEGER | No | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_po_lines__product_id__products | product_id | products(id) | N/A | N/A |
| fk_po_lines__purchase_order_id__purchase_orders | purchase_order_id | purchase_orders(id) | N/A | N/A |

---

### Table: `purchase_orders`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  supplier_id | VARCHAR(36) | No | NULL | No |
|  po_number | VARCHAR(50) | No | NULL | No |
|  status | VARCHAR(20) | Yes | NULL | No |
|  order_date | DATETIME | Yes | NULL | No |
|  expected_date | DATETIME | Yes | NULL | No |
|  received_date | DATETIME | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_purchase_orders__supplier_id__suppliers | supplier_id | suppliers(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_purchase_order_po_number | No | po_number |
| ix_purchase_orders_po_number | Yes | po_number |

---

### Table: `sales_orders`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  customer_id | VARCHAR(36) | No | NULL | No |
|  so_number | VARCHAR(50) | No | NULL | No |
|  status | VARCHAR(20) | Yes | NULL | No |
|  order_date | DATETIME | Yes | NULL | No |
|  requested_date | DATETIME | Yes | NULL | No |
|  shipped_date | DATETIME | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_sales_orders__customer_id__customers | customer_id | customers(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_sales_order_so_number | No | so_number |
| ix_sales_orders_so_number | Yes | so_number |

---

### Table: `so_lines`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  sales_order_id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  quantity_kg | NUMERIC(12, 3) | No | NULL | No |
|  unit_price_ex_tax | NUMERIC(10, 2) | No | NULL | No |
|  tax_rate | NUMERIC(5, 2) | No | NULL | No |
|  line_total_ex_tax | NUMERIC(12, 2) | No | NULL | No |
|  line_total_inc_tax | NUMERIC(12, 2) | No | NULL | No |
|  sequence | INTEGER | No | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_so_lines__product_id__products | product_id | products(id) | N/A | N/A |
| fk_so_lines__sales_order_id__sales_orders | sales_order_id | sales_orders(id) | N/A | N/A |

---

### Table: `suppliers`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(50) | No | NULL | No |
|  name | VARCHAR(200) | No | NULL | No |
|  contact_person | VARCHAR(100) | Yes | NULL | No |
|  email | VARCHAR(200) | Yes | NULL | No |
|  phone | VARCHAR(50) | Yes | NULL | No |
|  address | TEXT | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  xero_contact_id | VARCHAR(100) | Yes | NULL | No |
|  last_sync | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_supplier_code | No | code |
| ix_suppliers_code | Yes | code |

---

## Pricing & Packaging

### Table: `customer_prices`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  customer_id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  unit_price_ex_tax | NUMERIC(10, 2) | No | NULL | No |
|  effective_date | DATETIME | No | NULL | No |
|  expiry_date | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_customer_prices__customer_id__customers | customer_id | customers(id) | N/A | N/A |
| fk_customer_prices__product_id__products | product_id | products(id) | N/A | N/A |

#### Unique Constraints

- uq_customer_price_date: (`customer_id`, `product_id`, `effective_date`)

---

### Table: `pack_conversions`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  from_unit_id | VARCHAR(36) | No | NULL | No |
|  to_unit_id | VARCHAR(36) | No | NULL | No |
|  conversion_factor | NUMERIC(12, 6) | No | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_pack_conversions__from_unit_id__pack_units | from_unit_id | pack_units(id) | N/A | N/A |
| fk_pack_conversions__product_id__products | product_id | products(id) | N/A | N/A |
| fk_pack_conversions__to_unit_id__pack_units | to_unit_id | pack_units(id) | N/A | N/A |

#### Unique Constraints

- uq_pack_conversion: (`product_id`, `from_unit_id`, `to_unit_id`)

---

### Table: `pack_units`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(20) | No | NULL | No |
|  name | VARCHAR(100) | No | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_pack_unit_code | No | code |
| ix_pack_units_code | Yes | code |

---

### Table: `price_list_items`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  price_list_id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  unit_price_ex_tax | NUMERIC(10, 2) | No | NULL | No |
|  effective_date | DATETIME | No | NULL | No |
|  expiry_date | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_price_list_items__price_list_id__price_lists | price_list_id | price_lists(id) | N/A | N/A |
| fk_price_list_items__product_id__products | product_id | products(id) | N/A | N/A |

#### Unique Constraints

- uq_price_item_date: (`price_list_id`, `product_id`, `effective_date`)

---

### Table: `price_lists`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(50) | No | NULL | No |
|  name | VARCHAR(200) | No | NULL | No |
|  effective_date | DATETIME | No | NULL | No |
|  expiry_date | DATETIME | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_price_list_code | No | code |
| ix_price_lists_code | Yes | code |

---

## External Integrations

### Table: `xero_sync_log`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  ts | DATETIME | No | NULL | No |
|  object_type | VARCHAR(50) | Yes | NULL | No |
|  object_id | VARCHAR(100) | Yes | NULL | No |
|  direction | VARCHAR(10) | Yes | NULL | No |
|  status | VARCHAR(20) | Yes | NULL | No |
|  message | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_sync_log_object | No | object_type, object_id |
| ix_sync_log_ts | No | ts |

---

### Table: `xero_tokens`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  access_token | TEXT | No | NULL | No |
|  refresh_token | TEXT | No | NULL | No |
|  expires_at | DATETIME | No | NULL | No |
|  tenant_id | VARCHAR(100) | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  updated_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

---

## Reference Data

### Table: `condition_types`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(1) | No | NULL | No |
|  description | VARCHAR(100) | No | NULL | No |
|  extended_desc | TEXT | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Unique Constraints

- uq_condition_types__code: (`code`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_condition_type_code | Yes | code |

---

### Table: `datasets`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(3) | No | NULL | No |
|  name | VARCHAR(50) | No | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Unique Constraints

- uq_datasets__code: (`code`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_dataset_code | Yes | code |

---

### Table: `excise_rates`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  date_active_from | DATETIME | No | NULL | No |
|  rate_per_l_abv | NUMERIC(10, 4) | No | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  is_active | BOOLEAN | No | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  updated_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_excise_rates_date_active_from | No | date_active_from |

---

### Table: `manufacturing_config`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  qtyf | VARCHAR(10) | Yes | NULL | No |
|  bchno_width | VARCHAR(10) | Yes | NULL | No |
|  bch_offset | VARCHAR(10) | Yes | NULL | No |
|  company_name | VARCHAR(50) | Yes | NULL | No |
|  site_code | VARCHAR(10) | Yes | NULL | No |
|  max1 | NUMERIC(10, 2) | Yes | NULL | No |
|  max2 | NUMERIC(10, 2) | Yes | NULL | No |
|  max3 | NUMERIC(10, 2) | Yes | NULL | No |
|  max4 | NUMERIC(10, 2) | Yes | NULL | No |
|  max5 | NUMERIC(10, 2) | Yes | NULL | No |
|  max6 | NUMERIC(10, 2) | Yes | NULL | No |
|  max7 | NUMERIC(10, 2) | Yes | NULL | No |
|  max8 | NUMERIC(10, 2) | Yes | NULL | No |
|  max9 | NUMERIC(10, 2) | Yes | NULL | No |
|  flags1 | VARCHAR(10) | Yes | NULL | No |
|  flags2 | VARCHAR(10) | Yes | NULL | No |
|  flags3 | VARCHAR(10) | Yes | NULL | No |
|  flags4 | VARCHAR(10) | Yes | NULL | No |
|  flags5 | VARCHAR(10) | Yes | NULL | No |
|  flags6 | VARCHAR(10) | Yes | NULL | No |
|  flags7 | VARCHAR(10) | Yes | NULL | No |
|  flags8 | VARCHAR(10) | Yes | NULL | No |
|  rep1 | VARCHAR(10) | Yes | NULL | No |
|  rep2 | VARCHAR(10) | Yes | NULL | No |
|  rep3 | VARCHAR(10) | Yes | NULL | No |
|  rep4 | VARCHAR(10) | Yes | NULL | No |
|  rep5 | VARCHAR(10) | Yes | NULL | No |
|  rep6 | VARCHAR(10) | Yes | NULL | No |
|  print_hi1 | VARCHAR(10) | Yes | NULL | No |
|  db_month_raw | VARCHAR(10) | Yes | NULL | No |
|  cr_month_raw | VARCHAR(10) | Yes | NULL | No |
|  cans_idx | INTEGER | Yes | NULL | No |
|  label_idx | INTEGER | Yes | NULL | No |
|  labour_idx | INTEGER | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  updated_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

---

### Table: `markups`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(10) | No | NULL | No |
|  name | VARCHAR(100) | No | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  enabled_flag | VARCHAR(1) | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Unique Constraints

- uq_markups__code: (`code`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_markup_code | Yes | code |

---

### Table: `quality_test_definitions`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(50) | No | NULL | No |
|  name | VARCHAR(200) | No | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  test_type | VARCHAR(50) | Yes | NULL | No |
|  unit | VARCHAR(20) | Yes | NULL | No |
|  min_value | NUMERIC(12, 3) | Yes | NULL | No |
|  max_value | NUMERIC(12, 3) | Yes | NULL | No |
|  target_value | NUMERIC(12, 3) | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |
|  updated_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_quality_test_definitions_code | Yes | code |

---

### Table: `raw_material_groups`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  code | VARCHAR(10) | No | NULL | No |
|  name | VARCHAR(100) | No | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Unique Constraints

- uq_raw_material_groups__code: (`code`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_rm_group_code | Yes | code |

---

## Legacy Preservation

### Table: `finished_goods_inventory`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] fg_id | VARCHAR(36) | No | NULL | No |
|  soh | NUMERIC(12, 3) | No | NULL | No |

#### Primary Keys

`fg_id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_finished_goods_inventory__fg_id__finished_goods | fg_id | finished_goods(id) | N/A | N/A |

---

### Table: `legacy_acstk_data`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  product_id | VARCHAR(36) | No | NULL | No |
|  legacy_no | INTEGER | Yes | NULL | No |
|  legacy_search | VARCHAR(50) | Yes | NULL | No |
|  ean13 | NUMERIC(18, 4) | Yes | NULL | No |
|  desc1 | VARCHAR(50) | Yes | NULL | No |
|  desc2 | VARCHAR(20) | Yes | NULL | No |
|  legacy_suplr | VARCHAR(10) | Yes | NULL | No |
|  size | VARCHAR(10) | Yes | NULL | No |
|  legacy_unit | VARCHAR(10) | Yes | NULL | No |
|  pack | INTEGER | Yes | NULL | No |
|  dgflag | VARCHAR(1) | Yes | NULL | No |
|  form | VARCHAR(10) | Yes | NULL | No |
|  pkge | INTEGER | Yes | NULL | No |
|  label | INTEGER | Yes | NULL | No |
|  manu | INTEGER | Yes | NULL | No |
|  legacy_active | VARCHAR(1) | Yes | NULL | No |
|  taxinc | VARCHAR(1) | Yes | NULL | No |
|  salestaxcde | VARCHAR(1) | Yes | NULL | No |
|  purcost | NUMERIC(10, 2) | Yes | NULL | No |
|  purtax | NUMERIC(10, 2) | Yes | NULL | No |
|  wholesalecost | NUMERIC(10, 2) | Yes | NULL | No |
|  disccdeone | VARCHAR(1) | Yes | NULL | No |
|  disccdetwo | VARCHAR(1) | Yes | NULL | No |
|  wholesalecde | VARCHAR(1) | Yes | NULL | No |
|  retailcde | VARCHAR(1) | Yes | NULL | No |
|  countercde | VARCHAR(1) | Yes | NULL | No |
|  tradecde | VARCHAR(1) | Yes | NULL | No |
|  contractcde | VARCHAR(1) | Yes | NULL | No |
|  industrialcde | VARCHAR(1) | Yes | NULL | No |
|  distributorcde | VARCHAR(1) | Yes | NULL | No |
|  retail | NUMERIC(10, 2) | Yes | NULL | No |
|  counter | NUMERIC(10, 2) | Yes | NULL | No |
|  trade | NUMERIC(10, 2) | Yes | NULL | No |
|  contract | NUMERIC(10, 2) | Yes | NULL | No |
|  industrial | NUMERIC(10, 2) | Yes | NULL | No |
|  distributor | NUMERIC(10, 2) | Yes | NULL | No |
|  suplr4stdcost | VARCHAR(10) | Yes | NULL | No |
|  search4stdcost | VARCHAR(50) | Yes | NULL | No |
|  cogs | NUMERIC(10, 2) | Yes | NULL | No |
|  gpc | NUMERIC(10, 2) | Yes | NULL | No |
|  rmc | NUMERIC(10, 2) | Yes | NULL | No |
|  gpr | NUMERIC(10, 4) | Yes | NULL | No |
|  soh | INTEGER | Yes | NULL | No |
|  sohv | NUMERIC(10, 2) | Yes | NULL | No |
|  sip | INTEGER | Yes | NULL | No |
|  soo | INTEGER | Yes | NULL | No |
|  sold | INTEGER | Yes | NULL | No |
|  legacy_date | VARCHAR(10) | Yes | NULL | No |
|  bulk | NUMERIC(10, 2) | Yes | NULL | No |
|  lid | INTEGER | Yes | NULL | No |
|  pbox | INTEGER | Yes | NULL | No |
|  boxlbl | INTEGER | Yes | NULL | No |
|  imported_at | DATETIME | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_legacy_acstk_data__product_id__products | product_id | products(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_legacy_acstk_data_product_id | No | product_id |

---

## Other

### Table: `alembic_version`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] version_num | VARCHAR(32) | No | NULL | No |

#### Primary Keys

`version_num`

---

### Table: `formula_classes`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  name | VARCHAR(100) | No | NULL | No |
|  description | TEXT | Yes | NULL | No |
|  ytd_amounts | TEXT | Yes | NULL | No |
|  is_active | BOOLEAN | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Unique Constraints

- uq_formula_classes__name: (`name`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_formula_class_name | No | name |

---

### Table: `raw_material_suppliers`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  raw_material_id | VARCHAR(36) | No | NULL | No |
|  supplier_id | VARCHAR(36) | No | NULL | No |
|  is_primary | BOOLEAN | Yes | NULL | No |
|  min_qty | NUMERIC(12, 3) | Yes | NULL | No |
|  lead_time_days | INTEGER | Yes | NULL | No |
|  notes | TEXT | Yes | NULL | No |
|  created_at | DATETIME | Yes | NULL | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_raw_material_suppliers__raw_material_id__raw_materials | raw_material_id | raw_materials(id) | N/A | N/A |
| fk_raw_material_suppliers__supplier_id__suppliers | supplier_id | suppliers(id) | N/A | N/A |

#### Unique Constraints

- uq_rm_supplier: (`raw_material_id`, `supplier_id`)

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_rm_supplier_material | No | raw_material_id |
| ix_rm_supplier_supplier | No | supplier_id |

---

### Table: `revaluations`

#### Columns

| Name | Type | Nullable | Default | Auto Increment |
|------|------|----------|---------|----------------|
| [PK] id | VARCHAR(36) | No | NULL | No |
|  item_id | VARCHAR(36) | No | NULL | No |
|  lot_id | VARCHAR(36) | Yes | NULL | No |
|  old_unit_cost | NUMERIC(10, 2) | No | NULL | No |
|  new_unit_cost | NUMERIC(10, 2) | No | NULL | No |
|  delta_extended_cost | NUMERIC(12, 2) | No | NULL | No |
|  reason | TEXT | No | NULL | No |
|  revalued_by | VARCHAR(100) | No | NULL | No |
|  revalued_at | DATETIME | No | CURRENT_TIMESTAMP | No |
|  propagated_to_assemblies | BOOLEAN | Yes | '0' | No |

#### Primary Keys

`id`

#### Foreign Keys

| Name | Columns | References | On Update | On Delete |
|------|---------|-----------|-----------|-----------|
| fk_reval_item | item_id | products(id) | N/A | N/A |
| fk_reval_lot | lot_id | inventory_lots(id) | N/A | N/A |

#### Indexes

| Name | Unique | Columns |
|------|--------|---------|
| ix_reval_item_ts | No | item_id, revalued_at |
| ix_reval_lot | No | lot_id |

---
