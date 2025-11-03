"""add_units_and_purchase_fields

Revision ID: 93795fe8208b
Revises: 5809474d8078
Create Date: 2025-11-01 08:49:32.028234

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "93795fe8208b"
down_revision: Union[str, None] = "5809474d8078"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add purchase_unit_id column to products table
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("purchase_unit_id", sa.String(36), nullable=True))
        # Note: SQLite doesn't support adding foreign keys via ALTER TABLE
        # The relationship is enforced by SQLAlchemy at the ORM level
        # For PostgreSQL, we would use: batch_op.create_foreign_key('fk_products_purchase_unit_id', 'units', ['purchase_unit_id'], ['id'])


def downgrade() -> None:
    # Remove column (SQLite doesn't support dropping foreign key constraints)
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("purchase_unit_id")
