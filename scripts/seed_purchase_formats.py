#!/usr/bin/env python3
"""Seed the Purchase Formats table with standard format types."""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import PurchaseFormat


def seed_purchase_formats(db: Session, dry_run: bool = False) -> None:
    """Seed the Purchase Formats table with standard formats."""

    formats_data = [
        {
            "code": "IBC",
            "name": "Intermediate Bulk Container",
            "description": "IBC container",
            "is_active": True,
        },
        {"code": "BAG", "name": "Bag", "description": "Bag format", "is_active": True},
        {
            "code": "CARBOY",
            "name": "Carboy",
            "description": "Carboy container",
            "is_active": True,
        },
        {
            "code": "DRUM",
            "name": "Drum",
            "description": "Drum container",
            "is_active": True,
        },
        {"code": "BOX", "name": "Box", "description": "Box format", "is_active": True},
        {
            "code": "BOTTLE",
            "name": "Bottle",
            "description": "Bottle format",
            "is_active": True,
        },
        {"code": "CAN", "name": "Can", "description": "Can format", "is_active": True},
        {
            "code": "PALLET",
            "name": "Pallet",
            "description": "Pallet format",
            "is_active": True,
        },
    ]

    print(f"{'[DRY RUN] ' if dry_run else ''}Seeding Purchase Formats table...")
    created_count = 0
    updated_count = 0

    for format_data in formats_data:
        code = format_data["code"]

        # Check if format already exists
        existing = db.execute(
            select(PurchaseFormat).where(PurchaseFormat.code == code)
        ).scalar_one_or_none()

        if existing:
            print(f"  Updating existing format: {code}")
            if not dry_run:
                existing.name = format_data["name"]
                existing.description = format_data.get("description")
                existing.is_active = format_data.get("is_active", True)
            updated_count += 1
        else:
            print(f"  Creating new format: {code} - {format_data['name']}")
            if not dry_run:
                fmt = PurchaseFormat(
                    code=code,
                    name=format_data["name"],
                    description=format_data.get("description"),
                    is_active=format_data.get("is_active", True),
                )
                db.add(fmt)
            created_count += 1

        if not dry_run:
            db.flush()

    if not dry_run:
        db.commit()
        print("\n[SUCCESS] Purchase Formats table seeded successfully!")
    else:
        print(
            f"\n[DRY RUN] Would create {created_count} formats, update {updated_count} formats"
        )

    print(f"  Created: {created_count}")
    print(f"  Updated: {updated_count}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed the Purchase Formats table")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes",
    )
    args = parser.parse_args()

    db: Session = next(get_db())
    try:
        seed_purchase_formats(db, dry_run=args.dry_run)
    except Exception as e:
        print(f"Error seeding purchase formats: {e}", file=sys.stderr)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
