# app/services/batch_reporting.py
"""Service for batch reporting and data retrieval."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.adapters.db.models import (
    Batch, BatchComponent, QcResult, WorkOrder, Product, Formula, FormulaLine,
    InventoryLot, ProductVariant
)


class BatchReportingService:
    """Service for retrieving batch data for reporting."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_batch_data(self, batch_code: str) -> Optional[Dict[str, Any]]:
        """Get complete batch data for reporting."""
        # Query batch with all related data using joinedload for efficiency
        stmt = (
            select(Batch)
            .where(Batch.batch_code == batch_code)
            .options(
                joinedload(Batch.work_order).joinedload(WorkOrder.product),
                joinedload(Batch.work_order).joinedload(WorkOrder.formula),
                joinedload(Batch.components).joinedload(BatchComponent.ingredient_product),
                joinedload(Batch.components).joinedload(BatchComponent.lot),
                joinedload(Batch.qc_results)
            )
        )
        batch = self.db.execute(stmt).scalar_one_or_none()
        
        if not batch:
            return None
        
        work_order = batch.work_order
        product = work_order.product if work_order else None
        formula = work_order.formula if work_order else None
        
        # Get formula lines with ingredient products
        formula_lines = []
        if formula:
            formula_lines_stmt = (
                select(FormulaLine)
                .where(FormulaLine.formula_id == formula.id)
                .options(joinedload(FormulaLine.ingredient_product))
                .order_by(FormulaLine.sequence)
            )
            formula_lines = self.db.execute(formula_lines_stmt).scalars().all()
        
        # Get product variants if any
        variants = []
        if product:
            variants_stmt = (
                select(ProductVariant)
                .where(ProductVariant.product_id == product.id)
                .where(ProductVariant.is_active == True)
            )
            variants = self.db.execute(variants_stmt).scalars().all()
        
        return {
            'batch': batch,
            'work_order': work_order,
            'product': product,
            'formula': formula,
            'components': batch.components,
            'qc_results': batch.qc_results,
            'formula_lines': formula_lines,
            'variants': variants,
        }
    
    def get_batch_summary(self, batch_code: str) -> Optional[Dict[str, Any]]:
        """Get batch summary data for quick reporting."""
        batch_data = self.get_batch_data(batch_code)
        if not batch_data:
            return None
        
        batch = batch_data['batch']
        product = batch_data['product']
        formula = batch_data['formula']
        components = batch_data['components']
        
        # Calculate totals
        total_components = len(components)
        total_quantity_kg = sum(comp.quantity_kg for comp in components)
        
        # Get QC summary
        qc_results = batch_data['qc_results']
        qc_summary = {
            'total_tests': len(qc_results),
            'passed_tests': sum(1 for qc in qc_results if qc.pass_fail is True),
            'failed_tests': sum(1 for qc in qc_results if qc.pass_fail is False),
        }
        
        return {
            'batch_code': batch.batch_code,
            'product_name': product.name if product else 'Unknown',
            'formula_code': formula.formula_code if formula else 'Unknown',
            'formula_version': formula.version if formula else 0,
            'batch_quantity_kg': batch.quantity_kg,
            'status': batch.status,
            'started_at': batch.started_at,
            'completed_at': batch.completed_at,
            'total_components': total_components,
            'total_component_quantity_kg': total_quantity_kg,
            'qc_summary': qc_summary,
        }


def get_batch_data_for_reporting(batch_code: str, db: Session) -> Optional[Dict[str, Any]]:
    """Convenience function to get batch data."""
    service = BatchReportingService(db)
    return service.get_batch_data(batch_code)


def get_batch_summary_for_reporting(batch_code: str, db: Session) -> Optional[Dict[str, Any]]:
    """Convenience function to get batch summary."""
    service = BatchReportingService(db)
    return service.get_batch_summary(batch_code)
