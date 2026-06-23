from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.db import Base
from app.adapters.db.models import (
    Customer,
    CustomerSite,
    DeliveryDocket,
    InventoryLot,
    Pricebook,
    PricebookItem,
    Product,
    SalesChannel,
    SalesOrder,
    SalesOrderLine,
)
from apps.vndmanuf_sales.models import SalesOrderSource, SalesOrderStatus
from apps.vndmanuf_sales.services.analytics import (
    SalesAnalyticsService,
    current_financial_year_period,
    current_month_period,
    last_month_period,
    last_quarter_period,
    previous_financial_year_period,
)
from apps.vndmanuf_sales.services.customer_mapping import (
    CustomerMappingService,
    names_refer_to_same_entity,
)
from apps.vndmanuf_sales.services.import_sales_csv import (
    ImportFormat,
    ImportRow,
    SalesCSVImporter,
    decode_csv_bytes,
    detect_csv_format,
)
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


def test_period_presets_use_australian_financial_year():
    as_of = date(2026, 6, 23)
    fy_start, fy_end = current_financial_year_period(as_of)
    assert fy_start == date(2025, 7, 1)
    assert fy_end == as_of

    prev_start, prev_end = previous_financial_year_period(as_of)
    assert prev_start == date(2024, 7, 1)
    assert prev_end == date(2025, 6, 30)

    lm_start, lm_end = last_month_period(as_of)
    assert lm_start == date(2026, 5, 1)
    assert lm_end == date(2026, 5, 31)

    cm_start, cm_end = current_month_period(as_of)
    assert cm_start == date(2026, 6, 1)
    assert cm_end == as_of

    lq_start, lq_end = last_quarter_period(as_of)
    assert lq_start == date(2026, 1, 1)
    assert lq_end == date(2026, 3, 31)


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


