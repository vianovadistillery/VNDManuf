"""merge heads: core + vndmanuf_sales

Revision ID: 57d6b07b57d0
Revises: 2f0c52f5af1d, ae5d77380b60
Create Date: 2025-11-09 00:27:50.602792

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "57d6b07b57d0"
down_revision: Union[str, None] = ("2f0c52f5af1d", "ae5d77380b60")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
