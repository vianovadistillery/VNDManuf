# scripts/db_reset.py
"""Database reset script for development."""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.adapters.db.session import create_tables, drop_tables
from app.settings import settings


def reset_database():
    """Drop and recreate all database tables."""
    print("Resetting development database...")

    # Check if we're in development mode
    if not settings.debug:
        print("ERROR: This script should only be run in development mode!")
        print("Set debug=True in settings or use a development database URL.")
        sys.exit(1)

    # Check if we're using SQLite (safer for development)
    if not settings.database_url.startswith("sqlite"):
        print("WARNING: You are about to reset a non-SQLite database!")
        print(f"Database URL: {settings.database_url}")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Operation cancelled.")
            sys.exit(0)

    try:
        # Drop all tables
        print("Dropping all tables...")
        drop_tables()

        # Create all tables
        print("Creating all tables...")
        create_tables()

        print("[SUCCESS] Database reset completed successfully!")
        print(f"Database URL: {settings.database_url}")

    except Exception as e:
        print(f"[ERROR] Error resetting database: {e}")
        sys.exit(1)


def show_status():
    """Show database status."""
    print("Database Status:")
    print(f"URL: {settings.database_url}")
    print(f"Debug mode: {settings.debug}")

    # Check if database file exists (for SQLite)
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"Database file exists: {db_path} ({size} bytes)")
        else:
            print(f"Database file does not exist: {db_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        show_status()
    else:
        reset_database()
