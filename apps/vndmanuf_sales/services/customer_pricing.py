"""Customer default tier + special product pricing resolution."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Tuple

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.adapters.db.models import Contact, Customer, CustomerPrice, Product
from apps.vndmanuf_sales.services.pricing import PricingService, _dec, quantize_money

PRICING_LEVELS = (
    "retail",
    "wholesale",
    "distributor",
    "counter",
    "trade",
    "contract",
    "industrial",
)

PRICE_LEVEL_EX_FIELDS = {
    "retail": "retail_price_ex_gst",
    "wholesale": "wholesale_price_ex_gst",
    "distributor": "distributor_price_ex_gst",
    "counter": "counter_price_ex_gst",
    "trade": "trade_price_ex_gst",
    "contract": "contract_price_ex_gst",
    "industrial": "industrial_price_ex_gst",
}


def _as_datetime(d: date | datetime) -> datetime:
    if isinstance(d, datetime):
        return d
    return datetime.combine(d, datetime.min.time())


def get_customer_pricing_level(db: Session, customer_id: str) -> str:
    customer = db.get(Customer, customer_id)
    if not customer:
        return "retail"
    if customer.contact_id:
        contact = db.get(Contact, customer.contact_id)
        if contact and contact.default_pricing_level:
            level = contact.default_pricing_level.strip().lower()
            if level in PRICE_LEVEL_EX_FIELDS:
                return level
    return "retail"


def tier_price_from_product(
    product: Product, pricing_level: str, gst_rate: Decimal
) -> Tuple[Optional[Decimal], Optional[Decimal]]:
    key_ex = PRICE_LEVEL_EX_FIELDS.get(pricing_level, "retail_price_ex_gst")
    key_inc = key_ex.replace("_ex_gst", "_inc_gst")
    ex = _dec(getattr(product, key_ex, None))
    inc = _dec(getattr(product, key_inc, None))
    if ex is None and inc is None:
        ex = _dec(product.retail_price_ex_gst)
        inc = _dec(product.retail_price_inc_gst)
    if ex is None and inc is None:
        return None, None
    factor = Decimal("1") + gst_rate / Decimal("100")
    if ex is not None and inc is None:
        inc = quantize_money(ex * factor)
    elif inc is not None and ex is None:
        ex = quantize_money(inc / factor)
    return quantize_money(ex or Decimal("0")), quantize_money(inc or Decimal("0"))


def find_active_special_price(
    db: Session,
    customer_id: str,
    product_id: str,
    as_of: datetime,
) -> Optional[CustomerPrice]:
    rows = (
        db.execute(
            select(CustomerPrice)
            .where(
                CustomerPrice.customer_id == customer_id,
                CustomerPrice.product_id == product_id,
                CustomerPrice.deleted_at.is_(None),
                CustomerPrice.effective_date <= as_of,
                or_(
                    CustomerPrice.expiry_date.is_(None),
                    CustomerPrice.expiry_date >= as_of,
                ),
            )
            .order_by(CustomerPrice.effective_date.desc())
        )
        .scalars()
        .all()
    )
    return rows[0] if rows else None


def is_special_price_active(cp: CustomerPrice, as_of: datetime) -> bool:
    if getattr(cp, "deleted_at", None):
        return False
    if cp.effective_date > as_of:
        return False
    if cp.expiry_date and cp.expiry_date < as_of:
        return False
    return True


def resolve_customer_product_price(
    db: Session,
    customer_id: str,
    product_id: str,
    as_of: Optional[date | datetime] = None,
) -> dict:
    """
    Default tier price from customer's pricing level, overridden by active special price.
    """
    as_of_dt = _as_datetime(as_of or datetime.utcnow())
    product = db.get(Product, product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found")

    pricing_svc = PricingService(db)
    gst_rate = (
        pricing_svc._get_customer_tax_rate(customer_id)  # noqa: SLF001
        or pricing_svc.default_gst_rate
    )
    level = get_customer_pricing_level(db, customer_id)
    ex, inc = tier_price_from_product(product, level, gst_rate)
    source = f"tier:{level}"

    special = find_active_special_price(db, customer_id, product_id, as_of_dt)
    if special:
        ex = quantize_money(_dec(special.unit_price_ex_tax) or Decimal("0"))
        inc = quantize_money(ex * (Decimal("1") + gst_rate / Decimal("100")))
        source = "customer_special"

    if ex is None:
        raise ValueError(f"No price available for product {product_id}")

    if inc is None:
        inc = quantize_money(ex * (Decimal("1") + gst_rate / Decimal("100")))

    return {
        "unit_price_ex_gst": float(ex),
        "unit_price_inc_gst": float(inc),
        "pricing_level": level,
        "source": source,
        "special_price_id": str(special.id) if special else None,
    }


def list_tier_prices_for_level(db: Session, pricing_level: str) -> list[dict]:
    """Sellable products with unit prices for the given pricing tier."""
    level = (pricing_level or "retail").strip().lower()
    if level not in PRICE_LEVEL_EX_FIELDS:
        level = "retail"

    pricing_svc = PricingService(db)
    gst_rate = pricing_svc.default_gst_rate

    products = (
        db.execute(
            select(Product)
            .where(
                Product.is_sell.is_(True),
                Product.deleted_at.is_(None),
            )
            .order_by(Product.sku, Product.name)
        )
        .scalars()
        .all()
    )

    rows: list[dict] = []
    for product in products:
        ex, inc = tier_price_from_product(product, level, gst_rate)
        if ex is None and inc is None:
            continue
        sku = getattr(product, "sku", None) or ""
        name = getattr(product, "name", None) or ""
        product_label = f"{sku} – {name}".strip(" –") or str(product.id)
        rows.append(
            {
                "product_id": str(product.id),
                "product": product_label,
                "sku": sku,
                "unit_price_ex_gst": float(ex) if ex is not None else None,
                "unit_price_inc_gst": float(inc) if inc is not None else None,
            }
        )
    return rows


def count_active_special_prices_for_customers(
    db: Session, customer_ids: list[str], as_of: Optional[datetime] = None
) -> dict[str, int]:
    """Count active special prices (one per product) per customer."""
    if not customer_ids:
        return {}
    as_of_dt = _as_datetime(as_of or datetime.utcnow())
    rows = (
        db.execute(
            select(CustomerPrice)
            .where(
                CustomerPrice.customer_id.in_(customer_ids),
                CustomerPrice.deleted_at.is_(None),
            )
            .order_by(
                CustomerPrice.customer_id,
                CustomerPrice.product_id,
                CustomerPrice.effective_date.desc(),
            )
        )
        .scalars()
        .all()
    )
    counts: dict[str, int] = {}
    seen: set[tuple[str, str]] = set()
    for cp in rows:
        key = (str(cp.customer_id), str(cp.product_id))
        if key in seen:
            continue
        seen.add(key)
        if is_special_price_active(cp, as_of_dt):
            cid = str(cp.customer_id)
            counts[cid] = counts.get(cid, 0) + 1
    return counts


def active_special_prices_by_product(
    db: Session, customer_id: str, as_of: Optional[datetime] = None
) -> dict[str, CustomerPrice]:
    """Latest active special price per product for a customer."""
    as_of_dt = _as_datetime(as_of or datetime.utcnow())
    rows = (
        db.execute(
            select(CustomerPrice)
            .where(
                CustomerPrice.customer_id == customer_id,
                CustomerPrice.deleted_at.is_(None),
            )
            .order_by(CustomerPrice.product_id, CustomerPrice.effective_date.desc())
        )
        .scalars()
        .all()
    )
    by_product: dict[str, CustomerPrice] = {}
    for cp in rows:
        pid = str(cp.product_id)
        if pid in by_product:
            continue
        if is_special_price_active(cp, as_of_dt):
            by_product[pid] = cp
    return by_product


def list_tier_prices_for_customer(
    db: Session, pricing_level: str, customer_id: str
) -> list[dict]:
    """Tier catalog with active customer special prices merged per product."""
    level = (pricing_level or "retail").strip().lower()
    if level not in PRICE_LEVEL_EX_FIELDS:
        level = "retail"

    pricing_svc = PricingService(db)
    gst_rate = (
        pricing_svc._get_customer_tax_rate(customer_id)  # noqa: SLF001
        or pricing_svc.default_gst_rate
    )
    specials = active_special_prices_by_product(db, customer_id)
    rows = list_tier_prices_for_level(db, level)

    for row in rows:
        product_id = row["product_id"]
        special = specials.get(product_id)
        row["has_active_special"] = False
        row["special_price_ex_gst"] = None
        row["special_price_inc_gst"] = None
        if not special:
            continue
        special_ex = quantize_money(_dec(special.unit_price_ex_tax) or Decimal("0"))
        special_inc = quantize_money(
            special_ex * (Decimal("1") + gst_rate / Decimal("100"))
        )
        row["has_active_special"] = True
        row["special_price_ex_gst"] = float(special_ex)
        row["special_price_inc_gst"] = float(special_inc)
    return rows
