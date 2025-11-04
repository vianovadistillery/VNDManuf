# app/domain/rules.py
"""Domain rules for units conversions, FIFO, and business logic."""

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple

from app.adapters.db.models import InventoryLot


class UnitType(str, Enum):
    """Unit type enumeration."""

    MASS = "MASS"
    VOLUME = "VOLUME"
    DENSITY = "DENSITY"
    CONCENTRATION = "CONCENTRATION"
    COUNT = "COUNT"
    LENGTH = "LENGTH"
    AREA = "AREA"
    OTHER = "OTHER"


@dataclass
class ConversionResult:
    """Result of a unit conversion."""

    quantity_kg: Decimal
    conversion_factor: Decimal
    source_unit: str


@dataclass
class UnitConversionResult:
    """Result of a general unit conversion."""

    converted_quantity: Decimal
    conversion_factor: Decimal
    from_unit: str
    to_unit: str


# Mass conversion factors to kg (canonical storage unit)
MASS_TO_KG: Dict[str, Decimal] = {
    "MG": Decimal("0.000001"),  # milligram to kg
    "G": Decimal("0.001"),  # gram to kg
    "KG": Decimal("1"),  # kilogram (base unit)
    "TON": Decimal("1000"),  # metric ton to kg
}

# Volume conversion factors to liters (base volume unit)
VOLUME_TO_L: Dict[str, Decimal] = {
    "ML": Decimal("0.001"),  # milliliter to liter
    "L": Decimal("1"),  # liter (base unit)
}

# Density conversion factors to kg/L (canonical density unit)
DENSITY_TO_KG_L: Dict[str, Decimal] = {
    "G_CM3": Decimal("1"),  # g/cm³ = 1 kg/L (they are equivalent)
    "KG_L": Decimal("1"),  # kg/L (base unit)
    "KG_M3": Decimal("0.001"),  # kg/m³ to kg/L (divide by 1000)
}


def convert_mass(quantity: Decimal, from_unit: str, to_unit: str = "KG") -> Decimal:
    """
    Convert mass between units.

    Args:
        quantity: Quantity to convert
        from_unit: Source unit code (G, KG, TON, etc.)
        to_unit: Target unit code (default: KG)

    Returns:
        Converted quantity

    Raises:
        ValueError: If unit not supported
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()

    if from_unit == to_unit:
        return quantity

    if from_unit not in MASS_TO_KG:
        raise ValueError(f"Unsupported mass unit: {from_unit}")
    if to_unit not in MASS_TO_KG:
        raise ValueError(f"Unsupported mass unit: {to_unit}")

    # Convert to kg first, then to target unit
    quantity_kg = quantity * MASS_TO_KG[from_unit]
    converted = quantity_kg / MASS_TO_KG[to_unit]

    return round_quantity(converted)


def convert_volume(quantity: Decimal, from_unit: str, to_unit: str = "L") -> Decimal:
    """
    Convert volume between units.

    Args:
        quantity: Quantity to convert
        from_unit: Source unit code (ML, L, etc.)
        to_unit: Target unit code (default: L)

    Returns:
        Converted quantity

    Raises:
        ValueError: If unit not supported
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()

    if from_unit == to_unit:
        return quantity

    if from_unit not in VOLUME_TO_L:
        raise ValueError(f"Unsupported volume unit: {from_unit}")
    if to_unit not in VOLUME_TO_L:
        raise ValueError(f"Unsupported volume unit: {to_unit}")

    # Convert to liters first, then to target unit
    quantity_l = quantity * VOLUME_TO_L[from_unit]
    converted = quantity_l / VOLUME_TO_L[to_unit]

    return round_quantity(converted)


