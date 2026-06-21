#!/usr/bin/env python
"""Import sales orders from CSV (standard sales or delivery docket format)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.adapters.db import get_session  # noqa: E402
from apps.vndmanuf_sales.services.import_sales_csv import (  # noqa: E402
    ImportFormat,
    SalesCSVImporter,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import sales orders from CSV (sales or delivery docket layout)."
    )
    parser.add_argument("csv_path", type=Path, help="Path to CSV file")
    parser.add_argument(
        "--allow-create",
        action="store_true",
        help="Create missing customers, sites, and channels",
    )
    parser.add_argument(
        "--format",
        choices=[ImportFormat.SALES.value, ImportFormat.DOCKET.value],
        default=None,
        help="Force CSV format (auto-detected from headers by default)",
    )
    parser.add_argument(
        "--no-delivery-docket",
        action="store_true",
        help="For docket CSV: create sales order only, skip delivery docket record",
    )
    parser.add_argument(
        "--pricebook-id",
        default=None,
        help="Optional pricebook UUID for unresolved prices",
    )
    args = parser.parse_args()

    if not args.csv_path.is_file():
        print(f"File not found: {args.csv_path}", file=sys.stderr)
        return 1

    session = get_session()
    try:
        importer = SalesCSVImporter(session)
        summary = importer.import_file(
            args.csv_path,
            allow_create=args.allow_create,
            pricebook_id=args.pricebook_id,
            import_format=args.format,
            create_delivery_docket=not args.no_delivery_docket,
        )
        session.commit()
        print(json.dumps(summary.to_dict(), indent=2))
        return 1 if summary.errors else 0
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
