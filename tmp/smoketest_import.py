# ruff: noqa: E402
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.adapters.db.models import Base  # noqa: E402
from apps.vndmanuf_sales.services.import_sales_csv import SalesCSVImporter  # noqa: E402


def main():
    engine = create_engine("sqlite:///tmp/sales_smoke.db")
    metadata = Base.metadata
    for table in metadata.tables.values():
        seen = set()
        for index in list(table.indexes):
            if index.name in seen:
                table.indexes.remove(index)
            else:
                seen.add(index.name)
    metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    fixture = Path("apps/vndmanuf_sales/data/sample_sales_orders.csv")
    importer = SalesCSVImporter(session)
    summary = importer.import_file(fixture, allow_create=True)
    session.commit()

    print(
        {
            "orders_inserted": summary.orders_inserted,
            "orders_updated": summary.orders_updated,
            "lines_processed": summary.lines_processed,
            "errors": summary.errors,
        }
    )

    session.close()


if __name__ == "__main__":
    main()
