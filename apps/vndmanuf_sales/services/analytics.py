"""Sales analytics queries for overview and products dashboards."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.db.models import InventoryLot, Product
from apps.vndmanuf_sales.models import (
    Customer,
    Pricebook,
    SalesChannel,
    SalesOrder,
    SalesOrderLine,
    SalesOrderStatus,
)
from apps.vndmanuf_sales.services.totals import _dec, _quantize

Money = Decimal


def default_period() -> tuple[date, date]:
    end = date.today()
    start = end - timedelta(days=90)
    return start, end


def _as_datetime_start(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time())


def _as_datetime_end(d: date) -> datetime:
    return datetime.combine(d, datetime.max.time())


@dataclass
class OverviewMetrics:
    total_orders: int
    revenue_inc_gst: Money
    average_order_value: Money
    repeat_rate_pct: float
    new_customers: int
    repeat_customers: int
    inactive_customers: int
    trend: List[dict] = field(default_factory=list)
    top_skus: List[dict] = field(default_factory=list)
    top_customers: List[dict] = field(default_factory=list)


@dataclass
class ProductSalesRow:
    product_id: str
    sku: str
    name: str
    units: Decimal
    revenue_ex_gst: Money
    revenue_inc_gst: Money
    inventory_qty: Decimal
    channel_mix: str
    first_sale_in_period: bool


@dataclass
class ProductSalesSummary:
    rows: List[ProductSalesRow]
    total_units: Decimal
    total_revenue_inc_gst: Money
    total_revenue_ex_gst: Money


class SalesAnalyticsService:
    """Aggregate sales metrics for dashboards."""

    def __init__(self, db: Session):
        self.db = db

    def _base_order_filters(
        self,
        *,
        start_date: date,
        end_date: date,
        channel_id: Optional[str] = None,
        pricebook_id: Optional[str] = None,
    ):
        filters = [
            SalesOrder.deleted_at.is_(None),
            SalesOrder.archived_at.is_(None),
            SalesOrder.status != SalesOrderStatus.CANCELLED.value,
            SalesOrder.order_date >= _as_datetime_start(start_date),
            SalesOrder.order_date <= _as_datetime_end(end_date),
        ]
        if channel_id:
            filters.append(SalesOrder.channel_id == channel_id)
        if pricebook_id:
            filters.append(SalesOrder.pricebook_id == pricebook_id)
        return filters

    def get_overview(
        self,
        *,
        start_date: date,
        end_date: date,
        channel_id: Optional[str] = None,
        pricebook_id: Optional[str] = None,
    ) -> OverviewMetrics:
        filters = self._base_order_filters(
            start_date=start_date,
            end_date=end_date,
            channel_id=channel_id,
            pricebook_id=pricebook_id,
        )

        orders = self.db.execute(select(SalesOrder).where(*filters)).scalars().all()
        total_orders = len(orders)
        revenue_inc = sum(_dec(o.total_inc_gst) for o in orders)
        revenue_inc = _quantize(revenue_inc)
        avg_order = (
            _quantize(revenue_inc / total_orders) if total_orders else Decimal("0")
        )

        customer_ids = {o.customer_id for o in orders}
        repeat_customers = 0
        new_customers = 0
        period_start_dt = _as_datetime_start(start_date)

        for cid in customer_ids:
            first_ever = self.db.execute(
                select(func.min(SalesOrder.order_date)).where(
                    SalesOrder.customer_id == cid,
                    SalesOrder.deleted_at.is_(None),
                    SalesOrder.status != SalesOrderStatus.CANCELLED.value,
                )
            ).scalar_one()
            order_count_in_period = sum(1 for o in orders if o.customer_id == cid)
            if first_ever and first_ever >= period_start_dt:
                new_customers += 1
            elif order_count_in_period > 1:
                repeat_customers += 1
            elif (
                order_count_in_period == 1
                and first_ever
                and first_ever < period_start_dt
            ):
                repeat_customers += 1

        unique_customers = len(customer_ids)
        repeat_rate = (
            round(float(repeat_customers) / unique_customers * 100, 1)
            if unique_customers
            else 0.0
        )

        prior_customers = set(
            self.db.execute(
                select(SalesOrder.customer_id).where(
                    SalesOrder.deleted_at.is_(None),
                    SalesOrder.status != SalesOrderStatus.CANCELLED.value,
                    SalesOrder.order_date < period_start_dt,
                )
            ).scalars()
        )
        inactive_customers = len(prior_customers - customer_ids)

        trend_rows = self.db.execute(
            select(
                func.date(SalesOrder.order_date).label("day"),
                func.sum(SalesOrder.total_inc_gst).label("revenue"),
                func.count(SalesOrder.id).label("orders"),
            )
            .where(*filters)
            .group_by(func.date(SalesOrder.order_date))
            .order_by(func.date(SalesOrder.order_date))
        ).all()
        trend = [
            {
                "date": str(row.day),
                "revenue": float(_dec(row.revenue)),
                "orders": int(row.orders),
            }
            for row in trend_rows
        ]

        top_sku_rows = self.db.execute(
            select(
                Product.sku,
                Product.name,
                func.sum(SalesOrderLine.qty).label("units"),
                func.sum(SalesOrderLine.line_total_inc_gst).label("revenue"),
            )
            .select_from(SalesOrderLine)
            .join(SalesOrder, SalesOrderLine.order_id == SalesOrder.id)
            .join(Product, Product.id == SalesOrderLine.product_id)
            .where(*filters, SalesOrderLine.deleted_at.is_(None))
            .group_by(Product.id, Product.sku, Product.name)
            .order_by(func.sum(SalesOrderLine.line_total_inc_gst).desc())
            .limit(5)
        ).all()
        top_skus = [
            {
                "SKU": row.sku or "—",
                "Name": row.name or "—",
                "Units": float(_dec(row.units)),
                "Revenue": f"${_quantize(_dec(row.revenue)):,.2f}",
            }
            for row in top_sku_rows
        ]

        top_customer_rows = self.db.execute(
            select(
                Customer.name,
                func.count(SalesOrder.id).label("orders"),
                func.sum(SalesOrder.total_inc_gst).label("revenue"),
            )
            .select_from(SalesOrder)
            .join(Customer, Customer.id == SalesOrder.customer_id)
            .where(*filters)
            .group_by(Customer.id, Customer.name)
            .order_by(func.sum(SalesOrder.total_inc_gst).desc())
            .limit(5)
        ).all()
        top_customers = [
            {
                "Customer": row.name,
                "Orders": int(row.orders),
                "Revenue": f"${_quantize(_dec(row.revenue)):,.2f}",
            }
            for row in top_customer_rows
        ]

        return OverviewMetrics(
            total_orders=total_orders,
            revenue_inc_gst=revenue_inc,
            average_order_value=avg_order,
            repeat_rate_pct=repeat_rate,
            new_customers=new_customers,
            repeat_customers=repeat_customers,
            inactive_customers=inactive_customers,
            trend=trend,
            top_skus=top_skus,
            top_customers=top_customers,
        )

    def get_products_sold(
        self,
        *,
        start_date: date,
        end_date: date,
        channel_id: Optional[str] = None,
        pricebook_id: Optional[str] = None,
        segment: Optional[str] = None,
    ) -> ProductSalesSummary:
        filters = self._base_order_filters(
            start_date=start_date,
            end_date=end_date,
            channel_id=channel_id,
            pricebook_id=pricebook_id,
        )
        period_start_dt = _as_datetime_start(start_date)

        sales_query = (
            select(
                SalesOrderLine.product_id.label("product_id"),
                func.sum(SalesOrderLine.qty).label("qty_sold"),
                func.sum(SalesOrderLine.line_total_ex_gst).label("revenue_ex"),
                func.sum(SalesOrderLine.line_total_inc_gst).label("revenue_inc"),
            )
            .join(SalesOrder, SalesOrderLine.order_id == SalesOrder.id)
            .where(*filters, SalesOrderLine.deleted_at.is_(None))
            .group_by(SalesOrderLine.product_id)
        )
        sales_subq = sales_query.subquery()

        inventory_subq = (
            select(
                InventoryLot.product_id.label("product_id"),
                func.coalesce(func.sum(InventoryLot.quantity_kg), Decimal("0")).label(
                    "inventory_qty"
                ),
            )
            .where(InventoryLot.deleted_at.is_(None))
            .group_by(InventoryLot.product_id)
            .subquery()
        )

        query = (
            select(
                sales_subq.c.product_id,
                sales_subq.c.qty_sold,
                sales_subq.c.revenue_ex,
                sales_subq.c.revenue_inc,
                func.coalesce(inventory_subq.c.inventory_qty, Decimal("0")).label(
                    "inventory_qty"
                ),
                Product.sku,
                Product.name,
            )
            .join(Product, Product.id == sales_subq.c.product_id)
            .outerjoin(
                inventory_subq, inventory_subq.c.product_id == sales_subq.c.product_id
            )
            .order_by(sales_subq.c.revenue_inc.desc())
        )
        rows = self.db.execute(query).all()

        product_ids = [r.product_id for r in rows]
        channel_mix_map = self._channel_mix_for_products(product_ids, filters=filters)
        first_sale_map = self._first_sale_dates(product_ids)

        result_rows: List[ProductSalesRow] = []
        for row in rows:
            pid = row.product_id
            first_sale = first_sale_map.get(pid)
            first_in_period = bool(first_sale and first_sale >= period_start_dt)
            result_rows.append(
                ProductSalesRow(
                    product_id=pid,
                    sku=row.sku or "—",
                    name=row.name or "—",
                    units=_dec(row.qty_sold),
                    revenue_ex_gst=_quantize(_dec(row.revenue_ex)),
                    revenue_inc_gst=_quantize(_dec(row.revenue_inc)),
                    inventory_qty=_dec(row.inventory_qty),
                    channel_mix=channel_mix_map.get(pid, "—"),
                    first_sale_in_period=first_in_period,
                )
            )

        if segment == "slow":
            result_rows = sorted(result_rows, key=lambda r: r.revenue_inc_gst)
        elif segment == "new":
            result_rows = [r for r in result_rows if r.first_sale_in_period]
        # default "top" keeps revenue desc

        total_units = sum((r.units for r in result_rows), Decimal("0"))
        total_inc = sum((r.revenue_inc_gst for r in result_rows), Decimal("0"))
        total_ex = sum((r.revenue_ex_gst for r in result_rows), Decimal("0"))

        return ProductSalesSummary(
            rows=result_rows,
            total_units=total_units,
            total_revenue_inc_gst=_quantize(total_inc),
            total_revenue_ex_gst=_quantize(total_ex),
        )

    def _channel_mix_for_products(
        self, product_ids: List[str], *, filters
    ) -> Dict[str, str]:
        if not product_ids:
            return {}
        rows = self.db.execute(
            select(
                SalesOrderLine.product_id,
                SalesChannel.code,
                func.sum(SalesOrderLine.line_total_inc_gst).label("rev"),
            )
            .join(SalesOrder, SalesOrder.id == SalesOrderLine.order_id)
            .outerjoin(SalesChannel, SalesChannel.id == SalesOrder.channel_id)
            .where(
                *filters,
                SalesOrderLine.deleted_at.is_(None),
                SalesOrderLine.product_id.in_(product_ids),
            )
            .group_by(SalesOrderLine.product_id, SalesChannel.code)
        ).all()

        by_product: Dict[str, Dict[str, Decimal]] = {}
        for row in rows:
            code = (row.code or "UNKNOWN").upper()
            by_product.setdefault(row.product_id, {})
            by_product[row.product_id][code] = by_product[row.product_id].get(
                code, Decimal("0")
            ) + _dec(row.rev)

        result: Dict[str, str] = {}
        for pid, channels in by_product.items():
            total = sum(channels.values()) or Decimal("1")
            parts = []
            for code, rev in sorted(channels.items(), key=lambda x: -x[1]):
                pct = float(rev / total * 100)
                parts.append(f"{code} {pct:.0f}%")
            result[pid] = ", ".join(parts)
        return result

    def _first_sale_dates(self, product_ids: List[str]) -> Dict[str, datetime]:
        if not product_ids:
            return {}
        rows = self.db.execute(
            select(
                SalesOrderLine.product_id,
                func.min(SalesOrder.order_date).label("first_sale"),
            )
            .join(SalesOrder, SalesOrder.id == SalesOrderLine.order_id)
            .where(
                SalesOrder.deleted_at.is_(None),
                SalesOrder.status != SalesOrderStatus.CANCELLED.value,
                SalesOrderLine.deleted_at.is_(None),
                SalesOrderLine.product_id.in_(product_ids),
            )
            .group_by(SalesOrderLine.product_id)
        ).all()
        return {row.product_id: row.first_sale for row in rows if row.first_sale}

    def filter_options(self) -> dict:
        channels = (
            self.db.execute(
                select(SalesChannel)
                .where(SalesChannel.deleted_at.is_(None))
                .order_by(SalesChannel.name)
            )
            .scalars()
            .all()
        )
        pricebooks = (
            self.db.execute(
                select(Pricebook)
                .where(Pricebook.deleted_at.is_(None))
                .order_by(Pricebook.name)
            )
            .scalars()
            .all()
        )
        return {
            "channels": [{"label": c.name, "value": c.id} for c in channels],
            "pricebooks": [{"label": p.name, "value": p.id} for p in pricebooks],
        }
