"""Add archiving fields to products and formulas

Revision ID: add_archiving_fields
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "add_archiving_fields"
down_revision = "421ee5dcec13"  # Latest revision: add_notes_to_formulas
branch_labels = None
depends_on = None


def upgrade():
    """Add archiving fields to products and formulas tables."""
    # Add archiving fields to products table
    with op.batch_alter_table("products", schema=None) as batch_op:
        # Check if columns exist first (for idempotency)
        connection = op.get_bind()
        inspector = sa.inspect(connection)
        columns = [col["name"] for col in inspector.get_columns("products")]

        if "is_archived" not in columns:
            batch_op.add_column(
                sa.Column(
                    "is_archived", sa.Boolean(), nullable=False, server_default="0"
                )
            )
        if "archived_at" not in columns:
            batch_op.add_column(sa.Column("archived_at", sa.DateTime(), nullable=True))

    # Add archiving fields to formulas table
    with op.batch_alter_table("formulas", schema=None) as batch_op:
        connection = op.get_bind()
        inspector = sa.inspect(connection)
        columns = [col["name"] for col in inspector.get_columns("formulas")]

        if "is_archived" not in columns:
            batch_op.add_column(
                sa.Column(
                    "is_archived", sa.Boolean(), nullable=False, server_default="0"
                )
            )
        if "archived_at" not in columns:
            batch_op.add_column(sa.Column("archived_at", sa.DateTime(), nullable=True))


def downgrade():
    """Remove archiving fields from products and formulas tables."""
    with op.batch_alter_table("formulas", schema=None) as batch_op:
        batch_op.drop_column("archived_at")
        batch_op.drop_column("is_archived")

    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("archived_at")
        batch_op.drop_column("is_archived")
