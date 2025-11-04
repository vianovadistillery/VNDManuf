"""merge all heads

Revision ID: c9bc3efd8b86
Revises: 7b36008a8a95, fix_all_constraints_001, fix_products_pk
Create Date: 2025-11-04 10:34:36.238624

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "c9bc3efd8b86"
down_revision: Union[str, None] = (
    "7b36008a8a95",
    "fix_all_constraints_001",
    "fix_products_pk",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
