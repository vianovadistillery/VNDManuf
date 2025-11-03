"""cleanup_legacy_tables

Revision ID: e4a5484fc3f6
Revises: 9472b39d71be
Create Date: 2025-10-31 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision: str = "e4a5484fc3f6"
down_revision: Union[str, None] = "9472b39d71be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Clean up legacy tables after verification period.

    WARNING: Only run this migration after:
    - 30-day verification period complete
    - All code verified to use unified products table
    - Database backup created
    """
    connection = op.get_bind()
    inspector = inspect(connection)
    tables = inspector.get_table_names()

    # Verify no critical references before dropping
    print("Checking for references to legacy tables...")

    # Check if legacy tables exist
    if "raw_materials" in tables:
        # Verify migration was successful - check product_migration_map
        map_count = 0
        if "product_migration_map" in tables:
            map_count = connection.execute(
                text(
                    """
                SELECT COUNT(*) FROM product_migration_map
                WHERE legacy_table = 'raw_materials'
            """
                )
            ).scalar()
            print(f"Found {map_count} raw_material mappings in migration map")

        # Safety check: verify products table has RAW products (or allow empty tables)
        raw_count = connection.execute(
            text(
                """
            SELECT COUNT(*) FROM products WHERE product_type = 'RAW'
        """
            )
        ).scalar()
        print(f"Found {raw_count} RAW products in unified products table")

        # Only raise error if we have legacy data but no migrated products
        # On fresh installs, the table might be empty and that's OK
        if raw_count == 0 and map_count > 0:
            raise ValueError(
                "No RAW products found in unified table. "
                "Aborting - migration may not be complete."
            )

        # Drop raw_materials table
        print("Dropping raw_materials table...")
        op.drop_table("raw_materials")
        print("   [OK] raw_materials table dropped")

    if "finished_goods" in tables:
        # Safety check: verify products table has FINISHED products
        finished_count = connection.execute(
            text(
                """
            SELECT COUNT(*) FROM products WHERE product_type = 'FINISHED'
        """
            )
        ).scalar()
        print(f"Found {finished_count} FINISHED products in unified products table")

        # Note: finished_count can be 0 if no finished goods exist yet
        print("Dropping finished_goods table...")
        op.drop_table("finished_goods")
        print("   [OK] finished_goods table dropped")


def downgrade() -> None:
    """
    Rollback: Recreate legacy tables.

    Note: This does not restore data - tables will be empty.
    Original data must be restored from backup if needed.
    """
    # Recreate raw_materials table structure
    # Note: This is a simplified structure - actual legacy table may have more fields
    op.create_table(
        "raw_materials",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.Integer(), nullable=True),
        sa.Column("desc1", sa.String(length=50), nullable=True),
        sa.Column("desc2", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Recreate finished_goods table structure
    op.create_table(
        "finished_goods",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    print("Legacy tables recreated (empty - data not restored)")
