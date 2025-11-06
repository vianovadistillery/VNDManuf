"""add_work_areas_table

Revision ID: 8e02f8410816
Revises: fde4c825d571
Create Date: 2025-11-06 14:43:09.291068

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8e02f8410816"
down_revision: Union[str, None] = "fde4c825d571"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_table(insp, table_name):
    """Helper to check if table exists."""
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)

    # Create work_areas table
    if not has_table(insp, "work_areas"):
        op.create_table(
            "work_areas",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("code", sa.String(length=20), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(length=36), nullable=True),
            sa.Column("version", sa.Integer(), nullable=True, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(length=36), nullable=True),
            sa.Column("previous_version_id", sa.String(length=36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(length=36), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_work_area_code", "work_areas", ["code"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Drop work_areas table
    if has_table(insp, "work_areas"):
        op.drop_index("ix_work_area_code", table_name="work_areas")
        op.drop_table("work_areas")
