"""add_notes_to_formulas

Revision ID: 421ee5dcec13
Revises: d3b114a15ca4
Create Date: 2025-11-02 08:59:38.388364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '421ee5dcec13'
down_revision: Union[str, None] = 'd3b114a15ca4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notes field to formulas table
    op.add_column('formulas', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove notes field from formulas table
    op.drop_column('formulas', 'notes')
