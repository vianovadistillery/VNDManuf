"""Merge heads: 20250223_cust_contact and 20250223_ord_del_inv.

Revision ID: 20250223_merge2
Revises: 20250223_cust_contact, 20250223_ord_del_inv
Create Date: 2025-02-23

After this, 'alembic upgrade head' works with a single head.
"""

from __future__ import annotations

from typing import Sequence, Union

revision: str = "20250223_merge2"
down_revision: Union[str, None] = ("20250223_cust_contact", "20250223_ord_del_inv")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
