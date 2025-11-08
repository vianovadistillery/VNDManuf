from __future__ import annotations

import argparse
import json
from pathlib import Path

from apps.competitor_intel.app.services.db import session_scope
from apps.competitor_intel.app.services.ingest_csv import SKUImporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import SKU master data for Competitor Intel"
    )
    parser.add_argument("csv", type=Path, help="Path to skus.csv file")
    parser.add_argument(
        "--allow-create",
        action="store_true",
        help="Allow creation of brands/products/package specs that do not yet exist",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path: Path = args.csv
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    with session_scope() as session:
        importer = SKUImporter(session, allow_create=args.allow_create)
        report = importer.run(csv_path)
        session.commit()
    print(json.dumps(report.to_dict(), indent=2))


if __name__ == "__main__":
    main()