def convert_density(density: Decimal, from_unit: str, to_unit: str = "KG_L") -> Decimal:
    """
    Convert density between units.

    Args:
        density: Density value to convert
        from_unit: Source unit code (G_CM3, KG_L, KG_M3)
        to_unit: Target unit code (default: KG_L)

    Returns:
        Converted density

    Raises:
        ValueError: If unit not supported
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()

    if from_unit == to_unit:
        return density

    if from_unit not in DENSITY_TO_KG_L:
        raise ValueError(f"Unsupported density unit: {from_unit}")
    if to_unit not in DENSITY_TO_KG_L:
        raise ValueError(f"Unsupported density unit: {to_unit}")

    # Convert to kg/L first, then to target unit
    density_kg_l = density * DENSITY_TO_KG_L[from_unit]
    converted = density_kg_l / DENSITY_TO_KG_L[to_unit]

    return round_quantity(converted, decimal_places=6)


def to_kg(
    quantity: Decimal, uom: str, density_kg_per_l: Optional[Decimal] = None
) -> ConversionResult:
    """
    Convert quantity to kg (canonical storage unit).

    Supports mass units (g, kg, ton) and volume units (mL, L) with density.

    Args:
        quantity: The quantity to convert
        uom: Unit of measure code (KG, G, TON, L, ML, etc.)
        density_kg_per_l: Density in kg/L for liquid conversions

    Returns:
        ConversionResult with quantity in kg

    Raises:
        ValueError: If conversion is not supported or density missing for liquids
    """
    uom_upper = uom.upper()

    # Handle mass units
    if uom_upper in MASS_TO_KG:
        factor = MASS_TO_KG[uom_upper]
        converted_kg = quantity * factor
        return ConversionResult(round_quantity(converted_kg), factor, uom_upper)

    # Handle volume units (require density)
    if uom_upper in VOLUME_TO_L:
        if density_kg_per_l is None:
            raise ValueError(f"Density required for liquid conversion from {uom}")
        # Convert to liters first, then to kg using density
        quantity_l = quantity * VOLUME_TO_L[uom_upper]
        converted_kg = quantity_l * density_kg_per_l
        factor = VOLUME_TO_L[uom_upper] * density_kg_per_l
        return ConversionResult(round_quantity(converted_kg), factor, uom_upper)

    # Legacy support for common unit names
    if uom_upper in ("LITRE", "LITER"):
        if density_kg_per_l is None:
            raise ValueError(f"Density required for liquid conversion from {uom}")
        converted_kg = quantity * density_kg_per_l
        return ConversionResult(round_quantity(converted_kg), density_kg_per_l, uom)

    raise ValueError(
        f"Unsupported unit conversion from {uom} to kg. Supported units: {list(MASS_TO_KG.keys()) + list(VOLUME_TO_L.keys())}"
    )


def to_liters(
    quantity_kg: Decimal, density_kg_per_l: Decimal, target_unit: str = "L"
) -> Decimal:
    """
    Convert quantity from kg to volume units.

    Args:
        quantity_kg: Quantity in kg
        density_kg_per_l: Density in kg/L
        target_unit: Target volume unit (L, ML) - default L

    Returns:
        Quantity in target volume unit
    """
    if density_kg_per_l == 0:
        raise ValueError("Density cannot be zero")

    target_unit = target_unit.upper()
    quantity_l = quantity_kg / density_kg_per_l

    if target_unit == "L":
        return round_quantity(quantity_l)
    elif target_unit == "ML":
        return convert_volume(quantity_l, "L", "ML")
    else:
        raise ValueError(f"Unsupported target volume unit: {target_unit}")


def convert_units(
    quantity: Decimal,
    from_unit: str,
    to_unit: str,
    density_kg_per_l: Optional[Decimal] = None,
) -> UnitConversionResult:
    """
    General unit conversion function supporting mass, volume, and cross-type conversions.

    Args:
        quantity: Quantity to convert
        from_unit: Source unit code
        to_unit: Target unit code
        density_kg_per_l: Density in kg/L (required for volume/mass cross-conversions)

    Returns:
        UnitConversionResult with converted quantity and conversion factor

    Raises:
        ValueError: If conversion is not supported
    """
    from_unit_upper = from_unit.upper()
    to_unit_upper = to_unit.upper()

    # Same unit - no conversion
    if from_unit_upper == to_unit_upper:
        return UnitConversionResult(
            converted_quantity=quantity,
            conversion_factor=Decimal("1"),
            from_unit=from_unit,
            to_unit=to_unit,
        )

    # Mass to mass
    if from_unit_upper in MASS_TO_KG and to_unit_upper in MASS_TO_KG:
        converted = convert_mass(quantity, from_unit_upper, to_unit_upper)
        factor = MASS_TO_KG[from_unit_upper] / MASS_TO_KG[to_unit_upper]
        return UnitConversionResult(converted, factor, from_unit, to_unit)

    # Volume to volume
    if from_unit_upper in VOLUME_TO_L and to_unit_upper in VOLUME_TO_L:
        converted = convert_volume(quantity, from_unit_upper, to_unit_upper)
        factor = VOLUME_TO_L[from_unit_upper] / VOLUME_TO_L[to_unit_upper]
        return UnitConversionResult(converted, factor, from_unit, to_unit)

    # Mass to volume (requires density)
    if from_unit_upper in MASS_TO_KG and to_unit_upper in VOLUME_TO_L:
        if density_kg_per_l is None:
            raise ValueError(
                f"Density required to convert from mass ({from_unit}) to volume ({to_unit})"
            )
        # Convert to kg first, then to liters
        quantity_kg = quantity * MASS_TO_KG[from_unit_upper]
        quantity_l = quantity_kg / density_kg_per_l
        converted = quantity_l / VOLUME_TO_L[to_unit_upper]
        factor = (MASS_TO_KG[from_unit_upper] / density_kg_per_l) / VOLUME_TO_L[
            to_unit_upper
        ]
        return UnitConversionResult(
            round_quantity(converted), factor, from_unit, to_unit
        )

    # Volume to mass (requires density)
    if from_unit_upper in VOLUME_TO_L and to_unit_upper in MASS_TO_KG:
        if density_kg_per_l is None:
            raise ValueError(
                f"Density required to convert from volume ({from_unit}) to mass ({to_unit})"
            )
        # Convert to liters first, then to kg
        quantity_l = quantity * VOLUME_TO_L[from_unit_upper]
        quantity_kg = quantity_l * density_kg_per_l
        converted = quantity_kg / MASS_TO_KG[to_unit_upper]
        factor = (VOLUME_TO_L[from_unit_upper] * density_kg_per_l) / MASS_TO_KG[
            to_unit_upper
        ]
        return UnitConversionResult(
            round_quantity(converted), factor, from_unit, to_unit
        )

    raise ValueError(
        f"Unsupported conversion from {from_unit} to {to_unit}. "
        f"Supported mass units: {list(MASS_TO_KG.keys())}, "
        f"volume units: {list(VOLUME_TO_L.keys())}"
    )


def round_quantity(quantity: Decimal, decimal_places: int = 3) -> Decimal:
    """Round quantity to specified decimal places using bankers' rounding."""
    return quantity.quantize(
        Decimal(f"0.{'0' * decimal_places}"), rounding=ROUND_HALF_EVEN
    )


