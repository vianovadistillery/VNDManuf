"""Extend sales tables with full AuditMixin columns (deleted_by, version, archived_at, etc.)

Revision ID: 20250223_sales_audit
Revises: eaf2f04d3b5d
Create Date: 2025-02-23

Sales tables (sales_channels, customer_sites, pricebooks, sales_tags) were created
with only created_at, updated_at, deleted_at. This adds the remaining AuditMixin
columns so the ORM matches the schema.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250223_sales_audit"
down_revision: Union[str, None] = "eaf2f04d3b5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(col["name"] == column for col in insp.get_columns(table))


def _has_index(
    insp: sa.engine.reflection.Inspector, table: str, index_name: str
) -> bool:
    if not insp.has_table(table):
        return False
    return any(ix["name"] == index_name for ix in insp.get_indexes(table))


# Columns to add for full AuditMixin (beyond created_at, updated_at, deleted_at)
AUDIT_COLUMNS = [
    ("deleted_by", sa.String(100), True),
    ("version", sa.Integer(), False),  # server_default=1
    ("versioned_at", sa.DateTime(), True),
    ("versioned_by", sa.String(100), True),
    ("previous_version_id", sa.String(36), True),
    ("archived_at", sa.DateTime(), True),
    ("archived_by", sa.String(100), True),
]

SALES_AUDIT_TABLES = ("sales_channels", "customer_sites", "pricebooks", "sales_tags")


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    for table in SALES_AUDIT_TABLES:
        if not insp.has_table(table):
            continue
        cols_to_add = [
            (name, typ, nullable)
            for name, typ, nullable in AUDIT_COLUMNS
            if not _has_column(insp, table, name)
        ]
        if not cols_to_add:
            continue
        with op.batch_alter_table(table, schema=None) as batch:
            for name, typ, nullable in cols_to_add:
                kw = {"nullable": nullable}
                if name == "version" and not nullable:
                    kw["server_default"] = sa.text("1")
                batch.add_column(sa.Column(name, typ, **kw))
        insp = sa.inspect(bind)

    # Create indexes expected by AuditMixin (deleted_at, version, archived_at)
    for table in SALES_AUDIT_TABLES:
        if not insp.has_table(table):
            continue
        for col, idx_name in (
            ("deleted_at", f"ix_{table}_deleted_at"),
            ("version", f"ix_{table}_version"),
            ("archived_at", f"ix_{table}_archived_at"),
        ):
            if _has_column(insp, table, col) and not _has_index(insp, table, idx_name):
                op.create_index(idx_name, table, [col], unique=False)
        insp = sa.inspect(bind)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    for table in SALES_AUDIT_TABLES:
        if not insp.has_table(table):
            continue
        for idx_name in (
            f"ix_{table}_deleted_at",
            f"ix_{table}_version",
            f"ix_{table}_archived_at",
        ):
            if _has_index(insp, table, idx_name):
                op.drop_index(idx_name, table_name=table)
        insp = sa.inspect(bind)

    for table in SALES_AUDIT_TABLES:
        if not insp.has_table(table):
            continue
        with op.batch_alter_table(table, schema=None) as batch:
            for name, _typ, _nullable in AUDIT_COLUMNS:
                if _has_column(insp, table, name):
                    batch.drop_column(name)
        insp = sa.inspect(bind)
