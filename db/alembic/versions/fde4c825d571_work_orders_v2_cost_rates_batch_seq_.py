"""work orders v2 + cost rates + batch_seq + type fixes

Revision ID: fde4c825d571
Revises: a23b822a17cb
Create Date: 2025-11-05 13:12:28.055893

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fde4c825d571"
down_revision: Union[str, None] = "a23b822a17cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_column(insp, table, col):
    """Helper to check if column exists."""
    return any(c["name"] == col for c in insp.get_columns(table))


def has_index(insp, table, name):
    """Helper to check if index exists."""
    return any(ix["name"] == name for ix in insp.get_indexes(table))


def upgrade() -> None:
    import sqlalchemy as sa
    from alembic import op

    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)

    # ============================================================================
    # (A) CREATE NEW TABLES (with inline FKs)
    # ============================================================================

    # 1. product_cost_rates
    if "product_cost_rates" not in insp.get_table_names():
        op.create_table(
            "product_cost_rates",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("rate_code", sa.String(length=50), nullable=False),
            sa.Column("rate_type", sa.String(length=20), nullable=False),
            sa.Column("rate_value", sa.Numeric(precision=12, scale=4), nullable=False),
            sa.Column("uom", sa.String(length=20), nullable=True),
            sa.Column("effective_from", sa.DateTime(), nullable=False),
            sa.Column("effective_to", sa.DateTime(), nullable=True),
            # AuditMixin fields
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(length=100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(length=100), nullable=True),
            sa.Column("previous_version_id", sa.String(length=36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(length=100), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_cost_rate_code", "product_cost_rates", ["rate_code"], unique=True
        )

    # 2. batch_seq (no AuditMixin)
    if "batch_seq" not in insp.get_table_names():
        op.create_table(
            "batch_seq",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("product_id", sa.String(length=36), nullable=False),
            sa.Column("date", sa.String(length=10), nullable=False),
            sa.Column("seq", sa.Integer(), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(
                ["product_id"],
                ["products.id"],
                name="fk_batch_seq__product_id__products",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("product_id", "date", name="uq_batch_seq_product_date"),
        )

    # 3. wo_qc_tests
    if "wo_qc_tests" not in insp.get_table_names():
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
            # AuditMixin fields
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(length=100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(length=100), nullable=True),
            sa.Column("previous_version_id", sa.String(length=36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(length=100), nullable=True),
            sa.ForeignKeyConstraint(
                ["work_order_id"],
                ["work_orders.id"],
                name="fk_wo_qc_tests__work_order_id__work_orders",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_wo_qc_test_wo_id", "wo_qc_tests", ["work_order_id"])

    # 4. wo_timers
    if "wo_timers" not in insp.get_table_names():
        op.create_table(
            "wo_timers",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("work_order_id", sa.String(length=36), nullable=False),
            sa.Column("timer_type", sa.String(length=50), nullable=False),
            sa.Column("seconds", sa.Integer(), nullable=False),
            sa.Column(
                "rate_per_hour", sa.Numeric(precision=12, scale=4), nullable=True
            ),
            sa.Column("cost", sa.Numeric(precision=12, scale=4), nullable=True),
            # AuditMixin fields
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(length=100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(length=100), nullable=True),
            sa.Column("previous_version_id", sa.String(length=36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(length=100), nullable=True),
            sa.ForeignKeyConstraint(
                ["work_order_id"],
                ["work_orders.id"],
                name="fk_wo_timers__work_order_id__work_orders",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    # 5. work_order_outputs
    if "work_order_outputs" not in insp.get_table_names():
        op.create_table(
            "work_order_outputs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("work_order_id", sa.String(length=36), nullable=False),
            sa.Column("product_id", sa.String(length=36), nullable=False),
            sa.Column(
                "qty_produced", sa.Numeric(precision=12, scale=4), nullable=False
            ),
            sa.Column("uom", sa.String(length=10), nullable=False),
            sa.Column("batch_id", sa.String(length=36), nullable=False),
            sa.Column("unit_cost", sa.Numeric(precision=12, scale=4), nullable=True),
            sa.Column("scrap_qty", sa.Numeric(precision=12, scale=4), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            # AuditMixin fields
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(length=100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(length=100), nullable=True),
            sa.Column("previous_version_id", sa.String(length=36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(length=100), nullable=True),
            sa.ForeignKeyConstraint(
                ["work_order_id"],
                ["work_orders.id"],
                name="fk_work_order_outputs__work_order_id__work_orders",
            ),
            sa.ForeignKeyConstraint(
                ["product_id"],
                ["products.id"],
                name="fk_work_order_outputs__product_id__products",
            ),
            sa.ForeignKeyConstraint(
                ["batch_id"],
                ["batches.id"],
                name="fk_work_order_outputs__batch_id__batches",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_wo_output_wo_id", "work_order_outputs", ["work_order_id"])

    # ============================================================================
    # (B) DROP LEGACY TABLE work_order_items
    # ============================================================================

    if "work_order_items" in insp.get_table_names():
        for ix in (
            "ix_wo_items_batch_code",
            "ix_wo_items_product_id",
            "ix_wo_items_work_order_id",
        ):
            try:
                op.drop_index(ix, table_name="work_order_items")
            except Exception:
                pass
        op.drop_table("work_order_items")

    # ============================================================================
    # (C) BATCH-ALTER EXISTING TABLES (SQLite recreate mode)
    # ============================================================================

    # 1. products
    # Note: Skipping products table changes due to NullType column issues in current schema.
    # Products table modifications (FKs, type changes, column drops) should be handled
    # in a separate migration that fixes NullType columns first.

    # 2. batches
    # Note: Adding columns without recreate to avoid FK constraint issues.
    # FK will be added in a future migration if needed.
    if "batches" in insp.get_table_names():
        existing_cols = {c["name"] for c in insp.get_columns("batches")}
        if "product_id" not in existing_cols:
            with op.batch_alter_table("batches", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("product_id", sa.String(length=36), nullable=True)
                )
        if "mfg_date" not in existing_cols:
            with op.batch_alter_table("batches", schema=None) as batch_op:
                batch_op.add_column(sa.Column("mfg_date", sa.Date(), nullable=True))
        if "exp_date" not in existing_cols:
            with op.batch_alter_table("batches", schema=None) as batch_op:
                batch_op.add_column(sa.Column("exp_date", sa.Date(), nullable=True))
        if "meta" not in existing_cols:
            with op.batch_alter_table("batches", schema=None) as batch_op:
                batch_op.add_column(sa.Column("meta", sa.Text(), nullable=True))

    # Recreate indexes for batches
    if "batches" in insp.get_table_names():
        for idx_name in ["ix_batches_batch_code", "ix_batch_product_status"]:
            try:
                op.drop_index(idx_name, table_name="batches")
            except Exception:
                pass

        if not has_index(insp, "batches", "ix_batches_batch_code"):
            op.create_index(
                "ix_batches_batch_code", "batches", ["batch_code"], unique=True
            )
        if not has_index(insp, "batches", "ix_batch_product_status"):
            op.create_index(
                "ix_batch_product_status", "batches", ["product_id", "status"]
            )

    # 3. inventory_movements
    # Note: Adding columns without recreate to avoid FK constraint issues.
    if "inventory_movements" in insp.get_table_names():
        existing_cols = {c["name"] for c in insp.get_columns("inventory_movements")}
        if "timestamp" not in existing_cols:
            with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("timestamp", sa.DateTime(), nullable=True)
                )
        if "batch_id" not in existing_cols:
            with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("batch_id", sa.String(length=36), nullable=True)
                )
        if "uom" not in existing_cols:
            with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("uom", sa.String(length=10), nullable=True)
                )
        if "move_type" not in existing_cols:
            with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("move_type", sa.String(length=50), nullable=True)
                )
        if "ref_table" not in existing_cols:
            with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("ref_table", sa.String(length=50), nullable=True)
                )
        if "ref_id" not in existing_cols:
            with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("ref_id", sa.String(length=36), nullable=True)
                )
        if "unit_cost" not in existing_cols:
            with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column(
                        "unit_cost", sa.Numeric(precision=12, scale=4), nullable=True
                    )
                )

    # Recreate indexes for inventory_movements
    if "inventory_movements" in insp.get_table_names():
        # Drop old indexes
        for idx_name in [
            "ix_movements_batch",
            "ix_movements_move_type",
            "ix_movements_product_ts",
            "ix_movements_ref",
        ]:
            try:
                op.drop_index(idx_name, table_name="inventory_movements")
            except Exception:
                pass

        # Create new indexes
        if not has_index(insp, "inventory_movements", "ix_movements_batch"):
            op.create_index("ix_movements_batch", "inventory_movements", ["batch_id"])
        if not has_index(insp, "inventory_movements", "ix_movements_move_type"):
            op.create_index(
                "ix_movements_move_type", "inventory_movements", ["move_type"]
            )
        if not has_index(insp, "inventory_movements", "ix_movements_product_ts"):
            op.create_index(
                "ix_movements_product_ts",
                "inventory_movements",
                ["product_id", "timestamp"],
            )
        if not has_index(insp, "inventory_movements", "ix_movements_ref"):
            op.create_index(
                "ix_movements_ref", "inventory_movements", ["ref_table", "ref_id"]
            )

    # 4. work_orders
    # Note: Skipping work_orders changes for now. formula_id nullable and assembly_id FK
    # will be handled in a future migration if needed.
    pass

    # Recreate indexes for work_orders
    if "work_orders" in insp.get_table_names():
        for idx_name in [
            "ix_work_order_batch_code",
            "ix_work_order_status",
            "ix_work_order_product_status",
            "ix_work_orders_batch_code",
        ]:
            try:
                op.drop_index(idx_name, table_name="work_orders")
            except Exception:
                pass

        if not has_index(insp, "work_orders", "ix_work_order_batch_code"):
            op.create_index("ix_work_order_batch_code", "work_orders", ["batch_code"])
        if not has_index(insp, "work_orders", "ix_work_order_status"):
            op.create_index("ix_work_order_status", "work_orders", ["status"])
        if not has_index(insp, "work_orders", "ix_work_order_product_status"):
            op.create_index(
                "ix_work_order_product_status", "work_orders", ["product_id", "status"]
            )
        if not has_index(insp, "work_orders", "ix_work_orders_batch_code"):
            op.create_index(
                "ix_work_orders_batch_code", "work_orders", ["batch_code"], unique=True
            )

    # 5. work_order_lines
    # Note: Adding columns without recreate to avoid FK constraint issues.
    if "work_order_lines" in insp.get_table_names():
        existing_cols = {c["name"] for c in insp.get_columns("work_order_lines")}
        if "component_product_id" not in existing_cols:
            with op.batch_alter_table("work_order_lines", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column(
                        "component_product_id", sa.String(length=36), nullable=True
                    )
                )  # Start nullable
        if "planned_qty" not in existing_cols:
            with op.batch_alter_table("work_order_lines", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column(
                        "planned_qty", sa.Numeric(precision=12, scale=4), nullable=True
                    )
                )
        if "actual_qty" not in existing_cols:
            with op.batch_alter_table("work_order_lines", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column(
                        "actual_qty", sa.Numeric(precision=12, scale=4), nullable=True
                    )
                )
        if "uom" not in existing_cols:
            with op.batch_alter_table("work_order_lines", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("uom", sa.String(length=10), nullable=True)
                )
        if "source_batch_id" not in existing_cols:
            with op.batch_alter_table("work_order_lines", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column("source_batch_id", sa.String(length=36), nullable=True)
                )
        if "unit_cost" not in existing_cols:
            with op.batch_alter_table("work_order_lines", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column(
                        "unit_cost", sa.Numeric(precision=12, scale=4), nullable=True
                    )
                )
        if "line_type" not in existing_cols:
            with op.batch_alter_table("work_order_lines", schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column(
                        "line_type",
                        sa.String(length=20),
                        nullable=True,
                        server_default="material",
                    )
                )
        if "note" not in existing_cols:
            with op.batch_alter_table("work_order_lines", schema=None) as batch_op:
                batch_op.add_column(sa.Column("note", sa.Text(), nullable=True))

    # Recreate index for work_order_lines
    if "work_order_lines" in insp.get_table_names():
        try:
            op.drop_index("ix_work_order_line_wo_id", table_name="work_order_lines")
        except Exception:
            pass

        if not has_index(insp, "work_order_lines", "ix_work_order_line_wo_id"):
            op.create_index(
                "ix_work_order_line_wo_id", "work_order_lines", ["work_order_id"]
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)

    # Drop new tables
    for table in [
        "work_order_outputs",
        "wo_timers",
        "wo_qc_tests",
        "batch_seq",
        "product_cost_rates",
    ]:
        if table in insp.get_table_names():
            op.drop_table(table)

    # Note: Downgrade for batch-alter tables would require full recreation
    # which is complex and data-lossy, so we document this as intentionally limited
    pass
