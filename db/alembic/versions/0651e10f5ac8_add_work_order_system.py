"""add_work_order_system

Revision ID: 0651e10f5ac8
Revises: 212104c7dfa8
Create Date: 2025-11-04 21:48:31.123163

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0651e10f5ac8"
down_revision: Union[str, None] = "212104c7dfa8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add work order system tables and extend existing tables."""

    # Extend work_orders table
    op.add_column(
        "work_orders", sa.Column("assembly_id", sa.String(length=36), nullable=True)
    )
    op.add_column(
        "work_orders",
        sa.Column("planned_qty", sa.Numeric(precision=12, scale=4), nullable=True),
    )
    op.add_column("work_orders", sa.Column("uom", sa.String(length=10), nullable=True))
    op.add_column(
        "work_orders", sa.Column("work_center", sa.String(length=50), nullable=True)
    )
    op.add_column("work_orders", sa.Column("start_time", sa.DateTime(), nullable=True))
    op.add_column("work_orders", sa.Column("end_time", sa.DateTime(), nullable=True))
    op.add_column(
        "work_orders", sa.Column("batch_code", sa.String(length=50), nullable=True)
    )

    # Add FK for assembly_id and make formula_id nullable
    op.create_foreign_key(
        "fk_wo_assembly", "work_orders", "assemblies", ["assembly_id"], ["id"]
    )
    op.alter_column("work_orders", "formula_id", nullable=True)

    # Update work_orders status default and add indexes
    op.create_index("ix_work_order_status", "work_orders", ["status"])
    op.create_index(
        "ix_work_order_product_status", "work_orders", ["product_id", "status"]
    )
    op.create_index(
        "ix_work_order_batch_code", "work_orders", ["batch_code"], unique=True
    )

    # Extend work_order_lines table
    op.add_column(
        "work_order_lines",
        sa.Column("component_product_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "work_order_lines",
        sa.Column("planned_qty", sa.Numeric(precision=12, scale=4), nullable=True),
    )
    op.add_column(
        "work_order_lines",
        sa.Column("actual_qty", sa.Numeric(precision=12, scale=4), nullable=True),
    )
    op.add_column(
        "work_order_lines", sa.Column("uom", sa.String(length=10), nullable=True)
    )
    op.add_column(
        "work_order_lines",
        sa.Column("source_batch_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "work_order_lines",
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=4), nullable=True),
    )
    op.add_column(
        "work_order_lines", sa.Column("line_type", sa.String(length=20), nullable=True)
    )
    op.add_column("work_order_lines", sa.Column("note", sa.Text(), nullable=True))

    # Add FK for source_batch_id
    op.create_foreign_key(
        "fk_wo_line_source_batch",
        "work_order_lines",
        "batches",
        ["source_batch_id"],
        ["id"],
    )

    # Add FK for component_product_id
    op.create_foreign_key(
        "fk_wo_line_component_product",
        "work_order_lines",
        "products",
        ["component_product_id"],
        ["id"],
    )

    # Add index
    op.create_index("ix_work_order_line_wo_id", "work_order_lines", ["work_order_id"])

    # Migrate data: copy ingredient_product_id to component_product_id if not set
    op.execute("""
        UPDATE work_order_lines
        SET component_product_id = ingredient_product_id
        WHERE component_product_id IS NULL AND ingredient_product_id IS NOT NULL
    """)

    # Create work_order_outputs table
    op.create_table(
        "work_order_outputs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("qty_produced", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("uom", sa.String(length=10), nullable=False),
        sa.Column("batch_id", sa.String(length=36), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("scrap_qty", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.String(length=100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("versioned_at", sa.DateTime(), nullable=True),
        sa.Column("versioned_by", sa.String(length=100), nullable=True),
        sa.Column("previous_version_id", sa.String(length=36), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archived_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["work_orders.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["batch_id"],
            ["batches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_wo_output_wo_id", "work_order_outputs", ["work_order_id"])

    # Extend batches table
    op.add_column(
        "batches", sa.Column("product_id", sa.String(length=36), nullable=True)
    )
    op.add_column("batches", sa.Column("mfg_date", sa.Date(), nullable=True))
    op.add_column("batches", sa.Column("exp_date", sa.Date(), nullable=True))
    op.add_column("batches", sa.Column("meta", sa.Text(), nullable=True))

    # Make work_order_id nullable
    op.alter_column("batches", "work_order_id", nullable=True)

    # Drop old unique constraint and create new one
    op.drop_constraint("uq_batch_code", "batches", type_="unique")
    op.drop_index("ix_batch_wo_code", table_name="batches")
    op.create_unique_constraint("uq_batch_code_unique", "batches", ["batch_code"])

    # Add indexes
    op.create_index("ix_batch_product_status", "batches", ["product_id", "status"])

    # Migrate data: set product_id from work_order.product_id for existing batches
    op.execute("""
        UPDATE batches
        SET product_id = (
            SELECT product_id FROM work_orders WHERE work_orders.id = batches.work_order_id
        )
        WHERE product_id IS NULL AND work_order_id IS NOT NULL
    """)

    # Extend inventory_movements table
    op.add_column(
        "inventory_movements",
        sa.Column("batch_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "inventory_movements", sa.Column("timestamp", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "inventory_movements", sa.Column("uom", sa.String(length=10), nullable=True)
    )
    op.add_column(
        "inventory_movements",
        sa.Column("move_type", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "inventory_movements",
        sa.Column("ref_table", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "inventory_movements", sa.Column("ref_id", sa.String(length=36), nullable=True)
    )
    op.add_column(
        "inventory_movements",
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=4), nullable=True),
    )

    # Make direction nullable (legacy)
    op.alter_column("inventory_movements", "direction", nullable=True)

    # Change qty precision
    op.alter_column(
        "inventory_movements",
        "qty",
        type_=sa.Numeric(precision=12, scale=4),
        existing_type=sa.Numeric(precision=12, scale=3),
    )

    # Add FK for batch_id
    op.create_foreign_key(
        "fk_movements_batch", "inventory_movements", "batches", ["batch_id"], ["id"]
    )

    # Migrate data: copy source_batch_id to batch_id
    op.execute("""
        UPDATE inventory_movements
        SET batch_id = source_batch_id
        WHERE batch_id IS NULL AND source_batch_id IS NOT NULL
    """)

    # Copy ts to timestamp
    op.execute("""
        UPDATE inventory_movements
        SET timestamp = ts
        WHERE timestamp IS NULL
    """)

    # Copy unit to uom
    op.execute("""
        UPDATE inventory_movements
        SET uom = unit
        WHERE uom IS NULL
    """)

    # Add indexes
    op.create_index("ix_movements_move_type", "inventory_movements", ["move_type"])
    op.create_index("ix_movements_ref", "inventory_movements", ["ref_table", "ref_id"])
    op.create_index(
        "ix_movements_product_ts", "inventory_movements", ["product_id", "timestamp"]
    )

    # Create wo_qc_tests table
    op.create_table(
        "wo_qc_tests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=False),
        sa.Column("test_type", sa.String(length=50), nullable=False),
        sa.Column("result_value", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("tested_at", sa.DateTime(), nullable=True),
        sa.Column("tester", sa.String(length=100), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.String(length=100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("versioned_at", sa.DateTime(), nullable=True),
        sa.Column("versioned_by", sa.String(length=100), nullable=True),
        sa.Column("previous_version_id", sa.String(length=36), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archived_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["work_orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_wo_qc_test_wo_id", "wo_qc_tests", ["work_order_id"])

    # Create wo_timers table
    op.create_table(
        "wo_timers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=False),
        sa.Column("timer_type", sa.String(length=50), nullable=False),
        sa.Column("seconds", sa.Integer(), nullable=False),
        sa.Column("rate_per_hour", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("cost", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.String(length=100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("versioned_at", sa.DateTime(), nullable=True),
        sa.Column("versioned_by", sa.String(length=100), nullable=True),
        sa.Column("previous_version_id", sa.String(length=36), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archived_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["work_orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create product_cost_rates table
    op.create_table(
        "product_cost_rates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("rate_code", sa.String(length=50), nullable=False),
        sa.Column("rate_type", sa.String(length=20), nullable=False),
        sa.Column("rate_value", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("uom", sa.String(length=20), nullable=True),
        sa.Column("effective_from", sa.DateTime(), nullable=False),
        sa.Column("effective_to", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.String(length=100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("versioned_at", sa.DateTime(), nullable=True),
        sa.Column("versioned_by", sa.String(length=100), nullable=True),
        sa.Column("previous_version_id", sa.String(length=36), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archived_by", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rate_code"),
    )
    op.create_index("ix_cost_rate_code", "product_cost_rates", ["rate_code"])

    # Create batch_seq table
    op.create_table(
        "batch_seq",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("date", sa.String(length=10), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "date", name="uq_batch_seq_product_date"),
    )


def downgrade() -> None:
    """Remove work order system tables and extensions."""

    # Drop new tables
    op.drop_table("batch_seq")
    op.drop_table("product_cost_rates")
    op.drop_table("wo_timers")
    op.drop_table("wo_qc_tests")
    op.drop_table("work_order_outputs")

    # Remove indexes from inventory_movements
    op.drop_index("ix_movements_product_ts", table_name="inventory_movements")
    op.drop_index("ix_movements_ref", table_name="inventory_movements")
    op.drop_index("ix_movements_move_type", table_name="inventory_movements")

    # Remove FKs and columns from inventory_movements
    op.drop_constraint("fk_movements_batch", "inventory_movements", type_="foreignkey")
    op.drop_column("inventory_movements", "unit_cost")
    op.drop_column("inventory_movements", "ref_id")
    op.drop_column("inventory_movements", "ref_table")
    op.drop_column("inventory_movements", "move_type")
    op.drop_column("inventory_movements", "uom")
    op.drop_column("inventory_movements", "timestamp")
    op.drop_column("inventory_movements", "batch_id")

    # Restore direction not null
    op.alter_column("inventory_movements", "direction", nullable=False)

    # Restore batches table
    op.drop_index("ix_batch_product_status", table_name="batches")
    op.drop_constraint("uq_batch_code_unique", "batches", type_="unique")
    op.create_unique_constraint(
        "uq_batch_code", "batches", ["work_order_id", "batch_code"]
    )
    op.create_index("ix_batch_wo_code", "batches", ["work_order_id", "batch_code"])
    op.alter_column("batches", "work_order_id", nullable=False)
    op.drop_column("batches", "meta")
    op.drop_column("batches", "exp_date")
    op.drop_column("batches", "mfg_date")
    op.drop_column("batches", "product_id")

    # Remove columns from work_order_lines
    op.drop_index("ix_work_order_line_wo_id", table_name="work_order_lines")
    op.drop_constraint(
        "fk_wo_line_component_product", "work_order_lines", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_wo_line_source_batch", "work_order_lines", type_="foreignkey"
    )
    op.drop_column("work_order_lines", "note")
    op.drop_column("work_order_lines", "line_type")
    op.drop_column("work_order_lines", "unit_cost")
    op.drop_column("work_order_lines", "source_batch_id")
    op.drop_column("work_order_lines", "uom")
    op.drop_column("work_order_lines", "actual_qty")
    op.drop_column("work_order_lines", "planned_qty")
    op.drop_column("work_order_lines", "component_product_id")

    # Remove columns from work_orders
    op.drop_index("ix_work_order_batch_code", table_name="work_orders")
    op.drop_index("ix_work_order_product_status", table_name="work_orders")
    op.drop_index("ix_work_order_status", table_name="work_orders")
    op.drop_constraint("fk_wo_assembly", "work_orders", type_="foreignkey")
    op.drop_column("work_orders", "batch_code")
    op.drop_column("work_orders", "end_time")
    op.drop_column("work_orders", "start_time")
    op.drop_column("work_orders", "work_center")
    op.drop_column("work_orders", "uom")
    op.drop_column("work_orders", "planned_qty")
    op.drop_column("work_orders", "assembly_id")
    op.alter_column("work_orders", "formula_id", nullable=False)
