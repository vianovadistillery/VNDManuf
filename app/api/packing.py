# app/api/packing.py
"""Packing API router."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import PackConversion, PackUnit, Product
from app.api.dto import PackConversionResponse
from app.domain.rules import round_quantity, to_kg, to_liters

router = APIRouter(prefix="/pack", tags=["packing"])


@router.get("/convert", response_model=PackConversionResponse)
async def convert_pack_units(
    product_id: str = Query(..., description="Product ID"),
    qty: Decimal = Query(..., gt=0, description="Quantity to convert"),
    from_unit: str = Query(..., description="Source unit"),
    to_unit: str = Query(..., description="Target unit"),
    db: Session = Depends(get_db),
):
    """
    Convert quantity between pack units for a product.

    Uses product-specific conversions or falls back to standard conversions.
    """
    # Validate product exists
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Validate pack units exist
    from_unit_obj = db.execute(
        select(PackUnit).where(PackUnit.code == from_unit)
    ).scalar_one_or_none()
    to_unit_obj = db.execute(
        select(PackUnit).where(PackUnit.code == to_unit)
    ).scalar_one_or_none()

    if not from_unit_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack unit '{from_unit}' not found",
        )

    if not to_unit_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack unit '{to_unit}' not found",
        )

    # Same unit - no conversion needed
    if from_unit == to_unit:
        return PackConversionResponse(
            converted_qty=round_quantity(qty),
            conversion_factor=Decimal("1"),
            from_unit=from_unit,
            to_unit=to_unit,
        )

    # Try to find product-specific conversion
    conversion_stmt = select(PackConversion).where(
        and_(
            PackConversion.product_id == product_id,
            PackConversion.from_unit_id == from_unit_obj.id,
            PackConversion.to_unit_id == to_unit_obj.id,
            PackConversion.is_active.is_(True),
        )
    )
    conversion = db.execute(conversion_stmt).scalar_one_or_none()

    if conversion:
        converted_qty = round_quantity(qty * conversion.conversion_factor)
        return PackConversionResponse(
            converted_qty=converted_qty,
            conversion_factor=conversion.conversion_factor,
            from_unit=from_unit,
            to_unit=to_unit,
        )

    # Try reverse conversion
    reverse_conversion_stmt = select(PackConversion).where(
        and_(
            PackConversion.product_id == product_id,
            PackConversion.from_unit_id == to_unit_obj.id,
            PackConversion.to_unit_id == from_unit_obj.id,
            PackConversion.is_active.is_(True),
        )
    )
    reverse_conversion = db.execute(reverse_conversion_stmt).scalar_one_or_none()

    if reverse_conversion:
        # Use inverse of the conversion factor
        conversion_factor = Decimal("1") / reverse_conversion.conversion_factor
        converted_qty = round_quantity(qty * conversion_factor)
        return PackConversionResponse(
            converted_qty=converted_qty,
            conversion_factor=conversion_factor,
            from_unit=from_unit,
            to_unit=to_unit,
        )

    # Try standard unit conversions (kg/L)
    try:
        if from_unit.upper() in ["KG", "KILOGRAM"] and to_unit.upper() in [
            "L",
            "LITRE",
            "LITER",
        ]:
            if not product.density_kg_per_l:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Product {product.sku} has no density defined for L conversion",
                )
            converted_qty = round_quantity(to_liters(qty, product.density_kg_per_l))
            conversion_factor = Decimal("1") / product.density_kg_per_l
            return PackConversionResponse(
                converted_qty=converted_qty,
                conversion_factor=conversion_factor,
                from_unit=from_unit,
                to_unit=to_unit,
            )

        elif from_unit.upper() in ["L", "LITRE", "LITER"] and to_unit.upper() in [
            "KG",
            "KILOGRAM",
        ]:
            if not product.density_kg_per_l:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Product {product.sku} has no density defined for kg conversion",
                )
            converted_qty = round_quantity(
                to_kg(qty, from_unit, product.density_kg_per_l).quantity_kg
            )
            conversion_factor = product.density_kg_per_l
            return PackConversionResponse(
                converted_qty=converted_qty,
                conversion_factor=conversion_factor,
                from_unit=from_unit,
                to_unit=to_unit,
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )

    # No conversion path found
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"No conversion path found from '{from_unit}' to '{to_unit}' for product {product.sku}",
    )
