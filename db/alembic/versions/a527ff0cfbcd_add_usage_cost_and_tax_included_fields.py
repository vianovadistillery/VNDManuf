"""add_usage_cost_and_tax_included_fields

Revision ID: a527ff0cfbcd
Revises: bf78b64511f2
Create Date: 2025-11-02 16:39:13.787079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a527ff0cfbcd'
down_revision: Union[str, None] = 'bf78b64511f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add purchase tax included flag
    op.add_column('products', sa.Column('purchase_tax_included', sa.String(length=1), nullable=True))
    
    # Add usage cost fields (inc GST, ex GST, tax included)
    op.add_column('products', sa.Column('usage_cost_inc_gst', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('products', sa.Column('usage_cost_ex_gst', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('products', sa.Column('usage_tax_included', sa.String(length=1), nullable=True))


def downgrade() -> None:
    # Remove usage cost fields
    op.drop_column('products', 'usage_tax_included')
    op.drop_column('products', 'usage_cost_ex_gst')
    op.drop_column('products', 'usage_cost_inc_gst')
    
    # Remove purchase tax included flag
    op.drop_column('products', 'purchase_tax_included')
