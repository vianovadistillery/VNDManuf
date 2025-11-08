"""CSV importer for sales orders and lines."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.db.models import Product
from apps.vndmanuf_sales.models import (
    Customer,
    CustomerSite,
    SalesChannel,
    SalesOrder,
    SalesOrderLine,
    SalesOrderSource,
    SalesOrderStatus,
)
from apps.vndmanuf_sales.services.pricing import PriceResolution, PricingService
from apps.vndmanuf_sales.services.totals import TotalsService

REQUIRED_COLUMNS = {
    "order_date",
    "channel",
    "customer",
    "product_code",
    "qty",
}


def _normalize_code(value: str) -> str:
    return value.strip().upper().replace(" ", "_")


def _decimal(value: str) -> Decimal:
    if value is None or value == "":
        return Decimal("0")
    return Decimal(str(value))


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.strip())


@dataclass
class ImportRow:
    raw: Dict[str, str]
    order_date: datetime
    channel: str
    customer: str
    site_name: Optional[str]
    product_code: str
    qty: Decimal
    unit_price_ex_gst: Optional[Decimal]
    unit_price_inc_gst: Optional[Decimal]
    order_ref: Optional[str]
    notes: Optional[str]


@dataclass
class ImportSummary:
    orders_inserted: int = 0
    orders_updated: int = 0
    lines_processed: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class SalesCSVImporter:
    """Import sales orders from a CSV file."""

    def __init__(self, db: Session):
        self.db = db
        self.pricing = PricingService(db)
        self.totals = TotalsService(db)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def import_file(
        self,
        file_path: Path | str,
        *,
        allow_create: bool = False,
        pricebook_id: Optional[str] = None,
    ) -> ImportSummary:
        rows = list(self._parse_csv(file_path))
        return self.import_rows(
            rows,
            allow_create=allow_create,
            pricebook_id=pricebook_id,
        )

    def import_rows(
        self,
        rows: Iterable[ImportRow],
        *,
        allow_create: bool = False,
        pricebook_id: Optional[str] = None,
    ) -> ImportSummary:
        grouped = self._group_rows(rows)
        summary = ImportSummary()

        for key, order_rows in grouped.items():
            order_date, customer_name, order_ref = key
            try:
                with self.db.begin_nested():
                    order, created = self._get_or_create_order(
                        order_date=order_date,
                        customer_name=customer_name,
                        order_ref=order_ref,
                        allow_create=allow_create,
                        channel_name=order_rows[0].channel,
                        site_name=order_rows[0].site_name,
                    )
                    if created:
                        summary.orders_inserted += 1
                    else:
                        summary.orders_updated += 1
                        order.lines.clear()

                    for row in order_rows:
                        product = self._lookup_product(row.product_code)
                        resolution = self._resolve_price(
                            product_id=product.id,
                            row=row,
                            pricebook_id=pricebook_id,
                            customer_id=order.customer_id,
                        )

                        line_totals = self.totals.compute_line_totals(
                            qty=row.qty,
                            unit_price_ex_gst=resolution.unit_price_ex_gst,
                            unit_price_inc_gst=resolution.unit_price_inc_gst,
                        )

                        order.lines.append(
                            SalesOrderLine(
                                product_id=product.id,
                                qty=row.qty,
                                uom="unit",
                                unit_price_ex_gst=resolution.unit_price_ex_gst,
                                unit_price_inc_gst=resolution.unit_price_inc_gst,
                                discount_ex_gst=line_totals.discount_ex_gst,
                                line_total_ex_gst=line_totals.line_total_ex_gst,
                                line_total_inc_gst=line_totals.line_total_inc_gst,
                                sequence=len(order.lines) + 1,
                                tax_rate=resolution.gst_rate,
                            )
                        )
                        summary.lines_processed += 1

                    order.notes = order_rows[0].notes or order.notes
                    order.pricebook_id = pricebook_id
                    self.totals.refresh_order_totals(order)

            except Exception as exc:  # noqa: BLE001
                self.db.rollback()
                summary.errors.append(
                    f"Order {order_ref or '<no-ref>'} on {order_date.date()} failed: {exc}"
                )

        return summary

    # ------------------------------------------------------------------ #
    # Parsing helpers
    # ------------------------------------------------------------------ #
    def _parse_csv(self, file_path: Path | str) -> Iterable[ImportRow]:
        path = Path(file_path)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"Missing required columns: {', '.join(missing)}")

            for raw in reader:
                try:
                    yield ImportRow(
                        raw=raw,
                        order_date=_parse_date(raw["order_date"]),
                        channel=raw.get("channel", "").strip(),
                        customer=raw.get("customer", "").strip(),
                        site_name=raw.get("site_name") or None,
                        product_code=raw.get("product_code", "").strip(),
                        qty=_decimal(raw.get("qty")),
                        unit_price_ex_gst=_decimal(raw["unit_price_ex_gst"])
                        if raw.get("unit_price_ex_gst")
                        else None,
                        unit_price_inc_gst=_decimal(raw["unit_price_inc_gst"])
                        if raw.get("unit_price_inc_gst")
                        else None,
                        order_ref=raw.get("order_ref") or None,
                        notes=raw.get("notes") or None,
                    )
                except Exception as exc:  # noqa: BLE001
                    raise ValueError(f"Failed to parse row {raw}: {exc}") from exc

    def _group_rows(
        self, rows: Iterable[ImportRow]
    ) -> Dict[Tuple[datetime, str, Optional[str]], List[ImportRow]]:
        grouped: Dict[Tuple[datetime, str, Optional[str]], List[ImportRow]] = {}
        for row in rows:
            key = (row.order_date, row.customer, row.order_ref)
            grouped.setdefault(key, []).append(row)
        return grouped

    # ------------------------------------------------------------------ #
    # Domain helpers
    # ------------------------------------------------------------------ #
    def _get_or_create_order(
        self,
        *,
        order_date: datetime,
        customer_name: str,
        order_ref: Optional[str],
        allow_create: bool,
        channel_name: str,
        site_name: Optional[str],
    ) -> Tuple[SalesOrder, bool]:
        customer = self._get_or_create_customer(
            customer_name, allow_create=allow_create
        )
        channel = self._get_or_create_channel(channel_name, allow_create=allow_create)
        site = None
        if site_name:
            site = self._get_or_create_site(
                customer, site_name, allow_create=allow_create
            )

        existing = self._find_existing_order(customer.id, order_date, order_ref)
        if existing:
            existing.channel_id = channel.id
            existing.customer_site_id = site.id if site else None
            existing.status = SalesOrderStatus.CONFIRMED.value
            existing.source = SalesOrderSource.IMPORTED.value
            existing.order_date = order_date
            return existing, False

        order = SalesOrder(
            customer_id=customer.id,
            channel_id=channel.id,
            customer_site_id=site.id if site else None,
            order_ref=order_ref,
            status=SalesOrderStatus.CONFIRMED.value,
            source=SalesOrderSource.IMPORTED.value,
            order_date=order_date,
        )
        self.db.add(order)
        return order, True

    def _find_existing_order(
        self,
        customer_id: str,
        order_date: datetime,
        order_ref: Optional[str],
    ) -> Optional[SalesOrder]:
        if not order_ref:
            return None
        stmt = (
            select(SalesOrder)
            .where(
                SalesOrder.customer_id == customer_id,
                func.date(SalesOrder.order_date) == order_date.date(),
                SalesOrder.order_ref == order_ref,
                SalesOrder.deleted_at.is_(None),
            )
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def _lookup_product(self, product_code: str) -> Product:
        stmt = select(Product).where(
            func.lower(Product.sku) == product_code.lower(),
            Product.deleted_at.is_(None),
        )
        product = self.db.execute(stmt).scalar_one_or_none()
        if not product:
            stmt = select(Product).where(
                func.lower(Product.name) == product_code.lower(),
                Product.deleted_at.is_(None),
            )
            product = self.db.execute(stmt).scalar_one_or_none()
        if not product:
            raise ValueError(f"Product with code '{product_code}' not found")
        return product

    def _resolve_price(
        self,
        *,
        product_id: str,
        row: ImportRow,
        pricebook_id: Optional[str],
        customer_id: Optional[str],
    ) -> PriceResolution:
        if row.unit_price_ex_gst or row.unit_price_inc_gst:
            ex_price = row.unit_price_ex_gst
            inc_price = row.unit_price_inc_gst
            if not inc_price or not ex_price:
                ex_price, inc_price = self.pricing.compute_inc_gst(
                    unit_price_ex_gst=ex_price,
                    unit_price_inc_gst=inc_price,
                )
            return PriceResolution(
                unit_price_ex_gst=ex_price,
                unit_price_inc_gst=inc_price,
                gst_rate=self.pricing.default_gst_rate,
                source="csv_override",
            )

        return self.pricing.resolve_price(
            product_id,
            order_date=row.order_date.date(),
            pricebook_id=pricebook_id,
            customer_id=customer_id,
        )

    def _get_or_create_channel(self, name: str, *, allow_create: bool) -> SalesChannel:
        code = _normalize_code(name or "UNKNOWN")
        channel = self.db.execute(
            select(SalesChannel).where(
                func.lower(SalesChannel.code) == code.lower(),
                SalesChannel.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if channel:
            return channel
        if not allow_create:
            raise ValueError(
                f"Sales channel '{name}' does not exist (set --allow-create)"
            )
        channel = SalesChannel(code=code, name=name or code.title())
        self.db.add(channel)
        self.db.flush()
        return channel

    def _get_or_create_customer(self, name: str, *, allow_create: bool) -> Customer:
        stmt = select(Customer).where(
            func.lower(Customer.name) == name.lower(),
            Customer.deleted_at.is_(None),
        )
        customer = self.db.execute(stmt).scalar_one_or_none()
        if customer:
            return customer
        if not allow_create:
            raise ValueError(f"Customer '{name}' does not exist (set --allow-create)")
        code = _normalize_code(name)
        customer = Customer(code=code, name=name)
        self.db.add(customer)
        self.db.flush()
        return customer

    def _get_or_create_site(
        self,
        customer: Customer,
        site_name: str,
        *,
        allow_create: bool,
    ) -> CustomerSite:
        stmt = select(CustomerSite).where(
            CustomerSite.customer_id == customer.id,
            func.lower(CustomerSite.site_name) == site_name.lower(),
            CustomerSite.deleted_at.is_(None),
        )
        site = self.db.execute(stmt).scalar_one_or_none()
        if site:
            return site
        if not allow_create:
            raise ValueError(
                f"Site '{site_name}' for customer '{customer.name}' does not exist (set --allow-create)"
            )
        site = CustomerSite(
            customer_id=customer.id,
            site_name=site_name,
            state="UNKNOWN",
        )
        self.db.add(site)
        self.db.flush()
        return site
