"""Add generated_documents table for mail-merge PDF tracking.

Revision ID: 20250223_gendoc
Revises: distillation_runs_20251111
Create Date: 2025-02-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250223_gendoc"
down_revision: Union[str, None] = "distillation_runs_20251111"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "generated_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("doc_type", sa.String(50), nullable=False, index=True),
        sa.Column("doc_number", sa.String(50), nullable=True, index=True),
        sa.Column("status", sa.String(20), nullable=False, index=True),
        sa.Column("template_name", sa.String(200), nullable=False),
        sa.Column("pdf_path", sa.String(500), nullable=True),
        sa.Column("docx_path", sa.String(500), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "contact_id",
            sa.String(36),
            sa.ForeignKey("contacts.id"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "customer_id",
            sa.String(36),
            sa.ForeignKey("customers.id"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "sales_order_id",
            sa.String(36),
            sa.ForeignKey("sales_orders.id"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "delivery_docket_id",
            sa.String(36),
            sa.ForeignKey("delivery_dockets.id"),
            nullable=True,
            index=True,
        ),
        sa.Column("job_id", sa.String(100), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("generated_documents")
