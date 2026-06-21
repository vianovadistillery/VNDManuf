"""Add order discount, PO, total alcohol; Invoice.paid; support unified orders/delivery/invoice view.

Revision ID: 20250223_ord_del_inv
Revises: 20250223_merge
Create Date: 2025-02-23

- sales_orders: order_discount_ex_gst, po_number, total_alcohol_volume_litres
- invoices: paid (boolean)
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250223_ord_del_inv"
down_revision: Union[str, None] = "20250223_merge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if insp.has_table("sales_orders"):
        with op.batch_alter_table("sales_orders", schema=None) as batch:
            if not _has_column(insp, "sales_orders", "order_discount_ex_gst"):
                batch.add_column(
                    sa.Column(
                        "order_discount_ex_gst",
                        sa.Numeric(12, 2),
                        nullable=False,
                        server_default=sa.text("0"),
                    )
                )
            if not _has_column(insp, "sales_orders", "po_number"):
                batch.add_column(sa.Column("po_number", sa.String(50), nullable=True))
            if not _has_column(insp, "sales_orders", "total_alcohol_volume_litres"):
                batch.add_column(
                    sa.Column(
                        "total_alcohol_volume_litres", sa.Numeric(12, 4), nullable=True
                    )
                )
        insp = sa.inspect(bind)

    if insp.has_table("invoices"):
        with op.batch_alter_table("invoices", schema=None) as batch:
            if not _has_column(insp, "invoices", "paid"):
                batch.add_column(
                    sa.Column(
                        "paid",
                        sa.Boolean(),
                        nullable=False,
                        server_default=sa.text("0"),
                    )
                )
        insp = sa.inspect(bind)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if insp.has_table("invoices") and _has_column(insp, "invoices", "paid"):
        with op.batch_alter_table("invoices", schema=None) as batch:
            batch.drop_column("paid")

    if insp.has_table("sales_orders"):
        with op.batch_alter_table("sales_orders", schema=None) as batch:
            if _has_column(insp, "sales_orders", "total_alcohol_volume_litres"):
                batch.drop_column("total_alcohol_volume_litres")
            if _has_column(insp, "sales_orders", "po_number"):
                batch.drop_column("po_number")
            if _has_column(insp, "sales_orders", "order_discount_ex_gst"):
                batch.drop_column("order_discount_ex_gst")