def round_money(amount: Decimal, decimal_places: int = 2) -> Decimal:
    """Round money to specified decimal places using bankers' rounding."""
    return amount.quantize(
        Decimal(f"0.{'0' * decimal_places}"), rounding=ROUND_HALF_EVEN
    )


@dataclass
class FifoIssue:
    """Result of FIFO issue operation."""

    lot_id: str
    quantity_kg: Decimal
    unit_cost: Decimal
    remaining_quantity_kg: Decimal


def fifo_issue(
    lots: List[InventoryLot],
    required_quantity_kg: Decimal,
    override_negative: bool = False,
) -> List[FifoIssue]:
    """
    Implement FIFO (First In, First Out) issue logic.

    Args:
        lots: List of inventory lots ordered by received_at (oldest first)
        required_quantity_kg: Total quantity to issue
        override_negative: Allow negative lot quantities (Admin role only)

    Returns:
        List of FifoIssue results

    Raises:
        ValueError: If insufficient stock and override not allowed
    """
    if required_quantity_kg <= 0:
        return []

    issues = []
    remaining_required = required_quantity_kg

    for lot in lots:
        if remaining_required <= 0:
            break

        # Skip negative lots unless override is enabled
        if lot.quantity_kg <= 0 and not override_negative:
            continue

        # Calculate quantity to issue from this lot
        if lot.quantity_kg > 0:
            issue_quantity = min(remaining_required, lot.quantity_kg)
        else:
            # For negative lots with override, we can issue up to the absolute value
            issue_quantity = min(remaining_required, abs(lot.quantity_kg))

        if issue_quantity > 0:
            issues.append(
                FifoIssue(
                    lot_id=lot.id,
                    quantity_kg=round_quantity(issue_quantity),
                    unit_cost=lot.unit_cost or Decimal("0"),
                    remaining_quantity_kg=round_quantity(
                        lot.quantity_kg - issue_quantity
                    ),
                )
            )

            remaining_required -= issue_quantity

    if remaining_required > 0 and not override_negative:
        total_available = sum(lot.quantity_kg for lot in lots if lot.quantity_kg > 0)
        raise ValueError(
            f"Insufficient stock: required {required_quantity_kg} kg, "
            f"available {total_available} kg"
        )

    return issues


