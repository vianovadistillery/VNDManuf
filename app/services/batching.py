# app/services/batching.py
"""Batching service - Core manufacturing batch lifecycle operations."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.adapters.db.models import (
    Batch, BatchComponent, WorkOrder, Formula, FormulaLine, Product,
    InventoryLot, InventoryTxn, QcResult
)
from app.adapters.db.qb_models import RawMaterial
from app.domain.rules import fifo_issue, FifoIssue, round_quantity, validate_non_negative_lot


class BatchingService:
    """
    Service for batch lifecycle operations: create, release, issue, finish.
    Handles FIFO consumption, component explosion, QC capture, and FG receipt.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_batch(self, work_order_id: str, qty_target_kg: Decimal, batch_code: str) -> Batch:
        """
        Create a new batch from a work order.
        
        Args:
            work_order_id: Work order ID
            qty_target_kg: Target quantity for the batch
            batch_code: Batch code
            
        Returns:
            Created Batch
            
        Raises:
            ValueError: If work order not found or batch code already exists
        """
        # Validate work order exists
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")
        
        # Check for duplicate batch code
        existing = self.db.execute(
            select(Batch).where(
                Batch.work_order_id == work_order_id,
                Batch.batch_code == batch_code
            )
        ).scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Batch code '{batch_code}' already exists for work order")
        
        # Create batch in DRAFT status
        batch = Batch(
            id=str(uuid4()),
            work_order_id=work_order_id,
            batch_code=batch_code,
            quantity_kg=round_quantity(qty_target_kg),
            status="DRAFT",
            batch_status="planned"
        )
        
        self.db.add(batch)
        self.db.flush()
        
        return batch
    
    def release_batch(self, batch_id: str) -> Batch:
        """
        Release a batch: freeze formula version and explode components.
        
        This creates batch components for planning but does not consume inventory yet.
        Inventory is consumed when components are issued.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            Updated Batch
            
        Raises:
            ValueError: If batch not found or not in valid status
        """
        batch = self.db.get(Batch, batch_id)
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")
        
        if batch.status != "DRAFT":
            raise ValueError(f"Cannot release batch with status '{batch.status}'")
        
        # Freeze formula version by getting work order formula
        work_order = batch.work_order
        if not work_order:
            raise ValueError("Work order not found for batch")
        
        formula = work_order.formula
        if not formula:
            raise ValueError(f"No formula found for work order {work_order.id}")
        
        # Explode formula lines into batch components (planning only)
        formula_lines = self.db.execute(
            select(FormulaLine).where(
                FormulaLine.formula_id == formula.id
            ).order_by(FormulaLine.sequence)
        ).scalars().all()
        
        if not formula_lines:
            raise ValueError(f"No formula lines found for formula {formula.id}")
        
        # Calculate scale factor (batch qty / formula base qty)
        # For now, assume formula base quantity is 1:1 with batch target
        scale_factor = batch.quantity_kg / Decimal("100")  # Assume 100 kg base formula
        
        # Create batch components from formula
        for formula_line in formula_lines:
            raw_material = formula_line.raw_material
            if not raw_material:
                continue
            
            # Scale required quantity
            required_qty = round_quantity(formula_line.quantity_kg * scale_factor)
            
            # Find the best lot for this component (will be consumed later on issue)
            # For now, just mark the component quantity - lot allocation happens on issue
            lots = self.db.execute(
                select(InventoryLot).where(
                    InventoryLot.product_id == raw_material.id,
                    InventoryLot.is_active == True,
                    InventoryLot.quantity_kg > 0
                ).order_by(InventoryLot.received_at.asc())
            ).scalars().first()  # Get oldest lot for now
            
            if not lots:
                raise ValueError(f"No inventory available for ingredient {raw_material.code}")
            
            # Check sufficient quantity exists
            total_available = sum(
                lot.quantity_kg for lot in self.db.execute(
                    select(InventoryLot).where(
                        InventoryLot.product_id == raw_material.id,
                        InventoryLot.is_active == True
                    )
                ).scalars().all()
            )
            
            if total_available < required_qty:
                raise ValueError(
                    f"Insufficient stock: ingredient {raw_material.code} "
                    f"requires {required_qty} kg, available {total_available} kg"
                )
            
            # Create batch component (planned, not yet consumed)
            # Actual lot consumption happens during issue_component
            component = BatchComponent(
                id=str(uuid4()),
                batch_id=batch.id,
                ingredient_product_id=raw_material.id,
                lot_id=lots.id,  # Use oldest lot by default
                quantity_kg=required_qty,
                unit_cost=lots.unit_cost
            )
            self.db.add(component)
        
        # Update batch status
        batch.status = "RELEASED"
        batch.batch_status = "in_process"
        batch.started_at = datetime.utcnow()
        
        self.db.flush()
        return batch
    
    def issue_component(self, batch_id: str, component_id: str, qty_kg: Decimal) -> List[FifoIssue]:
        """
        Issue component from inventory using FIFO.
        
        Args:
            batch_id: Batch ID
            component_id: Component ID
            qty_kg: Quantity to issue
            
        Returns:
            List of FIFO issue results
            
        Raises:
            ValueError: If component not found or insufficient stock
        """
        # Get batch component
        component = self.db.get(BatchComponent, component_id)
        if not component:
            raise ValueError(f"Batch component {component_id} not found")
        
        if component.batch_id != batch_id:
            raise ValueError("Component does not belong to this batch")
        
        # Get lot
        lot = self.db.get(InventoryLot, component.lot_id)
        if not lot:
            raise ValueError(f"Inventory lot {component.lot_id} not found")
        
        # Check sufficient stock
        if lot.quantity_kg < qty_kg:
            raise ValueError(
                f"Insufficient stock: lot {lot.lot_code} has {lot.quantity_kg} kg, "
                f"required {qty_kg} kg"
            )
        
        # Issue from inventory
        lot.quantity_kg -= qty_kg
        validate_non_negative_lot(lot, override=False)
        
        # Write transaction
        txn = InventoryTxn(
            id=str(uuid4()),
            lot_id=lot.id,
            transaction_type="ISSUE",
            quantity_kg=-abs(qty_kg),  # Negative for issues
            unit_cost=lot.unit_cost,
            reference_type="BATCH",
            reference_id=batch_id,
            notes=f"Batch {component.batch_id} component issue",
            created_at=datetime.utcnow()
        )
        self.db.add(txn)
        self.db.flush()
        
        return [
            FifoIssue(
                lot_id=lot.id,
                quantity_kg=qty_kg,
                unit_cost=lot.unit_cost,
                remaining_quantity_kg=lot.quantity_kg
            )
        ]
    
    def finish_batch(
        self, 
        batch_id: str, 
        qty_fg_kg: Optional[Decimal] = None,
        lot_code: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Batch:
        """
        Finish a batch: create FG lot and receipt transaction.
        
        Args:
            batch_id: Batch ID
            qty_fg_kg: Finished goods quantity (defaults to batch target)
            lot_code: Lot code for finished goods
            notes: Optional notes
            
        Returns:
            Updated Batch
            
        Raises:
            ValueError: If batch not found or not in valid status
        """
        batch = self.db.get(Batch, batch_id)
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")
        
        if batch.status not in ["RELEASED", "IN_PROGRESS"]:
            raise ValueError(f"Cannot finish batch with status '{batch.status}'")
        
        # Get work order and product
        work_order = batch.work_order
        if not work_order:
            raise ValueError("Work order not found for batch")
        
        product = work_order.product
        if not product:
            raise ValueError("Product not found for work order")
        
        # Use target qty if not specified
        if qty_fg_kg is None:
            qty_fg_kg = batch.quantity_kg
        else:
            qty_fg_kg = round_quantity(qty_fg_kg)
        
        # Generate lot code if not provided
        if not lot_code:
            lot_code = f"FG-{batch.batch_code}"
        
        # Create finished goods lot
        fg_lot = InventoryLot(
            id=str(uuid4()),
            product_id=product.id,
            lot_code=lot_code,
            quantity_kg=qty_fg_kg,
            unit_cost=self._calculate_batch_cost(batch),
            received_at=datetime.utcnow(),
            is_active=True
        )
        self.db.add(fg_lot)
        self.db.flush()
        
        # Write RECEIPT transaction
        receipt_txn = InventoryTxn(
            id=str(uuid4()),
            lot_id=fg_lot.id,
            transaction_type="RECEIPT",
            quantity_kg=qty_fg_kg,
            unit_cost=fg_lot.unit_cost,
            reference_type="BATCH",
            reference_id=batch.id,
            notes=f"Finished goods from batch {batch.batch_code}",
            created_at=datetime.utcnow()
        )
        self.db.add(receipt_txn)
        
        # Update batch status
        batch.status = "COMPLETED"
        batch.batch_status = "closed"
        batch.completed_at = datetime.utcnow()
        
        if notes:
            batch.notes = (batch.notes or "") + f"\nFinish: {notes}"
        
        self.db.flush()
        return batch
    
    def record_qc_result(
        self,
        batch_id: str,
        test_name: str,
        test_value: Optional[Decimal],
        test_unit: Optional[str],
        pass_fail: Optional[bool],
        notes: Optional[str] = None
    ) -> QcResult:
        """
        Record QC test result for a batch.
        
        Args:
            batch_id: Batch ID
            test_name: Test name
            test_value: Test value
            test_unit: Test unit
            pass_fail: Pass/fail result
            notes: Optional notes
            
        Returns:
            Created QcResult
            
        Raises:
            ValueError: If batch not found
        """
        batch = self.db.get(Batch, batch_id)
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")
        
        # Round value if provided
        if test_value is not None:
            test_value = round_quantity(test_value)
        
        qc_result = QcResult(
            id=str(uuid4()),
            batch_id=batch_id,
            test_name=test_name,
            test_value=test_value,
            test_unit=test_unit,
            pass_fail=pass_fail,
            tested_at=datetime.utcnow(),
            notes=notes
        )
        
        self.db.add(qc_result)
        self.db.flush()
        
        return qc_result
    
    def _calculate_batch_cost(self, batch: Batch) -> Decimal:
        """
        Calculate batch cost from component costs.
        
        Args:
            batch: Batch
            
        Returns:
            Calculated unit cost per kg
        """
        if not batch.components:
            return Decimal("0")
        
        total_cost = sum(
            comp.quantity_kg * (comp.unit_cost or Decimal("0"))
            for comp in batch.components
        )
        
        total_qty = sum(comp.quantity_kg for comp in batch.components)
        
        if total_qty > 0:
            return round_quantity(total_cost / total_qty)
        else:
            return Decimal("0")


def create_batch(work_order_id: str, qty_target_kg: Decimal, batch_code: str, db: Session) -> Batch:
    """Convenience function to create a batch."""
    service = BatchingService(db)
    return service.create_batch(work_order_id, qty_target_kg, batch_code)


def release_batch(batch_id: str, db: Session) -> Batch:
    """Convenience function to release a batch."""
    service = BatchingService(db)
    return service.release_batch(batch_id)


def finish_batch(
    batch_id: str,
    qty_fg_kg: Optional[Decimal] = None,
    lot_code: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = None
) -> Batch:
    """Convenience function to finish a batch."""
    service = BatchingService(db)
    return service.finish_batch(batch_id, qty_fg_kg, lot_code, notes)
