"""Add missing columns: customers.contact_name, sales_orders.pricebook_id.

Revision ID: 20250223_cust_ord
Revises: 20250223_sales_audit
Create Date: 2025-02-23

Fixes ORM/schema mismatch so GET /api/v1/sales/customers and /sales/orders work.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250223_cust_ord"
down_revision: Union[str, None] = "20250223_sales_audit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def _has_table(insp: sa.engine.reflection.Inspector, name: str) -> bool:
    return name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if _has_table(insp, "customers") and not _has_column(
        insp, "customers", "contact_name"
    ):
        with op.batch_alter_table("customers", schema=None) as batch:
            batch.add_column(sa.Column("contact_name", sa.String(100), nullable=True))

    insp = sa.inspect(bind)
    if _has_table(insp, "sales_orders") and not _has_column(
        insp, "sales_orders", "pricebook_id"
    ):
        with op.batch_alter_table("sales_orders", schema=None) as batch:
            batch.add_column(sa.Column("pricebook_id", sa.String(36), nullable=True))
        if _has_table(insp, "pricebooks"):
            with op.batch_alter_table("sales_orders", schema=None) as batch:
                batch.create_foreign_key(
                    "fk_sales_orders__pricebook_id__pricebooks",
                    "pricebooks",
                    ["pricebook_id"],
                    ["id"],
                )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if _has_table(insp, "sales_orders") and _has_column(
        insp, "sales_orders", "pricebook_id"
    ):
        with op.batch_alter_table("sales_orders", schema=None) as batch:
            try:
                batch.drop_constraint(
                    "fk_sales_orders__pricebook_id__pricebooks",
                    type_="foreignkey",
                )
            except Exception:
                pass
            batch.drop_column("pricebook_id")

    if _has_table(insp, "customers") and _has_column(insp, "customers", "contact_name"):
        with op.batch_alter_table("customers", schema=None) as batch:
            batch.drop_column("contact_name")
