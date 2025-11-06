"""add_yield_factor_to_formulas

Revision ID: 3ffe25d38c5c
Revises: 8e02f8410816
Create Date: 2025-11-06 14:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3ffe25d38c5c"
down_revision: Union[str, None] = "8e02f8410816"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_column(insp, table, col):
    """Helper to check if column exists."""
    return any(c["name"] == col for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)

    # Add yield_factor column to formulas table
    # SQLite supports adding nullable columns directly without recreating the table
    if not has_column(insp, "formulas", "yield_factor"):
        if bind.dialect.name == "sqlite":
            # For SQLite, we can add the column directly since it's nullable with a default
            op.add_column(
                "formulas",
                sa.Column(
                    "yield_factor",
                    sa.Numeric(10, 4),
                    nullable=True,
                    server_default="1.0",
                ),
            )
        else:
            # For other databases, use batch mode if needed
            with op.batch_alter_table("formulas", recreate="always") as batch_op:
                batch_op.add_column(
                    sa.Column(
                        "yield_factor",
                        sa.Numeric(10, 4),
                        nullable=True,
                        server_default="1.0",
                    )
                )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Remove yield_factor column from formulas table
    if has_column(insp, "formulas", "yield_factor"):
        if bind.dialect.name == "sqlite":
            # SQLite doesn't support dropping columns directly, need to recreate
            with op.batch_alter_table("formulas", recreate="always") as batch_op:
                batch_op.drop_column("yield_factor")
        else:
            op.drop_column("formulas", "yield_factor")
