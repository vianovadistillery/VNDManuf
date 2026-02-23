"""Add delivery and billing address columns to customers.

Revision ID: 20250223_cust_addr
Revises: 20250223_dd
Create Date: 2025-02-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250223_cust_addr"
down_revision: Union[str, None] = "20250223_dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "customers" not in insp.get_table_names():
        return

    cols = [
        ("billing_address_line1", sa.String(200)),
        ("billing_address_line2", sa.String(200)),
        ("billing_suburb", sa.String(100)),
        ("billing_state", sa.String(50)),
        ("billing_postcode", sa.String(20)),
        ("billing_country", sa.String(100)),
        ("delivery_address_line1", sa.String(200)),
        ("delivery_address_line2", sa.String(200)),
        ("delivery_suburb", sa.String(100)),
        ("delivery_state", sa.String(50)),
        ("delivery_postcode", sa.String(20)),
        ("delivery_country", sa.String(100)),
    ]
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("customers", schema=None) as batch_op:
            for name, col_type in cols:
                if not _has_column(insp, "customers", name):
                    batch_op.add_column(sa.Column(name, col_type, nullable=True))
    else:
        for name, col_type in cols:
            if not _has_column(insp, "customers", name):
                op.add_column("customers", sa.Column(name, col_type, nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("customers", schema=None) as batch_op:
            for col in (
                "delivery_country",
                "delivery_postcode",
                "delivery_state",
                "delivery_suburb",
                "delivery_address_line2",
                "delivery_address_line1",
                "billing_country",
                "billing_postcode",
                "billing_state",
                "billing_suburb",
                "billing_address_line2",
                "billing_address_line1",
            ):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    else:
        for col in (
            "delivery_country",
            "delivery_postcode",
            "delivery_state",
            "delivery_suburb",
            "delivery_address_line2",
            "delivery_address_line1",
            "billing_country",
            "billing_postcode",
            "billing_state",
            "billing_suburb",
            "billing_address_line2",
            "billing_address_line1",
        ):
            try:
                op.drop_column("customers", col)
            except Exception:
                pass
