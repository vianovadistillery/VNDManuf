# app/api/units.py
"""Units API router."""

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import Product, Unit
from app.domain.rules import (
    calculate_alcohol_quantity,
    convert_concentration,
    convert_units,
)

router = APIRouter(prefix="/units", tags=["units"])


class UnitCreate(BaseModel):
    """Unit creation request."""

    code: str = Field(..., max_length=20, description="Unit code (e.g., 'KG', 'LT')")
    name: str = Field(..., max_length=100, description="Unit name")
    description: Optional[str] = None
    symbol: Optional[str] = Field(
        None, max_length=10, description="Display symbol (e.g., 'kg', 'L')"
    )
    unit_type: Optional[str] = Field(
        None, max_length=20, description="MASS, VOLUME, COUNT, etc."
    )
    conversion_formula: Optional[str] = Field(
        None, description="Mathematical formula for unit conversions"
    )
    is_active: bool = True


class UnitUpdate(BaseModel):
    """Unit update request."""

    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    symbol: Optional[str] = Field(None, max_length=10)
    unit_type: Optional[str] = Field(None, max_length=20)
    conversion_formula: Optional[str] = None
    is_active: Optional[bool] = None


class UnitResponse(BaseModel):
    """Unit response."""

    id: str
    code: str
    name: str
    description: Optional[str] = None
    symbol: Optional[str] = None
    unit_type: Optional[str] = None
    conversion_formula: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


def unit_to_response(unit: Unit) -> UnitResponse:
    """Convert Unit model to response DTO."""
    return UnitResponse(
        id=str(unit.id),
        code=unit.code,
        name=unit.name,
        description=unit.description,
        symbol=unit.symbol,
        unit_type=unit.unit_type,
        conversion_formula=unit.conversion_formula,
        is_active=unit.is_active,
    )