def test_analytics_overview_and_products(db_session: Session):
    product = create_product(db_session, sku="NNC", name="Nova Nectar")
    customer = create_customer(db_session)
    channel = create_channel(db_session)
    pricebook = create_pricebook_with_item(db_session, product)

    order = SalesOrder(
        customer_id=customer.id,
        channel_id=channel.id,
        pricebook_id=pricebook.id,
        order_ref="SO-AN-1",
        order_date=datetime(2025, 2, 10),
        status="confirmed",
        source="manual",
        total_ex_gst=Decimal("400.00"),
        total_inc_gst=Decimal("440.00"),
    )
    db_session.add(order)
    db_session.flush()
    db_session.add(
        SalesOrderLine(
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
    )
    db_session.add(
        InventoryLot(
            product_id=product.id,
            lot_code="LOT-AN",
            quantity_kg=Decimal("50"),
        )
    )
    db_session.commit()

    svc = SalesAnalyticsService(db_session)
    overview = svc.get_overview(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
    )
    assert overview.total_orders == 1
    assert overview.revenue_inc_gst == Decimal("440.00")
    assert len(overview.top_skus) == 1
    assert overview.top_skus[0]["SKU"] == "NNC"

    products = svc.get_products_sold(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
    )
    assert len(products.rows) == 1
    assert products.rows[0].sku == "NNC"
    assert products.total_units == Decimal("10")
    assert products.total_revenue_inc_gst == Decimal("440.00")


def test_customer_import_alias_maps_csv_name(db_session: Session):
    canonical = create_customer(db_session, "Bannockburn Cellarbrations")
    product = create_product(db_session)
    create_channel(db_session, "RETAIL")
    CustomerMappingService(db_session).add_alias(
        "Cellarbrations at Bannockburn",
        str(canonical.id),
    )
    db_session.commit()

    importer = SalesCSVImporter(db_session)
    rows = [
        ImportRow(
            raw={},
            order_date=datetime(2025, 2, 7),
            channel="RETAIL",
            customer="Cellarbrations at Bannockburn",
            site_name=None,
            product_code=product.sku,
            qty=Decimal("2"),
            unit_price_ex_gst=Decimal("40.00"),
            unit_price_inc_gst=Decimal("44.00"),
            order_ref="PO-ALIAS",
        )
    ]

    summary = importer.import_rows(rows, allow_create=False)
    db_session.commit()

    assert not summary.errors
    order = db_session.execute(
        select(SalesOrder).where(SalesOrder.order_ref == "PO-ALIAS")
    ).scalar_one()
    assert order.customer_id == canonical.id
    assert order.customer.name == "Bannockburn Cellarbrations"


def test_customer_import_alias_normalizes_whitespace_and_case(db_session: Session):
    canonical = create_customer(db_session, "Nardi Cellars")
    CustomerMappingService(db_session).add_alias("  nardi  cellars ", str(canonical.id))
    db_session.commit()

    resolved = CustomerMappingService(db_session).resolve_customer("NARDI   Cellars")
    assert resolved is not None
    assert resolved.id == canonical.id


def test_names_refer_to_same_entity_reorders_words():
    assert names_refer_to_same_entity(
        "Bannockburn Cellarbrations", "Cellarbrations Bannockburn"
    )
    assert names_refer_to_same_entity("Piano Bar", "Piano Bar Geelong")


def test_docket_import_omits_unknown_site_instead_of_failing(db_session: Session):
    nsc = create_product(db_session, sku="NSC", name="Nova Suncrush Carton")
    create_channel(db_session, "DIRECT")
    customer = create_customer(db_session, "Cellarbrations Bannockburn")
    CustomerMappingService(db_session).add_alias(
        "Bannockburn Cellarbrations",
        str(customer.id),
    )
    db_session.commit()

    csv_text = """docket_number,delivery_date,order_date,customer,site_name,channel,product_code,delivered_qty
DD250116,2025-11-18,2025-11-18,Bannockburn Cellarbrations,Bannockburn Cellarbrations,DIRECT,NSC,2
"""
    importer = SalesCSVImporter(db_session)
    summary = importer.import_text(
        csv_text, allow_create=False, create_delivery_docket=True
    )
    db_session.commit()

    assert not summary.errors
    assert summary.orders_inserted == 1
    order = db_session.execute(
        select(SalesOrder).where(SalesOrder.order_ref == "DD250116")
    ).scalar_one()
    assert order.customer_id == customer.id
    assert order.customer_site_id is None


def test_site_alias_allows_site_match(db_session: Session):
    nsc = create_product(db_session, sku="NSC", name="Nova Suncrush Carton")
    create_channel(db_session, "DIRECT")
    customer = create_customer(db_session, "Cellarbrations at Foxxy's Daylesford")
    CustomerMappingService(db_session).add_site_alias(
        "CBN AT FOXXYS DAYLESFORD X",
        str(customer.id),
        "Foxxy's Daylesford",
    )
    site = CustomerSite(
        customer_id=customer.id,
        site_name="Foxxy's Daylesford",
        state="VIC",
    )
    db_session.add(site)
    db_session.commit()

    csv_text = """docket_number,delivery_date,order_date,customer,site_name,channel,product_code,delivered_qty
DD250118,2025-11-18,2025-11-18,Cellarbrations at Foxxy's Daylesford,CBN AT FOXXYS DAYLESFORD X,DIRECT,NSC,2
"""
    importer = SalesCSVImporter(db_session)
    summary = importer.import_text(
        csv_text, allow_create=False, create_delivery_docket=True
    )
    db_session.commit()

    assert not summary.errors
    order = db_session.execute(
        select(SalesOrder).where(SalesOrder.order_ref == "DD250118")
    ).scalar_one()
    assert order.customer_site_id == site.id


def test_build_import_preview_applies_customer_mapping(db_session: Session):
    create_product(db_session)
    create_channel(db_session, "RETAIL")
    canonical = create_customer(db_session, "Bannockburn Cellarbrations")
    CustomerMappingService(db_session).add_alias(
        "Cellarbrations at Bannockburn",
        str(canonical.id),
    )
    db_session.commit()

    csv_text = (
        "order_date,channel,customer,site_name,product_code,qty,order_ref\n"
        "2025-02-07,RETAIL,Cellarbrations at Bannockburn,,SKU-1,2,PO-MAP\n"
    )
    preview = SalesCSVImporter(db_session).build_import_preview(
        csv_text, allow_create=False, filename="test.csv"
    )
    assert not preview.errors
    assert len(preview.groups) == 1
    group = preview.groups[0]
    assert group.customer_mapped
    assert group.customer_resolved == "Bannockburn Cellarbrations"
    assert group.include_by_default


def test_build_import_preview_flags_db_duplicate(db_session: Session):
    create_product(db_session)
    customer = create_customer(db_session, "Acme Retail")
    channel = create_channel(db_session, "RETAIL")
    order = SalesOrder(
        customer_id=customer.id,
        channel_id=channel.id,
        order_ref="PO-DUP",
        status=SalesOrderStatus.CONFIRMED.value,
        source=SalesOrderSource.IMPORTED.value,
        order_date=datetime(2025, 2, 7),
    )
    db_session.add(order)
    db_session.commit()

    csv_text = (
        "order_date,channel,customer,site_name,product_code,qty,order_ref\n"
        "2025-02-07,RETAIL,Acme Retail,,SKU-1,2,PO-DUP\n"
    )
    preview = SalesCSVImporter(db_session).build_import_preview(
        csv_text, allow_create=False, filename="test.csv"
    )
    assert preview.groups[0].duplicate_in_db
    assert not preview.groups[0].include_by_default


def test_import_text_selected_imports_only_chosen_groups(db_session: Session):
    product = create_product(db_session)
    create_channel(db_session, "RETAIL")
    create_customer(db_session, "Customer A")
    create_customer(db_session, "Customer B")
    db_session.commit()

    csv_text = (
        "order_date,channel,customer,site_name,product_code,qty,order_ref\n"
        "2025-02-07,RETAIL,Customer A,,SKU-1,1,PO-A\n"
        "2025-02-07,RETAIL,Customer B,,SKU-1,2,PO-B\n"
    )
    importer = SalesCSVImporter(db_session)
    preview = importer.build_import_preview(csv_text, allow_create=False)
    selected = [preview.groups[0].group_key]
    summary = importer.import_text_selected(csv_text, selected, allow_create=False)
    db_session.commit()

    assert summary.orders_inserted == 1
    assert summary.lines_processed == 1
    orders = db_session.execute(select(SalesOrder)).scalars().all()
    assert len(orders) == 1
    assert orders[0].order_ref == "PO-A"


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


def test_detect_csv_format():
    assert (
        detect_csv_format(["order_date", "channel", "customer", "product_code", "qty"])
        == ImportFormat.SALES
    )
    assert (
        detect_csv_format(
            [
                "docket_number",
                "delivery_date",
                "customer",
                "product_code",
                "delivered_qty",
            ]
        )
        == ImportFormat.DOCKET
    )


def test_decode_csv_bytes_handles_utf8_and_cp1252():
    assert (
        decode_csv_bytes("order_date,customer\n".encode("utf-8-sig"))
        == "order_date,customer\n"
    )
    assert decode_csv_bytes("customer\n".encode("cp1252")) == "customer\n"
    # Byte 0x9c is valid in cp1252 (œ) but invalid UTF-8 start byte.
    assert decode_csv_bytes(b"desc,\x9c\n") == "desc,œ\n"


def test_docket_csv_importer_creates_order_and_docket(db_session: Session):
    nsc = create_product(db_session, sku="NSC", name="Nova Suncrush Carton")
    npc = create_product(db_session, sku="NPC", name="Nova Paloma Carton")
    create_channel(db_session, "DIRECT")

    csv_text = """docket_number,delivery_date,order_date,customer,attention,site_name,site_suburb,site_state,site_postcode,channel,po_number,product_code,description,ordered_qty,delivered_qty,unit
DD250116,2025-11-18,2025-11-18,Bannockburn Cellarbrations,Michael Smith,Bannockburn Cellarbrations,Bannockburn,VIC,3331,DIRECT,BY PHONE,NSC,Nova Suncrush Carton (16 x 330mL),2,2,EA
DD250116,2025-11-18,2025-11-18,Bannockburn Cellarbrations,Michael Smith,Bannockburn Cellarbrations,Bannockburn,VIC,3331,DIRECT,BY PHONE,NPC,Nova Paloma Carton (16 x 330mL),2,2,EA
"""
    importer = SalesCSVImporter(db_session)
    summary = importer.import_text(
        csv_text, allow_create=True, create_delivery_docket=True
    )
    db_session.commit()

    assert not summary.errors
    assert summary.format == ImportFormat.DOCKET.value
    assert summary.orders_inserted == 1
    assert summary.dockets_created == 1
    assert summary.lines_processed == 2

    order = db_session.execute(
        select(SalesOrder).where(SalesOrder.order_ref == "DD250116")
    ).scalar_one()
    assert order.po_number == "BY PHONE"
    assert order.customer.name == "Bannockburn Cellarbrations"
    assert len(order.lines) == 2

    docket = db_session.execute(
        select(DeliveryDocket).where(DeliveryDocket.docket_number == "DD250116")
    ).scalar_one()
    assert docket.sales_order_id == order.id
    assert len(docket.lines) == 2
    assert {line.product_id for line in docket.lines} == {nsc.id, npc.id}
