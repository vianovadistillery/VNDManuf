#!/usr/bin/env python3
"""Count rows in the products table."""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import Product


def count_products(db: Session) -> int:
    """Count the number of rows in the products table."""
    result = db.execute(select(func.count(Product.id)))
    return result.scalar() or 0


def main():
    """Main entry point."""
    db: Session = next(get_db())
    try:
        count = count_products(db)
        print(f"Products table row count: {count}")
        return count
    except Exception as e:
        print(f"Error counting products: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
