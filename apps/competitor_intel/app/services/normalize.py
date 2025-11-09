from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover
    from apps.competitor_intel.app.models.purchase_price import PurchasePrice
    from apps.competitor_intel.app.models.sku import SKU

MONEY_QUANT = Decimal("0.01")
FOUR_DP = Decimal("0.0001")
TWO_DP = Decimal("0.01")
STANDARD_DRINK_FACTOR = Decimal("0.789")
LITRE = Decimal("1000")


@dataclass(frozen=True)
class CostProfile:
    cost_type: Optional[str]
    currency: Optional[str]
    unit_cost: Optional[Decimal]
    pack_cost: Optional[Decimal]
    carton_cost: Optional[Decimal]


@dataclass(frozen=True)
class NormalizedPrices:
    price_ex_gst: Decimal
    price_inc_gst: Decimal
    unit_price_inc_gst: Decimal
    pack_price_inc_gst: Optional[Decimal]
    carton_price_inc_gst: Optional[Decimal]
    price_per_litre: Decimal
    price_per_unit_pure_alcohol: Decimal
    standard_drinks: Decimal
    price_basis: str
    gp_unit_abs: Optional[Decimal]
    gp_unit_pct: Optional[Decimal]
    gp_pack_abs: Optional[Decimal]
    gp_pack_pct: Optional[Decimal]
    gp_carton_abs: Optional[Decimal]
    gp_carton_pct: Optional[Decimal]
    cost_type: Optional[str]
    cost_currency: Optional[str]


class NormalizationError(Exception):
    """Raised when supplied pricing data cannot be normalized safely."""


def _quantize(value: Decimal, quant: Decimal) -> Decimal:
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def quantize_money(value: Decimal) -> Decimal:
    return _quantize(value, MONEY_QUANT)


def quantize_metric(value: Decimal) -> Decimal:
    return _quantize(value, FOUR_DP)


def normalize_gst_prices(
    price_ex_gst_raw: Optional[Decimal],
    price_inc_gst_raw: Optional[Decimal],
    gst_rate: Decimal,
) -> tuple[Decimal, Decimal]:
    if price_ex_gst_raw is None and price_inc_gst_raw is None:
        raise NormalizationError(
            "At least one of price_ex_gst_raw or price_inc_gst_raw must be provided"
        )

    if price_ex_gst_raw is None:
        price_inc = Decimal(price_inc_gst_raw)
        price_ex = price_inc / (Decimal("1") + gst_rate)
    elif price_inc_gst_raw is None:
        price_ex = Decimal(price_ex_gst_raw)
        price_inc = price_ex * (Decimal("1") + gst_rate)
    else:
        price_ex = Decimal(price_ex_gst_raw)
        price_inc = Decimal(price_inc_gst_raw)

    return quantize_money(price_ex), quantize_money(price_inc)


def compute_standard_drinks(container_ml: int, abv_percent: Decimal) -> Decimal:
    abv_fraction = abv_percent / Decimal("100")
    pure_alcohol_grams = Decimal(container_ml) * abv_fraction * STANDARD_DRINK_FACTOR
    std_drinks = pure_alcohol_grams / Decimal("10")
    return _quantize(std_drinks, TWO_DP)


def _units_per_pack(sku: "SKU") -> int:
    assignment = getattr(sku, "pack_assignment", None)
    if assignment and assignment.pack_spec and assignment.pack_spec.units_per_pack:
        return int(assignment.pack_spec.units_per_pack)
    return 1


def compute_price_metrics(
    *,
    sku: "SKU",
    price_inc_gst: Decimal,
    carton_units: Optional[int],
    is_carton_price: bool,
    is_pack_price: bool,
) -> tuple[
    Decimal, Optional[Decimal], Optional[Decimal], Decimal, Decimal, Decimal, int
]:
    units_per_pack = _units_per_pack(sku)
    container_ml = Decimal(sku.package_spec.container_ml)

    if is_carton_price:
        total_unit_count = Decimal(carton_units or 0)
        if total_unit_count <= 0:
            raise NormalizationError("Carton price provided without carton unit count")
        unit_price_inc = price_inc_gst / total_unit_count
        pack_price_inc = (
            unit_price_inc * Decimal(units_per_pack) if units_per_pack > 1 else None
        )
        carton_price_inc = price_inc_gst
    else:
        if units_per_pack > 1 and is_pack_price:
            pack_price_inc = price_inc_gst
            unit_price_inc = price_inc_gst / Decimal(units_per_pack)
        else:
            unit_price_inc = price_inc_gst
            pack_price_inc = (
                price_inc_gst * Decimal(units_per_pack) if units_per_pack > 1 else None
            )
        carton_price_inc = None

    unit_price_inc = quantize_money(unit_price_inc)
    pack_price_inc = (
        quantize_money(pack_price_inc) if pack_price_inc is not None else None
    )
    carton_price_inc = (
        quantize_money(carton_price_inc) if carton_price_inc is not None else None
    )

    volume_litres = (container_ml / LITRE) if container_ml else Decimal("0")
    price_per_litre = (
        quantize_metric(unit_price_inc / volume_litres)
        if volume_litres
        else Decimal("0")
    )

    standard_drinks = compute_standard_drinks(
        sku.package_spec.container_ml,
        Decimal(sku.product.abv_percent),
    )
    if standard_drinks == Decimal("0"):
        price_per_pure_alcohol = Decimal("0")
    else:
        price_per_pure_alcohol = quantize_metric(unit_price_inc / standard_drinks)

    return (
        unit_price_inc,
        pack_price_inc,
        carton_price_inc,
        price_per_litre,
        price_per_pure_alcohol,
        standard_drinks,
        units_per_pack,
    )


