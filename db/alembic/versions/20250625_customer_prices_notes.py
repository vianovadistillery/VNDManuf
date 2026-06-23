"""Add notes column to customer_prices for special pricing offers.

Revision ID: 20250625_cust_price_notes
Revises: 20250624_so_payment
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250625_cust_price_notes"
down_revision: Union[str, None] = "20250624_so_payment"
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
    insp = sa.inspect(bind)
    if insp.has_table("customer_prices") and not _has_column(
        insp, "customer_prices", "notes"
    ):
        try:
            with op.batch_alter_table("customer_prices", recreate="always") as batch:
                batch.add_column(sa.Column("notes", sa.Text(), nullable=True))
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
    insp = sa.inspect(bind)
    cols = (
        [c["name"] for c in insp.get_columns("customer_prices")]
        if insp.has_table("customer_prices")
        else []
    )
    if "notes" in cols:
        try:
            with op.batch_alter_table("customer_prices", recreate="always") as batch:
                batch.drop_column("notes")
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))
