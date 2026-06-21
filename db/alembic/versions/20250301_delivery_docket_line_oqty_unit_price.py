"""Add ordered_quantity and unit_price to delivery_docket_lines for oqty/dqty and pricing.

Revision ID: 20250301_dd_line_oqty
Revises: 20250226_doc_links
Create Date: 2025-03-01

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250301_dd_line_oqty"
down_revision: Union[str, None] = "20250226_doc_links"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("delivery_docket_lines"):
        return
    with op.batch_alter_table("delivery_docket_lines", schema=None) as batch:
        if not _has_column(insp, "delivery_docket_lines", "ordered_quantity"):
            batch.add_column(
                sa.Column("ordered_quantity", sa.Numeric(12, 3), nullable=True)
            )
        if not _has_column(insp, "delivery_docket_lines", "unit_price"):
            batch.add_column(sa.Column("unit_price", sa.Numeric(14, 4), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("delivery_docket_lines"):
        return
    with op.batch_alter_table("delivery_docket_lines", schema=None) as batch:
        if _has_column(insp, "delivery_docket_lines", "ordered_quantity"):
            batch.drop_column("ordered_quantity")
        if _has_column(insp, "delivery_docket_lines", "unit_price"):
            batch.drop_column("unit_price")
