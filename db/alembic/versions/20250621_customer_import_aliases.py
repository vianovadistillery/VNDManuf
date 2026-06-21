"""Add customer_import_aliases for CSV import name mapping.

Revision ID: 20250621_cust_alias
Revises: 20250301_contacts_pay
Create Date: 2025-06-21

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250621_cust_alias"
down_revision: Union[str, None] = "20250301_contacts_pay"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)
    if insp.has_table("customer_import_aliases"):
        return

    op.create_table(
        "customer_import_aliases",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("alias_key", sa.String(200), nullable=False),
        sa.Column("alias_label", sa.String(200), nullable=False),
        sa.Column("customer_id", sa.String(36), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.String(100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("versioned_at", sa.DateTime(), nullable=True),
        sa.Column("versioned_by", sa.String(100), nullable=True),
        sa.Column("previous_version_id", sa.String(36), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archived_by", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_customer_import_aliases__customer_id__customers",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_customer_import_aliases"),
        sa.UniqueConstraint("alias_key", name="uq_customer_import_aliases_alias_key"),
    )
    op.create_index(
        "ix_customer_import_aliases_alias_key",
        "customer_import_aliases",
        ["alias_key"],
        unique=False,
    )
    op.create_index(
        "ix_customer_import_aliases_customer",
        "customer_import_aliases",
        ["customer_id"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)
    if not insp.has_table("customer_import_aliases"):
        return
    for ix in (
        "ix_customer_import_aliases_customer",
        "ix_customer_import_aliases_alias_key",
    ):
        try:
            op.drop_index(ix, table_name="customer_import_aliases")
        except Exception:
            pass
    op.drop_table("customer_import_aliases")
