# Database ERD Diagram

This diagram shows all tables and relationships in the database.

```mermaid
erDiagram

    alembic_version {
        string version_num PK "not null"
    }

    assemblies {
        string id PK "not null"
        string parent_product_id "not null"
        datetime effective_from "nullable"
        datetime effective_to "nullable"
        int version "nullable"
        bool is_active "nullable"
        decimal yield_factor "nullable"
        bool is_primary "not null"
        string notes "nullable"
        datetime created_at "nullable"
        datetime updated_at "nullable"
        string assembly_code "not null"
        string assembly_name "not null"
    }

    assembly_cost_dependencies {
        string id PK "not null"
        string consumed_lot_id FK "not null"
        string produced_lot_id FK "not null"
        string consumed_txn_id FK "not null"
        string produced_txn_id FK "not null"
        datetime dependency_ts "not null"
    }

    assembly_lines {
        string id PK "not null"
        string assembly_id FK "not null"
        string component_product_id FK "not null"
        decimal quantity "not null"
        int sequence "not null"
        string unit "nullable"
        bool is_energy_or_overhead "nullable"
        string notes "nullable"
    }

    batch_components {
        string id PK "not null"
        string batch_id FK "not null"
        string ingredient_product_id FK "not null"
        string lot_id FK "not null"
        decimal quantity_kg "not null"
        decimal unit_cost "nullable"
    }

    batch_lines {
        string id PK "not null"
        string batch_id FK "not null"
        string material_id FK "not null"
        string role "nullable"
        decimal qty_theoretical "not null"
        decimal qty_actual "nullable"
        string unit "not null"
        decimal cost_at_time "nullable"
    }

    batches {
        string id PK "not null"
        string work_order_id FK "not null"
        string batch_code "not null"
        decimal quantity_kg "not null"
        string status "nullable"
        datetime started_at "nullable"
        datetime completed_at "nullable"
        string notes "nullable"
        string batch_status "nullable"
        decimal yield_actual "nullable"
        decimal yield_litres "nullable"
        decimal variance_percent "nullable"
    }

    condition_types {
        string id PK "not null"
        string code "not null"
        string description "not null"
        string extended_desc "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    contacts {
        string id PK "not null"
        string code "not null"
        string name "not null"
        string contact_person "nullable"
        string email "nullable"
        string phone "nullable"
        string address "nullable"
        bool is_customer "not null"
        bool is_supplier "not null"
        bool is_other "not null"
        decimal tax_rate "nullable"
        string xero_contact_id "nullable"
        datetime last_sync "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
        datetime updated_at "nullable"
    }

    customer_prices {
        string id PK "not null"
        string customer_id FK "not null"
        string product_id FK "not null"
        decimal unit_price_ex_tax "not null"
        datetime effective_date "not null"
        datetime expiry_date "nullable"
    }

    customers {
        string id PK "not null"
        string code "not null"
        string name "not null"
        string contact_person "nullable"
        string email "nullable"
        string phone "nullable"
        string address "nullable"
        decimal tax_rate "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
        string xero_contact_id "nullable"
        datetime last_sync "nullable"
    }

    datasets {
        string id PK "not null"
        string code "not null"
        string name "not null"
        string description "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    excise_rates {
        string id PK "not null"
        datetime date_active_from "not null"
        decimal rate_per_l_abv "not null"
        string description "nullable"
        bool is_active "not null"
        datetime created_at "nullable"
        datetime updated_at "nullable"
    }

    finished_goods_inventory {
        string fg_id PK FK "not null"
        decimal soh "not null"
    }

    formula_classes {
        string id PK "not null"
        string name "not null"
        string description "nullable"
        string ytd_amounts "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    formula_lines {
        string id PK "not null"
        string formula_id FK "not null"
        decimal quantity_kg "not null"
        int sequence "not null"
        string notes "nullable"
        string unit "nullable"
        string product_id "nullable"
    }

    formulas {
        string id PK "not null"
        string product_id FK "not null"
        string formula_code "not null"
        string formula_name "not null"
        int version "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
        datetime updated_at "nullable"
        string notes "nullable"
        bool is_archived "not null"
        datetime archived_at "nullable"
        string instructions "nullable"
    }

    inventory_lots {
        string id PK "not null"
        string product_id FK "not null"
        string lot_code "not null"
        decimal quantity_kg "not null"
        decimal unit_cost "nullable"
        datetime received_at "nullable"
        datetime expires_at "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
        decimal original_unit_cost "nullable"
        decimal current_unit_cost "nullable"
    }

    inventory_movements {
        string id PK "not null"
        datetime ts "not null"
        string date "not null"
        decimal qty "not null"
        string unit "not null"
        string direction "not null"
        string source_batch_id FK "nullable"
        string note "nullable"
        string product_id "nullable"
    }

    inventory_reservations {
        string id PK "not null"
        string product_id "not null"
        decimal qty_canonical "not null"
        string source "not null"
        string reference_id "nullable"
        string status "not null"
        datetime created_at "not null"
        datetime updated_at "not null"
    }

    inventory_txns {
        string id PK "not null"
        string lot_id FK "not null"
        string transaction_type "not null"
        decimal quantity_kg "not null"
        decimal unit_cost "nullable"
        string reference_type "nullable"
        string reference_id "nullable"
        string notes "nullable"
        datetime created_at "nullable"
        string created_by "nullable"
        string cost_source "nullable"
        decimal extended_cost "nullable"
        bool estimate_flag "nullable"
        string estimate_reason "nullable"
    }

    invoice_lines {
        string id PK "not null"
        string invoice_id FK "not null"
        string product_id FK "not null"
        decimal quantity_kg "not null"
        decimal unit_price_ex_tax "not null"
        decimal tax_rate "not null"
        decimal line_total_ex_tax "not null"
        decimal line_total_inc_tax "not null"
        int sequence "not null"
    }

    invoices {
        string id PK "not null"
        string customer_id FK "not null"
        string sales_order_id FK "nullable"
        string invoice_number "not null"
        datetime invoice_date "nullable"
        datetime due_date "nullable"
        string status "nullable"
        decimal subtotal_ex_tax "not null"
        decimal total_tax "not null"
        decimal total_inc_tax "not null"
        string notes "nullable"
    }

    legacy_acstk_data {
        string id PK "not null"
        string product_id FK "not null"
        int legacy_no "nullable"
        string legacy_search "nullable"
        decimal ean13 "nullable"
        string desc1 "nullable"
        string desc2 "nullable"
        string legacy_suplr "nullable"
        string size "nullable"
        string legacy_unit "nullable"
        int pack "nullable"
        string dgflag "nullable"
        string form "nullable"
        int pkge "nullable"
        int label "nullable"
        int manu "nullable"
        string legacy_active "nullable"
        string taxinc "nullable"
        string salestaxcde "nullable"
        decimal purcost "nullable"
        decimal purtax "nullable"
        decimal wholesalecost "nullable"
        string disccdeone "nullable"
        string disccdetwo "nullable"
        string wholesalecde "nullable"
        string retailcde "nullable"
        string countercde "nullable"
        string tradecde "nullable"
        string contractcde "nullable"
        string industrialcde "nullable"
        string distributorcde "nullable"
        decimal retail "nullable"
        decimal counter "nullable"
        decimal trade "nullable"
        decimal contract "nullable"
        decimal industrial "nullable"
        decimal distributor "nullable"
        string suplr4stdcost "nullable"
        string search4stdcost "nullable"
        decimal cogs "nullable"
        decimal gpc "nullable"
        decimal rmc "nullable"
        decimal gpr "nullable"
        int soh "nullable"
        decimal sohv "nullable"
        int sip "nullable"
        int soo "nullable"
        int sold "nullable"
        string legacy_date "nullable"
        decimal bulk "nullable"
        int lid "nullable"
        int pbox "nullable"
        int boxlbl "nullable"
        datetime imported_at "nullable"
        string notes "nullable"
    }

    manufacturing_config {
        string id PK "not null"
        string qtyf "nullable"
        string bchno_width "nullable"
        string bch_offset "nullable"
        string company_name "nullable"
        string site_code "nullable"
        decimal max1 "nullable"
        decimal max2 "nullable"
        decimal max3 "nullable"
        decimal max4 "nullable"
        decimal max5 "nullable"
        decimal max6 "nullable"
        decimal max7 "nullable"
        decimal max8 "nullable"
        decimal max9 "nullable"
        string flags1 "nullable"
        string flags2 "nullable"
        string flags3 "nullable"
        string flags4 "nullable"
        string flags5 "nullable"
        string flags6 "nullable"
        string flags7 "nullable"
        string flags8 "nullable"
        string rep1 "nullable"
        string rep2 "nullable"
        string rep3 "nullable"
        string rep4 "nullable"
        string rep5 "nullable"
        string rep6 "nullable"
        string print_hi1 "nullable"
        string db_month_raw "nullable"
        string cr_month_raw "nullable"
        int cans_idx "nullable"
        int label_idx "nullable"
        int labour_idx "nullable"
        datetime created_at "nullable"
        datetime updated_at "nullable"
    }

    markups {
        string id PK "not null"
        string code "not null"
        string name "not null"
        string description "nullable"
        string enabled_flag "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    pack_conversions {
        string id PK "not null"
        string product_id FK "not null"
        string from_unit_id FK "not null"
        string to_unit_id FK "not null"
        decimal conversion_factor "not null"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    pack_units {
        string id PK "not null"
        string code "not null"
        string name "not null"
        string description "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    po_lines {
        string id PK "not null"
        string purchase_order_id FK "not null"
        string product_id FK "not null"
        decimal quantity_kg "not null"
        decimal unit_price "not null"
        decimal line_total "not null"
        int sequence "not null"
    }

    price_list_items {
        string id PK "not null"
        string price_list_id FK "not null"
        string product_id FK "not null"
        decimal unit_price_ex_tax "not null"
        datetime effective_date "not null"
        datetime expiry_date "nullable"
    }

    price_lists {
        string id PK "not null"
        string code "not null"
        string name "not null"
        datetime effective_date "not null"
        datetime expiry_date "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    product_channel_links {
        string id PK "not null"
        string product_id "not null"
        string channel "not null"
        string shopify_product_id "nullable"
        string shopify_variant_id "nullable"
        string shopify_location_id "nullable"
    }

    product_migration_map {
        string id PK "not null"
        string legacy_table "not null"
        string legacy_id "not null"
        string product_id "not null"
        datetime migrated_at "nullable"
    }

    product_variants {
        string id PK "not null"
        string product_id FK "not null"
        string variant_code "not null"
        string variant_name "not null"
        string description "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    products {
        string id "nullable"
        string sku "nullable"
        string name "nullable"
        string description "nullable"
        decimal density_kg_per_l "nullable"
        decimal abv_percent "nullable"
        decimal is_active "nullable"
        decimal created_at "nullable"
        decimal updated_at "nullable"
        string ean13 "nullable"
        string supplier_id "nullable"
        string size "nullable"
        string base_unit "nullable"
        int pack "nullable"
        string dgflag "nullable"
        string form "nullable"
        int pkge "nullable"
        int label "nullable"
        int manu "nullable"
        string taxinc "nullable"
        string salestaxcde "nullable"
        decimal purcost "nullable"
        decimal purtax "nullable"
        decimal wholesalecost "nullable"
        string disccdeone "nullable"
        string disccdetwo "nullable"
        string xero_item_id "nullable"
        decimal last_sync "nullable"
        string product_type "nullable"
        string raw_material_group_id "nullable"
        int raw_material_code "nullable"
        string raw_material_search_key "nullable"
        string raw_material_search_ext "nullable"
        decimal specific_gravity "nullable"
        decimal vol_solid "nullable"
        decimal solid_sg "nullable"
        decimal wt_solid "nullable"
        string usage_unit "nullable"
        decimal usage_cost "nullable"
        decimal restock_level "nullable"
        decimal used_ytd "nullable"
        string hazard "nullable"
        string condition "nullable"
        string msds_flag "nullable"
        int altno1 "nullable"
        int altno2 "nullable"
        int altno3 "nullable"
        int altno4 "nullable"
        int altno5 "nullable"
        string last_movement_date "nullable"
        string last_purchase_date "nullable"
        decimal ean13_raw "nullable"
        string xero_account "nullable"
        string formula_id "nullable"
        int formula_revision "nullable"
        string purchase_unit_id "nullable"
        decimal purchase_volume "nullable"
        decimal is_archived "nullable"
        decimal archived_at "nullable"
        decimal is_tracked "nullable"
        decimal sellable "nullable"
        decimal standard_cost "nullable"
        decimal estimated_cost "nullable"
        string estimate_reason "nullable"
        string estimated_by "nullable"
        decimal estimated_at "nullable"
        decimal wholesalecde "nullable"
        decimal retailcde "nullable"
        decimal countercde "nullable"
        decimal tradecde "nullable"
        decimal contractcde "nullable"
        decimal industrialcde "nullable"
        decimal distributorcde "nullable"
        decimal retail_price_inc_gst "nullable"
        decimal retail_price_ex_gst "nullable"
        decimal retail_excise "nullable"
        decimal wholesale_price_inc_gst "nullable"
        decimal wholesale_price_ex_gst "nullable"
        decimal wholesale_excise "nullable"
        decimal distributor_price_inc_gst "nullable"
        decimal distributor_price_ex_gst "nullable"
        decimal distributor_excise "nullable"
        decimal counter_price_inc_gst "nullable"
        decimal counter_price_ex_gst "nullable"
        decimal counter_excise "nullable"
        decimal trade_price_inc_gst "nullable"
        decimal trade_price_ex_gst "nullable"
        decimal trade_excise "nullable"
        decimal contract_price_inc_gst "nullable"
        decimal contract_price_ex_gst "nullable"
        decimal contract_excise "nullable"
        decimal industrial_price_inc_gst "nullable"
        decimal industrial_price_ex_gst "nullable"
        decimal industrial_excise "nullable"
        decimal purchase_cost_inc_gst "nullable"
        decimal purchase_cost_ex_gst "nullable"
        string purchase_tax_included "nullable"
        decimal usage_cost_inc_gst "nullable"
        decimal usage_cost_ex_gst "nullable"
        string usage_tax_included "nullable"
        decimal is_purchase "nullable"
        decimal is_sell "nullable"
        decimal is_assemble "nullable"
        decimal manufactured_cost_inc_gst "nullable"
        decimal manufactured_cost_ex_gst "nullable"
        string manufactured_tax_included "nullable"
        string purchase_tax_included_bool "nullable"
    }

    purchase_orders {
        string id PK "not null"
        string supplier_id FK "not null"
        string po_number "not null"
        string status "nullable"
        datetime order_date "nullable"
        datetime expected_date "nullable"
        datetime received_date "nullable"
        string notes "nullable"
    }

    qc_results {
        string id PK "not null"
        string batch_id FK "not null"
        string test_name "not null"
        decimal test_value "nullable"
        string test_unit "nullable"
        bool pass_fail "nullable"
        datetime tested_at "nullable"
        string tested_by "nullable"
        string notes "nullable"
        string test_definition_id "nullable"
    }

    quality_test_definitions {
        string id PK "not null"
        string code "not null"
        string name "not null"
        string description "nullable"
        string test_type "nullable"
        string unit "nullable"
        decimal min_value "nullable"
        decimal max_value "nullable"
        decimal target_value "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
        datetime updated_at "nullable"
    }

    raw_material_groups {
        string id PK "not null"
        string code "not null"
        string name "not null"
        string description "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
    }

    raw_material_suppliers {
        string id PK "not null"
        string raw_material_id FK "not null"
        string supplier_id FK "not null"
        bool is_primary "nullable"
        decimal min_qty "nullable"
        int lead_time_days "nullable"
        string notes "nullable"
        datetime created_at "nullable"
    }

    revaluations {
        string id PK "not null"
        string item_id FK "not null"
        string lot_id FK "nullable"
        decimal old_unit_cost "not null"
        decimal new_unit_cost "not null"
        decimal delta_extended_cost "not null"
        string reason "not null"
        string revalued_by "not null"
        datetime revalued_at "not null"
        bool propagated_to_assemblies "nullable"
    }

    sales_orders {
        string id PK "not null"
        string customer_id FK "not null"
        string so_number "not null"
        string status "nullable"
        datetime order_date "nullable"
        datetime requested_date "nullable"
        datetime shipped_date "nullable"
        string notes "nullable"
    }

    so_lines {
        string id PK "not null"
        string sales_order_id FK "not null"
        string product_id FK "not null"
        decimal quantity_kg "not null"
        decimal unit_price_ex_tax "not null"
        decimal tax_rate "not null"
        decimal line_total_ex_tax "not null"
        decimal line_total_inc_tax "not null"
        int sequence "not null"
    }

    suppliers {
        string id PK "not null"
        string code "not null"
        string name "not null"
        string contact_person "nullable"
        string email "nullable"
        string phone "nullable"
        string address "nullable"
        bool is_active "nullable"
        datetime created_at "nullable"
        string xero_contact_id "nullable"
        datetime last_sync "nullable"
    }

    work_order_lines {
        string id PK "not null"
        string work_order_id FK "not null"
        string ingredient_product_id FK "not null"
        decimal required_quantity_kg "not null"
        decimal allocated_quantity_kg "nullable"
        int sequence "not null"
    }

    work_orders {
        string id PK "not null"
        string code "not null"
        string product_id FK "not null"
        string formula_id FK "not null"
        decimal quantity_kg "not null"
        string status "nullable"
        datetime created_at "nullable"
        datetime released_at "nullable"
        datetime completed_at "nullable"
        string notes "nullable"
    }

    xero_sync_log {
        string id PK "not null"
        datetime ts "not null"
        string object_type "nullable"
        string object_id "nullable"
        string direction "nullable"
        string status "nullable"
        string message "nullable"
    }

    xero_tokens {
        string id PK "not null"
        string access_token "not null"
        string refresh_token "not null"
        datetime expires_at "not null"
        string tenant_id "nullable"
        datetime created_at "nullable"
        datetime updated_at "nullable"
    }


    assembly_cost_dependencies }o--|| inventory_lots : "consumed_lot_id -> id"
    assembly_cost_dependencies }o--|| inventory_lots : "produced_lot_id -> id"
    assembly_cost_dependencies }o--|| inventory_txns : "consumed_txn_id -> id"
    assembly_cost_dependencies }o--|| inventory_txns : "produced_txn_id -> id"
    assembly_lines }o--|| assemblies : "assembly_id -> id"
    assembly_lines }o--|| products : "component_product_id -> id"
    batch_components }o--|| batches : "batch_id -> id"
    batch_components }o--|| products : "ingredient_product_id -> id"
    batch_components }o--|| inventory_lots : "lot_id -> id"
    batch_lines }o--|| batches : "batch_id -> id"
    batch_lines }o--|| products : "material_id -> id"
    batches }o--|| work_orders : "work_order_id -> id"
    customer_prices }o--|| customers : "customer_id -> id"
    customer_prices }o--|| products : "product_id -> id"
    finished_goods_inventory }o--|| finished_goods : "fg_id -> id"
    formula_lines }o--|| formulas : "formula_id -> id"
    formulas }o--|| products : "product_id -> id"
    inventory_lots }o--|| products : "product_id -> id"
    inventory_movements }o--|| batches : "source_batch_id -> id"
    inventory_txns }o--|| inventory_lots : "lot_id -> id"
    invoice_lines }o--|| invoices : "invoice_id -> id"
    invoice_lines }o--|| products : "product_id -> id"
    invoices }o--|| customers : "customer_id -> id"
    invoices }o--|| sales_orders : "sales_order_id -> id"
    legacy_acstk_data }o--|| products : "product_id -> id"
    pack_conversions }o--|| pack_units : "from_unit_id -> id"
    pack_conversions }o--|| products : "product_id -> id"
    pack_conversions }o--|| pack_units : "to_unit_id -> id"
    po_lines }o--|| products : "product_id -> id"
    po_lines }o--|| purchase_orders : "purchase_order_id -> id"
    price_list_items }o--|| price_lists : "price_list_id -> id"
    price_list_items }o--|| products : "product_id -> id"
    product_variants }o--|| products : "product_id -> id"
    purchase_orders }o--|| suppliers : "supplier_id -> id"
    qc_results }o--|| batches : "batch_id -> id"
    raw_material_suppliers }o--|| raw_materials : "raw_material_id -> id"
    raw_material_suppliers }o--|| suppliers : "supplier_id -> id"
    revaluations }o--|| products : "item_id -> id"
    revaluations }o--|| inventory_lots : "lot_id -> id"
    sales_orders }o--|| customers : "customer_id -> id"
    so_lines }o--|| products : "product_id -> id"
    so_lines }o--|| sales_orders : "sales_order_id -> id"
    work_order_lines }o--|| products : "ingredient_product_id -> id"
    work_order_lines }o--|| work_orders : "work_order_id -> id"
    work_orders }o--|| formulas : "formula_id -> id"
    work_orders }o--|| products : "product_id -> id"
```

## How to View

1. Install Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`
2. Generate PNG: `mmdc -i docs/snapshot/erd_diagram.mmd -o docs/snapshot/erd_diagram.png`
3. Or view in GitHub/GitLab (renders automatically in markdown)
4. Or use online viewer: https://mermaid.live/
