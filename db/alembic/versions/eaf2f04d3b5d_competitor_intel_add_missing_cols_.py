"""competitor_intel: add missing cols + manufacturing_costs

Revision ID: eaf2f04d3b5d
Revises: 57d6b07b57d0
Create Date: 2025-11-10 22:29:08.729141

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eaf2f04d3b5d"
down_revision: Union[str, None] = "57d6b07b57d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_table(insp: sa.Inspector, table_name: str) -> bool:
    return table_name in insp.get_table_names()


def has_column(insp: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in insp.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    # --- price_observations: add columns if table exists ---
    table_name = "price_observations"
    if has_table(insp, table_name):
        existing_cols = {col["name"] for col in insp.get_columns(table_name)}
        with op.batch_alter_table(table_name, recreate="always") as batch_op:
            if "pack_price_inc_gst" not in existing_cols:
                batch_op.add_column(
                    sa.Column("pack_price_inc_gst", sa.Numeric(12, 4), nullable=True)
                )
            if "price_basis" not in existing_cols:
                batch_op.add_column(
                    sa.Column("price_basis", sa.String(length=50), nullable=True)
                )
            if "gp_unit_pct" not in existing_cols:
                batch_op.add_column(
                    sa.Column("gp_unit_pct", sa.Numeric(7, 4), nullable=True)
                )

    # --- carton_specs: add pack_spec_id if table exists ---
    table_name = "carton_specs"
    if has_table(insp, table_name):
        with op.batch_alter_table(table_name, recreate="always") as batch_op:
            if not has_column(insp, table_name, "pack_spec_id"):
                batch_op.add_column(
                    sa.Column("pack_spec_id", sa.Integer(), nullable=True)
                )

    # --- locations: add address if table exists ---
    table_name = "locations"
    if has_table(insp, table_name):
        with op.batch_alter_table(table_name, recreate="always") as batch_op:
            if not has_column(insp, table_name, "address"):
                batch_op.add_column(
                    sa.Column("address", sa.String(length=255), nullable=True)
                )

    # --- manufacturing_costs: create if missing ---
    if not has_table(insp, "manufacturing_costs"):
        op.create_table(
            "manufacturing_costs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("sku_id", sa.Integer(), nullable=False),
            sa.Column("cost_type", sa.String(length=50), nullable=True),
            sa.Column("cost_currency", sa.String(length=10), nullable=True),
            sa.Column("cost_per_unit", sa.Numeric(12, 4), nullable=True),
            sa.Column("cost_per_pack", sa.Numeric(12, 4), nullable=True),
            sa.Column("cost_per_carton", sa.Numeric(12, 4), nullable=True),
            sa.Column("effective_date", sa.Date(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], name="fk_mfg_costs_sku"),
        )
    # Create indexes if table exists and index absent
    if has_table(insp, "manufacturing_costs"):
        if not any(
            ix["name"] == "ix_mfg_costs_sku_id"
            for ix in insp.get_indexes("manufacturing_costs")
        ):
            op.create_index(
                "ix_mfg_costs_sku_id",
                "manufacturing_costs",
                ["sku_id"],
            )
        if not any(
            ix["name"] == "ix_mfg_costs_effective_date"
            for ix in insp.get_indexes("manufacturing_costs")
        ):
            op.create_index(
                "ix_mfg_costs_effective_date",
                "manufacturing_costs",
                ["effective_date"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if has_table(insp, "manufacturing_costs"):
        if any(
            ix["name"] == "ix_mfg_costs_effective_date"
            for ix in insp.get_indexes("manufacturing_costs")
        ):
            op.drop_index(
                "ix_mfg_costs_effective_date", table_name="manufacturing_costs"
            )
        if any(
            ix["name"] == "ix_mfg_costs_sku_id"
            for ix in insp.get_indexes("manufacturing_costs")
        ):
            op.drop_index("ix_mfg_costs_sku_id", table_name="manufacturing_costs")
        op.drop_table("manufacturing_costs")

    table_name = "locations"
    if has_table(insp, table_name) and has_column(insp, table_name, "address"):
        with op.batch_alter_table(table_name, recreate="always") as batch_op:
            batch_op.drop_column("address")

    table_name = "carton_specs"
    if has_table(insp, table_name) and has_column(insp, table_name, "pack_spec_id"):
        with op.batch_alter_table(table_name, recreate="always") as batch_op:
            batch_op.drop_column("pack_spec_id")

    table_name = "price_observations"
    if has_table(insp, table_name):
        columns_to_drop = [
            ("gp_unit_pct", sa.Numeric(7, 4)),
            ("price_basis", sa.String(length=50)),
            ("pack_price_inc_gst", sa.Numeric(12, 4)),
        ]
        with op.batch_alter_table(table_name, recreate="always") as batch_op:
            for column_name, _ in columns_to_drop:
                if has_column(insp, table_name, column_name):
                    batch_op.drop_column(column_name)
