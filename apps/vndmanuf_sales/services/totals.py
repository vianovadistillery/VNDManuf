"""Totals and analytics helper for sales orders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.db.models import InventoryLot
from apps.vndmanuf_sales.models import SalesOrder, SalesOrderLine

Money = Decimal


def _dec(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _quantize(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)


@dataclass
class LineTotals:
    qty: Decimal
    line_total_ex_gst: Money
    line_total_inc_gst: Money
    discount_ex_gst: Money


@dataclass
class OrderTotals:
    total_ex_gst: Money
    total_inc_gst: Money
    total_discount_ex_gst: Money


@dataclass
class ProductSalesSnapshot:
    product_id: str
    qty_sold: Decimal
    revenue_ex_gst: Money
    revenue_inc_gst: Money
    inventory_qty: Decimal


class TotalsService:
    """Aggregate and compute totals for sales orders."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # Totals computation
    # ------------------------------------------------------------------ #
    def compute_line_totals(
        self,
        *,
        qty: Decimal,
        unit_price_ex_gst: Decimal,
        unit_price_inc_gst: Optional[Decimal] = None,
        discount_ex_gst: Optional[Decimal] = None,
    ) -> LineTotals:
        qty = _dec(qty)
        unit_price_ex_gst = _dec(unit_price_ex_gst)
        unit_price_inc_gst = (
            _dec(unit_price_inc_gst)
            if unit_price_inc_gst is not None
            else _quantize(unit_price_ex_gst * Decimal("1.1"))
        )
        discount_ex_gst = _dec(discount_ex_gst or Decimal("0"))

        effective_unit_ex = unit_price_ex_gst - discount_ex_gst
        line_ex = _quantize(effective_unit_ex * qty)

        if unit_price_ex_gst > 0:
            ratio = unit_price_inc_gst / unit_price_ex_gst
            line_inc = _quantize(line_ex * ratio)
        else:
            line_inc = _quantize(unit_price_inc_gst * qty)

        return LineTotals(
            qty=qty,
            line_total_ex_gst=line_ex,
            line_total_inc_gst=line_inc,
            discount_ex_gst=_quantize(discount_ex_gst * qty),
        )

    def refresh_order_totals(self, order: SalesOrder) -> OrderTotals:
        """
        Recalculate and persist the order totals from its lines.
        """
        totals = self._summarize_lines(order.lines)
        order.total_ex_gst = totals.total_ex_gst
        order.total_inc_gst = totals.total_inc_gst
        self.db.flush()
        return totals

    def summarize_order(self, order_id: str) -> OrderTotals:
        order = self.db.get(SalesOrder, order_id)
        if not order:
            raise ValueError(f"SalesOrder {order_id} not found")
        return self.refresh_order_totals(order)

    # ------------------------------------------------------------------ #
    # Analytics helper
    # ------------------------------------------------------------------ #
    def product_sales_with_inventory(
        self,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[ProductSalesSnapshot]:
        """
        Return sales aggregation joined with current inventory balances.
        """
        order_filter = []
        if start_date:
            order_filter.append(
                SalesOrder.order_date
                >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            order_filter.append(
                SalesOrder.order_date <= datetime.combine(end_date, datetime.max.time())
            )

        sales_query = select(
            SalesOrderLine.product_id.label("product_id"),
            func.sum(SalesOrderLine.qty).label("qty_sold"),
            func.sum(SalesOrderLine.line_total_ex_gst).label("revenue_ex"),
            func.sum(SalesOrderLine.line_total_inc_gst).label("revenue_inc"),
        ).join(SalesOrder, SalesOrderLine.order)
        if order_filter:
            sales_query = sales_query.where(*order_filter)
        sales_subq = sales_query.group_by(SalesOrderLine.product_id).subquery()

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
            )
            .outerjoin(
                inventory_subq, inventory_subq.c.product_id == sales_subq.c.product_id
            )
            .order_by(sales_subq.c.revenue_inc.desc())
        )

        rows = self.db.execute(query).all()
        return [
            ProductSalesSnapshot(
                product_id=row.product_id,
                qty_sold=_dec(row.qty_sold),
                revenue_ex_gst=_quantize(_dec(row.revenue_ex)),
                revenue_inc_gst=_quantize(_dec(row.revenue_inc)),
                inventory_qty=_dec(row.inventory_qty),
            )
            for row in rows
        ]

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _summarize_lines(self, lines: Iterable[SalesOrderLine]) -> OrderTotals:
        total_ex = Decimal("0")
        total_inc = Decimal("0")
        total_discount = Decimal("0")
        for line in lines:
            total_ex += _dec(line.line_total_ex_gst)
            total_inc += _dec(line.line_total_inc_gst)
            total_discount += _dec(line.discount_ex_gst or Decimal("0"))

        return OrderTotals(
            total_ex_gst=_quantize(total_ex),
            total_inc_gst=_quantize(total_inc),
            total_discount_ex_gst=_quantize(total_discount),
        )
