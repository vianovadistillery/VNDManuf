"""add_work_order_system

Revision ID: 0651e10f5ac8
Revises: 212104c7dfa8
Create Date: 2025-11-05 12:20:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0651e10f5ac8"
down_revision: Union[str, None] = "212104c7dfa8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    insp = sa.inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # Ensure SQLite enforces foreign keys at runtime.
    # (No-op on other dialects.)
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    # --- work_orders table ---
    if not _table_exists(bind, "work_orders"):
        op.create_table(
            "work_orders",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column(
                "status", sa.String(length=50), nullable=False, server_default="draft"
            ),
            sa.Column("reference", sa.String(length=100), nullable=True, unique=True),
            sa.Column("scheduled_date", sa.Date(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            mysql_engine="InnoDB",
        )
        op.create_index("ix_work_orders_status", "work_orders", ["status"])

    # --- work_order_items table ---
    if not _table_exists(bind, "work_order_items"):
        # Define with FKs inline so SQLite is happy.
        op.create_table(
            "work_order_items",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("work_order_id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("batch_code", sa.String(length=64), nullable=True),
            sa.Column(
                "planned_qty",
                sa.Numeric(precision=14, scale=3),
                nullable=False,
                server_default="0",
            ),
            sa.Column("actual_qty", sa.Numeric(precision=14, scale=3), nullable=True),
            sa.Column("uom", sa.String(length=16), nullable=True),
            sa.Column(
                "qc_required", sa.Boolean(), nullable=False, server_default=sa.text("0")
            ),
            sa.Column("qc_passed", sa.Boolean(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            # --- Foreign keys inline ---
            sa.ForeignKeyConstraint(
                ["work_order_id"],
                ["work_orders.id"],
                name="fk_wo_items_work_order",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["product_id"],
                ["products.id"],
                name="fk_wo_items_product",
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            mysql_engine="InnoDB",
        )
        op.create_index(
            "ix_wo_items_work_order_id", "work_order_items", ["work_order_id"]
        )
        op.create_index("ix_wo_items_product_id", "work_order_items", ["product_id"])
        op.create_index("ix_wo_items_batch_code", "work_order_items", ["batch_code"])

    # NOTE:
    # If an earlier version of this migration partially created the tables *without* FKs,
    # and you need the constraints enforced, the SQLite-safe path is to do a follow-up
    # migration that recreates `work_order_items` with the FK constraints (copy/move).
    # We can provide that if needed.


def downgrade() -> None:
    bind = op.get_bind()
    # Drop child first (FK to parent)
    if _table_exists(bind, "work_order_items"):
        op.drop_index("ix_wo_items_batch_code", table_name="work_order_items")
        op.drop_index("ix_wo_items_product_id", table_name="work_order_items")
        op.drop_index("ix_wo_items_work_order_id", table_name="work_order_items")
        op.drop_table("work_order_items")

    if _table_exists(bind, "work_orders"):
        op.drop_index("ix_work_orders_status", table_name="work_orders")
        op.drop_table("work_orders")
