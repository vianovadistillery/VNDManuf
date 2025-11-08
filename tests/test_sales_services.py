from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.db import Base
from app.adapters.db.models import (
    Customer,
    InventoryLot,
    Pricebook,
    PricebookItem,
    Product,
    SalesChannel,
    SalesOrder,
    SalesOrderLine,
)
from apps.vndmanuf_sales.services.import_sales_csv import ImportRow, SalesCSVImporter
from apps.vndmanuf_sales.services.pricing import PricingService
from apps.vndmanuf_sales.services.totals import TotalsService


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    _dedupe_indexes(Base.metadata)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def _dedupe_indexes(metadata):
    for table in metadata.tables.values():
        seen = set()
        for index in list(table.indexes):
            if index.name in seen:
                table.indexes.remove(index)
            else:
                seen.add(index.name)


def create_product(
    session: Session, sku: str = "SKU-1", name: str = "Sample Product"
) -> Product:
    product = Product(
        sku=sku,
        name=name,
        product_type="FINISHED",
        retail_price_ex_gst=Decimal("40.00"),
        retail_price_inc_gst=Decimal("44.00"),
    )
    session.add(product)
    session.commit()
    return product


def create_customer(session: Session, name: str = "Acme Retail") -> Customer:
    customer = Customer(code=name.upper().replace(" ", "-"), name=name)
    session.add(customer)
    session.commit()
    return customer


def create_channel(session: Session, code: str = "RETAIL") -> SalesChannel:
    channel = SalesChannel(code=code, name=code.title())
    session.add(channel)
    session.commit()
    return channel


def create_pricebook_with_item(session: Session, product: Product) -> Pricebook:
    pricebook = Pricebook(
        name="Default 2025",
        currency="AUD",
        active_from=date(2025, 1, 1),
    )
    session.add(pricebook)
    session.flush()

    item = PricebookItem(
        pricebook_id=pricebook.id,
        product_id=product.id,
        unit_price_ex_gst=Decimal("38.00"),
        unit_price_inc_gst=Decimal("41.80"),
    )
    session.add(item)
    session.commit()
    return pricebook


def test_pricing_resolves_from_pricebook(db_session: Session):
    product = create_product(db_session)
    customer = create_customer(db_session)
    pricebook = create_pricebook_with_item(db_session, product)

    service = PricingService(db_session)
    result = service.resolve_price(
        product_id=product.id,
        order_date=date(2025, 2, 1),
        pricebook_id=pricebook.id,
        customer_id=customer.id,
    )

    assert result.unit_price_ex_gst == Decimal("38.00")
    assert result.unit_price_inc_gst == Decimal("41.80")
    assert result.source == "pricebook_item"


def test_totals_refreshes_order(db_session: Session):
    product = create_product(db_session)
    customer = create_customer(db_session)
    channel = create_channel(db_session)

    order = SalesOrder(
        customer_id=customer.id,
        channel_id=channel.id,
        order_ref="SO-123",
        order_date=datetime(2025, 2, 5),
        status="confirmed",
        source="manual",
    )
    db_session.add(order)
    db_session.flush()

    line = SalesOrderLine(
        order_id=order.id,
        product_id=product.id,
        qty=Decimal("10"),
        uom="unit",
        unit_price_ex_gst=Decimal("40.00"),
        unit_price_inc_gst=Decimal("44.00"),
        line_total_ex_gst=Decimal("400.00"),
        line_total_inc_gst=Decimal("440.00"),
        sequence=1,
    )
    db_session.add(line)
    db_session.commit()

    totals = TotalsService(db_session).refresh_order_totals(order)

    assert totals.total_ex_gst == Decimal("400.00")
    assert totals.total_inc_gst == Decimal("440.00")
    assert order.total_inc_gst == Decimal("440.00")


def test_totals_product_sales_snapshot(db_session: Session):
    product = create_product(db_session)
    customer = create_customer(db_session)
    channel = create_channel(db_session)

    order = SalesOrder(
        customer_id=customer.id,
        channel_id=channel.id,
        order_ref="SO-001",
        order_date=datetime(2025, 2, 1),
        status="confirmed",
        source="imported",
    )
    db_session.add(order)
    db_session.flush()

    db_session.add(
        SalesOrderLine(
            order_id=order.id,
            product_id=product.id,
            qty=Decimal("5"),
            uom="unit",
            unit_price_ex_gst=Decimal("38.00"),
            unit_price_inc_gst=Decimal("41.80"),
            line_total_ex_gst=Decimal("190.00"),
            line_total_inc_gst=Decimal("209.00"),
            sequence=1,
        )
    )

    db_session.add(
        InventoryLot(
            product_id=product.id,
            lot_code="LOT-1",
            quantity_kg=Decimal("120"),
        )
    )
    db_session.commit()

    snapshots = TotalsService(db_session).product_sales_with_inventory()
    assert len(snapshots) == 1
    snapshot = snapshots[0]
    assert snapshot.product_id == product.id
    assert snapshot.qty_sold == Decimal("5")
    assert snapshot.inventory_qty == Decimal("120")


def test_csv_importer_creates_orders(db_session: Session):
    product = create_product(db_session)
    create_channel(db_session, "RETAIL")
    importer = SalesCSVImporter(db_session)

    rows = [
        ImportRow(
            raw={},
            order_date=datetime(2025, 2, 7),
            channel="RETAIL",
            customer="Nardi Cellars",
            site_name="Geelong",
            product_code=product.sku,
            qty=Decimal("2"),
            unit_price_ex_gst=Decimal("40.00"),
            unit_price_inc_gst=Decimal("44.00"),
            order_ref="PO123",
            notes="Intro deal",
        )
    ]

    summary = importer.import_rows(rows, allow_create=True)
    db_session.commit()

    assert not summary.errors
    order = db_session.execute(
        select(SalesOrder).where(SalesOrder.order_ref == "PO123")
    ).scalar_one()
    assert order.customer.name == "Nardi Cellars"
    assert len(order.lines) == 1
    assert order.total_inc_gst == Decimal("88.00")
