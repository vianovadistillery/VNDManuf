"""add pack specs and manufacturing costs

Revision ID: 20251108_104900
Revises: 20251107_142500
Create Date: 2025-11-08 10:49:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251108_104900"
down_revision = "20251107_142500"
branch_labels = None
depends_on = None


def _has_table(insp, name: str) -> bool:
    return name in insp.get_table_names()


def _has_column(insp, table: str, column: str) -> bool:
    return any(col["name"] == column for col in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if not _has_table(insp, "pack_specs"):
        op.create_table(
            "pack_specs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("package_spec_id", sa.String(length=36), nullable=False),
            sa.Column("units_per_pack", sa.Integer(), nullable=False),
            sa.Column("gtin", sa.String(length=32), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["package_spec_id"],
                ["package_specs.id"],
                name="fk_pack_specs__package_spec_id__package_specs",
                ondelete="RESTRICT",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_pack_specs"),
            sa.UniqueConstraint(
                "package_spec_id", "units_per_pack", name="uq_pack_specs_package_units"
            ),
            sa.UniqueConstraint("gtin", name="uq_pack_specs_gtin"),
        )

    if not _has_table(insp, "sku_packs"):
        op.create_table(
            "sku_packs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("sku_id", sa.String(length=36), nullable=False),
            sa.Column("pack_spec_id", sa.String(length=36), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["pack_spec_id"],
                ["pack_specs.id"],
                name="fk_sku_packs__pack_spec_id__pack_specs",
                ondelete="RESTRICT",
            ),
            sa.ForeignKeyConstraint(
                ["sku_id"],
                ["skus.id"],
                name="fk_sku_packs__sku_id__skus",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_sku_packs"),
            sa.UniqueConstraint("sku_id", name="uq_sku_packs_sku"),
        )

    if _has_table(insp, "carton_specs"):
        cols = {col["name"] for col in insp.get_columns("carton_specs")}
        uniques = {uc["name"] for uc in insp.get_unique_constraints("carton_specs")}
        need_alter = any(
            name not in cols
            for name in ("gtin", "package_spec_id", "pack_spec_id", "pack_count")
        )
        if need_alter:
            fk_names = {fk["name"] for fk in insp.get_foreign_keys("carton_specs")}
            with op.batch_alter_table("carton_specs", recreate="always") as batch:
                if "uq_carton_specs_units" in uniques:
                    batch.drop_constraint("uq_carton_specs_units", type_="unique")
                if "gtin" not in cols:
                    batch.add_column(sa.Column("gtin", sa.String(length=32)))
                if "package_spec_id" not in cols:
                    batch.add_column(
                        sa.Column(
                            "package_spec_id", sa.String(length=36), nullable=True
                        )
                    )
                if "pack_spec_id" not in cols:
                    batch.add_column(
                        sa.Column("pack_spec_id", sa.String(length=36), nullable=True)
                    )
                if "pack_count" not in cols:
                    batch.add_column(
                        sa.Column("pack_count", sa.Integer(), nullable=True)
                    )
                if "fk_carton_specs__package_spec_id__package_specs" not in fk_names:
                    batch.create_foreign_key(
                        "fk_carton_specs__package_spec_id__package_specs",
                        "package_specs",
                        ["package_spec_id"],
                        ["id"],
                        ondelete="RESTRICT",
                    )
                if "fk_carton_specs__pack_spec_id__pack_specs" not in fk_names:
                    batch.create_foreign_key(
                        "fk_carton_specs__pack_spec_id__pack_specs",
                        "pack_specs",
                        ["pack_spec_id"],
                        ["id"],
                        ondelete="RESTRICT",
                    )
                batch.create_check_constraint(
                    "ck_carton_specs_pack_or_unit",
                    "(pack_spec_id IS NOT NULL AND package_spec_id IS NULL) OR (pack_spec_id IS NULL AND package_spec_id IS NOT NULL)",
                )
                batch.create_unique_constraint("uq_carton_specs_gtin", ["gtin"])

    if not _has_table(insp, "manufacturing_costs"):
        op.create_table(
            "manufacturing_costs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("sku_id", sa.String(length=36), nullable=False),
            sa.Column("cost_type", sa.String(length=16), nullable=False),
            sa.Column(
                "cost_currency",
                sa.String(length=8),
                nullable=False,
                server_default="AUD",
            ),
            sa.Column("cost_per_unit", sa.Numeric(12, 4), nullable=True),
            sa.Column("cost_per_pack", sa.Numeric(12, 4), nullable=True),
            sa.Column("cost_per_carton", sa.Numeric(12, 4), nullable=True),
            sa.Column("effective_date", sa.Date(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["sku_id"],
                ["skus.id"],
                name="fk_manufacturing_costs__sku_id__skus",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_manufacturing_costs"),
            sa.UniqueConstraint(
                "sku_id",
                "cost_type",
                "effective_date",
                name="uq_manufacturing_costs_sku_type_effective",
            ),
            sa.CheckConstraint(
                "cost_type IN ('estimated','known')", name="ck_manufacturing_costs_type"
            ),
        )

    if _has_table(insp, "price_observations"):
        cols = {col["name"] for col in insp.get_columns("price_observations")}
        gp_columns = [
            {
                "name": "gp_unit_abs",
                "type": sa.Numeric(12, 4),
                "nullable": True,
                "server_default": None,
            },
            {
                "name": "gp_unit_pct",
                "type": sa.Numeric(10, 4),
                "nullable": True,
                "server_default": None,
            },
            {
                "name": "gp_pack_abs",
                "type": sa.Numeric(12, 4),
                "nullable": True,
                "server_default": None,
            },
            {
                "name": "gp_pack_pct",
                "type": sa.Numeric(10, 4),
                "nullable": True,
                "server_default": None,
            },
            {
                "name": "gp_carton_abs",
                "type": sa.Numeric(12, 4),
                "nullable": True,
                "server_default": None,
            },
            {
                "name": "gp_carton_pct",
                "type": sa.Numeric(10, 4),
                "nullable": True,
                "server_default": None,
            },
        ]
        additional_columns = [
            {
                "name": "pack_price_inc_gst",
                "type": sa.Numeric(12, 2),
                "nullable": True,
                "server_default": None,
            },
            {
                "name": "price_basis",
                "type": sa.String(length=16),
                "nullable": False,
                "server_default": sa.text("'unit'"),
            },
        ]
        pending = [
            col for col in gp_columns + additional_columns if col["name"] not in cols
        ]
        if pending:
            with op.batch_alter_table("price_observations", recreate="always") as batch:
                for spec in gp_columns:
                    if spec["name"] not in cols:
                        batch.add_column(
                            sa.Column(
                                spec["name"],
                                spec["type"],
                                nullable=spec["nullable"],
                                server_default=spec["server_default"],
                            )
                        )
                for spec in additional_columns:
                    if spec["name"] not in cols:
                        batch.add_column(
                            sa.Column(
                                spec["name"],
                                spec["type"],
                                nullable=spec["nullable"],
                                server_default=spec["server_default"],
                            )
                        )
                        if spec["server_default"] is not None:
                            batch.alter_column(spec["name"], server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if _has_table(insp, "price_observations"):
        cols = {col["name"] for col in insp.get_columns("price_observations")}
        gp_columns = [
            "gp_unit_abs",
            "gp_unit_pct",
            "gp_pack_abs",
            "gp_pack_pct",
            "gp_carton_abs",
            "gp_carton_pct",
        ]
        additional_columns = ["pack_price_inc_gst", "price_basis"]
        if any(name in cols for name in gp_columns + additional_columns):
            with op.batch_alter_table("price_observations", recreate="always") as batch:
                for name in gp_columns:
                    if name in cols:
                        batch.drop_column(name)
                for name in additional_columns:
                    if name in cols:
                        batch.drop_column(name)

    if _has_table(insp, "manufacturing_costs"):
        op.drop_table("manufacturing_costs")

    if _has_table(insp, "sku_packs"):
        op.drop_table("sku_packs")

    if _has_table(insp, "pack_specs"):
        op.drop_table("pack_specs")

    if _has_table(insp, "carton_specs"):
        cols = {col["name"] for col in insp.get_columns("carton_specs")}
        columns_to_remove = ["gtin", "package_spec_id", "pack_spec_id", "pack_count"]
        fk_names = {fk["name"] for fk in insp.get_foreign_keys("carton_specs")}
        unique_names = {
            uc["name"] for uc in insp.get_unique_constraints("carton_specs")
        }
        check_names = {ck["name"] for ck in insp.get_check_constraints("carton_specs")}
        constraints = [
            ("fk_carton_specs__package_spec_id__package_specs", "foreignkey", fk_names),
            ("fk_carton_specs__pack_spec_id__pack_specs", "foreignkey", fk_names),
            ("ck_carton_specs_pack_or_unit", "check", check_names),
            ("uq_carton_specs_gtin", "unique", unique_names),
        ]
        if any(name in cols for name in columns_to_remove):
            with op.batch_alter_table("carton_specs", recreate="always") as batch:
                for constraint, constraint_type, existing in constraints:
                    if constraint in existing:
                        batch.drop_constraint(constraint, type_=constraint_type)
                for name in columns_to_remove:
                    if name in cols:
                        batch.drop_column(name)
                if "uq_carton_specs_units" not in unique_names:
                    batch.create_unique_constraint(
                        "uq_carton_specs_units", ["units_per_carton"]
                    )
