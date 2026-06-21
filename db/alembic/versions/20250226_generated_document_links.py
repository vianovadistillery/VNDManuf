"""Add generated_document_id to delivery_dockets and invoices.

Revision ID: 20250226_doc_links
Revises: 20250226_inv_dd
Create Date: 2026-02-26

Links created mail-merge files (PDF) to docket/invoice for Open vs Create button.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250226_doc_links"
down_revision: Union[str, None] = "20250226_inv_dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if insp.has_table("delivery_dockets") and not _has_column(
        insp, "delivery_dockets", "generated_document_id"
    ):
        with op.batch_alter_table("delivery_dockets", schema=None) as batch:
            batch.add_column(
                sa.Column(
                    "generated_document_id",
                    sa.String(36),
                    sa.ForeignKey("generated_documents.id"),
                    nullable=True,
                )
            )

    if insp.has_table("invoices") and not _has_column(
        insp, "invoices", "generated_document_id"
    ):
        with op.batch_alter_table("invoices", schema=None) as batch:
            batch.add_column(
                sa.Column(
                    "generated_document_id",
                    sa.String(36),
                    sa.ForeignKey("generated_documents.id"),
                    nullable=True,
                )
            )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if insp.has_table("invoices") and _has_column(
        insp, "invoices", "generated_document_id"
    ):
        with op.batch_alter_table("invoices", schema=None) as batch:
            batch.drop_column("generated_document_id")

    if insp.has_table("delivery_dockets") and _has_column(
        insp, "delivery_dockets", "generated_document_id"
    ):
        with op.batch_alter_table("delivery_dockets", schema=None) as batch:
            batch.drop_column("generated_document_id")
