"""Add invoices.delivery_docket_id (FK to delivery_dockets.id).

Revision ID: 20250226_inv_dd
Revises: 20250223_merge2
Create Date: 2026-02-26

Fixes: no such column invoices.delivery_docket_id when loading orders.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250226_inv_dd"
down_revision: Union[str, None] = "20250223_merge2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if insp.has_table("invoices") and not _has_column(
        insp, "invoices", "delivery_docket_id"
    ):
        with op.batch_alter_table("invoices", schema=None) as batch:
            batch.add_column(
                sa.Column(
                    "delivery_docket_id",
                    sa.String(36),
                    sa.ForeignKey("delivery_dockets.id"),
                    nullable=True,
                )
            )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if insp.has_table("invoices") and _has_column(
        insp, "invoices", "delivery_docket_id"
    ):
        with op.batch_alter_table("invoices", schema=None) as batch:
            batch.drop_column("delivery_docket_id")
