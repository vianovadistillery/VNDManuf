"""create competitor pricing core

Revision ID: 20251107_142500
Revises:
Create Date: 2025-11-07 14:25:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251107_142500"
down_revision = None
branch_labels = ("competitor_intel",)
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    op.create_table(
        "brands",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("owner_company", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("name", name="uq_brands_name"),
    )
    op.create_index("ix_brands_name", "brands", ["name"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("brand_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("abv_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
            name="fk_products__brand_id__brands",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("brand_id", "name", name="uq_products_brand_name"),
        sa.CheckConstraint(
            "category IN ('gin_bottle','rtd_can')", name="ck_products_category"
        ),
    )

    op.create_table(
        "package_specs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("container_ml", sa.Integer, nullable=False),
        sa.Column("can_form_factor", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "type", "container_ml", "can_form_factor", name="uq_package_specs_unique"
        ),
        sa.CheckConstraint("type IN ('bottle','can')", name="ck_package_specs_type"),
        sa.CheckConstraint(
            "(type = 'can' AND can_form_factor IS NOT NULL) OR (type = 'bottle' AND can_form_factor IS NULL)",
            name="ck_package_specs_can_form_factor",
        ),
        sa.CheckConstraint(
            "(can_form_factor IS NULL) OR can_form_factor IN ('slim','sleek','classic')",
            name="ck_package_specs_can_form_factor_values",
        ),
    )

    op.create_table(
        "carton_specs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("units_per_carton", sa.Integer, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("units_per_carton", name="uq_carton_specs_units"),
    )

    op.create_table(
        "skus",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("package_spec_id", sa.String(length=36), nullable=False),
        sa.Column("gtin", sa.String(length=32), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_skus__product_id__products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["package_spec_id"],
            ["package_specs.id"],
            name="fk_skus__package_spec_id__package_specs",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "product_id", "package_spec_id", name="uq_skus_product_package"
        ),
        sa.UniqueConstraint("gtin", name="uq_skus_gtin"),
    )

    op.create_table(
        "sku_cartons",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("sku_id", sa.String(length=36), nullable=False),
        sa.Column("carton_spec_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["sku_id"],
            ["skus.id"],
            name="fk_sku_cartons__sku_id__skus",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["carton_spec_id"],
            ["carton_specs.id"],
            name="fk_sku_cartons__carton_spec_id__carton_specs",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("sku_id", "carton_spec_id", name="uq_sku_cartons_parent"),
    )

    op.create_table(
        "companies",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("parent_company_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_company_id"],
            ["companies.id"],
            name="fk_companies__parent_company_id__companies",
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("name", name="uq_companies_name"),
        sa.CheckConstraint(
            "type IN ('distributor','retailer','venue','other')",
            name="ck_companies_type",
        ),
    )

    op.create_table(
        "locations",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("store_name", sa.String(length=255), nullable=True),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("suburb", sa.String(length=255), nullable=False),
        sa.Column("postcode", sa.String(length=16), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_locations__company_id__companies",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "company_id",
            "store_name",
            "state",
            "suburb",
            "postcode",
            name="uq_locations_company_store",
        ),
    )

    op.create_table(
        "price_observations",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("sku_id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("location_id", sa.String(length=36), nullable=True),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column(
            "price_context",
            sa.String(length=32),
            nullable=False,
            server_default="shelf",
        ),
        sa.Column("promo_name", sa.String(length=255), nullable=True),
        sa.Column(
            "availability",
            sa.String(length=32),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("price_ex_gst_raw", sa.Numeric(12, 2), nullable=True),
        sa.Column("price_inc_gst_raw", sa.Numeric(12, 2), nullable=True),
        sa.Column("gst_rate", sa.Numeric(6, 4), nullable=False, server_default="0.10"),
        sa.Column(
            "currency", sa.String(length=8), nullable=False, server_default="AUD"
        ),
        sa.Column(
            "is_carton_price", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column("carton_units", sa.Integer, nullable=True),
        sa.Column("price_ex_gst_norm", sa.Numeric(12, 2), nullable=False),
        sa.Column("price_inc_gst_norm", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit_price_inc_gst", sa.Numeric(12, 4), nullable=False),
        sa.Column("carton_price_inc_gst", sa.Numeric(12, 2), nullable=True),
        sa.Column("price_per_litre", sa.Numeric(12, 4), nullable=False),
        sa.Column("price_per_unit_pure_alcohol", sa.Numeric(14, 4), nullable=False),
        sa.Column("standard_drinks", sa.Numeric(12, 4), nullable=False),
        sa.Column("observation_dt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("source_note", sa.Text(), nullable=True),
        sa.Column("hash_key", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["sku_id"],
            ["skus.id"],
            name="fk_price_observations__sku_id__skus",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_price_observations__company_id__companies",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            name="fk_price_observations__location_id__locations",
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "channel IN ('distributor_to_retailer','wholesale_to_venue','retail_instore','retail_online','direct_to_consumer')",
            name="ck_price_observations_channel",
        ),
        sa.CheckConstraint(
            "price_context IN ('shelf','promo','member','online','quote','other')",
            name="ck_price_observations_price_context",
        ),
        sa.CheckConstraint(
            "availability IN ('in_stock','low_stock','out_of_stock','unknown')",
            name="ck_price_observations_availability",
        ),
        sa.CheckConstraint(
            "source_type IN ('web','in_store','brochure','email','verbal','receipt','photo')",
            name="ck_price_observations_source_type",
        ),
    )

    op.create_index(
        "ix_price_observations_sku_id_observation_dt",
        "price_observations",
        ["sku_id", "observation_dt"],
    )
    op.create_index(
        "ix_price_observations_company_id_observation_dt",
        "price_observations",
        ["company_id", "observation_dt"],
    )
    op.create_index(
        "ix_price_observations_location_id_observation_dt",
        "price_observations",
        ["location_id", "observation_dt"],
    )
    op.create_index(
        "ix_price_observations_channel_observation_dt",
        "price_observations",
        ["channel", "observation_dt"],
    )
    op.create_index(
        "ix_price_observations_observation_dt",
        "price_observations",
        ["observation_dt"],
    )
    op.create_index(
        "ix_price_observations_hash_key",
        "price_observations",
        ["hash_key"],
    )

    op.create_table(
        "attachments",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("price_observation_id", sa.String(length=36), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("caption", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["price_observation_id"],
            ["price_observations.id"],
            name="fk_attachments__price_observation_id__price_observations",
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    op.drop_table("attachments")

    op.drop_index("ix_price_observations_hash_key", table_name="price_observations")
    op.drop_index(
        "ix_price_observations_observation_dt", table_name="price_observations"
    )
    op.drop_index(
        "ix_price_observations_channel_observation_dt", table_name="price_observations"
    )
    op.drop_index(
        "ix_price_observations_location_id_observation_dt",
        table_name="price_observations",
    )
    op.drop_index(
        "ix_price_observations_company_id_observation_dt",
        table_name="price_observations",
    )
    op.drop_index(
        "ix_price_observations_sku_id_observation_dt", table_name="price_observations"
    )
    op.drop_table("price_observations")

    op.drop_table("locations")
    op.drop_table("companies")
    op.drop_table("sku_cartons")
    op.drop_table("skus")
    op.drop_table("carton_specs")
    op.drop_table("package_specs")
    op.drop_table("products")
    op.drop_index("ix_brands_name", table_name="brands")
    op.drop_table("brands")
