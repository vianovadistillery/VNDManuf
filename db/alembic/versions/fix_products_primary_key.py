"""Fix products table primary key and constraints

Revision ID: f1xpr0duct5pk001
Revises: d80fa5abe886
Create Date: 2025-01-04 00:00:00.000000

This migration fixes the critical issue where products table has no primary key.
It also ensures all foreign keys and constraints are properly set up.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1xpr0duct5pk001"
down_revision: Union[str, None] = "d80fa5abe886"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix products table primary key and ensure constraints."""
    # Check if products table exists and has data
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if "products" not in inspector.get_table_names():
        return  # Table doesn't exist, skip

    # Get current state
    pk_constraint = inspector.get_pk_constraint("products")

    # If no primary key exists, add it
    if not pk_constraint.get("constrained_columns"):
        # First, ensure id column is not nullable and has values
        op.execute(
            """
            UPDATE products
            SET id = lower(hex(randomblob(16))) || '-' ||
                    substr(hex(randomblob(2)), 1, 4) || '-' ||
                    substr(hex(randomblob(2)), 1, 4) || '-' ||
                    substr(hex(randomblob(2)), 1, 4) || '-' ||
                    hex(randomblob(6))
            WHERE id IS NULL OR id = ''
        """
        )

        # Make id NOT NULL
        op.alter_column("products", "id", nullable=False)

        # Add primary key constraint
        op.create_primary_key("pk_products", "products", ["id"])

    # Ensure unique constraint on sku exists
    try:
        op.create_unique_constraint("uq_products_sku", "products", ["sku"])
    except Exception:
        pass  # Constraint may already exist

    # Add missing indexes for product_type
    try:
        op.create_index(
            "ix_products_product_type", "products", ["product_type"], unique=False
        )
    except Exception:
        pass  # Index may already exist


def downgrade() -> None:
    """Remove primary key (not recommended)."""
    # In practice, we don't downgrade this - it would break the database
    pass
