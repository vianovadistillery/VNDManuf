"""merge_excise_and_product_updates

Revision ID: 7b36008a8a95
Revises: 67a21e84ab61, 79b57e831916
Create Date: 2025-11-03 16:25:09.709287

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "7b36008a8a95"
down_revision: Union[str, None] = ("67a21e84ab61", "79b57e831916")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
