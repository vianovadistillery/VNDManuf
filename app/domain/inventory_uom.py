"""Inventory unit resolution — stock is stored in each product's usage unit."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from app.domain.rules import (
    MASS_TO_KG,
    VOLUME_TO_L,
    convert_mass,
    convert_volume,
    round_quantity,
)

if TYPE_CHECKING:
    from app.adapters.db.models import Product

EACH_UNITS = frozenset(
    {"EA", "EACH", "UNIT", "UNITS", "ITEM", "ITEMS", "CTN", "CARTON", "PK", "PACK"}
)

_UNIT_ALIASES = {
    "ML": "ML",
    "mL": "ML",
    "LT": "L",
    "LTR": "L",
    "LITRE": "L",
    "LITER": "L",
    "LITRES": "L",
    "LITERS": "L",
    "KILOGRAM": "KG",
    "KILOGRAMS": "KG",
    "GRAM": "G",
    "GRAMS": "G",
    "EACH": "EA",
}


def normalize_unit(unit: Optional[str], default: str = "EA") -> str:
    if not unit or not str(unit).strip():
        return default
    raw = str(unit).strip().upper()
    return _UNIT_ALIASES.get(raw, raw)


def unit_kind(unit: str) -> str:
    """Return COUNT, MASS, VOLUME, or OTHER."""
    u = normalize_unit(unit)
    if u in EACH_UNITS:
        return "COUNT"
    if u in MASS_TO_KG:
        return "MASS"
    if u in VOLUME_TO_L:
        return "VOLUME"
    return "OTHER"


def inventory_uom_for_product(product: Optional["Product"]) -> str:
    """
    Unit used for inventory lots and stock on hand.

    Prefers usage_unit, then base_unit. Sellable products default to EA;
    purchase bulk defaults to KG when unset.
    """
    if not product:
        return "EA"

    for attr in ("usage_unit", "base_unit"):
        val = getattr(product, attr, None)
        if val and str(val).strip():
            return normalize_unit(str(val))

    if getattr(product, "is_sell", False) or getattr(product, "sellable", False):
        return "EA"
    if getattr(product, "is_purchase", False):
        return "KG"
    return "EA"


def convert_quantity(
    quantity: Decimal,
    from_unit: str,
    to_unit: str,
    density_kg_per_l: Optional[Decimal] = None,
) -> Decimal:
    """Convert quantity between compatible units."""
    src = normalize_unit(from_unit)
    dst = normalize_unit(to_unit)
    qty = Decimal(str(quantity))

    if src == dst:
        return round_quantity(qty)

    src_kind = unit_kind(src)
    dst_kind = unit_kind(dst)

    if src_kind == "COUNT" or dst_kind == "COUNT":
        raise ValueError(
            f"Cannot convert between count unit '{src}' and '{dst}'. "
            "Use the product inventory unit."
        )

    if src_kind == "MASS" and dst_kind == "MASS":
        return round_quantity(convert_mass(qty, src, dst))

    if src_kind == "VOLUME" and dst_kind == "VOLUME":
        return round_quantity(convert_volume(qty, src, dst))

    if src_kind == "MASS" and dst_kind == "VOLUME":
        if not density_kg_per_l or density_kg_per_l <= 0:
            raise ValueError("Density (kg/L) required to convert mass to volume")
        kg = qty * MASS_TO_KG[src]
        litres = kg / density_kg_per_l
        return round_quantity(convert_volume(litres, "L", dst))

    if src_kind == "VOLUME" and dst_kind == "MASS":
        if not density_kg_per_l or density_kg_per_l <= 0:
            raise ValueError("Density (kg/L) required to convert volume to mass")
        litres = qty * VOLUME_TO_L[src]
        kg = litres * density_kg_per_l
        return round_quantity(convert_mass(kg, "KG", dst))

    raise ValueError(f"Unsupported unit conversion from '{src}' to '{dst}'")


def format_stock(quantity: Decimal, unit: str, precision: int = 3) -> str:
    u = normalize_unit(unit)
    q = float(quantity)
    if u in EACH_UNITS and abs(q - round(q)) < 0.0005:
        return f"{int(round(q))} {u}"
    return f"{q:.{precision}f} {u}"
