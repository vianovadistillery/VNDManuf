-- Database Schema Snapshot
-- Generated: 2025-11-03T20:55:33.066874

-- Table: alembic_version
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL,
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
)
;

-- Table: assemblies
CREATE TABLE "assemblies" (
	id VARCHAR(36) NOT NULL,
	parent_product_id VARCHAR(36) NOT NULL,
	effective_from DATETIME,
	effective_to DATETIME,
	version INTEGER DEFAULT '1',
	is_active BOOLEAN DEFAULT '1',
	yield_factor NUMERIC(6, 4) DEFAULT '1.0',
	is_primary BOOLEAN DEFAULT '0' NOT NULL,
	notes VARCHAR(255),
	created_at DATETIME,
	updated_at DATETIME,
	assembly_code VARCHAR(50) NOT NULL,
	assembly_name VARCHAR(200) NOT NULL,
	CONSTRAINT pk_assemblies PRIMARY KEY (id)
)
;

-- Table: assembly_cost_dependencies
CREATE TABLE assembly_cost_dependencies (
	id VARCHAR(36) NOT NULL,
	consumed_lot_id VARCHAR(36) NOT NULL,
	produced_lot_id VARCHAR(36) NOT NULL,
	consumed_txn_id VARCHAR(36) NOT NULL,
	produced_txn_id VARCHAR(36) NOT NULL,
	dependency_ts DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT pk_assembly_cost_dependencies PRIMARY KEY (id),
	CONSTRAINT fk_dep_consumed_lot FOREIGN KEY(consumed_lot_id) REFERENCES inventory_lots (id),
	CONSTRAINT fk_dep_produced_lot FOREIGN KEY(produced_lot_id) REFERENCES inventory_lots (id),
	CONSTRAINT fk_dep_consumed_txn FOREIGN KEY(consumed_txn_id) REFERENCES inventory_txns (id),
	CONSTRAINT fk_dep_produced_txn FOREIGN KEY(produced_txn_id) REFERENCES inventory_txns (id)
)
;

-- Table: assembly_lines
CREATE TABLE assembly_lines (
	id VARCHAR(36) NOT NULL,
	assembly_id VARCHAR(36) NOT NULL,
	component_product_id VARCHAR(36) NOT NULL,
	quantity NUMERIC(12, 3) NOT NULL,
	sequence INTEGER NOT NULL,
	unit VARCHAR(10),
	is_energy_or_overhead BOOLEAN,
	notes TEXT,
	CONSTRAINT pk_assembly_lines PRIMARY KEY (id),
	CONSTRAINT fk_assembly_lines__assembly_id__assemblies FOREIGN KEY(assembly_id) REFERENCES assemblies (id),
	CONSTRAINT fk_assembly_lines__component_product_id__products FOREIGN KEY(component_product_id) REFERENCES products (id),
	CONSTRAINT uq_assembly_line_sequence UNIQUE (assembly_id, sequence)
)
;

-- Table: batch_components
CREATE TABLE batch_components (
	id VARCHAR(36) NOT NULL,
	batch_id VARCHAR(36) NOT NULL,
	ingredient_product_id VARCHAR(36) NOT NULL,
	lot_id VARCHAR(36) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	unit_cost NUMERIC(10, 2),
	CONSTRAINT pk_batch_components PRIMARY KEY (id),
	CONSTRAINT fk_batch_components__batch_id__batches FOREIGN KEY(batch_id) REFERENCES batches (id),
	CONSTRAINT fk_batch_components__ingredient_product_id__products FOREIGN KEY(ingredient_product_id) REFERENCES products (id),
	CONSTRAINT fk_batch_components__lot_id__inventory_lots FOREIGN KEY(lot_id) REFERENCES inventory_lots (id)
)
;

-- Table: batch_lines
CREATE TABLE batch_lines (
	id VARCHAR(36) NOT NULL,
	batch_id VARCHAR(36) NOT NULL,
	material_id VARCHAR(36) NOT NULL,
	role VARCHAR(50),
	qty_theoretical NUMERIC(12, 3) NOT NULL,
	qty_actual NUMERIC(12, 3),
	unit VARCHAR(10) NOT NULL,
	cost_at_time NUMERIC(10, 2),
	CONSTRAINT pk_batch_lines PRIMARY KEY (id),
	CONSTRAINT fk_batch_lines__batch_id__batches FOREIGN KEY(batch_id) REFERENCES batches (id) ON DELETE CASCADE,
	CONSTRAINT fk_batch_lines__material_id__products FOREIGN KEY(material_id) REFERENCES products (id),
	CONSTRAINT uq_batch_line UNIQUE (batch_id, material_id)
)
;