def calculate_abv_mass(
    volume_l: Decimal, abv_percent: Decimal, density_kg_per_l: Decimal
) -> Decimal:
    """
    Calculate mass of alcohol from volume, ABV, and density.

    Args:
        volume_l: Volume in liters
        abv_percent: ABV as percentage (e.g., 40.0 for 40%)
        density_kg_per_l: Density of the solution in kg/L

    Returns:
        Mass of alcohol in kg
    """
    # Convert ABV percentage to decimal
    abv_decimal = abv_percent / Decimal("100")

    # Calculate alcohol mass (assuming alcohol density ~0.789 kg/L)
    alcohol_density_kg_per_l = Decimal("0.789")
    alcohol_mass_kg = volume_l * abv_decimal * alcohol_density_kg_per_l

    return round_quantity(alcohol_mass_kg)


def calculate_alcohol_quantity(
    quantity: Decimal,
    quantity_unit: str,
    abv_percent: Decimal,
    solution_density_kg_per_l: Optional[Decimal] = None,
    target_unit: str = "KG",
) -> UnitConversionResult:
    """
    Calculate alcohol quantity in a solution from volume or mass.

    Supports calculating alcohol content when:
    - Input is volume (L, mL) with ABV % - calculates alcohol mass or volume
    - Input is mass (kg, g) with ABV % and solution density - calculates alcohol mass

    Args:
        quantity: Quantity of solution
        quantity_unit: Unit of quantity (KG, G, L, ML)
        abv_percent: ABV as percentage (e.g., 40.0 for 40% vol/vol)
        solution_density_kg_per_l: Density of solution in kg/L (required if quantity is mass)
        target_unit: Target unit for alcohol quantity (KG, G, L, ML) - default KG

    Returns:
        UnitConversionResult with alcohol quantity in target unit

    Raises:
        ValueError: If parameters are invalid
    """
    quantity_unit_upper = quantity_unit.upper()
    target_unit_upper = target_unit.upper()

    # Convert ABV percentage to decimal
    abv_decimal = abv_percent / Decimal("100")

    # Alcohol density (pure ethanol at 20°C)
    alcohol_density_kg_per_l = Decimal("0.789")

    alcohol_quantity_kg: Decimal

    if quantity_unit_upper in VOLUME_TO_L:
        # Input is volume - calculate alcohol volume, then convert to target
        volume_l = quantity * VOLUME_TO_L[quantity_unit_upper]
        alcohol_volume_l = volume_l * abv_decimal
        # Convert alcohol volume to mass
        alcohol_quantity_kg = alcohol_volume_l * alcohol_density_kg_per_l

    elif quantity_unit_upper in MASS_TO_KG:
        # Input is mass - need solution density to find volume, then calculate alcohol
        if solution_density_kg_per_l is None:
            raise ValueError(
                f"Density required when converting from mass ({quantity_unit}) with ABV"
            )
        if solution_density_kg_per_l == 0:
            raise ValueError("Solution density cannot be zero")

        # Convert mass to volume
        solution_mass_kg = quantity * MASS_TO_KG[quantity_unit_upper]
        solution_volume_l = solution_mass_kg / solution_density_kg_per_l

        # Calculate alcohol volume and mass
        alcohol_volume_l = solution_volume_l * abv_decimal
        alcohol_quantity_kg = alcohol_volume_l * alcohol_density_kg_per_l

    else:
        raise ValueError(
            f"Unsupported quantity unit for alcohol calculation: {quantity_unit}"
        )

    # Convert to target unit
    if target_unit_upper in MASS_TO_KG:
        converted = alcohol_quantity_kg / MASS_TO_KG[target_unit_upper]
        factor = Decimal("1") / MASS_TO_KG[target_unit_upper]  # Simplified for clarity
    elif target_unit_upper in VOLUME_TO_L:
        # Convert alcohol mass back to volume
        alcohol_volume_l = alcohol_quantity_kg / alcohol_density_kg_per_l
        converted = alcohol_volume_l / VOLUME_TO_L[target_unit_upper]
        factor = Decimal("1") / (
            alcohol_density_kg_per_l * VOLUME_TO_L[target_unit_upper]
        )
    else:
        raise ValueError(f"Unsupported target unit: {target_unit}")

    return UnitConversionResult(
        converted_quantity=round_quantity(converted),
        conversion_factor=factor,
        from_unit=quantity_unit,
        to_unit=target_unit,
    )


