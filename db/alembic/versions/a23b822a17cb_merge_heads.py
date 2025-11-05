"""merge heads

Revision ID: a23b822a17cb
Revises: 0651e10f5ac8, c3805f609e81
Create Date: 2025-11-05 12:40:03.539243

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "a23b822a17cb"
down_revision: Union[str, None] = ("0651e10f5ac8", "c3805f609e81")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