-- Table: batches
CREATE TABLE batches (
	id VARCHAR(36) NOT NULL,
	work_order_id VARCHAR(36) NOT NULL,
	batch_code VARCHAR(50) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	status VARCHAR(20),
	started_at DATETIME,
	completed_at DATETIME,
	notes TEXT, batch_status VARCHAR(20), yield_actual NUMERIC(12, 3), yield_litres NUMERIC(12, 3), variance_percent NUMERIC(5, 2),
	CONSTRAINT pk_batches PRIMARY KEY (id),
	CONSTRAINT fk_batches__work_order_id__work_orders FOREIGN KEY(work_order_id) REFERENCES work_orders (id),
	CONSTRAINT uq_batch_code UNIQUE (work_order_id, batch_code)
)
;

-- Table: condition_types
CREATE TABLE condition_types (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(1) NOT NULL,
	description VARCHAR(100) NOT NULL,
	extended_desc TEXT,
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_condition_types PRIMARY KEY (id),
	CONSTRAINT uq_condition_types__code UNIQUE (code)
)
;

-- Table: contacts
CREATE TABLE contacts (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(50) NOT NULL,
	name VARCHAR(200) NOT NULL,
	contact_person VARCHAR(100),
	email VARCHAR(200),
	phone VARCHAR(50),
	address TEXT,
	is_customer BOOLEAN DEFAULT '0' NOT NULL,
	is_supplier BOOLEAN DEFAULT '0' NOT NULL,
	is_other BOOLEAN DEFAULT '0' NOT NULL,
	tax_rate NUMERIC(5, 2),
	xero_contact_id VARCHAR(100),
	last_sync DATETIME,
	is_active BOOLEAN DEFAULT '1',
	created_at DATETIME,
	updated_at DATETIME,
	CONSTRAINT pk_contacts PRIMARY KEY (id)
)
;

-- Table: customer_prices
CREATE TABLE customer_prices (
	id VARCHAR(36) NOT NULL,
	customer_id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	unit_price_ex_tax NUMERIC(10, 2) NOT NULL,
	effective_date DATETIME NOT NULL,
	expiry_date DATETIME,
	CONSTRAINT pk_customer_prices PRIMARY KEY (id),
	CONSTRAINT fk_customer_prices__customer_id__customers FOREIGN KEY(customer_id) REFERENCES customers (id),
	CONSTRAINT fk_customer_prices__product_id__products FOREIGN KEY(product_id) REFERENCES products (id),
	CONSTRAINT uq_customer_price_date UNIQUE (customer_id, product_id, effective_date)
)
;

-- Table: customers
CREATE TABLE customers (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(50) NOT NULL,
	name VARCHAR(200) NOT NULL,
	contact_person VARCHAR(100),
	email VARCHAR(200),
	phone VARCHAR(50),
	address TEXT,
	tax_rate NUMERIC(5, 2),
	is_active BOOLEAN,
	created_at DATETIME, xero_contact_id VARCHAR(100), last_sync DATETIME,
	CONSTRAINT pk_customers PRIMARY KEY (id)
)
;

-- Table: datasets
CREATE TABLE datasets (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(3) NOT NULL,
	name VARCHAR(50) NOT NULL,
	description TEXT,
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_datasets PRIMARY KEY (id),
	CONSTRAINT uq_datasets__code UNIQUE (code)
)
;

-- Table: excise_rates
CREATE TABLE excise_rates (
	id VARCHAR(36) NOT NULL,
	date_active_from DATETIME NOT NULL,
	rate_per_l_abv NUMERIC(10, 4) NOT NULL,
	description TEXT,
	is_active BOOLEAN NOT NULL,
	created_at DATETIME,
	updated_at DATETIME,
	CONSTRAINT pk_excise_rates PRIMARY KEY (id)
)
;

