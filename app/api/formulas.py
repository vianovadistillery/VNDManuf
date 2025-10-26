# app/api/formulas.py
"""Formulas API router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.adapters.db import get_db
from app.adapters.db.models import Formula, FormulaLine, Product
from app.adapters.db.qb_models import RawMaterial
from app.api.dto import ErrorResponse
from app.error_handlers import BusinessRuleViolation

router = APIRouter(prefix="/formulas", tags=["formulas"])


# Request/Response DTOs
class FormulaLineCreate(BaseModel):
    """Create formula line request."""
    raw_material_id: str
    quantity_kg: float
    sequence: int
    notes: Optional[str] = None
    unit: Optional[str] = None  # Display unit (kg, g, L, mL, etc.)


class FormulaLineResponse(BaseModel):
    """Formula line response."""
    id: str
    formula_id: str
    raw_material_id: str
    quantity_kg: float
    sequence: int
    notes: Optional[str]
    unit: Optional[str] = None  # Display unit (kg, g, L, mL, etc.)
    
    ingredient_name: Optional[str] = None


class FormulaCreate(BaseModel):
    """Create formula request."""
    product_id: str
    formula_code: str
    formula_name: str
    version: int = 1
    is_active: bool = True
    lines: List[FormulaLineCreate] = []


class FormulaResponse(BaseModel):
    """Formula response."""
    id: str
    product_id: str
    formula_code: str
    formula_name: str
    version: int
    is_active: bool
    created_at: str
    updated_at: str
    
    product_name: Optional[str] = None
    lines: List[FormulaLineResponse] = []


def formula_to_response(f: Formula, db: Session) -> FormulaResponse:
    """Convert Formula model to response DTO."""
    # Load lines with raw material relationship
    stmt = select(FormulaLine).options(joinedload(FormulaLine.raw_material)).where(FormulaLine.formula_id == f.id).order_by(FormulaLine.sequence)
    lines = db.execute(stmt).scalars().unique().all()
    
    product = db.get(Product, f.product_id)
    
    return FormulaResponse(
        id=str(f.id),
        product_id=f.product_id,
        product_name=product.name if product else None,
        formula_code=f.formula_code,
        formula_name=f.formula_name,
        version=f.version,
        is_active=f.is_active,
        created_at=f.created_at.isoformat(),
        updated_at=f.updated_at.isoformat(),
        lines=[
            FormulaLineResponse(
                id=str(line.id),
                formula_id=str(line.formula_id),
                raw_material_id=line.raw_material_id,
                quantity_kg=float(line.quantity_kg),
                sequence=line.sequence,
                notes=line.notes,
                unit=line.unit,
                ingredient_name=f"{line.raw_material.desc1} {line.raw_material.desc2}".strip() if line.raw_material else None
            )
            for line in lines
        ]
    )


@router.get("/", response_model=List[FormulaResponse])
async def list_formulas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    product_id: Optional[str] = None,
    formula_code: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List formulas with optional filtering."""
    stmt = select(Formula)
    
    # Filter by product
    if product_id:
        stmt = stmt.where(Formula.product_id == product_id)
    
    # Filter by code
    if formula_code:
        stmt = stmt.where(Formula.formula_code.contains(formula_code))
    
    # Filter by active status
    if is_active is not None:
        stmt = stmt.where(Formula.is_active == is_active)
    
    stmt = stmt.order_by(Formula.formula_code, Formula.version.desc()).offset(skip).limit(limit)
    formulas = db.execute(stmt).scalars().all()
    
    return [formula_to_response(f, db) for f in formulas]


@router.get("/{formula_id}", response_model=FormulaResponse)
async def get_formula(formula_id: str, db: Session = Depends(get_db)):
    """Get formula by ID."""
    formula = db.get(Formula, formula_id)
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formula not found"
        )
    
    return formula_to_response(formula, db)


@router.get("/code/{code}/versions", response_model=List[FormulaResponse])
async def get_formula_versions(code: str, db: Session = Depends(get_db)):
    """Get all versions of a formula."""
    stmt = select(Formula).where(Formula.formula_code == code).order_by(Formula.version.desc())
    formulas = db.execute(stmt).scalars().all()
    
    if not formulas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Formula {code} not found"
        )
    
    return [formula_to_response(f, db) for f in formulas]


@router.get("/code/{code}/version/{version}", response_model=FormulaResponse)
async def get_formula_version(code: str, version: int, db: Session = Depends(get_db)):
    """Get specific version of a formula."""
    stmt = select(Formula).where(
        Formula.formula_code == code,
        Formula.version == version
    )
    formula = db.execute(stmt).scalar_one_or_none()
    
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Formula {code} version {version} not found"
        )
    
    return formula_to_response(formula, db)


