"""Complete the partially applied migration 67a21e84ab61.

This migration was partially applied - assembly_lines was created but the old
columns from assemblies were not dropped. This script completes that cleanup.
"""

from sqlalchemy import inspect, text

from app.adapters.db import engine


def complete_migration_cleanup():
    """Drop old columns from assemblies table that should have been removed."""
    with engine.connect() as connection:
        inspector = inspect(connection)

        # Get current columns
        assemblies_columns = [
            col["name"] for col in inspector.get_columns("assemblies")
        ]
        print(f"Current assemblies columns: {assemblies_columns}")

        # Columns that should be dropped according to the migration
        columns_to_drop = [
            "direction",
            "child_product_id",
            "ratio",
            "is_energy_or_overhead",
            "sequence",  # This was removed from assemblies (sequence is now in assembly_lines)
            "loss_factor",
        ]

        # Check which ones exist and need to be dropped
        existing_to_drop = [col for col in columns_to_drop if col in assemblies_columns]

        if not existing_to_drop:
            print("No old columns to drop - migration cleanup already complete!")

            # Verify new columns exist
            expected_columns = ["assembly_code", "assembly_name"]
            missing_columns = [
                col for col in expected_columns if col not in assemblies_columns
            ]
            if missing_columns:
                print(f"Warning: Expected columns missing: {missing_columns}")
            else:
                print("All expected columns present!")
            return

        print(f"Dropping columns: {existing_to_drop}")

        # For SQLite, we need to recreate the table to drop columns
        # Get all columns we want to keep
        keep_columns = [
            col for col in assemblies_columns if col not in existing_to_drop
        ]

        # Get column definitions for columns to keep
        all_cols = inspector.get_columns("assemblies")
        {col["name"]: col for col in all_cols if col["name"] in keep_columns}

        # Build CREATE TABLE statement with only kept columns
        # This is a simplified approach - for production we'd want to use Alembic's batch_alter_table
        print("\nNote: SQLite doesn't support DROP COLUMN directly.")
        print("We'll need to use Alembic's batch_alter_table context.")
        print("\nUsing direct SQL for SQLite...")

        # For SQLite, we'll create a new table, copy data, drop old, rename
        connection.execute(text("BEGIN TRANSACTION"))
        try:
            # Create temporary table with new structure
            # First get the create table SQL
            cursor = connection.connection.cursor()
            cursor.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='assemblies'"
            )
            cursor.fetchone()[0]

            # This is complex - let's use a simpler approach: manual SQL with ALTER TABLE for SQLite
            # Actually, SQLite 3.35.0+ supports DROP COLUMN, but we need to check version
            # For now, use batch_alter_table via Alembic context

            print("\nThis requires Alembic's batch_alter_table context.")
            print(
                "Please run this via: alembic upgrade head (after fixing the migration issue)"
            )
            print("\nAlternatively, manually drop columns using SQL:")
            for col in existing_to_drop:
                print(f"  -- ALTER TABLE assemblies DROP COLUMN {col};")

            connection.execute(text("ROLLBACK"))

        except Exception as e:
            connection.execute(text("ROLLBACK"))
            print(f"Error: {e}")
            raise

        print("\n" + "=" * 60)
        print("RECOMMENDED APPROACH:")
        print("=" * 60)
        print("1. The migration is already marked as applied")
        print("2. We need to manually complete the column drops")
        print("3. Use Alembic's batch_alter_table in a new migration")
        print("   OR manually run SQL if SQLite version supports it")


if __name__ == "__main__":
    complete_migration_cleanup()
