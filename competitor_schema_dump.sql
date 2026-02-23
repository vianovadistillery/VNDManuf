
-- index ix_brands_name on brands
CREATE INDEX ix_brands_name ON brands (name);

-- index ix_carton_specs_deleted_at on carton_specs
CREATE INDEX ix_carton_specs_deleted_at ON carton_specs(deleted_at);

-- index ix_carton_specs_pack_spec_id on carton_specs
CREATE INDEX ix_carton_specs_pack_spec_id ON carton_specs(pack_spec_id);

-- index ix_carton_specs_package_spec_id on carton_specs
CREATE INDEX ix_carton_specs_package_spec_id ON carton_specs(package_spec_id);

-- index ix_mfg_costs_effective_date on manufacturing_costs
CREATE INDEX ix_mfg_costs_effective_date ON manufacturing_costs(effective_date);

-- index ix_mfg_costs_sku_id on manufacturing_costs
CREATE INDEX ix_mfg_costs_sku_id ON manufacturing_costs(sku_id);

-- index ix_pack_specs_deleted_at on pack_specs
CREATE INDEX ix_pack_specs_deleted_at ON pack_specs(deleted_at);

-- index ix_pack_specs_package_spec_id on pack_specs
CREATE INDEX ix_pack_specs_package_spec_id ON pack_specs(package_spec_id);

-- index ix_price_observations_channel_observation_dt on price_observations
CREATE INDEX ix_price_observations_channel_observation_dt ON price_observations (channel, observation_dt);

-- index ix_price_observations_company_id_observation_dt on price_observations
CREATE INDEX ix_price_observations_company_id_observation_dt ON price_observations (company_id, observation_dt);

-- index ix_price_observations_hash_key on price_observations
CREATE INDEX ix_price_observations_hash_key ON price_observations (hash_key);

-- index ix_price_observations_location_id_observation_dt on price_observations
CREATE INDEX ix_price_observations_location_id_observation_dt ON price_observations (location_id, observation_dt);

-- index ix_price_observations_observation_dt on price_observations
CREATE INDEX ix_price_observations_observation_dt ON price_observations (observation_dt);

-- index ix_price_observations_sku_id_observation_dt on price_observations
CREATE INDEX ix_price_observations_sku_id_observation_dt ON price_observations (sku_id, observation_dt);

-- index ix_sku_packs_deleted_at on sku_packs
CREATE INDEX ix_sku_packs_deleted_at ON sku_packs(deleted_at);

-- index ix_sku_packs_pack_spec_id on sku_packs
CREATE INDEX ix_sku_packs_pack_spec_id ON sku_packs(pack_spec_id);

-- index sqlite_autoindex_alembic_version_1 on alembic_version
-- no SQL;

-- index sqlite_autoindex_attachments_1 on attachments
-- no SQL;

-- index sqlite_autoindex_brands_1 on brands
-- no SQL;

-- index sqlite_autoindex_brands_2 on brands
-- no SQL;

-- index sqlite_autoindex_carton_specs_1 on carton_specs
-- no SQL;

-- index sqlite_autoindex_carton_specs_2 on carton_specs
-- no SQL;

-- index sqlite_autoindex_companies_1 on companies
-- no SQL;

-- index sqlite_autoindex_companies_2 on companies
-- no SQL;

-- index sqlite_autoindex_locations_1 on locations
-- no SQL;

-- index sqlite_autoindex_locations_2 on locations
-- no SQL;

-- index sqlite_autoindex_package_specs_1 on package_specs
-- no SQL;

-- index sqlite_autoindex_package_specs_2 on package_specs
-- no SQL;

-- index sqlite_autoindex_price_observations_1 on price_observations
-- no SQL;

-- index sqlite_autoindex_products_1 on products
-- no SQL;

-- index sqlite_autoindex_products_2 on products
-- no SQL;

-- index sqlite_autoindex_sku_cartons_1 on sku_cartons
-- no SQL;

-- index sqlite_autoindex_sku_cartons_2 on sku_cartons
-- no SQL;

-- index sqlite_autoindex_skus_1 on skus
-- no SQL;

-- index sqlite_autoindex_skus_2 on skus
-- no SQL;

-- index sqlite_autoindex_skus_3 on skus
-- no SQL;

-- table alembic_version on alembic_version
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL,
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- table attachments on attachments
CREATE TABLE attachments (
	id VARCHAR(36) NOT NULL,
	price_observation_id VARCHAR(36) NOT NULL,
	file_path VARCHAR(1024) NOT NULL,
	caption VARCHAR(255),
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME,
	CONSTRAINT pk_attachments PRIMARY KEY (id),
	CONSTRAINT fk_attachments__price_observation_id__price_observations FOREIGN KEY(price_observation_id) REFERENCES price_observations (id) ON DELETE CASCADE
);

