"""Add payment_method, paramount_number, default_pricing_level to contacts.

Revision ID: 20250301_contacts_pay
Revises: 20250301_dd_line_oqty
Create Date: 2025-03-01

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250301_contacts_pay"
down_revision: Union[str, None] = "20250301_dd_line_oqty"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("contacts"):
        return
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("contacts", schema=None) as batch_op:
            if not _has_column(insp, "contacts", "payment_method"):
                batch_op.add_column(
                    sa.Column("payment_method", sa.String(50), nullable=True)
                )
            if not _has_column(insp, "contacts", "paramount_number"):
                batch_op.add_column(
                    sa.Column("paramount_number", sa.String(50), nullable=True)
                )
            if not _has_column(insp, "contacts", "default_pricing_level"):
                batch_op.add_column(
                    sa.Column("default_pricing_level", sa.String(50), nullable=True)
                )
    else:
        if not _has_column(insp, "contacts", "payment_method"):
            op.add_column(
                "contacts", sa.Column("payment_method", sa.String(50), nullable=True)
            )
        if not _has_column(insp, "contacts", "paramount_number"):
            op.add_column(
                "contacts", sa.Column("paramount_number", sa.String(50), nullable=True)
            )
        if not _has_column(insp, "contacts", "default_pricing_level"):
            op.add_column(
                "contacts",
                sa.Column("default_pricing_level", sa.String(50), nullable=True),
            )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("contacts"):
        return
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("contacts", schema=None) as batch_op:
            if _has_column(insp, "contacts", "payment_method"):
                batch_op.drop_column("payment_method")
            if _has_column(insp, "contacts", "paramount_number"):
                batch_op.drop_column("paramount_number")
            if _has_column(insp, "contacts", "default_pricing_level"):
                batch_op.drop_column("default_pricing_level")
    else:
        if _has_column(insp, "contacts", "payment_method"):
            op.drop_column("contacts", "payment_method")
        if _has_column(insp, "contacts", "paramount_number"):
            op.drop_column("contacts", "paramount_number")
        if _has_column(insp, "contacts", "default_pricing_level"):
            op.drop_column("contacts", "default_pricing_level")
