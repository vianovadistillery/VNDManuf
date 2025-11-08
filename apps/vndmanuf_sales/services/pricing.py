"""Sales pricing service - resolves unit prices and GST pairs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional, Tuple

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.adapters.db.models import Product
from app.settings import settings
from apps.vndmanuf_sales.models import (
    Customer,
    CustomerType,
    Pricebook,
    PricebookItem,
)

Money = Decimal


def _dec(value: Optional[Decimal | float | int | str]) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def quantize_money(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PriceResolution:
    """Container for resolved pricing data."""

    unit_price_ex_gst: Money
    unit_price_inc_gst: Money
    gst_rate: Decimal
    source: str
    pricebook_id: Optional[str] = None


class PriceComputationError(RuntimeError):
    """Raised when pricing cannot be resolved."""


class PricingService:
    """Resolve pricing for sales orders using pricebooks and customer defaults."""

    def __init__(self, db: Session, default_gst_rate: Optional[Decimal] = None):
        self.db = db
        self.default_gst_rate = _dec(default_gst_rate) or Decimal(
            str(settings.business.default_tax_rate)
        )

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def resolve_price(
        self,
        product_id: str,
        *,
        order_date: Optional[date] = None,
        pricebook_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        override_gst_rate: Optional[Decimal] = None,
    ) -> PriceResolution:
        """
        Resolve the unit prices (ex/in GST) for a product.

        Resolution precedence:
            1. Explicit pricebook_id supplied → matching pricebook item
            2. First active pricebook covering order_date (or today) ordered by active_from desc
            3. Customer channel defaults (future extension hook)
            4. Product fallback pricing (retail/wholesale fields) if available
        """
        product = self._get_product(product_id)
        gst_rate = (
            _dec(override_gst_rate)
            or (self._get_customer_tax_rate(customer_id) if customer_id else None)
            or self.default_gst_rate
        )

        order_date = order_date or datetime.utcnow().date()

        # Step 1 / 2 - pricebook pricing
        pricebook_item, resolved_pricebook_id = self._resolve_pricebook_item(
            product_id=product_id,
            order_date=order_date,
            pricebook_id=pricebook_id,
        )
        if pricebook_item:
            ex, inc = self._pair_prices(
                pricebook_item.unit_price_ex_gst,
                pricebook_item.unit_price_inc_gst,
                gst_rate,
            )
            return PriceResolution(
                unit_price_ex_gst=ex,
                unit_price_inc_gst=inc,
                gst_rate=gst_rate,
                source="pricebook_item",
                pricebook_id=resolved_pricebook_id,
            )

        # Step 4 - product fallback
        ex = (
            _dec(product.retail_price_ex_gst)
            or _dec(product.wholesale_price_ex_gst)
            or _dec(product.distributor_price_ex_gst)
        )
        inc = (
            _dec(product.retail_price_inc_gst)
            or _dec(product.wholesale_price_inc_gst)
            or _dec(product.distributor_price_inc_gst)
        )
        if ex is not None or inc is not None:
            ex_val, inc_val = self._pair_prices(ex, inc, gst_rate)
            return PriceResolution(
                unit_price_ex_gst=ex_val,
                unit_price_inc_gst=inc_val,
                gst_rate=gst_rate,
                source="product_fallback",
                pricebook_id=None,
            )

        raise PriceComputationError(
            f"Unable to resolve pricing for product {product_id}. "
            "No pricebook item or fallback price available."
        )

    def compute_inc_gst(
        self,
        *,
        unit_price_ex_gst: Optional[Decimal] = None,
        unit_price_inc_gst: Optional[Decimal] = None,
        gst_rate: Optional[Decimal] = None,
    ) -> Tuple[Decimal, Decimal]:
        """
        Normalize price pair ensuring both ex/inc GST are present.
        """
        gst_rate = _dec(gst_rate) or self.default_gst_rate
        ex, inc = self._pair_prices(unit_price_ex_gst, unit_price_inc_gst, gst_rate)
        return ex, inc

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _get_product(self, product_id: str) -> Product:
        product = self.db.get(Product, product_id)
        if not product:
            raise PriceComputationError(f"Product {product_id} not found")
        return product

    def _get_customer_tax_rate(self, customer_id: str) -> Optional[Decimal]:
        customer = self.db.get(Customer, customer_id)
        if not customer:
            raise PriceComputationError(f"Customer {customer_id} not found")
        if (
            customer.customer_type == CustomerType.DISTRIBUTOR.value
            and customer.tax_rate
        ):
            return _dec(customer.tax_rate)
        return _dec(customer.tax_rate) if customer.tax_rate is not None else None

    def _resolve_pricebook_item(
        self,
        *,
        product_id: str,
        order_date: date,
        pricebook_id: Optional[str],
    ) -> Tuple[Optional[PricebookItem], Optional[str]]:
        """
        Return matching pricebook item and the pricebook_id used.
        """
        query = select(PricebookItem, Pricebook.id.label("pb_id")).join(Pricebook)

        if pricebook_id:
            query = query.where(Pricebook.id == pricebook_id)
        else:
            query = query.where(
                Pricebook.active_from <= order_date,
                or_(Pricebook.active_to.is_(None), Pricebook.active_to >= order_date),
            )

        query = query.where(
            and_(
                PricebookItem.product_id == product_id,
                Pricebook.deleted_at.is_(None),
                PricebookItem.deleted_at.is_(None),
            )
        ).order_by(Pricebook.active_from.desc(), PricebookItem.updated_at.desc())

        row = self.db.execute(query).first()
        if row:
            return row[0], row[1]
        return None, None

    def _pair_prices(
        self,
        unit_price_ex_gst: Optional[Decimal],
        unit_price_inc_gst: Optional[Decimal],
        gst_rate: Decimal,
    ) -> Tuple[Decimal, Decimal]:
        ex = _dec(unit_price_ex_gst)
        inc = _dec(unit_price_inc_gst)
        factor = Decimal("1") + (gst_rate / Decimal("100"))

        if ex is None and inc is None:
            raise PriceComputationError("Both ex and inc GST prices are missing.")

        if ex is None and inc is not None:
            ex = quantize_money(inc / factor)
        elif inc is None and ex is not None:
            inc = quantize_money(ex * factor)
        else:
            # Both provided -> ensure they align, favour ex value
            inc = quantize_money(ex * factor)

        return quantize_money(ex), quantize_money(inc)
