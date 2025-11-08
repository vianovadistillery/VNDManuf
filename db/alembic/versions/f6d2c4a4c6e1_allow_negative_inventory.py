"""Add per-product allow negative inventory flag.

Revision ID: f6d2c4a4c6e1
Revises: rev_assemblies_shopify
Create Date: 2025-11-08
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6d2c4a4c6e1"
down_revision = "d5e11b38c91a"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)
    columns = [col["name"] for col in insp.get_columns("products")]

    if "allow_negative_inventory" in columns:
        return

    if bind.dialect.name == "sqlite":
        op.execute(
            sa.text(
                "ALTER TABLE products "
                "ADD COLUMN allow_negative_inventory INTEGER NOT NULL DEFAULT 1"
            )
        )
    else:
        op.add_column(
            "products",
            sa.Column(
                "allow_negative_inventory",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)
    columns = [col["name"] for col in insp.get_columns("products")]

    if "allow_negative_inventory" not in columns:
        return

    if bind.dialect.name == "sqlite":
        # Downgrading (dropping the column) would require full table recreation.
        # Skipping for SQLite to avoid data loss; documented no-op.
        return

    op.drop_column("products", "allow_negative_inventory")
