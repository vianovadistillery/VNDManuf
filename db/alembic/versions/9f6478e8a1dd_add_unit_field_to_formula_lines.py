"""add_unit_field_to_formula_lines

Revision ID: 9f6478e8a1dd
Revises: 59998e0da549
Create Date: 2025-10-26 21:47:53.807174

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f6478e8a1dd"
down_revision: Union[str, None] = "59998e0da549"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unit column to formula_lines table
    try:
        with op.batch_alter_table("formula_lines", schema=None) as batch_op:
            batch_op.add_column(sa.Column("unit", sa.String(length=10), nullable=True))
    except Exception as e:
        print(f"Column may already exist: {e}")


def downgrade() -> None:
    # Remove unit column
    with op.batch_alter_table("formula_lines", schema=None) as batch_op:
        batch_op.drop_column("unit")
