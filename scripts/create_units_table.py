#!/usr/bin/env python3
"""Create the units table if it doesn't exist."""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.adapters.db import create_tables


def main():
    """Main entry point."""
    print("Creating all tables (including units)...")
    try:
        create_tables()
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