-- Table: finished_goods_inventory
CREATE TABLE finished_goods_inventory (
	fg_id VARCHAR(36) NOT NULL,
	soh NUMERIC(12, 3) NOT NULL,
	CONSTRAINT pk_finished_goods_inventory PRIMARY KEY (fg_id),
	CONSTRAINT fk_finished_goods_inventory__fg_id__finished_goods FOREIGN KEY(fg_id) REFERENCES finished_goods (id) ON DELETE CASCADE
)
;

-- Table: formula_classes
CREATE TABLE formula_classes (
	id VARCHAR(36) NOT NULL,
	name VARCHAR(100) NOT NULL,
	description TEXT,
	ytd_amounts TEXT,
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_formula_classes PRIMARY KEY (id),
	CONSTRAINT uq_formula_classes__name UNIQUE (name)
)
;

-- Table: formula_lines
CREATE TABLE "formula_lines" (
	id VARCHAR(36) NOT NULL,
	formula_id VARCHAR(36) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	sequence INTEGER NOT NULL,
	notes TEXT,
	unit VARCHAR(10),
	product_id VARCHAR(36),
	CONSTRAINT pk_formula_lines PRIMARY KEY (id),
	CONSTRAINT fk_formula_lines__formula_id__formulas FOREIGN KEY(formula_id) REFERENCES formulas (id),
	CONSTRAINT uq_formula_line_sequence UNIQUE (formula_id, sequence)
)
;

-- Table: formulas
CREATE TABLE formulas (
	id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	formula_code VARCHAR(50) NOT NULL,
	formula_name VARCHAR(200) NOT NULL,
	version INTEGER,
	is_active BOOLEAN,
	created_at DATETIME,
	updated_at DATETIME, notes TEXT, is_archived BOOLEAN DEFAULT '0' NOT NULL, archived_at DATETIME, instructions TEXT,
	CONSTRAINT pk_formulas PRIMARY KEY (id),
	CONSTRAINT fk_formulas__product_id__products FOREIGN KEY(product_id) REFERENCES products (id),
	CONSTRAINT uq_formula_version UNIQUE (product_id, formula_code, version)
)
;

-- Table: inventory_lots
CREATE TABLE inventory_lots (
	id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	lot_code VARCHAR(50) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	unit_cost NUMERIC(10, 2),
	received_at DATETIME,
	expires_at DATETIME,
	is_active BOOLEAN,
	created_at DATETIME, original_unit_cost NUMERIC(10, 2), current_unit_cost NUMERIC(10, 2),
	CONSTRAINT pk_inventory_lots PRIMARY KEY (id),
	CONSTRAINT fk_inventory_lots__product_id__products FOREIGN KEY(product_id) REFERENCES products (id),
	CONSTRAINT uq_lot_code UNIQUE (product_id, lot_code)
)
;

-- Table: inventory_movements
CREATE TABLE "inventory_movements" (
	id VARCHAR(36) NOT NULL,
	ts DATETIME NOT NULL,
	date VARCHAR(10) NOT NULL,
	qty NUMERIC(12, 3) NOT NULL,
	unit VARCHAR(10) NOT NULL,
	direction VARCHAR(10) NOT NULL,
	source_batch_id VARCHAR(36),
	note TEXT,
	product_id VARCHAR(36),
	CONSTRAINT pk_inventory_movements PRIMARY KEY (id),
	CONSTRAINT fk_inventory_movements__source_batch_id__batches FOREIGN KEY(source_batch_id) REFERENCES batches (id)
)
;

-- Table: inventory_reservations
CREATE TABLE inventory_reservations (
	id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	qty_canonical NUMERIC(18, 6) NOT NULL,
	source VARCHAR(16) NOT NULL,
	reference_id VARCHAR(128),
	status VARCHAR(16) DEFAULT 'ACTIVE' NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT pk_inventory_reservations PRIMARY KEY (id)
)
;

-- Table: inventory_txns
CREATE TABLE inventory_txns (
	id VARCHAR(36) NOT NULL,
	lot_id VARCHAR(36) NOT NULL,
	transaction_type VARCHAR(20) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	unit_cost NUMERIC(10, 2),
	reference_type VARCHAR(50),
	reference_id VARCHAR(36),
	notes TEXT,
	created_at DATETIME,
	created_by VARCHAR(100), cost_source VARCHAR(20), extended_cost NUMERIC(12, 2), estimate_flag BOOLEAN DEFAULT '0', estimate_reason TEXT,
	CONSTRAINT pk_inventory_txns PRIMARY KEY (id),
	CONSTRAINT fk_inventory_txns__lot_id__inventory_lots FOREIGN KEY(lot_id) REFERENCES inventory_lots (id)
)
;

