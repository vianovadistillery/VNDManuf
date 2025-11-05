"""add_usage_quantity_and_update_cost_precision

Revision ID: c3805f609e81
Revises: 212104c7dfa8
Create Date: 2025-11-05 12:31:25.099591
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3805f609e81"
down_revision: Union[str, None] = "212104c7dfa8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Step 1 (safe on SQLite): add usage_quantity only if missing.
    Step 2 (deferred): precision changes will be done in a separate migration
    that recreates the table with explicit types for every column (to avoid
    NullType reflection issues on SQLite).
    """
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_cols = {col["name"] for col in insp.get_columns("products")}

    if "usage_quantity" not in existing_cols:
        op.add_column(
            "products",
            sa.Column(
                "usage_quantity", sa.Numeric(precision=10, scale=3), nullable=True
            ),
        )

    # Precision changes intentionally deferred; see comment above.


def downgrade() -> None:
    """Revert: drop usage_quantity if it exists."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_cols = {col["name"] for col in insp.get_columns("products")}

    if "usage_quantity" in existing_cols:
        op.drop_column("products", "usage_quantity")
