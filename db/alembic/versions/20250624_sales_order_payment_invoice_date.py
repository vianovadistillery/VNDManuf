"""Add payment_date, payment_reference, invoice_date to sales_orders.

Revision ID: 20250624_so_payment
Revises: 20250623_so_freight
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250624_so_payment"
down_revision: Union[str, None] = "20250623_so_freight"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
        bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_sales_orders"))
    insp = sa.inspect(bind)
    if not insp.has_table("sales_orders"):
        return

    cols = []
    if not _has_column(insp, "sales_orders", "payment_date"):
        cols.append(
            sa.Column("payment_date", sa.DateTime(), nullable=True),
        )
    if not _has_column(insp, "sales_orders", "payment_reference"):
        cols.append(
            sa.Column("payment_reference", sa.String(100), nullable=True),
        )
    if not _has_column(insp, "sales_orders", "invoice_date"):
        cols.append(
            sa.Column("invoice_date", sa.DateTime(), nullable=True),
        )
    if cols:
        try:
            with op.batch_alter_table("sales_orders", recreate="always") as batch:
                for col in cols:
                    batch.add_column(col)
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
    insp = sa.inspect(bind)
    if not insp.has_table("sales_orders"):
        return
    cols = [c["name"] for c in insp.get_columns("sales_orders")]
    drop = [
        c for c in ("invoice_date", "payment_reference", "payment_date") if c in cols
    ]
    if drop:
        try:
            with op.batch_alter_table("sales_orders", recreate="always") as batch:
                for col in drop:
                    batch.drop_column(col)
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))
