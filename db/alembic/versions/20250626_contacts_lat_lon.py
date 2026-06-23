"""Add latitude and longitude to contacts.

Revision ID: 20250626_contacts_geo
Revises: 20250625_cust_map
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250626_contacts_geo"
down_revision: Union[str, None] = "20250625_cust_map"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
        bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_contacts"))
    insp = sa.inspect(bind)
    if not insp.has_table("contacts"):
        return
    pending = []
    if not _has_column(insp, "contacts", "latitude"):
        pending.append(sa.Column("latitude", sa.Numeric(10, 6), nullable=True))
    if not _has_column(insp, "contacts", "longitude"):
        pending.append(sa.Column("longitude", sa.Numeric(10, 6), nullable=True))
    if pending:
        if bind.dialect.name == "sqlite":
            bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
        try:
            with op.batch_alter_table("contacts", recreate="always") as batch:
                for col in pending:
                    batch.add_column(col)
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)
    cols = [c for c in ("latitude", "longitude") if _has_column(insp, "contacts", c)]
    if cols:
        if bind.dialect.name == "sqlite":
            bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
        try:
            with op.batch_alter_table("contacts", recreate="always") as batch:
                for col in cols:
                    batch.drop_column(col)
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))