-- Table: invoice_lines
CREATE TABLE invoice_lines (
	id VARCHAR(36) NOT NULL,
	invoice_id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	unit_price_ex_tax NUMERIC(10, 2) NOT NULL,
	tax_rate NUMERIC(5, 2) NOT NULL,
	line_total_ex_tax NUMERIC(12, 2) NOT NULL,
	line_total_inc_tax NUMERIC(12, 2) NOT NULL,
	sequence INTEGER NOT NULL,
	CONSTRAINT pk_invoice_lines PRIMARY KEY (id),
	CONSTRAINT fk_invoice_lines__invoice_id__invoices FOREIGN KEY(invoice_id) REFERENCES invoices (id),
	CONSTRAINT fk_invoice_lines__product_id__products FOREIGN KEY(product_id) REFERENCES products (id)
)
;

-- Table: invoices
CREATE TABLE invoices (
	id VARCHAR(36) NOT NULL,
	customer_id VARCHAR(36) NOT NULL,
	sales_order_id VARCHAR(36),
	invoice_number VARCHAR(50) NOT NULL,
	invoice_date DATETIME,
	due_date DATETIME,
	status VARCHAR(20),
	subtotal_ex_tax NUMERIC(12, 2) NOT NULL,
	total_tax NUMERIC(12, 2) NOT NULL,
	total_inc_tax NUMERIC(12, 2) NOT NULL,
	notes TEXT,
	CONSTRAINT pk_invoices PRIMARY KEY (id),
	CONSTRAINT fk_invoices__customer_id__customers FOREIGN KEY(customer_id) REFERENCES customers (id),
	CONSTRAINT fk_invoices__sales_order_id__sales_orders FOREIGN KEY(sales_order_id) REFERENCES sales_orders (id)
)
;

-- Table: legacy_acstk_data
CREATE TABLE legacy_acstk_data (
	id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	legacy_no INTEGER,
	legacy_search VARCHAR(50),
	ean13 NUMERIC(18, 4),
	desc1 VARCHAR(50),
	desc2 VARCHAR(20),
	legacy_suplr VARCHAR(10),
	size VARCHAR(10),
	legacy_unit VARCHAR(10),
	pack INTEGER,
	dgflag VARCHAR(1),
	form VARCHAR(10),
	pkge INTEGER,
	label INTEGER,
	manu INTEGER,
	legacy_active VARCHAR(1),
	taxinc VARCHAR(1),
	salestaxcde VARCHAR(1),
	purcost NUMERIC(10, 2),
	purtax NUMERIC(10, 2),
	wholesalecost NUMERIC(10, 2),
	disccdeone VARCHAR(1),
	disccdetwo VARCHAR(1),
	wholesalecde VARCHAR(1),
	retailcde VARCHAR(1),
	countercde VARCHAR(1),
	tradecde VARCHAR(1),
	contractcde VARCHAR(1),
	industrialcde VARCHAR(1),
	distributorcde VARCHAR(1),
	retail NUMERIC(10, 2),
	counter NUMERIC(10, 2),
	trade NUMERIC(10, 2),
	contract NUMERIC(10, 2),
	industrial NUMERIC(10, 2),
	distributor NUMERIC(10, 2),
	suplr4stdcost VARCHAR(10),
	search4stdcost VARCHAR(50),
	cogs NUMERIC(10, 2),
	gpc NUMERIC(10, 2),
	rmc NUMERIC(10, 2),
	gpr NUMERIC(10, 4),
	soh INTEGER,
	sohv NUMERIC(10, 2),
	sip INTEGER,
	soo INTEGER,
	sold INTEGER,
	legacy_date VARCHAR(10),
	bulk NUMERIC(10, 2),
	lid INTEGER,
	pbox INTEGER,
	boxlbl INTEGER,
	imported_at DATETIME,
	notes TEXT,
	CONSTRAINT pk_legacy_acstk_data PRIMARY KEY (id),
	CONSTRAINT fk_legacy_acstk_data__product_id__products FOREIGN KEY(product_id) REFERENCES products (id)
)
;

