"""Import historic DD CSV after mappings are seeded."""

from __future__ import annotations

import sys
from contextlib import closing
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.adapters.db import get_session
from apps.vndmanuf_sales.services.import_sales_csv import (
    SalesCSVImporter,
    decode_csv_bytes,
)


def main() -> None:
    csv_path = Path(r"c:\Users\pduxs\Downloads\dd_output.csv")
    text = decode_csv_bytes(csv_path.read_bytes())

    with closing(get_session()) as session:
        importer = SalesCSVImporter(session)
        preview = importer.build_import_preview(
            text, allow_create=False, filename=csv_path.name
        )
        if preview.errors:
            print("Preview errors:", preview.errors)
            return
        keys = [g.group_key for g in preview.groups]
        print(f"Importing {len(keys)} dockets from {csv_path.name}...")
        for g in preview.groups:
            print(f"  {g.order_ref}: {g.flags}")
        summary = importer.import_text_selected(
            text,
            keys,
            allow_create=False,
            create_delivery_docket=True,
        )
        session.commit()

    print(
        f"\nInserted: {summary.orders_inserted} | Updated: {summary.orders_updated} | "
        f"Dockets: {summary.dockets_created} | Lines: {summary.lines_processed}"
    )
    if summary.errors:
        print("Errors:")
        for err in summary.errors:
            print(f"  {err}")
    else:
        print("No errors.")


if __name__ == "__main__":
    main()
