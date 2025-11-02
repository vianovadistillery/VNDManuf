"""add_purchase_volume_to_products

Revision ID: d3b114a15ca4
Revises: 93795fe8208b
Create Date: 2025-11-01 12:19:32.222813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3b114a15ca4'
down_revision: Union[str, None] = '93795fe8208b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add purchase_volume column to products table
    # Use batch mode for SQLite compatibility
    try:
        with op.batch_alter_table('products', schema=None) as batch_op:
            batch_op.add_column(sa.Column('purchase_volume', sa.Numeric(12, 3), nullable=True))
    except Exception:
        # Column might already exist, ignore
        pass


def downgrade() -> None:
    # Remove purchase_volume column
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('purchase_volume')
