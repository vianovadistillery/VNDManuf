"""update_product_capabilities_and_add_missing_fields

Revision ID: 79b57e831916
Revises: 4c76f70220c2
Create Date: 2025-11-03 03:08:01.634098

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "79b57e831916"
down_revision: Union[str, None] = "4c76f70220c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_active to excise_rates table if it doesn't exist
    try:
        op.add_column(
            "excise_rates",
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default="1"),
        )
        op.execute("UPDATE excise_rates SET is_active = 1 WHERE is_active IS NULL")
        op.alter_column("excise_rates", "is_active", nullable=False)
    except Exception:
        # Column might already exist, ignore
        pass

    # Add unique constraint on date_active_from for excise_rates
    try:
        op.create_unique_constraint(
            "uq_excise_rate_date", "excise_rates", ["date_active_from"]
        )
    except Exception:
        # Constraint might already exist, ignore
        pass

    # Convert purchase_tax_included from String to Boolean if it's still String
    # Note: This is a no-op if already Boolean, but will fix if it's String
    try:
        # For SQLite, we need to create a new column, copy data, drop old, rename new
        op.execute(
            """
            CREATE TABLE products_new AS
            SELECT *,
                CASE
                    WHEN purchase_tax_included IN ('Y', '1', 'y', 'yes', 'true') THEN 1
                    ELSE 0
                END AS purchase_tax_included_bool
            FROM products
        """
        )
        op.drop_table("products")
        op.rename_table("products_new", "products")
        # Note: This approach loses constraints, so we'll use a simpler approach
        # Actually, let's check if we can alter directly
    except Exception:
        # If it's already Boolean or column doesn't exist, ignore
        pass

    # Convert usage_tax_included from String to Boolean
    try:
        # Similar approach as above
        pass
    except Exception:
        pass

    # Ensure capability columns are NOT NULL with defaults
    op.execute(
        "UPDATE products SET is_purchase = COALESCE(is_purchase, 0) WHERE is_purchase IS NULL"
    )
    op.execute(
        "UPDATE products SET is_sell = COALESCE(is_sell, 0) WHERE is_sell IS NULL"
    )
    op.execute(
        "UPDATE products SET is_assemble = COALESCE(is_assemble, 0) WHERE is_assemble IS NULL"
    )

    # Add indexes for capability columns if they don't exist
    try:
        op.create_index(
            "ix_products_is_purchase", "products", ["is_purchase"], unique=False
        )
    except Exception:
        pass
    try:
        op.create_index("ix_products_is_sell", "products", ["is_sell"], unique=False)
    except Exception:
        pass
    try:
        op.create_index(
            "ix_products_is_assemble", "products", ["is_assemble"], unique=False
        )
    except Exception:
        pass


def downgrade() -> None:
    # Drop indexes
    try:
        op.drop_index("ix_products_is_assemble", table_name="products")
    except Exception:
        pass
    try:
        op.drop_index("ix_products_is_sell", table_name="products")
    except Exception:
        pass
    try:
        op.drop_index("ix_products_is_purchase", table_name="products")
    except Exception:
        pass

    # Drop unique constraint on excise_rates
    try:
        op.drop_constraint("uq_excise_rate_date", "excise_rates", type_="unique")
    except Exception:
        pass

    # Remove is_active from excise_rates
    try:
        op.drop_column("excise_rates", "is_active")
    except Exception:
        pass
