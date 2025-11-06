"""add_work_order_cost_and_qty_fields

Revision ID: d5e11b38c91a
Revises: 3ffe25d38c5c
Create Date: 2025-11-06 15:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5e11b38c91a"
down_revision: Union[str, None] = "3ffe25d38c5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_column(insp, table, col):
    """Helper to check if column exists."""
    return any(c["name"] == col for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)

    # Add actual_qty, estimated_cost, actual_cost columns to work_orders table
    # SQLite supports adding nullable columns directly without recreating the table
    if not has_column(insp, "work_orders", "actual_qty"):
        if bind.dialect.name == "sqlite":
            op.add_column(
                "work_orders", sa.Column("actual_qty", sa.Numeric(12, 4), nullable=True)
            )
        else:
            with op.batch_alter_table("work_orders", recreate="always") as batch_op:
                batch_op.add_column(
                    sa.Column("actual_qty", sa.Numeric(12, 4), nullable=True)
                )

    if not has_column(insp, "work_orders", "estimated_cost"):
        if bind.dialect.name == "sqlite":
            op.add_column(
                "work_orders",
                sa.Column("estimated_cost", sa.Numeric(12, 4), nullable=True),
            )
        else:
            with op.batch_alter_table("work_orders", recreate="always") as batch_op:
                batch_op.add_column(
                    sa.Column("estimated_cost", sa.Numeric(12, 4), nullable=True)
                )

    if not has_column(insp, "work_orders", "actual_cost"):
        if bind.dialect.name == "sqlite":
            op.add_column(
                "work_orders",
                sa.Column("actual_cost", sa.Numeric(12, 4), nullable=True),
            )
        else:
            with op.batch_alter_table("work_orders", recreate="always") as batch_op:
                batch_op.add_column(
                    sa.Column("actual_cost", sa.Numeric(12, 4), nullable=True)
                )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Remove columns from work_orders table
    if has_column(insp, "work_orders", "actual_cost"):
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("work_orders", recreate="always") as batch_op:
                batch_op.drop_column("actual_cost")
        else:
            op.drop_column("work_orders", "actual_cost")

    if has_column(insp, "work_orders", "estimated_cost"):
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("work_orders", recreate="always") as batch_op:
                batch_op.drop_column("estimated_cost")
        else:
            op.drop_column("work_orders", "estimated_cost")

    if has_column(insp, "work_orders", "actual_qty"):
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("work_orders", recreate="always") as batch_op:
                batch_op.drop_column("actual_qty")
        else:
            op.drop_column("work_orders", "actual_qty")
