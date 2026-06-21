"""Add audit columns to pricebook_items for AuditMixin parity.

Revision ID: 20250621_pb_items_audit
Revises: 20250621_site_alias
Create Date: 2025-06-21

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250621_pb_items_audit"
down_revision: Union[str, None] = "20250621_site_alias"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (column_name, sqlite_ddl_fragment)
_AUDIT_COLUMNS = (
    ("deleted_by", "VARCHAR(100)"),
    ("version", "INTEGER NOT NULL DEFAULT 1"),
    ("versioned_at", "DATETIME"),
    ("versioned_by", "VARCHAR(100)"),
    ("previous_version_id", "VARCHAR(36)"),
    ("archived_at", "DATETIME"),
    ("archived_by", "VARCHAR(100)"),
)


def _has_column(insp, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)
    if not insp.has_table("pricebook_items"):
        return

    for name, ddl in _AUDIT_COLUMNS:
        if _has_column(insp, "pricebook_items", name):
            continue
        bind.execute(sa.text(f"ALTER TABLE pricebook_items ADD COLUMN {name} {ddl}"))


def downgrade() -> None:
    # SQLite cannot drop columns safely without table rebuild; leave as no-op.
    pass
