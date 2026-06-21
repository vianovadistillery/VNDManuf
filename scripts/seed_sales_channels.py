#!/usr/bin/env python3
"""Seed the Sales Channels table with default channels: ALM, Direct, Shopify."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import SalesChannel

DEFAULT_CHANNELS = [
    {"code": "ALM", "name": "ALM", "description": "ALM sales channel"},
    {"code": "DIRECT", "name": "Direct", "description": "Direct sales"},
    {"code": "SHOPIFY", "name": "Shopify", "description": "Online sales via Shopify"},
]


def seed_sales_channels(db: Session, dry_run: bool = False) -> None:
    """Ensure default sales channels exist (ALM, Direct, Shopify)."""
    print(f"{'[DRY RUN] ' if dry_run else ''}Seeding Sales Channels...")
    created = 0
    for ch in DEFAULT_CHANNELS:
        existing = db.execute(
            select(SalesChannel).where(
                SalesChannel.code == ch["code"], SalesChannel.deleted_at.is_(None)
            )
        ).scalar_one_or_none()
        if existing:
            if not dry_run:
                existing.name = ch["name"]
                existing.description = ch.get("description")
            continue
        print(f"  Creating channel: {ch['code']} - {ch['name']}")
        if not dry_run:
            db.add(
                SalesChannel(
                    code=ch["code"],
                    name=ch["name"],
                    description=ch.get("description"),
                )
            )
            created += 1
    if not dry_run:
        db.commit()
        print(f"[SUCCESS] Sales channels seeded. Created: {created}")
    else:
        print("[DRY RUN] No changes made.")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed default sales channels (ALM, Direct, Shopify)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    args = parser.parse_args()
    db: Session = next(get_db())
    try:
        seed_sales_channels(db, dry_run=args.dry_run)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
