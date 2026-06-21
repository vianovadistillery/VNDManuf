"""Merge heads: 20250223_alm and 20250223_cust_ord.

Revision ID: 20250223_merge
Revises: 20250223_alm, 20250223_cust_ord
Create Date: 2025-02-23

After this, 'alembic upgrade head' will work without specifying a branch.
"""

from __future__ import annotations

from typing import Sequence, Union

revision: str = "20250223_merge"
down_revision: Union[str, None] = ("20250223_alm", "20250223_cust_ord")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
