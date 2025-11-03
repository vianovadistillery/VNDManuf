"""add_qb_models_for_raw_materials_formulas_batches

Revision ID: b7a47f197d45
Revises: 74980f3155d7
Create Date: 2025-10-26 18:01:23.986240

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7a47f197d45"
down_revision: Union[str, None] = "74980f3155d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create raw_material_groups table
    op.create_table(
        "raw_material_groups",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_rm_group_code", "raw_material_groups", ["code"], unique=True)

    # Create raw_materials table
    op.create_table(
        "raw_materials",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.Integer(), nullable=False),
        sa.Column("desc1", sa.String(length=25)),
        sa.Column("desc2", sa.String(length=25)),
        sa.Column("search_key", sa.String(length=5)),
        sa.Column("search_ext", sa.String(length=8)),
        sa.Column("sg", sa.Numeric(precision=10, scale=6)),
        sa.Column("vol_solid", sa.Numeric(precision=10, scale=6)),
        sa.Column("solid_sg", sa.Numeric(precision=10, scale=6)),
        sa.Column("wt_solid", sa.Numeric(precision=10, scale=6)),
        sa.Column("purqty", sa.Integer()),
        sa.Column("purchase_cost", sa.Numeric(precision=10, scale=2)),
        sa.Column("purchase_unit", sa.String(length=2)),
        sa.Column("deal_cost", sa.Numeric(precision=10, scale=2)),
        sa.Column("sup_unit", sa.String(length=2)),
        sa.Column("sup_qty", sa.Numeric(precision=10, scale=3)),
        sa.Column("usage_cost", sa.Numeric(precision=10, scale=2)),
        sa.Column("usage_unit", sa.String(length=2)),
        sa.Column("group_id", sa.String(length=36)),
        sa.Column("active_flag", sa.String(length=1)),
        sa.Column("soh", sa.Numeric(precision=12, scale=3)),
        sa.Column("opening_soh", sa.Numeric(precision=12, scale=3)),
        sa.Column("soh_value", sa.Numeric(precision=12, scale=2)),
        sa.Column("so_on_order", sa.Integer()),
        sa.Column("so_in_process", sa.Numeric(precision=12, scale=3)),
        sa.Column("restock_level", sa.Numeric(precision=12, scale=3)),
        sa.Column("used_ytd", sa.Numeric(precision=12, scale=3)),
        sa.Column("hazard", sa.String(length=1)),
        sa.Column("condition", sa.String(length=1)),
        sa.Column("msds_flag", sa.String(length=1)),
        sa.Column("altno1", sa.Integer()),
        sa.Column("altno2", sa.Integer()),
        sa.Column("altno3", sa.Integer()),
        sa.Column("altno4", sa.Integer()),
        sa.Column("altno5", sa.Integer()),
        sa.Column("last_movement_date", sa.String(length=8)),
        sa.Column("last_purchase_date", sa.String(length=8)),
        sa.Column("notes", sa.String(length=25)),
        sa.Column("ean13", sa.Numeric(precision=18, scale=4)),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["raw_material_groups.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_raw_material_code", "raw_materials", ["code"], unique=True)
    op.create_index("ix_raw_material_desc1", "raw_materials", ["desc1"])
    op.create_index("ix_raw_material_active", "raw_materials", ["active_flag"])

    # Create formula_classes table
    op.create_table(
        "formula_classes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("ytd_amounts", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_formula_class_name", "formula_classes", ["name"])

    # Create markups table
    op.create_table(
        "markups",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("enabled_flag", sa.String(length=1)),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_markup_code", "markups", ["code"], unique=True)

    # Create condition_types table
    op.create_table(
        "condition_types",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=1), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=False),
        sa.Column("extended_desc", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_condition_type_code", "condition_types", ["code"], unique=True)

    # Create datasets table
    op.create_table(
        "datasets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=3), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_dataset_code", "datasets", ["code"], unique=True)

    # Create manufacturing_config table
    op.create_table(
        "manufacturing_config",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("qtyf", sa.String(length=10)),
        sa.Column("bchno_width", sa.String(length=10)),
        sa.Column("bch_offset", sa.String(length=10)),
        sa.Column("company_name", sa.String(length=50)),
        sa.Column("site_code", sa.String(length=10)),
        sa.Column("max1", sa.Numeric(precision=10, scale=2)),
        sa.Column("max2", sa.Numeric(precision=10, scale=2)),
        sa.Column("max3", sa.Numeric(precision=10, scale=2)),
        sa.Column("max4", sa.Numeric(precision=10, scale=2)),
        sa.Column("max5", sa.Numeric(precision=10, scale=2)),
        sa.Column("max6", sa.Numeric(precision=10, scale=2)),
        sa.Column("max7", sa.Numeric(precision=10, scale=2)),
        sa.Column("max8", sa.Numeric(precision=10, scale=2)),
        sa.Column("max9", sa.Numeric(precision=10, scale=2)),
        sa.Column("flags1", sa.String(length=10)),
        sa.Column("flags2", sa.String(length=10)),
        sa.Column("flags3", sa.String(length=10)),
        sa.Column("flags4", sa.String(length=10)),
        sa.Column("flags5", sa.String(length=10)),
        sa.Column("flags6", sa.String(length=10)),
        sa.Column("flags7", sa.String(length=10)),
        sa.Column("flags8", sa.String(length=10)),
        sa.Column("rep1", sa.String(length=10)),
        sa.Column("rep2", sa.String(length=10)),
        sa.Column("rep3", sa.String(length=10)),
        sa.Column("rep4", sa.String(length=10)),
        sa.Column("rep5", sa.String(length=10)),
        sa.Column("rep6", sa.String(length=10)),
        sa.Column("print_hi1", sa.String(length=10)),
        sa.Column("db_month_raw", sa.String(length=10)),
        sa.Column("cr_month_raw", sa.String(length=10)),
        sa.Column("cans_idx", sa.Integer()),
        sa.Column("label_idx", sa.Integer()),
        sa.Column("labour_idx", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("manufacturing_config")
    op.drop_table("datasets")
    op.drop_index("ix_condition_type_code", "condition_types")
    op.drop_table("condition_types")
    op.drop_index("ix_markup_code", "markups")
    op.drop_table("markups")
    op.drop_index("ix_formula_class_name", "formula_classes")
    op.drop_table("formula_classes")
    op.drop_index("ix_raw_material_active", "raw_materials")
    op.drop_index("ix_raw_material_desc1", "raw_materials")
    op.drop_index("ix_raw_material_code", "raw_materials")
    op.drop_table("raw_materials")
    op.drop_index("ix_rm_group_code", "raw_material_groups")
    op.drop_table("raw_material_groups")
