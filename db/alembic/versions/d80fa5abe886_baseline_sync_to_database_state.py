"""baseline_sync_to_database_state

Revision ID: d80fa5abe886
Revises:
Create Date: 2025-01-03 21:00:00.000000

This migration represents a baseline sync to the current database state.
The database schema already exists (48 tables) from previous migrations.

This migration:
1. Sets alembic_version to this revision (baseline)
2. Is idempotent - safe to run on existing database
3. Documents the current schema state per docs/snapshot/

After this migration, all future migrations will build from this baseline.

Database state at baseline:
- 48 tables
- 3 previously applied migrations (now superseded by this baseline)
- Schema documented in docs/snapshot/db_schema.json
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d80fa5abe886"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Baseline migration - database already has all tables.

    This migration is idempotent:
    - If alembic_version table exists, update it to this revision
    - If alembic_version table doesn't exist, create it and set this revision
    - All tables already exist, so no CREATE TABLE statements needed

    Future migrations will build incrementally from this baseline.
    """
    # Get connection
    conn = op.get_bind()

    # Check if alembic_version table exists
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "alembic_version" in tables:
        # Update to this revision (clear any previous state)
        op.execute("DELETE FROM alembic_version")
        op.execute("INSERT INTO alembic_version (version_num) VALUES ('d80fa5abe886')")
    else:
        # Create alembic_version table and set this revision
        op.create_table(
            "alembic_version",
            sa.Column("version_num", sa.String(length=32), nullable=False),
            sa.PrimaryKeyConstraint("version_num"),
        )
        op.execute("INSERT INTO alembic_version (version_num) VALUES ('d80fa5abe886')")

    # Note: All other tables already exist in the database.
    # See docs/snapshot/db_schema.json for complete schema documentation.
    # Future migrations will use autogenerate from SQLAlchemy models.


def downgrade() -> None:
    """
    Downgrade would drop all tables, but we preserve data.

    In practice, we don't downgrade from baseline.
    If needed, restore from backup.
    """
    # Remove alembic version tracking
    op.execute("DELETE FROM alembic_version")
    # Note: We do NOT drop tables in downgrade to preserve data.
    # To fully reset, use db_reset.py script instead.
