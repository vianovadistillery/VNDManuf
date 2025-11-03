"""add_xero_id_to_suppliers

Revision ID: 1647ea8a022a
Revises: 7fe22ea20cea
Create Date: 2025-10-26 20:40:04.167615

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1647ea8a022a"
down_revision: Union[str, None] = "7fe22ea20cea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add xero_id column to suppliers table
    op.add_column(
        "suppliers", sa.Column("xero_id", sa.String(length=100), nullable=True)
    )


def downgrade() -> None:
    # Remove xero_id column from suppliers table
    op.drop_column("suppliers", "xero_id")