def convert_concentration(
    value: Decimal,
    from_type: str,
    to_type: str,
    solution_density_kg_per_l: Optional[Decimal] = None,
    solute_density_kg_per_l: Optional[Decimal] = None,
) -> Decimal:
    """
    Convert between concentration types (ABV, wt%, solids%).

    Args:
        value: Concentration value to convert
        from_type: Source concentration type (ABV_VOL_VOL, WT_PCT, SOLIDS_PCT)
        to_type: Target concentration type
        solution_density_kg_per_l: Density of solution (required for ABV conversions)
        solute_density_kg_per_l: Density of solute (optional, for solids%)

    Returns:
        Converted concentration value

    Raises:
        ValueError: If conversion not supported or parameters missing
    """
    from_type_upper = from_type.upper()
    to_type_upper = to_type.upper()

    if from_type_upper == to_type_upper:
        return value

    # ABV to weight percentage (requires solution density)
    if from_type_upper == "ABV_VOL_VOL" and to_type_upper == "WT_PCT":
        if solution_density_kg_per_l is None:
            raise ValueError(
                "Solution density required to convert ABV to weight percentage"
            )
        # ABV is vol/vol, convert to weight/weight
        # Alcohol density ~0.789 kg/L
        alcohol_density_kg_per_l = Decimal("0.789")
        abv_decimal = value / Decimal("100")
        wt_pct = (
            (abv_decimal * alcohol_density_kg_per_l)
            / solution_density_kg_per_l
            * Decimal("100")
        )
        return round_quantity(wt_pct, decimal_places=2)

    # Weight percentage to ABV (requires solution density)
    if from_type_upper == "WT_PCT" and to_type_upper == "ABV_VOL_VOL":
        if solution_density_kg_per_l is None:
            raise ValueError(
                "Solution density required to convert weight percentage to ABV"
            )
        alcohol_density_kg_per_l = Decimal("0.789")
        wt_decimal = value / Decimal("100")
        abv_pct = (
            (wt_decimal * solution_density_kg_per_l)
            / alcohol_density_kg_per_l
            * Decimal("100")
        )
        return round_quantity(abv_pct, decimal_places=2)

    # For now, other conversions are not implemented
    raise ValueError(
        f"Conversion from {from_type} to {to_type} not yet implemented. "
        f"Supported: ABV_VOL_VOL <-> WT_PCT (requires solution_density_kg_per_l)"
    )


