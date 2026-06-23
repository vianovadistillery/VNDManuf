"""Add freight, commission, and distributor fields to sales_orders.

Revision ID: 20250623_so_freight
Revises: 20250623_nu_rich
Create Date: 2025-06-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250623_so_freight"
down_revision: Union[str, None] = "20250623_nu_rich"
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
        bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_sales_orders"))
    insp = sa.inspect(bind)
    if not insp.has_table("sales_orders"):
        return

    cols_to_add = []
    if not _has_column(insp, "sales_orders", "freight_ex_gst"):
        cols_to_add.append(
            (
                "freight_ex_gst",
                sa.Column(
                    "freight_ex_gst",
                    sa.Numeric(12, 2),
                    nullable=False,
                    server_default=sa.text("0"),
                ),
            )
        )
    if not _has_column(insp, "sales_orders", "freight_gst"):
        cols_to_add.append(
            (
                "freight_gst",
                sa.Column(
                    "freight_gst",
                    sa.Numeric(12, 2),
                    nullable=False,
                    server_default=sa.text("0"),
                ),
            )
        )
    if not _has_column(insp, "sales_orders", "freight_inc_gst"):
        cols_to_add.append(
            (
                "freight_inc_gst",
                sa.Column(
                    "freight_inc_gst",
                    sa.Numeric(12, 2),
                    nullable=False,
                    server_default=sa.text("0"),
                ),
            )
        )
    if not _has_column(insp, "sales_orders", "commission_amount"):
        cols_to_add.append(
            (
                "commission_amount",
                sa.Column("commission_amount", sa.Numeric(12, 2), nullable=True),
            )
        )
    if not _has_column(insp, "sales_orders", "distributor"):
        cols_to_add.append(
            (
                "distributor",
                sa.Column("distributor", sa.String(50), nullable=True),
            )
        )

    if cols_to_add:
        if bind.dialect.name == "sqlite":
            bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
        try:
            with op.batch_alter_table("sales_orders", recreate="always") as batch:
                for _name, col in cols_to_add:
                    batch.add_column(col)
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)
    if not insp.has_table("sales_orders"):
        return

    cols = [c["name"] for c in insp.get_columns("sales_orders")]
    drop_cols = [
        c
        for c in (
            "distributor",
            "commission_amount",
            "freight_inc_gst",
            "freight_gst",
            "freight_ex_gst",
        )
        if c in cols
    ]
    if drop_cols:
        if bind.dialect.name == "sqlite":
            bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
        try:
            with op.batch_alter_table("sales_orders", recreate="always") as batch:
                for col in drop_cols:
                    batch.drop_column(col)
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))