-- table brands on brands
CREATE TABLE brands (
	id VARCHAR(36) NOT NULL,
	name VARCHAR(255) NOT NULL,
	owner_company VARCHAR(255),
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME,
	CONSTRAINT pk_brands PRIMARY KEY (id),
	CONSTRAINT uq_brands_name UNIQUE (name)
);

-- table carton_specs on carton_specs
CREATE TABLE carton_specs (
	id VARCHAR(36) NOT NULL,
	units_per_carton INTEGER NOT NULL,
	notes TEXT,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME, pack_spec_id INTEGER, pack_count INTEGER, package_spec_id INTEGER, gtin TEXT,
	CONSTRAINT pk_carton_specs PRIMARY KEY (id),
	CONSTRAINT uq_carton_specs_units UNIQUE (units_per_carton)
);

-- table companies on companies
CREATE TABLE companies (
	id VARCHAR(36) NOT NULL,
	name VARCHAR(255) NOT NULL,
	type VARCHAR(32) DEFAULT 'other' NOT NULL,
	parent_company_id VARCHAR(36),
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME,
	CONSTRAINT pk_companies PRIMARY KEY (id),
	CONSTRAINT fk_companies__parent_company_id__companies FOREIGN KEY(parent_company_id) REFERENCES companies (id) ON DELETE SET NULL,
	CONSTRAINT uq_companies_name UNIQUE (name),
	CONSTRAINT ck_companies_ck_companies_type CHECK (type IN ('distributor','retailer','venue','other'))
);

-- table locations on locations
CREATE TABLE locations (
	id VARCHAR(36) NOT NULL,
	company_id VARCHAR(36) NOT NULL,
	store_name VARCHAR(255),
	state VARCHAR(64) NOT NULL,
	suburb VARCHAR(255) NOT NULL,
	postcode VARCHAR(16),
	lat FLOAT,
	lon FLOAT,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME, address TEXT, chain_alignment TEXT, main_contact TEXT, decision_maker TEXT,
	CONSTRAINT pk_locations PRIMARY KEY (id),
	CONSTRAINT fk_locations__company_id__companies FOREIGN KEY(company_id) REFERENCES companies (id) ON DELETE CASCADE,
	CONSTRAINT uq_locations_company_store UNIQUE (company_id, store_name, state, suburb, postcode)
);

-- table manufacturing_costs on manufacturing_costs
CREATE TABLE manufacturing_costs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          sku_id INTEGER NOT NULL,
          cost_type TEXT,
          cost_currency TEXT,
          cost_per_unit REAL,
          cost_per_pack REAL,
          cost_per_carton REAL,
          effective_date TEXT,
          notes TEXT,
          created_at TEXT,
          updated_at TEXT,
          deleted_at TEXT
        );

-- table pack_specs on pack_specs
CREATE TABLE pack_specs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          package_spec_id INTEGER NOT NULL,
          units_per_pack INTEGER,
          gtin TEXT,
          notes TEXT,
          created_at TEXT,
          updated_at TEXT,
          deleted_at TEXT
        );

-- table package_specs on package_specs
CREATE TABLE package_specs (
	id VARCHAR(36) NOT NULL,
	type VARCHAR(32) NOT NULL,
	container_ml INTEGER NOT NULL,
	can_form_factor VARCHAR(32),
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME,
	CONSTRAINT pk_package_specs PRIMARY KEY (id),
	CONSTRAINT uq_package_specs_unique UNIQUE (type, container_ml, can_form_factor),
	CONSTRAINT ck_package_specs_ck_package_specs_type CHECK (type IN ('bottle','can')),
	CONSTRAINT ck_package_specs_ck_package_specs_can_form_factor CHECK ((type = 'can' AND can_form_factor IS NOT NULL) OR (type = 'bottle' AND can_form_factor IS NULL)),
	CONSTRAINT ck_package_specs_ck_package_specs_can_form_factor_values CHECK ((can_form_factor IS NULL) OR can_form_factor IN ('slim','sleek','classic'))
);