-- Table: manufacturing_config
CREATE TABLE manufacturing_config (
	id VARCHAR(36) NOT NULL,
	qtyf VARCHAR(10),
	bchno_width VARCHAR(10),
	bch_offset VARCHAR(10),
	company_name VARCHAR(50),
	site_code VARCHAR(10),
	max1 NUMERIC(10, 2),
	max2 NUMERIC(10, 2),
	max3 NUMERIC(10, 2),
	max4 NUMERIC(10, 2),
	max5 NUMERIC(10, 2),
	max6 NUMERIC(10, 2),
	max7 NUMERIC(10, 2),
	max8 NUMERIC(10, 2),
	max9 NUMERIC(10, 2),
	flags1 VARCHAR(10),
	flags2 VARCHAR(10),
	flags3 VARCHAR(10),
	flags4 VARCHAR(10),
	flags5 VARCHAR(10),
	flags6 VARCHAR(10),
	flags7 VARCHAR(10),
	flags8 VARCHAR(10),
	rep1 VARCHAR(10),
	rep2 VARCHAR(10),
	rep3 VARCHAR(10),
	rep4 VARCHAR(10),
	rep5 VARCHAR(10),
	rep6 VARCHAR(10),
	print_hi1 VARCHAR(10),
	db_month_raw VARCHAR(10),
	cr_month_raw VARCHAR(10),
	cans_idx INTEGER,
	label_idx INTEGER,
	labour_idx INTEGER,
	created_at DATETIME,
	updated_at DATETIME,
	CONSTRAINT pk_manufacturing_config PRIMARY KEY (id)
)
;

-- Table: markups
CREATE TABLE markups (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(10) NOT NULL,
	name VARCHAR(100) NOT NULL,
	description TEXT,
	enabled_flag VARCHAR(1),
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_markups PRIMARY KEY (id),
	CONSTRAINT uq_markups__code UNIQUE (code)
)
;

-- Table: pack_conversions
CREATE TABLE pack_conversions (
	id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	from_unit_id VARCHAR(36) NOT NULL,
	to_unit_id VARCHAR(36) NOT NULL,
	conversion_factor NUMERIC(12, 6) NOT NULL,
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_pack_conversions PRIMARY KEY (id),
	CONSTRAINT fk_pack_conversions__from_unit_id__pack_units FOREIGN KEY(from_unit_id) REFERENCES pack_units (id),
	CONSTRAINT fk_pack_conversions__product_id__products FOREIGN KEY(product_id) REFERENCES products (id),
	CONSTRAINT fk_pack_conversions__to_unit_id__pack_units FOREIGN KEY(to_unit_id) REFERENCES pack_units (id),
	CONSTRAINT uq_pack_conversion UNIQUE (product_id, from_unit_id, to_unit_id)
)
;

-- Table: pack_units
CREATE TABLE pack_units (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(20) NOT NULL,
	name VARCHAR(100) NOT NULL,
	description TEXT,
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_pack_units PRIMARY KEY (id)
)
;

-- Table: po_lines
CREATE TABLE po_lines (
	id VARCHAR(36) NOT NULL,
	purchase_order_id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	unit_price NUMERIC(10, 2) NOT NULL,
	line_total NUMERIC(12, 2) NOT NULL,
	sequence INTEGER NOT NULL,
	CONSTRAINT pk_po_lines PRIMARY KEY (id),
	CONSTRAINT fk_po_lines__product_id__products FOREIGN KEY(product_id) REFERENCES products (id),
	CONSTRAINT fk_po_lines__purchase_order_id__purchase_orders FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id)
)
;

-- Table: price_list_items
CREATE TABLE price_list_items (
	id VARCHAR(36) NOT NULL,
	price_list_id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	unit_price_ex_tax NUMERIC(10, 2) NOT NULL,
	effective_date DATETIME NOT NULL,
	expiry_date DATETIME,
	CONSTRAINT pk_price_list_items PRIMARY KEY (id),
	CONSTRAINT fk_price_list_items__price_list_id__price_lists FOREIGN KEY(price_list_id) REFERENCES price_lists (id),
	CONSTRAINT fk_price_list_items__product_id__products FOREIGN KEY(product_id) REFERENCES products (id),
	CONSTRAINT uq_price_item_date UNIQUE (price_list_id, product_id, effective_date)
)
;

