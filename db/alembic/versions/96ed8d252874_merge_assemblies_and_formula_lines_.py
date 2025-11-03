"""merge assemblies and formula lines branches

Revision ID: 96ed8d252874
Revises: rev_assemblies_shopify, 9f6478e8a1dd
Create Date: 2025-10-26 23:09:24.235368

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "96ed8d252874"
down_revision: Union[str, None] = ("rev_assemblies_shopify", "9f6478e8a1dd")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
