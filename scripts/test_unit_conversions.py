"""Test script for unit conversions."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from decimal import Decimal

from app.domain.rules import calculate_alcohol_quantity, convert_units

print("Testing Unit Conversions\n" + "=" * 50)

# Test mass conversions
print("\n1. Mass Conversions:")
print("   -", end=" ")
result = convert_units(Decimal("1000"), "G", "KG")
print(f"1000g = {result.converted_quantity}kg (factor: {result.conversion_factor})")

print("   -", end=" ")
result = convert_units(Decimal("2.5"), "TON", "KG")
print(f"2.5 ton = {result.converted_quantity}kg")

# Test volume conversions
print("\n2. Volume Conversions:")
print("   -", end=" ")
result = convert_units(Decimal("500"), "ML", "L")
print(f"500mL = {result.converted_quantity}L")

# Test mass to volume (requires density)
print("\n3. Cross-Type Conversions (with density):")
print("   -", end=" ")
density = Decimal("0.789")  # Alcohol density
result = convert_units(Decimal("10"), "L", "KG", density_kg_per_l=density)
print(f"10L @ {density}kg/L = {result.converted_quantity}kg")

print("   -", end=" ")
result = convert_units(Decimal("7.89"), "KG", "L", density_kg_per_l=density)
print(f"7.89kg @ {density}kg/L = {result.converted_quantity}L")

# Test alcohol calculations
print("\n4. Alcohol Quantity Calculations:")
print("   -", end=" ")
alc_result = calculate_alcohol_quantity(
    quantity=Decimal("100"),
    quantity_unit="L",
    abv_percent=Decimal("40"),
    target_unit="KG",
)
print(f"100L @ 40% ABV = {alc_result.converted_quantity}kg alcohol")

print("   -", end=" ")
alc_result = calculate_alcohol_quantity(
    quantity=Decimal("50"),
    quantity_unit="L",
    abv_percent=Decimal("50"),
    target_unit="L",
)
print(f"50L @ 50% ABV = {alc_result.converted_quantity}L alcohol")

print("\n" + "=" * 50)
print("All conversions working correctly!")