-- Table: price_lists
CREATE TABLE price_lists (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(50) NOT NULL,
	name VARCHAR(200) NOT NULL,
	effective_date DATETIME NOT NULL,
	expiry_date DATETIME,
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_price_lists PRIMARY KEY (id)
)
;

-- Table: product_channel_links
CREATE TABLE product_channel_links (
	id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	channel VARCHAR(32) DEFAULT 'shopify' NOT NULL,
	shopify_product_id VARCHAR(64),
	shopify_variant_id VARCHAR(64),
	shopify_location_id VARCHAR(64),
	CONSTRAINT pk_product_channel_links PRIMARY KEY (id),
	CONSTRAINT uq_product_channel UNIQUE (product_id, channel)
)
;

-- Table: product_migration_map
CREATE TABLE product_migration_map (
	id VARCHAR(36) NOT NULL,
	legacy_table VARCHAR(50) NOT NULL,
	legacy_id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	migrated_at DATETIME,
	CONSTRAINT pk_product_migration_map PRIMARY KEY (id)
)
;

-- Table: product_variants
CREATE TABLE product_variants (
	id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	variant_code VARCHAR(50) NOT NULL,
	variant_name VARCHAR(200) NOT NULL,
	description TEXT,
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_product_variants PRIMARY KEY (id),
	CONSTRAINT fk_product_variants__product_id__products FOREIGN KEY(product_id) REFERENCES products (id),
	CONSTRAINT uq_product_variant_code UNIQUE (product_id, variant_code)
)
;

-- Table: products
CREATE TABLE "products"(
  id TEXT,
  sku TEXT,
  name TEXT,
  description TEXT,
  density_kg_per_l NUM,
  abv_percent NUM,
  is_active NUM,
  created_at NUM,
  updated_at NUM,
  ean13 TEXT,
  supplier_id TEXT,
  size TEXT,
  base_unit TEXT,
  pack INT,
  dgflag TEXT,
  form TEXT,
  pkge INT,
  label INT,
  manu INT,
  taxinc TEXT,
  salestaxcde TEXT,
  purcost NUM,
  purtax NUM,
  wholesalecost NUM,
  disccdeone TEXT,
  disccdetwo TEXT,
  xero_item_id TEXT,
  last_sync NUM,
  product_type TEXT,
  raw_material_group_id TEXT,
  raw_material_code INT,
  raw_material_search_key TEXT,
  raw_material_search_ext TEXT,
  specific_gravity NUM,
  vol_solid NUM,
  solid_sg NUM,
  wt_solid NUM,
  usage_unit TEXT,
  usage_cost NUM,
  restock_level NUM,
  used_ytd NUM,
  hazard TEXT,
  condition TEXT,
  msds_flag TEXT,
  altno1 INT,
  altno2 INT,
  altno3 INT,
  altno4 INT,
  altno5 INT,
  last_movement_date TEXT,
  last_purchase_date TEXT,
  ean13_raw NUM,
  xero_account TEXT,
  formula_id TEXT,
  formula_revision INT,
  purchase_unit_id TEXT,
  purchase_volume NUM,
  is_archived NUM,
  archived_at NUM,
  is_tracked NUM,
  sellable NUM,
  standard_cost NUM,
  estimated_cost NUM,
  estimate_reason TEXT,
  estimated_by TEXT,
  estimated_at NUM,
  wholesalecde NUM,
  retailcde NUM,
  countercde NUM,
  tradecde NUM,
  contractcde NUM,
  industrialcde NUM,
  distributorcde NUM,
  retail_price_inc_gst NUM,
  retail_price_ex_gst NUM,
  retail_excise NUM,
  wholesale_price_inc_gst NUM,
  wholesale_price_ex_gst NUM,
  wholesale_excise NUM,
  distributor_price_inc_gst NUM,
  distributor_price_ex_gst NUM,
  distributor_excise NUM,
  counter_price_inc_gst NUM,
  counter_price_ex_gst NUM,
  counter_excise NUM,
  trade_price_inc_gst NUM,
  trade_price_ex_gst NUM,
  trade_excise NUM,
  contract_price_inc_gst NUM,
  contract_price_ex_gst NUM,
  contract_excise NUM,
  industrial_price_inc_gst NUM,
  industrial_price_ex_gst NUM,
  industrial_excise NUM,
  purchase_cost_inc_gst NUM,
  purchase_cost_ex_gst NUM,
  purchase_tax_included TEXT,
  usage_cost_inc_gst NUM,
  usage_cost_ex_gst NUM,
  usage_tax_included TEXT,
  is_purchase NUM,
  is_sell NUM,
  is_assemble NUM,
  manufactured_cost_inc_gst NUM,
  manufactured_cost_ex_gst NUM,
  manufactured_tax_included TEXT,
  purchase_tax_included_bool
)
;

