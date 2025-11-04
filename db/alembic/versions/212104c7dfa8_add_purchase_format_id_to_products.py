"""add_purchase_format_id_to_products

Revision ID: 212104c7dfa8
Revises: e0d13df96836
Create Date: 2025-11-04 15:08:10.342813

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "212104c7dfa8"
down_revision: Union[str, None] = "e0d13df96836"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add purchase_format_id and purchase_quantity columns."""
    # Use direct column operations instead of batch_alter_table to avoid type inference issues
    # Add new columns
    op.add_column(
        "products", sa.Column("purchase_format_id", sa.String(length=36), nullable=True)
    )
    op.add_column(
        "products",
        sa.Column(
            "purchase_quantity", sa.Numeric(precision=10, scale=3), nullable=True
        ),
    )

    # Note: We don't remove deprecated columns here to avoid data loss.
    # They can be removed in a separate migration after data migration if needed.


def downgrade() -> None:
    """Remove purchase_format_id and purchase_quantity columns."""
    op.drop_column("products", "purchase_quantity")
    op.drop_column("products", "purchase_format_id")
