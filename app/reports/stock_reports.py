"""Stock reports for SOH valuation, reorder analysis, usage reports."""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_


def generate_stock_valuation_report(active_only: bool = True, db: Session = None) -> List[Dict[str, Any]]:
    """Generate stock valuation report per tpmanu.plan.md Phase 7.3."""
    from app.adapters.db.qb_models import RawMaterial
    
    if db is None:
        return []
    
    stmt = select(RawMaterial).where(RawMaterial.active_flag == "A" if active_only else True)
    stmt = stmt.order_by(RawMaterial.code)
    
    materials = db.execute(stmt).scalars().all()
    
    total_value = Decimal('0.00')
    items = []
    
    for material in materials:
        soh = material.soh or Decimal('0')
        unit_cost = material.usage_cost or Decimal('0')
        value = soh * unit_cost
        total_value += value
        
        items.append({
            'code': material.code,
            'description': f"{material.desc1} {material.desc2 or ''}",
            'soh': float(soh),
            'unit_cost': float(unit_cost),
            'value': float(value),
            'purchase_unit': material.purchase_unit,
            'hazard': material.hazard,
            'condition': material.condition,
            'restock_level': float(material.restock_level or 0)
        })
    
    return {
        'report_date': date.today().isoformat(),
        'total_value': float(total_value),
        'items': items,
        'item_count': len(items)
    }


def generate_reorder_analysis_report(db: Session = None) -> List[Dict[str, Any]]:
    """Generate materials below reorder level report."""
    from app.adapters.db.qb_models import RawMaterial
    
    if db is None:
        return []
    
    stmt = select(RawMaterial).where(
        and_(
            RawMaterial.active_flag == "A",
            RawMaterial.restock_level.isnot(None),
            RawMaterial.soh < RawMaterial.restock_level
        )
    ).order_by(RawMaterial.code)
    
    materials = db.execute(stmt).scalars().all()
    
    items = []
    
    for material in materials:
        soh = material.soh or Decimal('0')
        restock_level = material.restock_level or Decimal('0')
        deficiency = restock_level - soh
        
        items.append({
            'code': material.code,
            'description': f"{material.desc1} {material.desc2 or ''}",
            'soh': float(soh),
            'restock_level': float(restock_level),
            'deficiency': float(deficiency),
            'purchase_cost': float(material.purchase_cost or 0),
            'purchase_unit': material.purchase_unit,
            'supplier': material.sup_unit
        })
    
    return {
        'report_date': date.today().isoformat(),
        'items': items,
        'item_count': len(items)
    }


def generate_usage_report(start_date: date, end_date: date, material_id: Optional[str] = None, db: Session = None) -> List[Dict[str, Any]]:
    """Generate raw material usage report (YTD)."""
    from app.adapters.db.models import BatchComponent, Batch
    from app.adapters.db.qb_models import RawMaterial
    
    if db is None:
        return []
    
    stmt = (
        select(
            RawMaterial.id,
            RawMaterial.code,
            RawMaterial.desc1,
            RawMaterial.desc2,
            func.sum(BatchComponent.quantity_kg).label('total_kg'),
            func.sum(BatchComponent.unit_cost * BatchComponent.quantity_kg).label('total_cost'),
            func.count(BatchComponent.id).label('batch_count')
        )
        .join(BatchComponent, BatchComponent.ingredient_product_id == RawMaterial.id)
        .join(Batch, BatchComponent.batch_id == Batch.id)
        .where(
            and_(
                Batch.completed_at >= datetime.combine(start_date, datetime.min.time()),
                Batch.completed_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
    )
    
    if material_id:
        stmt = stmt.where(RawMaterial.id == material_id)
    
    stmt = stmt.group_by(RawMaterial.id, RawMaterial.code, RawMaterial.desc1, RawMaterial.desc2)
    
    results = db.execute(stmt).all()
    
    return [
        {
            'material_id': str(r.id),
            'code': r.code,
            'description': f"{r.desc1} {r.desc2 or ''}",
            'total_kg': float(r.total_kg or 0),
            'total_cost': float(r.total_cost or 0),
            'batch_count': r.batch_count
        }
        for r in results
    ]


def generate_slow_moving_report(threshold_days: int = 180, db: Session = None) -> List[Dict[str, Any]]:
    """Generate slow-moving stock report."""
    from datetime import timedelta
    from app.adapters.db.qb_models import RawMaterial
    
    if db is None:
        return []
    
    cutoff_date = datetime.now() - timedelta(days=threshold_days)
    
    stmt = select(RawMaterial).where(
        and_(
            RawMaterial.active_flag == "A",
            RawMaterial.soh > 0
        )
    )
    
    materials = db.execute(stmt).scalars().all()
    
    slow_moving = []
    
    for material in materials:
        last_movement = material.last_movement_date
        if not last_movement:
            slow_moving.append({
                'code': material.code,
                'description': f"{material.desc1} {material.desc2 or ''}",
                'soh': float(material.soh or 0),
                'soh_value': float((material.soh or 0) * (material.usage_cost or 0)),
                'last_movement': 'N/A',
                'days_since_movement': 'N/A'
            })
            continue
        
        # Parse last_movement_date (format: YYYYMMDD)
        try:
            move_date = datetime.strptime(last_movement, '%Y%m%d')
            days_ago = (datetime.now() - move_date).days
            
            if days_ago > threshold_days:
                slow_moving.append({
                    'code': material.code,
                    'description': f"{material.desc1} {material.desc2 or ''}",
                    'soh': float(material.soh or 0),
                    'soh_value': float((material.soh or 0) * (material.usage_cost or 0)),
                    'last_movement': last_movement,
                    'days_since_movement': days_ago
                })
        except:
            pass
    
    return {
        'report_date': date.today().isoformat(),
        'threshold_days': threshold_days,
        'items': slow_moving,
        'item_count': len(slow_moving),
        'total_value': sum(item['soh_value'] for item in slow_moving)
    }

