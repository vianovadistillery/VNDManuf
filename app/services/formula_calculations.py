"""
Formula calculation services for theoretical costs, yields, and variances.
Per Phase 6.1 of tpmanu.plan.md
"""

from decimal import Decimal
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.adapters.db import get_db
from app.adapters.db.models import Formula, FormulaLine, Product
from app.adapters.db.qb_models import RawMaterial


def calculate_theoretical_cost(formula_id: str, db: Session) -> Decimal:
    """
    Calculate theoretical cost for a formula.
    Sum of (line.quantity_kg * raw_material.usage_cost) for all lines.
    """
    stmt = (
        select(
            func.sum(FormulaLine.quantity_kg * RawMaterial.usage_cost)
        )
        .join(RawMaterial, FormulaLine.ingredient_product_id == RawMaterial.id)
        .where(FormulaLine.formula_id == formula_id)
    )
    
    result = db.execute(stmt).scalar()
    return Decimal(str(result)) if result else Decimal('0.00')


def calculate_theoretical_cost_per_line(formula_id: str, db: Session) -> Dict[str, Decimal]:
    """
    Calculate cost per formula line.
    Returns dict mapping line_id to cost.
    """
    stmt = (
        select(
            FormulaLine.id,
            (FormulaLine.quantity_kg * RawMaterial.usage_cost).label('line_cost')
        )
        .join(RawMaterial, FormulaLine.ingredient_product_id == RawMaterial.id)
        .where(FormulaLine.formula_id == formula_id)
    )
    
    results = db.execute(stmt).all()
    
    return {
        str(line.id): Decimal(str(line.line_cost)) if line.line_cost else Decimal('0.00')
        for line in results
    }


def calculate_theoretical_yield(formula_id: str, db: Session) -> Dict[str, Decimal]:
    """
    Calculate theoretical yield considering SG (specific gravity).
    Returns dict with 'kg' and 'litres' keys.
    """
    # Sum of line quantities (kg)
    stmt_kg = (
        select(func.sum(FormulaLine.quantity_kg))
        .where(FormulaLine.formula_id == formula_id)
    )
    total_kg = db.execute(stmt_kg).scalar()
    total_kg = Decimal(str(total_kg)) if total_kg else Decimal('0.000')
    
    # Calculate litres using weighted average SG
    stmt_sg = (
        select(
            func.sum(FormulaLine.quantity_kg * RawMaterial.sg).label('weighted_sg'),
            func.sum(FormulaLine.quantity_kg).label('total_qty')
        )
        .join(RawMaterial, FormulaLine.ingredient_product_id == RawMaterial.id)
        .where(FormulaLine.formula_id == formula_id)
    )
    
    result_sg = db.execute(stmt_sg).first()
    
    if result_sg and result_sg.total_qty and result_sg.total_qty > 0:
        avg_sg = (result_sg.weighted_sg or Decimal('0')) / result_sg.total_qty
        total_litres = total_kg / avg_sg if avg_sg > 0 else Decimal('0.000')
    else:
        total_litres = Decimal('0.000')
    
    return {
        'kg': total_kg,
        'litres': total_litres
    }


def calculate_batch_variance(batch_id: str, db: Session) -> Dict[str, Optional[Decimal]]:
    """
    Calculate variance between actual and theoretical batch results.
    Returns dict with yield variance, cost variance, and percentages.
    """
    from app.adapters.db.models import Batch
    
    batch = db.get(Batch, batch_id)
    if not batch:
        raise ValueError(f"Batch {batch_id} not found")
    
    # For now, use quantity_kg as theoretical
    # TODO: Link to formula to get true theoretical yields
    theoretical_kg = batch.quantity_kg
    actual_kg = batch.yield_actual
    
    if theoretical_kg and actual_kg:
        yield_var_kg = actual_kg - theoretical_kg
        yield_var_pct = (yield_var_kg / theoretical_kg * 100) if theoretical_kg > 0 else Decimal('0.00')
    else:
        yield_var_kg = None
        yield_var_pct = None
    
    return {
        'yield_variance_pct': yield_var_pct,
        'yield_variance_kg': yield_var_kg,
        'cost_variance': None  # TODO: calculate from batch components
    }


def validate_formula_lines(formula_id: str, db: Session) -> Dict[str, any]:
    """
    Validate formula lines for completeness and correctness.
    Returns validation result with missing materials, etc.
    """
    stmt = (
        select(FormulaLine)
        .where(FormulaLine.formula_id == formula_id)
        .order_by(FormulaLine.sequence)
    )
    
    lines = db.execute(stmt).scalars().all()
    
    issues = []
    warnings = []
    
    # Check each line
    for line in lines:
        material = db.get(RawMaterial, line.ingredient_product_id)
        
        if not material:
            issues.append(f"Line {line.sequence}: Material {line.ingredient_product_id} not found")
        
        if material:
            if not material.usage_cost:
                warnings.append(f"Line {line.sequence}: Material {material.desc1} has no usage cost")
            
            if not material.sg:
                warnings.append(f"Line {line.sequence}: Material {material.desc1} has no SG value")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'line_count': len(lines)
    }

