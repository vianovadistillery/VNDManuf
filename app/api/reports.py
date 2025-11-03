# app/api/reports.py
"""Reports API router."""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import Batch, BatchComponent, Formula, FormulaLine
from app.adapters.db.qb_models import RawMaterial

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/raw-materials/usage")
async def raw_material_usage_report(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    material_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Raw material usage report with YTD usage and costs.
    Returns summary by raw material for given date range.
    """
    # Query batch components in date range
    stmt = (
        select(
            RawMaterial.id,
            RawMaterial.code,
            RawMaterial.desc1,
            RawMaterial.desc2,
            func.sum(BatchComponent.quantity_kg).label("total_kg"),
            func.sum(BatchComponent.unit_cost * BatchComponent.quantity_kg).label(
                "total_cost"
            ),
            func.count(BatchComponent.id).label("batch_count"),
        )
        .join(BatchComponent, BatchComponent.ingredient_product_id == RawMaterial.id)
        .join(Batch, BatchComponent.batch_id == Batch.id)
        .where(
            and_(
                Batch.completed_at >= datetime.combine(start_date, datetime.min.time()),
                Batch.completed_at <= datetime.combine(end_date, datetime.max.time()),
            )
        )
    )

    if material_id:
        stmt = stmt.where(RawMaterial.id == material_id)

    stmt = stmt.group_by(
        RawMaterial.id, RawMaterial.code, RawMaterial.desc1, RawMaterial.desc2
    )

    results = db.execute(stmt).all()

    return [
        {
            "material_id": str(r.id),
            "code": r.code,
            "description": f"{r.desc1} {r.desc2 or ''}",
            "total_kg": float(r.total_kg),
            "total_cost": float(r.total_cost),
            "batch_count": r.batch_count,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
        }
        for r in results
    ]


@router.get("/formulas/cost-analysis")
async def formula_cost_analysis(
    formula_code: str, revision: Optional[int] = None, db: Session = Depends(get_db)
):
    """
    Formula cost analysis - raw cost breakdown per line.
    Calculates theoretical cost for a formula.
    """
    # Get formula
    stmt = select(Formula).where(Formula.formula_code == formula_code)
    if revision:
        stmt = stmt.where(Formula.version == revision)
    else:
        stmt = stmt.order_by(Formula.version.desc())

    formula = db.execute(stmt).scalar_one_or_none()

    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Formula {formula_code} revision {revision or 'latest'} not found",
        )

    # Get formula lines with raw material costs
    stmt = (
        select(
            FormulaLine.id,
            FormulaLine.sequence,
            RawMaterial.code,
            RawMaterial.desc1,
            FormulaLine.quantity_kg,
            RawMaterial.usage_cost,
            (FormulaLine.quantity_kg * RawMaterial.usage_cost).label("line_cost"),
        )
        .join(RawMaterial, FormulaLine.ingredient_product_id == RawMaterial.id)
        .where(FormulaLine.formula_id == formula.id)
        .order_by(FormulaLine.sequence)
    )

    lines = db.execute(stmt).all()

    total_cost = sum(float(line.line_cost or 0) for line in lines)

    return {
        "formula_code": formula_code,
        "revision": formula.version,
        "formula_name": formula.formula_name,
        "theoretical_cost": total_cost,
        "lines": [
            {
                "sequence": line.sequence,
                "material_code": line.code,
                "material_desc": line.desc1,
                "quantity_kg": float(line.quantity_kg),
                "unit_cost": float(line.usage_cost or 0),
                "line_cost": float(line.line_cost or 0),
            }
            for line in lines
        ],
        "analysis_date": datetime.utcnow().isoformat(),
    }


@router.get("/batch-history")
async def batch_history_report(
    formula_code: Optional[str] = None,
    year: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Batch history report with variance analysis.
    Shows planned vs actual for batches.
    """
    stmt = select(Batch)

    # Filter by year (batch_code format: YYNNNN)
    if year:
        stmt = stmt.where(Batch.batch_code.like(f"{year}%"))

    # Filter by status
    if status:
        stmt = stmt.where(Batch.status == status.upper())

    # Filter by formula (would need JOIN with WorkOrder → Product → Formula)
    # For now, return all

    stmt = stmt.order_by(Batch.created_at.desc()).limit(100)
    batches = db.execute(stmt).scalars().all()

    return [
        {
            "batch_id": str(b.id),
            "batch_code": b.batch_code,
            "work_order_id": str(b.work_order_id),
            "quantity_kg": float(b.quantity_kg),
            "yield_actual": float(b.yield_actual) if b.yield_actual else None,
            "yield_litres": float(b.yield_litres) if b.yield_litres else None,
            "variance_percent": float(b.variance_percent)
            if b.variance_percent
            else None,
            "status": b.status,
            "started_at": b.started_at.isoformat() if b.started_at else None,
            "completed_at": b.completed_at.isoformat() if b.completed_at else None,
        }
        for b in batches
    ]


@router.get("/stock-valuation")
async def stock_valuation_report(
    active_only: bool = Query(True), db: Session = Depends(get_db)
):
    """
    Stock valuation report showing SOH value per raw material.
    """
    stmt = (
        select(
            RawMaterial.id,
            RawMaterial.code,
            RawMaterial.desc1,
            RawMaterial.desc2,
            RawMaterial.soh,
            RawMaterial.usage_cost,
            (RawMaterial.soh * RawMaterial.usage_cost).label("value"),
        )
        .where(RawMaterial.active_flag == "A" if active_only else True)
        .order_by(RawMaterial.code)
    )

    results = db.execute(stmt).all()

    total_value = sum(float(r.value or 0) for r in results)

    return {
        "report_date": datetime.utcnow().isoformat(),
        "total_value": total_value,
        "items": [
            {
                "material_id": str(r.id),
                "code": r.code,
                "description": f"{r.desc1} {r.desc2 or ''}",
                "soh": float(r.soh or 0),
                "unit_cost": float(r.usage_cost or 0),
                "value": float(r.value or 0),
            }
            for r in results
        ],
    }


@router.get("/reorder-analysis")
async def reorder_analysis_report(db: Session = Depends(get_db)):
    """
    Report on raw materials below reorder level.
    """
    stmt = (
        select(RawMaterial)
        .where(
            and_(
                RawMaterial.active_flag == "A",
                RawMaterial.restock_level.isnot(None),
                RawMaterial.soh < RawMaterial.restock_level,
            )
        )
        .order_by(RawMaterial.code)
    )

    results = db.execute(stmt).scalars().all()

    return [
        {
            "material_id": str(r.id),
            "code": r.code,
            "description": f"{r.desc1} {r.desc2 or ''}",
            "soh": float(r.soh or 0),
            "restock_level": float(r.restock_level or 0),
            "deficiency": float((r.restock_level or 0) - (r.soh or 0)),
            "purchase_cost": float(r.purchase_cost or 0),
            "purchase_unit": r.purchase_unit,
        }
        for r in results
    ]