@router.get("/", response_model=List[UnitResponse])
async def list_units(
    skip: int = 0,
    limit: int = 100,
    query: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List units with optional filtering."""
    stmt = select(Unit)

    if query:
        stmt = stmt.where(Unit.code.contains(query) | Unit.name.contains(query))

    if is_active is not None:
        stmt = stmt.where(Unit.is_active == is_active)

    stmt = stmt.order_by(Unit.code).offset(skip).limit(limit)
    units = db.execute(stmt).scalars().all()

    return [unit_to_response(u) for u in units]


@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(unit_id: str, db: Session = Depends(get_db)):
    """Get a unit by ID."""
    unit = db.get(Unit, unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found"
        )
    return unit_to_response(unit)


@router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(unit_data: UnitCreate, db: Session = Depends(get_db)):
    """Create a new unit."""
    # Check if code already exists
    existing = db.execute(
        select(Unit).where(Unit.code == unit_data.code)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Unit with code '{unit_data.code}' already exists",
        )

    unit = Unit(
        code=unit_data.code,
        name=unit_data.name,
        description=unit_data.description,
        symbol=unit_data.symbol,
        unit_type=unit_data.unit_type,
        conversion_formula=unit_data.conversion_formula,
        is_active=unit_data.is_active,
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit_to_response(unit)


@router.put("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: str, unit_data: UnitUpdate, db: Session = Depends(get_db)
):
    """Update a unit."""
    unit = db.get(Unit, unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found"
        )

    # Check if new code conflicts with existing unit
    if unit_data.code and unit_data.code != unit.code:
        existing = db.execute(
            select(Unit).where(Unit.code == unit_data.code)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Unit with code '{unit_data.code}' already exists",
            )

    # Update fields
    if unit_data.code is not None:
        unit.code = unit_data.code
    if unit_data.name is not None:
        unit.name = unit_data.name
    if unit_data.description is not None:
        unit.description = unit_data.description
    if unit_data.symbol is not None:
        unit.symbol = unit_data.symbol
    if unit_data.unit_type is not None:
        unit.unit_type = unit_data.unit_type
    if unit_data.conversion_formula is not None:
        unit.conversion_formula = unit_data.conversion_formula
    if unit_data.is_active is not None:
        unit.is_active = unit_data.is_active

    db.commit()
    db.refresh(unit)
    return unit_to_response(unit)


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unit(unit_id: str, db: Session = Depends(get_db)):
    """Delete a unit."""
    unit = db.get(Unit, unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found"
        )

    db.delete(unit)
    db.commit()
    return None


class UnitConversionRequest(BaseModel):
    """Unit conversion request."""

    quantity: Decimal = Field(..., gt=0, description="Quantity to convert")
    from_unit: str = Field(..., description="Source unit code")
    to_unit: str = Field(..., description="Target unit code")
    density_kg_per_l: Optional[Decimal] = Field(
        None, description="Density in kg/L (required for volume/mass conversions)"
    )
    product_id: Optional[str] = Field(
        None, description="Product ID to look up density from"
    )


class UnitConversionResponse(BaseModel):
    """Unit conversion response."""

    converted_quantity: Decimal
    conversion_factor: Decimal
    from_unit: str
    to_unit: str


class AlcoholConversionRequest(BaseModel):
    """Alcohol quantity conversion request."""

    quantity: Decimal = Field(..., gt=0, description="Quantity of solution")
    quantity_unit: str = Field(..., description="Unit of quantity (KG, G, L, ML)")
    abv_percent: Decimal = Field(..., ge=0, le=100, description="ABV as percentage")
    solution_density_kg_per_l: Optional[Decimal] = Field(
        None, description="Density of solution (required if quantity is mass)"
    )
    target_unit: str = Field("KG", description="Target unit for alcohol quantity")
    product_id: Optional[str] = Field(
        None, description="Product ID to look up density from"
    )


class AlcoholConversionResponse(BaseModel):
    """Alcohol conversion response."""

    alcohol_quantity: Decimal
    conversion_factor: Decimal
    quantity_unit: str
    target_unit: str


@router.post("/convert", response_model=UnitConversionResponse)
async def convert_units_endpoint(
    request: UnitConversionRequest, db: Session = Depends(get_db)
):
    """
    Convert quantity between units.

    Supports mass, volume, and cross-type conversions (mass ↔ volume) with density.
    """
    density = request.density_kg_per_l

    # If product_id provided, try to get density from product
    if not density and request.product_id:
        product = db.get(Product, request.product_id)
        if product and product.density_kg_per_l:
            density = product.density_kg_per_l

    try:
        result = convert_units(
            quantity=request.quantity,
            from_unit=request.from_unit,
            to_unit=request.to_unit,
            density_kg_per_l=density,
        )

        return UnitConversionResponse(
            converted_quantity=result.converted_quantity,
            conversion_factor=result.conversion_factor,
            from_unit=result.from_unit,
            to_unit=result.to_unit,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/convert/alcohol", response_model=AlcoholConversionResponse)
async def convert_alcohol_endpoint(
    request: AlcoholConversionRequest, db: Session = Depends(get_db)
):
    """
    Calculate alcohol quantity in a solution.

    Supports calculating alcohol content from volume (L, mL) or mass (kg, g) with ABV.
    """
    solution_density = request.solution_density_kg_per_l

    # If product_id provided, try to get density from product
    if not solution_density and request.product_id:
        product = db.get(Product, request.product_id)
        if product and product.density_kg_per_l:
            solution_density = product.density_kg_per_l

    try:
        result = calculate_alcohol_quantity(
            quantity=request.quantity,
            quantity_unit=request.quantity_unit,
            abv_percent=request.abv_percent,
            solution_density_kg_per_l=solution_density,
            target_unit=request.target_unit,
        )

        return AlcoholConversionResponse(
            alcohol_quantity=result.converted_quantity,
            conversion_factor=result.conversion_factor,
            quantity_unit=result.from_unit,
            target_unit=result.to_unit,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/convert/concentration", response_model=dict)
async def convert_concentration_endpoint(
    value: Decimal = Query(..., ge=0, description="Concentration value to convert"),
    from_type: str = Query(
        ..., description="Source concentration type (ABV_VOL_VOL, WT_PCT, SOLIDS_PCT)"
    ),
    to_type: str = Query(..., description="Target concentration type"),
    solution_density_kg_per_l: Optional[Decimal] = Query(
        None, description="Solution density (required for ABV conversions)"
    ),
    product_id: Optional[str] = Query(
        None, description="Product ID to look up density from"
    ),
    db: Session = Depends(get_db),
):
    """
    Convert between concentration types (ABV, weight%, solids%).

    Supports ABV ↔ weight% conversions (requires solution density).
    """
    density = solution_density_kg_per_l

    # If product_id provided, try to get density from product
    if not density and product_id:
        product = db.get(Product, product_id)
        if product and product.density_kg_per_l:
            density = product.density_kg_per_l

    try:
        converted_value = convert_concentration(
            value=value,
            from_type=from_type,
            to_type=to_type,
            solution_density_kg_per_l=density,
        )

        return {
            "converted_value": converted_value,
            "from_type": from_type,
            "to_type": to_type,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