-- Table: purchase_orders
CREATE TABLE purchase_orders (
	id VARCHAR(36) NOT NULL,
	supplier_id VARCHAR(36) NOT NULL,
	po_number VARCHAR(50) NOT NULL,
	status VARCHAR(20),
	order_date DATETIME,
	expected_date DATETIME,
	received_date DATETIME,
	notes TEXT,
	CONSTRAINT pk_purchase_orders PRIMARY KEY (id),
	CONSTRAINT fk_purchase_orders__supplier_id__suppliers FOREIGN KEY(supplier_id) REFERENCES suppliers (id)
)
;

-- Table: qc_results
CREATE TABLE qc_results (
	id VARCHAR(36) NOT NULL,
	batch_id VARCHAR(36) NOT NULL,
	test_name VARCHAR(100) NOT NULL,
	test_value NUMERIC(12, 3),
	test_unit VARCHAR(20),
	pass_fail BOOLEAN,
	tested_at DATETIME,
	tested_by VARCHAR(100),
	notes TEXT, test_definition_id VARCHAR(36),
	CONSTRAINT pk_qc_results PRIMARY KEY (id),
	CONSTRAINT fk_qc_results__batch_id__batches FOREIGN KEY(batch_id) REFERENCES batches (id)
)
;

-- Table: quality_test_definitions
CREATE TABLE quality_test_definitions (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(50) NOT NULL,
	name VARCHAR(200) NOT NULL,
	description TEXT,
	test_type VARCHAR(50),
	unit VARCHAR(20),
	min_value NUMERIC(12, 3),
	max_value NUMERIC(12, 3),
	target_value NUMERIC(12, 3),
	is_active BOOLEAN,
	created_at DATETIME,
	updated_at DATETIME,
	CONSTRAINT pk_quality_test_definitions PRIMARY KEY (id)
)
;

-- Table: raw_material_groups
CREATE TABLE raw_material_groups (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(10) NOT NULL,
	name VARCHAR(100) NOT NULL,
	description TEXT,
	is_active BOOLEAN,
	created_at DATETIME,
	CONSTRAINT pk_raw_material_groups PRIMARY KEY (id),
	CONSTRAINT uq_raw_material_groups__code UNIQUE (code)
)
;

-- Table: raw_material_suppliers
CREATE TABLE raw_material_suppliers (
	id VARCHAR(36) NOT NULL,
	raw_material_id VARCHAR(36) NOT NULL,
	supplier_id VARCHAR(36) NOT NULL,
	is_primary BOOLEAN,
	min_qty NUMERIC(12, 3),
	lead_time_days INTEGER,
	notes TEXT,
	created_at DATETIME,
	CONSTRAINT pk_raw_material_suppliers PRIMARY KEY (id),
	CONSTRAINT fk_raw_material_suppliers__raw_material_id__raw_materials FOREIGN KEY(raw_material_id) REFERENCES raw_materials (id),
	CONSTRAINT fk_raw_material_suppliers__supplier_id__suppliers FOREIGN KEY(supplier_id) REFERENCES suppliers (id),
	CONSTRAINT uq_rm_supplier UNIQUE (raw_material_id, supplier_id)
)
;

-- Table: revaluations
CREATE TABLE revaluations (
	id VARCHAR(36) NOT NULL,
	item_id VARCHAR(36) NOT NULL,
	lot_id VARCHAR(36),
	old_unit_cost NUMERIC(10, 2) NOT NULL,
	new_unit_cost NUMERIC(10, 2) NOT NULL,
	delta_extended_cost NUMERIC(12, 2) NOT NULL,
	reason TEXT NOT NULL,
	revalued_by VARCHAR(100) NOT NULL,
	revalued_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
	propagated_to_assemblies BOOLEAN DEFAULT '0',
	CONSTRAINT pk_revaluations PRIMARY KEY (id),
	CONSTRAINT fk_reval_item FOREIGN KEY(item_id) REFERENCES products (id),
	CONSTRAINT fk_reval_lot FOREIGN KEY(lot_id) REFERENCES inventory_lots (id)
)
;

