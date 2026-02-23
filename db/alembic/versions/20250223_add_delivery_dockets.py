"""Add delivery_dockets and delivery_docket_lines tables.

Revision ID: 20250223_dd
Revises: 20250223_gendoc
Create Date: 2025-02-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250223_dd"
down_revision: Union[str, None] = "20250223_gendoc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "delivery_dockets" in insp.get_table_names():
        return

    op.create_table(
        "delivery_dockets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "customer_id",
            sa.String(36),
            sa.ForeignKey("customers.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "sales_order_id",
            sa.String(36),
            sa.ForeignKey("sales_orders.id"),
            nullable=True,
            index=True,
        ),
        sa.Column("docket_number", sa.String(50), nullable=False, index=True),
        sa.Column("docket_date", sa.DateTime(), nullable=False),
        sa.Column("delivery_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.String(100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("versioned_at", sa.DateTime(), nullable=True),
        sa.Column("versioned_by", sa.String(100), nullable=True),
        sa.Column("previous_version_id", sa.String(36), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archived_by", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_delivery_docket_number", "delivery_dockets", ["docket_number"], unique=True
    )

    op.create_table(
        "delivery_docket_lines",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "docket_id",
            sa.String(36),
            sa.ForeignKey("delivery_dockets.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False
        ),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("uom", sa.String(20), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.String(100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("versioned_at", sa.DateTime(), nullable=True),
        sa.Column("versioned_by", sa.String(100), nullable=True),
        sa.Column("previous_version_id", sa.String(36), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("archived_by", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_delivery_docket_lines_docket",
        "delivery_docket_lines",
        ["docket_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_delivery_docket_lines_docket", table_name="delivery_docket_lines")
    op.drop_table("delivery_docket_lines")
    op.drop_index("ix_delivery_docket_number", table_name="delivery_dockets")
    op.drop_table("delivery_dockets")