@router.post("/", response_model=FormulaResponse, status_code=status.HTTP_201_CREATED)
async def create_formula(
    formula_data: FormulaCreate,
    db: Session = Depends(get_db)
):
    """Create a new formula with lines."""
    # Validate product exists
    product = db.get(Product, formula_data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {formula_data.product_id} not found"
        )
    
    # Check if code/version exists
    existing = db.execute(
        select(Formula).where(
            Formula.product_id == formula_data.product_id,
            Formula.formula_code == formula_data.formula_code,
            Formula.version == formula_data.version
        )
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Formula {formula_data.formula_code} version {formula_data.version} already exists"
        )
    
    # Create formula
    import uuid
    formula = Formula(
        id=str(uuid.uuid4()),
        product_id=formula_data.product_id,
        formula_code=formula_data.formula_code,
        formula_name=formula_data.formula_name,
        version=formula_data.version,
        is_active=formula_data.is_active
    )
    db.add(formula)
    db.flush()  # Get formula.id
    
    # Create lines
    for line_data in formula_data.lines:
        # Validate raw material exists
        raw_material = db.get(RawMaterial, line_data.raw_material_id)
        if not raw_material:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Raw material {line_data.raw_material_id} not found"
            )
        
        line = FormulaLine(
            id=str(uuid.uuid4()),
            formula_id=formula.id,
            raw_material_id=line_data.raw_material_id,
            quantity_kg=line_data.quantity_kg,
            sequence=line_data.sequence,
            notes=line_data.notes,
            unit=line_data.unit
        )
        db.add(line)
    
    db.commit()
    db.refresh(formula)
    
    return formula_to_response(formula, db)


@router.post("/{formula_id}/new-version", response_model=FormulaResponse, status_code=status.HTTP_201_CREATED)
async def create_formula_revision(
    formula_id: str,
    revision_data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Clone formula as new revision."""
    # Get original formula
    original = db.get(Formula, formula_id)
    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formula not found"
        )
    
    # Get latest version
    stmt = select(Formula).where(
        Formula.formula_code == original.formula_code
    ).order_by(Formula.version.desc())
    latest = db.execute(stmt).scalar_one_or_none()
    
    new_version = latest.version + 1 if latest else 1
    
    # Create new revision
    import uuid
    new_formula = Formula(
        id=str(uuid.uuid4()),
        product_id=original.product_id,
        formula_code=original.formula_code,
        formula_name=revision_data.get('formula_name', original.formula_name) if revision_data else original.formula_name,
        version=new_version,
        is_active=True
    )
    db.add(new_formula)
    db.flush()
    
    # Copy lines
    old_lines = db.execute(
        select(FormulaLine).where(FormulaLine.formula_id == original.id)
    ).scalars().all()
    
    for old_line in old_lines:
        new_line = FormulaLine(
            id=str(uuid.uuid4()),
            formula_id=new_formula.id,
            raw_material_id=old_line.raw_material_id,
            quantity_kg=old_line.quantity_kg,
            sequence=old_line.sequence,
            notes=old_line.notes,
            unit=old_line.unit
        )
        db.add(new_line)
    
    db.commit()
    db.refresh(new_formula)
    
    return formula_to_response(new_formula, db)


@router.put("/{formula_id}", response_model=FormulaResponse)
async def update_formula(
    formula_id: str,
    formula_data: dict,
    db: Session = Depends(get_db)
):
    """Update formula (header only; lines managed separately)."""
    formula = db.get(Formula, formula_id)
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formula not found"
        )
    
    # Update fields
    if 'formula_name' in formula_data:
        formula.formula_name = formula_data['formula_name']
    if 'is_active' in formula_data:
        formula.is_active = formula_data['is_active']
    
    db.commit()
    db.refresh(formula)
    
    return formula_to_response(formula, db)


@router.put("/{formula_id}/lines", response_model=FormulaResponse)
async def replace_formula_lines(
    formula_id: str,
    lines_data: List[FormulaLineCreate],
    db: Session = Depends(get_db)
):
    """Replace all lines in a formula."""
    formula = db.get(Formula, formula_id)
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formula not found"
        )
    
    # Delete existing lines
    stmt = select(FormulaLine).where(FormulaLine.formula_id == formula.id)
    existing_lines = db.execute(stmt).scalars().all()
    for line in existing_lines:
        db.delete(line)
    
    # Commit the deletions before adding new lines
    db.flush()
    
    # Add new lines
    import uuid
    for line_data in lines_data:
        # Validate raw material exists
        raw_material = db.get(RawMaterial, line_data.raw_material_id)
        if not raw_material:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Raw material {line_data.raw_material_id} not found"
            )
        
        line = FormulaLine(
            id=str(uuid.uuid4()),
            formula_id=formula.id,
            raw_material_id=line_data.raw_material_id,
            quantity_kg=line_data.quantity_kg,
            sequence=line_data.sequence,
            notes=line_data.notes,
            unit=line_data.unit
        )
        db.add(line)
    
    db.commit()
    db.refresh(formula)
    
    return formula_to_response(formula, db)


@router.delete("/{formula_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_formula(formula_id: str, db: Session = Depends(get_db)):
    """Delete formula (and its lines)."""
    formula = db.get(Formula, formula_id)
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formula not found"
        )
    
    # Delete lines
    stmt = select(FormulaLine).where(FormulaLine.formula_id == formula.id)
    lines = db.execute(stmt).scalars().all()
    for line in lines:
        db.delete(line)
    
    db.delete(formula)
    db.commit()

