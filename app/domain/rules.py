# app/domain/rules.py
"""Domain rules for units conversions, FIFO, and business logic."""

from decimal import Decimal, ROUND_HALF_EVEN
from typing import List, Optional, Tuple
from dataclasses import dataclass

from app.adapters.db.models import InventoryLot, InventoryTxn


@dataclass
class ConversionResult:
    """Result of a unit conversion."""
    quantity_kg: Decimal
    conversion_factor: Decimal
    source_unit: str


def to_kg(quantity: Decimal, uom: str, density_kg_per_l: Optional[Decimal] = None) -> ConversionResult:
    """
    Convert quantity to kg (canonical storage unit).
    
    Args:
        quantity: The quantity to convert
        uom: Unit of measure (kg, L, etc.)
        density_kg_per_l: Density in kg/L for liquid conversions
        
    Returns:
        ConversionResult with quantity in kg
        
    Raises:
        ValueError: If conversion is not supported or density missing for liquids
    """
    if uom.upper() == "KG":
        return ConversionResult(quantity, Decimal("1"), "kg")
    
    elif uom.upper() == "L" or uom.upper() == "LITRE" or uom.upper() == "LITER":
        if density_kg_per_l is None:
            raise ValueError(f"Density required for liquid conversion from {uom}")
        converted_kg = quantity * density_kg_per_l
        return ConversionResult(converted_kg, density_kg_per_l, uom)
    
    else:
        raise ValueError(f"Unsupported unit conversion from {uom} to kg")


def to_liters(quantity_kg: Decimal, density_kg_per_l: Decimal) -> Decimal:
    """
    Convert quantity from kg to liters.
    
    Args:
        quantity_kg: Quantity in kg
        density_kg_per_l: Density in kg/L
        
    Returns:
        Quantity in liters
    """
    if density_kg_per_l == 0:
        raise ValueError("Density cannot be zero")
    return quantity_kg / density_kg_per_l


def round_quantity(quantity: Decimal, decimal_places: int = 3) -> Decimal:
    """Round quantity to specified decimal places using bankers' rounding."""
    return quantity.quantize(Decimal(f"0.{'0' * decimal_places}"), rounding=ROUND_HALF_EVEN)


def round_money(amount: Decimal, decimal_places: int = 2) -> Decimal:
    """Round money to specified decimal places using bankers' rounding."""
    return amount.quantize(Decimal(f"0.{'0' * decimal_places}"), rounding=ROUND_HALF_EVEN)


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
    override_negative: bool = False
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
            issues.append(FifoIssue(
                lot_id=lot.id,
                quantity_kg=round_quantity(issue_quantity),
                unit_cost=lot.unit_cost or Decimal("0"),
                remaining_quantity_kg=round_quantity(lot.quantity_kg - issue_quantity)
            ))
            
            remaining_required -= issue_quantity
    
    if remaining_required > 0 and not override_negative:
        total_available = sum(lot.quantity_kg for lot in lots if lot.quantity_kg > 0)
        raise ValueError(
            f"Insufficient stock: required {required_quantity_kg} kg, "
            f"available {total_available} kg"
        )
    
    return issues


def calculate_abv_mass(volume_l: Decimal, abv_percent: Decimal, density_kg_per_l: Decimal) -> Decimal:
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
    
    # Calculate mass of solution
    solution_mass_kg = volume_l * density_kg_per_l
    
    # Calculate alcohol mass (assuming alcohol density ~0.789 kg/L)
    alcohol_density_kg_per_l = Decimal("0.789")
    alcohol_mass_kg = volume_l * abv_decimal * alcohol_density_kg_per_l
    
    return round_quantity(alcohol_mass_kg)


def validate_non_negative_lot(lot: InventoryLot, override: bool = False, audit_note: str = "") -> None:
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
            raise ValueError(f"Lot {lot.lot_code} cannot have negative quantity: {lot.quantity_kg} kg")
        if not audit_note:
            raise ValueError("Audit note required when overriding negative lot validation")


def calculate_line_totals(
    quantity_kg: Decimal,
    unit_price_ex_tax: Decimal,
    tax_rate: Decimal
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
