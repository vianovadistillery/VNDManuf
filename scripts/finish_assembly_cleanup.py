"""Finish the cleanup from migration 67a21e84ab61.

The migration was partially applied - assembly_lines exists but old columns
in assemblies were not dropped. This script completes that cleanup.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

# Use the database from alembic.ini or default
db_path = project_root / "tpmanuf.db"
engine = create_engine(f"sqlite:///{db_path}")


def complete_cleanup():
    """Complete the assembly migration cleanup."""
    with engine.connect() as connection:
        # Clean up any leftover temporary tables from failed migrations
        cursor = connection.connection.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE '_alembic_tmp_%'
        """
        )
        temp_tables = cursor.fetchall()
        for table in temp_tables:
            print(f"[INFO] Cleaning up temporary table: {table[0]}")
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
        connection.commit()

        inspector = inspect(connection)

        # Get current columns
        assemblies_columns = [
            col["name"] for col in inspector.get_columns("assemblies")
        ]
        print(f"Current assemblies columns ({len(assemblies_columns)}):")
        for col in assemblies_columns:
            print(f"  - {col}")

        # Columns that should be dropped
        columns_to_drop = [
            "direction",
            "child_product_id",
            "ratio",
            "is_energy_or_overhead",
            "sequence",  # Removed from assemblies (now in assembly_lines)
            "loss_factor",
        ]

        existing_to_drop = [col for col in columns_to_drop if col in assemblies_columns]

        if not existing_to_drop:
            print("\n[OK] No old columns to drop - cleanup already complete!")

            # Verify new columns exist
            expected_columns = ["assembly_code", "assembly_name"]
            missing_columns = [
                col for col in expected_columns if col not in assemblies_columns
            ]
            if missing_columns:
                print(f"[WARN] Warning: Expected columns missing: {missing_columns}")
            else:
                print("[OK] All expected columns present!")
            return

        print(f"\n[INFO] Columns to drop: {existing_to_drop}")

        # First, drop any indexes on columns we're about to drop
        indexes = inspector.get_indexes("assemblies")
        indexes_to_drop = []
        for idx in indexes:
            # Check if index references any column we're dropping
            # Index column names are in idx.get('column_names', [])
            if hasattr(idx, "column_names"):
                (
                    idx.column_names
                    if isinstance(idx.column_names, list)
                    else [idx.column_names]
                )
            else:
                # For SQLite, column info might be in a different format
                idx_sql = cursor.execute(
                    f"SELECT sql FROM sqlite_master WHERE type='index' AND name='{idx['name']}'"
                ).fetchone()
                if idx_sql and idx_sql[0]:
                    # Parse the CREATE INDEX SQL to find column names
                    sql = idx_sql[0].upper()
                    for col in existing_to_drop:
                        if col.upper() in sql:
                            indexes_to_drop.append(idx["name"])
                            break

        # Also check by querying sqlite_master directly
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='assemblies' AND sql LIKE '%child_product_id%'
        """
        )
        for row in cursor.fetchall():
            if (
                row[0] not in indexes_to_drop
                and row[0] != "sqlite_autoindex_assemblies_1"
            ):
                indexes_to_drop.append(row[0])

        for col in existing_to_drop:
            cursor.execute(
                f"""
                SELECT name FROM sqlite_master
                WHERE type='index' AND tbl_name='assemblies' AND sql LIKE '%{col}%'
            """
            )
            for row in cursor.fetchall():
                if row[0] not in indexes_to_drop and not row[0].startswith(
                    "sqlite_autoindex"
                ):
                    indexes_to_drop.append(row[0])

        if indexes_to_drop:
            print(
                f"\n[INFO] Dropping indexes on columns to be removed: {indexes_to_drop}"
            )
            for idx_name in indexes_to_drop:
                print(f"  Dropping index {idx_name}...")
                cursor.execute(f"DROP INDEX IF EXISTS {idx_name}")
            connection.commit()

        # Use Alembic's batch_alter_table for SQLite
        context = MigrationContext.configure(connection)
        op = Operations(context)

        print("\n[INFO] Dropping old columns...")
        with op.batch_alter_table("assemblies") as batch_op:
            for col in existing_to_drop:
                print(f"  Dropping {col}...")
                batch_op.drop_column(col)

        # Verify new columns exist and add if missing
        assemblies_columns_after = [
            col["name"] for col in inspector.get_columns("assemblies")
        ]
        expected_columns = ["assembly_code", "assembly_name"]
        missing_columns = [
            col for col in expected_columns if col not in assemblies_columns_after
        ]

        if missing_columns:
            print(f"\n[WARN] Adding missing columns: {missing_columns}")
            import sqlalchemy as sa

            with op.batch_alter_table("assemblies") as batch_op:
                for col in missing_columns:
                    print(f"  Adding {col}...")
                    if col == "assembly_code":
                        batch_op.add_column(
                            sa.Column(
                                "assembly_code", sa.String(length=50), nullable=True
                            )
                        )
                    elif col == "assembly_name":
                        batch_op.add_column(
                            sa.Column(
                                "assembly_name", sa.String(length=200), nullable=True
                            )
                        )

            # Set defaults for existing rows
            connection.execute(
                text(
                    """
                UPDATE assemblies
                SET assembly_code = COALESCE(assembly_code, 'MIGRATED-1'),
                    assembly_name = COALESCE(assembly_name, 'Migrated Assembly')
                WHERE assembly_code IS NULL OR assembly_code = ''
                   OR assembly_name IS NULL OR assembly_name = ''
            """
                )
            )
            connection.commit()

            # Make them NOT NULL
            with op.batch_alter_table("assemblies") as batch_op:
                batch_op.alter_column("assembly_code", nullable=False)
                batch_op.alter_column("assembly_name", nullable=False)

        print("\n[OK] Cleanup complete!")

        # Show final state
        final_columns = [col["name"] for col in inspector.get_columns("assemblies")]
        print(f"\nFinal assemblies columns ({len(final_columns)}):")
        for col in final_columns:
            print(f"  - {col}")


if __name__ == "__main__":
    try:
        complete_cleanup()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