-- table price_observations on price_observations
CREATE TABLE price_observations (
	id VARCHAR(36) NOT NULL,
	sku_id VARCHAR(36) NOT NULL,
	company_id VARCHAR(36) NOT NULL,
	location_id VARCHAR(36),
	channel VARCHAR(64) NOT NULL,
	price_context VARCHAR(32) DEFAULT 'shelf' NOT NULL,
	promo_name VARCHAR(255),
	availability VARCHAR(32) DEFAULT 'unknown' NOT NULL,
	price_ex_gst_raw NUMERIC(12, 2),
	price_inc_gst_raw NUMERIC(12, 2),
	gst_rate NUMERIC(6, 4) DEFAULT '0.10' NOT NULL,
	currency VARCHAR(8) DEFAULT 'AUD' NOT NULL,
	is_carton_price BOOLEAN DEFAULT 0 NOT NULL,
	carton_units INTEGER,
	price_ex_gst_norm NUMERIC(12, 2) NOT NULL,
	price_inc_gst_norm NUMERIC(12, 2) NOT NULL,
	unit_price_inc_gst NUMERIC(12, 4) NOT NULL,
	carton_price_inc_gst NUMERIC(12, 2),
	price_per_litre NUMERIC(12, 4) NOT NULL,
	price_per_unit_pure_alcohol NUMERIC(14, 4) NOT NULL,
	standard_drinks NUMERIC(12, 4) NOT NULL,
	observation_dt DATETIME NOT NULL,
	source_type VARCHAR(32) NOT NULL,
	source_url VARCHAR(1024),
	source_note TEXT,
	hash_key VARCHAR(128) NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME, pack_price_inc_gst REAL, price_basis TEXT, gp_unit_pct REAL, gp_unit_abs REAL, gp_pack_abs REAL, gp_pack_pct REAL, gp_carton_abs REAL, gp_carton_pct REAL,
	CONSTRAINT pk_price_observations PRIMARY KEY (id),
	CONSTRAINT fk_price_observations__sku_id__skus FOREIGN KEY(sku_id) REFERENCES skus (id) ON DELETE CASCADE,
	CONSTRAINT fk_price_observations__company_id__companies FOREIGN KEY(company_id) REFERENCES companies (id) ON DELETE RESTRICT,
	CONSTRAINT fk_price_observations__location_id__locations FOREIGN KEY(location_id) REFERENCES locations (id) ON DELETE SET NULL,
	CONSTRAINT ck_price_observations_ck_price_observations_channel CHECK (channel IN ('distributor_to_retailer','wholesale_to_venue','retail_instore','retail_online','direct_to_consumer')),
	CONSTRAINT ck_price_observations_ck_price_observations_price_context CHECK (price_context IN ('shelf','promo','member','online','quote','other')),
	CONSTRAINT ck_price_observations_ck_price_observations_availability CHECK (availability IN ('in_stock','low_stock','out_of_stock','unknown')),
	CONSTRAINT ck_price_observations_ck_price_observations_source_type CHECK (source_type IN ('web','in_store','brochure','email','verbal','receipt','photo'))
);

-- table products on products
CREATE TABLE products (
	id VARCHAR(36) NOT NULL,
	brand_id VARCHAR(36) NOT NULL,
	name VARCHAR(255) NOT NULL,
	category VARCHAR(32) NOT NULL,
	abv_percent NUMERIC(5, 2) NOT NULL,
	notes TEXT,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME,
	CONSTRAINT pk_products PRIMARY KEY (id),
	CONSTRAINT fk_products__brand_id__brands FOREIGN KEY(brand_id) REFERENCES brands (id) ON DELETE RESTRICT,
	CONSTRAINT uq_products_brand_name UNIQUE (brand_id, name),
	CONSTRAINT ck_products_ck_products_category CHECK (category IN ('gin_bottle','gin_rtd','vodka_bottle','vodka_rtd'))
);

-- table sku_cartons on sku_cartons
CREATE TABLE sku_cartons (
	id VARCHAR(36) NOT NULL,
	sku_id VARCHAR(36) NOT NULL,
	carton_spec_id VARCHAR(36) NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME,
	CONSTRAINT pk_sku_cartons PRIMARY KEY (id),
	CONSTRAINT fk_sku_cartons__sku_id__skus FOREIGN KEY(sku_id) REFERENCES skus (id) ON DELETE CASCADE,
	CONSTRAINT fk_sku_cartons__carton_spec_id__carton_specs FOREIGN KEY(carton_spec_id) REFERENCES carton_specs (id) ON DELETE CASCADE,
	CONSTRAINT uq_sku_cartons_parent UNIQUE (sku_id, carton_spec_id)
);

-- table sku_packs on sku_packs
CREATE TABLE sku_packs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          sku_id INTEGER,
          pack_spec_id INTEGER,
          created_at TEXT,
          updated_at TEXT,
          deleted_at TEXT
        );

-- table skus on skus
CREATE TABLE skus (
	id VARCHAR(36) NOT NULL,
	product_id VARCHAR(36) NOT NULL,
	package_spec_id VARCHAR(36) NOT NULL,
	gtin VARCHAR(32),
	is_active BOOLEAN DEFAULT 1 NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	deleted_at DATETIME,
	CONSTRAINT pk_skus PRIMARY KEY (id),
	CONSTRAINT fk_skus__product_id__products FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE RESTRICT,
	CONSTRAINT fk_skus__package_spec_id__package_specs FOREIGN KEY(package_spec_id) REFERENCES package_specs (id) ON DELETE RESTRICT,
	CONSTRAINT uq_skus_product_package UNIQUE (product_id, package_spec_id),
	CONSTRAINT uq_skus_gtin UNIQUE (gtin)
);

-- table sqlite_sequence on sqlite_sequence
CREATE TABLE sqlite_sequence(name,seq);
