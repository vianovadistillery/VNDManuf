"""Add ALM account number to contacts.

Revision ID: 20250223_alm
Revises: 20250223_contacts_addr
Create Date: 2025-02-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250223_alm"
down_revision: Union[str, None] = "20250223_contacts_addr"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "contacts" not in insp.get_table_names():
        return
    if _has_column(insp, "contacts", "alm_account_number"):
        return
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("contacts", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("alm_account_number", sa.String(50), nullable=True)
            )
    else:
        op.add_column(
            "contacts", sa.Column("alm_account_number", sa.String(50), nullable=True)
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "contacts" not in insp.get_table_names():
        return
    if not _has_column(insp, "contacts", "alm_account_number"):
        return
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("contacts", schema=None) as batch_op:
            batch_op.drop_column("alm_account_number")
    else:
        op.drop_column("contacts", "alm_account_number")