-- Table: sales_orders
CREATE TABLE sales_orders (
	id VARCHAR(36) NOT NULL,
	customer_id VARCHAR(36) NOT NULL,
	so_number VARCHAR(50) NOT NULL,
	status VARCHAR(20),
	order_date DATETIME,
	requested_date DATETIME,
	shipped_date DATETIME,
	notes TEXT,
	CONSTRAINT pk_sales_orders PRIMARY KEY (id),
	CONSTRAINT fk_sales_orders__customer_id__customers FOREIGN KEY(customer_id) REFERENCES customers (id)
)
;

-- Table: so_lines
CREATE TABLE so_lines (
	id VARCHAR(36) NOT NULL,
	sales_order_id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	unit_price_ex_tax NUMERIC(10, 2) NOT NULL,
	tax_rate NUMERIC(5, 2) NOT NULL,
	line_total_ex_tax NUMERIC(12, 2) NOT NULL,
	line_total_inc_tax NUMERIC(12, 2) NOT NULL,
	sequence INTEGER NOT NULL,
	CONSTRAINT pk_so_lines PRIMARY KEY (id),
	CONSTRAINT fk_so_lines__product_id__products FOREIGN KEY(product_id) REFERENCES products (id),
	CONSTRAINT fk_so_lines__sales_order_id__sales_orders FOREIGN KEY(sales_order_id) REFERENCES sales_orders (id)
)
;

-- Table: suppliers
CREATE TABLE suppliers (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(50) NOT NULL,
	name VARCHAR(200) NOT NULL,
	contact_person VARCHAR(100),
	email VARCHAR(200),
	phone VARCHAR(50),
	address TEXT,
	is_active BOOLEAN,
	created_at DATETIME, xero_contact_id VARCHAR(100), last_sync DATETIME,
	CONSTRAINT pk_suppliers PRIMARY KEY (id)
)
;

-- Table: work_order_lines
CREATE TABLE work_order_lines (
	id VARCHAR(36) NOT NULL,
	work_order_id VARCHAR(36) NOT NULL,
	ingredient_product_id VARCHAR(36) NOT NULL,
	required_quantity_kg NUMERIC(12, 3) NOT NULL,
	allocated_quantity_kg NUMERIC(12, 3),
	sequence INTEGER NOT NULL,
	CONSTRAINT pk_work_order_lines PRIMARY KEY (id),
	CONSTRAINT fk_work_order_lines__ingredient_product_id__products FOREIGN KEY(ingredient_product_id) REFERENCES products (id),
	CONSTRAINT fk_work_order_lines__work_order_id__work_orders FOREIGN KEY(work_order_id) REFERENCES work_orders (id)
)
;

-- Table: work_orders
CREATE TABLE work_orders (
	id VARCHAR(36) NOT NULL,
	code VARCHAR(50) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	formula_id VARCHAR(36) NOT NULL,
	quantity_kg NUMERIC(12, 3) NOT NULL,
	status VARCHAR(20),
	created_at DATETIME,
	released_at DATETIME,
	completed_at DATETIME,
	notes TEXT,
	CONSTRAINT pk_work_orders PRIMARY KEY (id),
	CONSTRAINT fk_work_orders__formula_id__formulas FOREIGN KEY(formula_id) REFERENCES formulas (id),
	CONSTRAINT fk_work_orders__product_id__products FOREIGN KEY(product_id) REFERENCES products (id)
)
;

-- Table: xero_sync_log
CREATE TABLE xero_sync_log (
	id VARCHAR(36) NOT NULL,
	ts DATETIME NOT NULL,
	object_type VARCHAR(50),
	object_id VARCHAR(100),
	direction VARCHAR(10),
	status VARCHAR(20),
	message TEXT,
	CONSTRAINT pk_xero_sync_log PRIMARY KEY (id)
)
;

-- Table: xero_tokens
CREATE TABLE xero_tokens (
	id VARCHAR(36) NOT NULL,
	access_token TEXT NOT NULL,
	refresh_token TEXT NOT NULL,
	expires_at DATETIME NOT NULL,
	tenant_id VARCHAR(100),
	created_at DATETIME,
	updated_at DATETIME,
	CONSTRAINT pk_xero_tokens PRIMARY KEY (id)
)
;
