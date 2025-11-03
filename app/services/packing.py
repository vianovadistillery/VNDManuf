# app/services/packing.py
"""Packing service - Unit conversions and pack hierarchy."""

from decimal import Decimal

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.adapters.db.models import PackConversion, PackUnit, Product
from app.domain.rules import round_quantity, to_kg, to_liters


class PackingService:
    """
    Service for pack unit conversions.

    Handles conversions between units (CAN, 4PK, CTN) and kg/L conversions.
    """

    def __init__(self, db: Session):
        self.db = db

    def convert(
        self, product_id: str, qty: Decimal, from_unit: str, to_unit: str
    ) -> dict:
        """
        Convert quantity between pack units for a product.

        Args:
            product_id: Product ID
            qty: Quantity to convert
            from_unit: Source unit code
            to_unit: Target unit code

        Returns:
            Dict with converted_qty, conversion_factor, from_unit, to_unit

        Raises:
            ValueError: If conversion path not found
        """
        # Validate product exists
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Validate pack units exist
        from_unit_obj = self.db.execute(
            select(PackUnit).where(PackUnit.code == from_unit)
        ).scalar_one_or_none()

        to_unit_obj = self.db.execute(
            select(PackUnit).where(PackUnit.code == to_unit)
        ).scalar_one_or_none()

        if not from_unit_obj:
            raise ValueError(f"Pack unit '{from_unit}' not found")

        if not to_unit_obj:
            raise ValueError(f"Pack unit '{to_unit}' not found")

        # Same unit - no conversion needed
        if from_unit == to_unit:
            return {
                "converted_qty": round_quantity(qty),
                "conversion_factor": Decimal("1"),
                "from_unit": from_unit,
                "to_unit": to_unit,
            }

        # Try to find product-specific conversion
        conversion = self.db.execute(
            select(PackConversion).where(
                and_(
                    PackConversion.product_id == product_id,
                    PackConversion.from_unit_id == from_unit_obj.id,
                    PackConversion.to_unit_id == to_unit_obj.id,
                    PackConversion.is_active.is_(True),
                )
            )
        ).scalar_one_or_none()

        if conversion:
            converted_qty = round_quantity(qty * conversion.conversion_factor)
            return {
                "converted_qty": converted_qty,
                "conversion_factor": conversion.conversion_factor,
                "from_unit": from_unit,
                "to_unit": to_unit,
            }

        # Try reverse conversion
        reverse_conversion = self.db.execute(
            select(PackConversion).where(
                and_(
                    PackConversion.product_id == product_id,
                    PackConversion.from_unit_id == to_unit_obj.id,
                    PackConversion.to_unit_id == from_unit_obj.id,
                    PackConversion.is_active.is_(True),
                )
            )
        ).scalar_one_or_none()

        if reverse_conversion:
            # Use inverse of the conversion factor
            conversion_factor = Decimal("1") / reverse_conversion.conversion_factor
            converted_qty = round_quantity(qty * conversion_factor)
            return {
                "converted_qty": converted_qty,
                "conversion_factor": conversion_factor,
                "from_unit": from_unit,
                "to_unit": to_unit,
            }

        # Try standard unit conversions (kg/L)
        if from_unit.upper() in ["KG", "KILOGRAM"] and to_unit.upper() in [
            "L",
            "LITRE",
            "LITER",
        ]:
            if not product.density_kg_per_l:
                raise ValueError(
                    f"Product {product.sku} has no density defined for L conversion"
                )

            converted_qty = round_quantity(to_liters(qty, product.density_kg_per_l))
            conversion_factor = Decimal("1") / product.density_kg_per_l
            return {
                "converted_qty": converted_qty,
                "conversion_factor": conversion_factor,
                "from_unit": from_unit,
                "to_unit": to_unit,
            }

        elif from_unit.upper() in ["L", "LITRE", "LITER"] and to_unit.upper() in [
            "KG",
            "KILOGRAM",
        ]:
            if not product.density_kg_per_l:
                raise ValueError(
                    f"Product {product.sku} has no density defined for kg conversion"
                )

            result = to_kg(qty, from_unit, product.density_kg_per_l)
            converted_qty = round_quantity(result.quantity_kg)
            return {
                "converted_qty": converted_qty,
                "conversion_factor": product.density_kg_per_l,
                "from_unit": from_unit,
                "to_unit": to_unit,
            }

        # No conversion path found
        raise ValueError(
            f"No conversion path found from '{from_unit}' to '{to_unit}' for product {product.sku}"
        )


def convert_pack_units(
    product_id: str, qty: Decimal, from_unit: str, to_unit: str, db: Session
) -> dict:
    """Convenience function to convert pack units."""
    service = PackingService(db)
    return service.convert(product_id, qty, from_unit, to_unit)
