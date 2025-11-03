"""add_batch_yield_fields

Revision ID: 262c7cd34fdd
Revises: 96ed8d252874
Create Date: 2025-10-26 23:14:10.503294

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "262c7cd34fdd"
down_revision: Union[str, None] = "96ed8d252874"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add actual production result fields to batch
    op.add_column(
        "batches", sa.Column("yield_actual", sa.Numeric(12, 3), nullable=True)
    )
    op.add_column(
        "batches", sa.Column("yield_litres", sa.Numeric(12, 3), nullable=True)
    )
    op.add_column(
        "batches", sa.Column("variance_percent", sa.Numeric(5, 2), nullable=True)
    )


def downgrade() -> None:
    # Remove actual production result fields from batch
    op.drop_column("batches", "variance_percent")
    op.drop_column("batches", "yield_litres")
    op.drop_column("batches", "yield_actual")