def validate_non_negative_lot(
    lot: InventoryLot, override: bool = False, audit_note: str = ""
) -> None:
    """
    Validate that lot quantity is non-negative unless override is allowed.

    Args:
        lot: Inventory lot to validate
        override: Allow negative quantities (Admin role)
        audit_note: Required audit note if override is used

    Raises:
        ValueError: If lot is negative and override not allowed
    """
    if lot.quantity_kg < 0:
        if not override:
            raise ValueError(
                f"Lot {lot.lot_code} cannot have negative quantity: {lot.quantity_kg} kg"
            )
        if not audit_note:
            raise ValueError(
                "Audit note required when overriding negative lot validation"
            )


def calculate_line_totals(
    quantity_kg: Decimal, unit_price_ex_tax: Decimal, tax_rate: Decimal
) -> Tuple[Decimal, Decimal, Decimal]:
    """
    Calculate line totals for invoices and sales orders.

    Args:
        quantity_kg: Quantity in kg
        unit_price_ex_tax: Unit price excluding tax
        tax_rate: Tax rate as percentage (e.g., 10.0 for 10%)

    Returns:
        Tuple of (line_total_ex_tax, tax_amount, line_total_inc_tax)
    """
    line_total_ex_tax = round_money(quantity_kg * unit_price_ex_tax)
    tax_amount = round_money(line_total_ex_tax * (tax_rate / Decimal("100")))
    line_total_inc_tax = round_money(line_total_ex_tax + tax_amount)

    return line_total_ex_tax, tax_amount, line_total_inc_tax


def fifo_peek_cost(
    lots: List[InventoryLot], batch_id: Optional[str] = None
) -> Optional[Decimal]:
    """
    Get FIFO unit cost without consuming inventory (peek operation).

    Args:
        lots: List of inventory lots ordered by received_at (oldest first)
        batch_id: Optional batch ID to get cost for specific batch

    Returns:
        Unit cost (Decimal) or None if no stock available
    """
    if not lots:
        return None

    # If batch_id specified, find that specific batch
    if batch_id:
        batch_lot = next((lot for lot in lots if lot.id == batch_id), None)
        if batch_lot and batch_lot.quantity_kg > 0:
            return batch_lot.unit_cost or Decimal("0")
        return None

    # Otherwise, return cost of oldest lot with stock
    for lot in lots:
        if lot.quantity_kg > 0:
            return lot.unit_cost or Decimal("0")

    return None


# Valid work order status transitions
VALID_WO_STATUS_TRANSITIONS = {
    "draft": ["released", "void"],
    "released": ["in_progress", "hold", "void"],
    "in_progress": ["hold", "complete"],
    "hold": ["released", "in_progress", "void"],
    "complete": [],  # Terminal state
    "void": [],  # Terminal state
}


def validate_wo_status_transition(from_status: str, to_status: str) -> bool:
    """
    Validate work order status transition.

    Args:
        from_status: Current status
        to_status: Target status

    Returns:
        True if transition is valid

    Raises:
        ValueError: If transition is invalid
    """
    from_status = from_status.lower()
    to_status = to_status.lower()

    if from_status == to_status:
        return True

    valid_next = VALID_WO_STATUS_TRANSITIONS.get(from_status, [])
    if to_status not in valid_next:
        raise ValueError(
            f"Invalid status transition from '{from_status}' to '{to_status}'. "
            f"Valid transitions: {valid_next}"
        )

    return True