def _select_cost_record(sku: "SKU") -> Optional["PurchasePrice"]:
    records = [
        c
        for c in getattr(sku, "purchase_prices", [])
        if getattr(c, "deleted_at", None) is None
    ]
    if not records:
        return None
    records.sort(
        key=lambda c: (
            c.effective_date or date.min,
            0 if c.cost_type == "known" else 1,
        ),
        reverse=True,
    )
    return records[0]


def _build_cost_profile(
    sku: "SKU", units_per_pack: int, carton_units: Optional[int]
) -> CostProfile:
    record = _select_cost_record(sku)
    if record is None:
        return CostProfile(None, None, None, None, None)

    unit_cost = (
        Decimal(record.cost_per_unit) if record.cost_per_unit is not None else None
    )
    pack_cost = (
        Decimal(record.cost_per_pack) if record.cost_per_pack is not None else None
    )
    carton_cost = (
        Decimal(record.cost_per_carton) if record.cost_per_carton is not None else None
    )

    if pack_cost is None and unit_cost is not None and units_per_pack > 0:
        pack_cost = unit_cost * Decimal(units_per_pack)

    if carton_cost is None and carton_units:
        total_units = Decimal(carton_units)
        if pack_cost is not None and units_per_pack > 0:
            pack_count = total_units / Decimal(units_per_pack)
            carton_cost = pack_cost * pack_count
        elif unit_cost is not None:
            carton_cost = unit_cost * total_units

    return CostProfile(
        record.cost_type,
        record.cost_currency,
        unit_cost,
        pack_cost,
        carton_cost,
    )


def _calc_gp(
    price_ex: Optional[Decimal], cost: Optional[Decimal]
) -> tuple[Optional[Decimal], Optional[Decimal]]:
    if price_ex is None or cost is None or cost == 0:
        return None, None
    gp_abs = quantize_money(price_ex - cost)
    gp_pct = _quantize((price_ex - cost) / cost, FOUR_DP)
    return gp_abs, gp_pct


def normalize_price(
    *,
    sku: "SKU",
    price_ex_gst_raw: Optional[Decimal],
    price_inc_gst_raw: Optional[Decimal],
    gst_rate: Decimal,
    carton_units: Optional[int],
    is_carton_price: bool,
    is_pack_price: bool = False,
) -> NormalizedPrices:
    price_ex, price_inc = normalize_gst_prices(
        price_ex_gst_raw, price_inc_gst_raw, gst_rate
    )
    (
        unit_price,
        pack_price,
        carton_price,
        price_per_litre,
        price_per_pure_alcohol,
        standard_drinks,
        units_per_pack,
    ) = compute_price_metrics(
        sku=sku,
        price_inc_gst=price_inc,
        carton_units=carton_units
        if is_carton_price
        else (-1 if is_pack_price else None),
        is_carton_price=is_carton_price,
        is_pack_price=is_pack_price,
    )

    unit_price_ex = unit_price / (Decimal("1") + gst_rate)
    pack_price_ex = (
        pack_price / (Decimal("1") + gst_rate) if pack_price is not None else None
    )
    carton_price_ex = price_ex if is_carton_price else None

    costs = _build_cost_profile(sku, units_per_pack, carton_units)
    gp_unit_abs, gp_unit_pct = _calc_gp(unit_price_ex, costs.unit_cost)
    gp_pack_abs, gp_pack_pct = _calc_gp(pack_price_ex, costs.pack_cost)
    gp_carton_abs, gp_carton_pct = _calc_gp(carton_price_ex, costs.carton_cost)
    price_basis = (
        "carton"
        if is_carton_price
        else "pack"
        if is_pack_price and units_per_pack > 1
        else "unit"
    )

    return NormalizedPrices(
        price_ex_gst=price_ex,
        price_inc_gst=price_inc,
        unit_price_inc_gst=unit_price,
        pack_price_inc_gst=pack_price,
        carton_price_inc_gst=carton_price,
        price_per_litre=price_per_litre,
        price_per_unit_pure_alcohol=price_per_pure_alcohol,
        standard_drinks=standard_drinks,
        price_basis=price_basis,
        gp_unit_abs=gp_unit_abs,
        gp_unit_pct=gp_unit_pct,
        gp_pack_abs=gp_pack_abs,
        gp_pack_pct=gp_pack_pct,
        gp_carton_abs=gp_carton_abs,
        gp_carton_pct=gp_carton_pct,
        cost_type=costs.cost_type,
        cost_currency=costs.currency,
    )


__all__ = [
    "CostProfile",
    "NormalizedPrices",
    "NormalizationError",
    "normalize_price",
    "normalize_gst_prices",
    "compute_standard_drinks",
    "compute_price_metrics",
    "quantize_money",
    "quantize_metric",
]
