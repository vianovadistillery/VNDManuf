"""Run sync document generation for a delivery docket or sales order (quote).
Usage:
  python scripts/run_sync_generate_delivery_docket.py [delivery_docket_id]
  python scripts/run_sync_generate_delivery_docket.py --quote <sales_order_id>
  If no ID given, uses first delivery docket, else first sales order, or creates a test docket.
"""

import sys
from pathlib import Path

# Project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.adapters.db import get_session
from app.adapters.db.models import (
    Customer,
    DeliveryDocket,
    DeliveryDocketLine,
    Product,
    SalesOrder,
)
from app.documents.service import DocumentGenerationService


def ensure_template():
    template_path = (
        Path(__file__).resolve().parent.parent / "templates" / "delivery_docket.docx"
    )
    if not template_path.exists():
        from scripts.create_delivery_docket_template import main as create_template

        create_template()


def get_or_create_test_docket(session):
    """Return (delivery_docket_id, doc_number) or (None, None) if table missing. Creates minimal docket if none exist."""
    try:
        existing = session.execute(select(DeliveryDocket).limit(1)).scalars().first()
    except Exception:
        return None, None
    if existing:
        return str(existing.id), existing.docket_number

    customer_id = (
        session.execute(select(Customer.id).where(Customer.is_active).limit(1))
        .scalars()
        .first()
    )
    product_id = session.execute(select(Product.id).limit(1)).scalars().first()
    if not product_id:
        return None, None
    if not customer_id:
        # Create minimal test customer via raw SQL (schema may lack contact_name, billing_*, etc.)
        import uuid
        from datetime import datetime, timezone

        from sqlalchemy import text

        now = datetime.now(timezone.utc).isoformat()
        uid = str(uuid.uuid4())
        session.execute(
            text(
                "INSERT INTO customers (id, code, name, customer_type, is_active, created_at, updated_at, version) "
                "VALUES (:id, :code, :name, :ct, 1, :now, :now, 1)"
            ),
            {
                "id": uid,
                "code": "TEST-CUST-001",
                "name": "Test Customer (Delivery Docket)",
                "ct": "other",
                "now": now,
            },
        )
        session.commit()
        customer_id = uid

    from datetime import datetime
    from decimal import Decimal

    docket = DeliveryDocket(
        customer_id=customer_id,
        docket_number=f"DD-TEST-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
        docket_date=datetime.utcnow(),
        status="DRAFT",
        notes="Test delivery docket for PDF generation",
    )
    session.add(docket)
    session.flush()
    line = DeliveryDocketLine(
        docket_id=docket.id,
        product_id=product_id,
        quantity=Decimal("1"),
        uom="unit",
        sequence=1,
    )
    session.add(line)
    session.commit()
    return str(docket.id), docket.docket_number


def get_first_sales_order(session):
    """Return (sales_order_id, doc_number) for first sales order (id-only to avoid schema drift)."""
    from sqlalchemy import text

    row = session.execute(
        text("SELECT id, order_ref FROM sales_orders LIMIT 1")
    ).first()
    if not row:
        return None, None
    return str(row[0]), (row[1] or str(row[0]))


def main():
    ensure_template()
    session = get_session()
    try:
        use_quote = len(sys.argv) >= 2 and sys.argv[1] == "--quote"
        arg = sys.argv[2] if use_quote else (sys.argv[1] if len(sys.argv) > 1 else None)

        delivery_docket_id = None
        quote_id = None
        doc_number = "doc"

        if use_quote and arg:
            order = session.get(SalesOrder, arg)
            if not order:
                print(f"SalesOrder not found: {arg}")
                sys.exit(1)
            quote_id = arg
            doc_number = order.order_ref or str(order.id)
        elif arg:
            docket = session.get(DeliveryDocket, arg)
            if not docket:
                print(f"DeliveryDocket not found: {arg}")
                sys.exit(1)
            delivery_docket_id = arg
            doc_number = docket.docket_number
        else:
            docket_id, doc_number = get_or_create_test_docket(session)
            if docket_id:
                delivery_docket_id = docket_id
                session = get_session()
            else:
                quote_id, doc_number = get_first_sales_order(session)
                if not quote_id:
                    print(
                        "No delivery docket or sales order in DB. Add a customer, product, and run again (script will create a test docket), or pass delivery_docket_id / --quote sales_order_id."
                    )
                    sys.exit(1)

        svc = DocumentGenerationService(session)
        doc_record, pdf_path, docx_path, err = svc.generate(
            template_name="delivery_docket.docx",
            doc_type="delivery_docket",
            doc_number=doc_number,
            delivery_docket_id=delivery_docket_id,
            quote_id=quote_id,
        )
        if err:
            print("Generation failed:", err)
            if doc_record:
                print(
                    "Document record id:", doc_record.id, "status:", doc_record.status
                )
            sys.exit(1)
        print("Generated:", doc_record.id)
        print("PDF:", pdf_path)
        if docx_path:
            print("DOCX:", docx_path)
        print(
            "Download via API: GET /api/v1/documents/{}/download".format(doc_record.id)
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()
