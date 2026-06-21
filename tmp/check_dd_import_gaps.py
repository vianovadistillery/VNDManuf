"""Compare dd_output.csv lines against imported orders in DB."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from contextlib import closing
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.adapters.db import get_session
from app.adapters.db.models import Product, SalesOrder, SalesOrderLine
from apps.vndmanuf_sales.services.import_sales_csv import (
    SalesCSVImporter,
    decode_csv_bytes,
)

CSV_PATH = Path(r"c:\Users\pduxs\Downloads\dd_output.csv")


def main() -> None:
    text = decode_csv_bytes(CSV_PATH.read_bytes())

    with closing(get_session()) as session:
        # Re-import anything still missing
        importer = SalesCSVImporter(session)
        preview = importer.build_import_preview(
            text, allow_create=False, filename=CSV_PATH.name
        )
        existing_refs = {
            o
            for o in session.execute(
                select(SalesOrder.order_ref).where(
                    SalesOrder.deleted_at.is_(None),
                    SalesOrder.order_ref.is_not(None),
                )
            ).scalars()
        }
        missing_keys = [
            g.group_key for g in preview.groups if g.order_ref not in existing_refs
        ]
        if missing_keys:
            summary = importer.import_text_selected(
                text,
                missing_keys,
                allow_create=False,
                create_delivery_docket=True,
            )
            session.commit()
            print(
                f"Re-import: inserted={summary.orders_inserted} errors={len(summary.errors)}"
            )
            if summary.errors:
                for e in summary.errors[:10]:
                    print(f"  {e}")
                if len(summary.errors) > 10:
                    print(f"  ... and {len(summary.errors) - 10} more")

        imported_refs = set(
            session.execute(
                select(SalesOrder.order_ref).where(
                    SalesOrder.deleted_at.is_(None),
                    SalesOrder.order_ref.is_not(None),
                )
            ).scalars()
        )

    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    csv_dockets = sorted(
        {r["docket_number"].strip() for r in rows if r.get("docket_number")}
    )
    missing_dockets = [d for d in csv_dockets if d not in imported_refs]

    line_groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        line_groups[r["docket_number"].strip()].append(r)

    print(
        f"\nCSV dockets: {len(csv_dockets)} | In DB: {len(imported_refs & set(csv_dockets))} | Missing dockets: {len(missing_dockets)}"
    )
    if missing_dockets:
        print("\nMissing dockets:")
        for d in missing_dockets:
            lines = line_groups[d]
            codes = sorted({ln["product_code"] for ln in lines})
            print(f"  {d}: {len(lines)} line(s) products={codes}")

    # Line-level check for imported dockets
    print("\nLine qty check on imported dockets...")
    with closing(get_session()) as session:
        for docket in csv_dockets:
            if docket not in imported_refs:
                continue
            order = session.execute(
                select(SalesOrder).where(
                    SalesOrder.order_ref == docket,
                    SalesOrder.deleted_at.is_(None),
                )
            ).scalar_one_or_none()
            if not order:
                continue
            csv_lines = line_groups[docket]
            db_lines = session.execute(
                select(SalesOrderLine, Product.sku)
                .join(Product, Product.id == SalesOrderLine.product_id)
                .where(
                    SalesOrderLine.order_id == order.id,
                    SalesOrderLine.deleted_at.is_(None),
                )
            ).all()
            csv_by_code = defaultdict(lambda: Decimal("0"))
            for ln in csv_lines:
                csv_by_code[ln["product_code"].strip()] += Decimal(
                    ln["delivered_qty"] or "0"
                )
            db_by_code = defaultdict(lambda: Decimal("0"))
            for line, sku in db_lines:
                db_by_code[sku] += line.qty
            if csv_by_code != db_by_code:
                print(
                    f"  MISMATCH {docket}: csv={dict(csv_by_code)} db={dict(db_by_code)}"
                )


if __name__ == "__main__":
    main()
