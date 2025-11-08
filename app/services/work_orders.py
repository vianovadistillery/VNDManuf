# app/services/work_orders.py
"""Work Order Service - Core manufacturing work order lifecycle operations."""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db.models import (
    Batch,
    Formula,
    FormulaLine,
    InventoryMovement,
    Product,
    ProductCostRate,
    QcTestType,
    WoQcTest,
    WorkOrder,
    WorkOrderLine,
    WorkOrderOutput,
    WoTimer,
)
from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyLine
from app.domain.rules import (
    fifo_peek_cost,
    round_money,
    round_quantity,
    to_kg,
    validate_wo_status_transition,
)
from app.services.batch_codes import BatchCodeGenerator
from app.services.inventory import InventoryService


class WorkOrderService:
    """
    Service for work order lifecycle operations: create, release, start, issue materials,
    record QC, apply overheads, complete, and void.
    """

    def __init__(self, db: Session):
        self.db = db
        self.inventory_service = InventoryService(db)
        self.batch_code_gen = BatchCodeGenerator(db)

    def create_work_order(
        self,
        product_id: str,
        planned_qty: Decimal,
        work_center: Optional[str] = None,
        assembly_id: Optional[str] = None,
        uom: str = "KG",
        notes: Optional[str] = None,
    ) -> WorkOrder:
        """
        Create a new work order and explode assembly to inputs.

        Args:
            product_id: Output product ID
            planned_qty: Planned run size
            work_center: Work center (e.g., Still01, Canning01)
            assembly_id: Assembly ID (optional, uses product's primary assembly if not provided)
            uom: Unit of measure (default: KG)
            notes: Optional notes

        Returns:
            Created WorkOrder

        Raises:
            ValueError: If product not found or assembly missing
        """
        # Validate product
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Get assembly (primary recipe definition) - try Formula first, then Assembly
        formula = None
        assembly = None

        if not assembly_id:
            # Try to get primary formula for product
            formula_stmt = (
                select(Formula)
                .where(
                    Formula.product_id == product_id,
                    Formula.is_active.is_(True),
                )
                .order_by(
                    Formula.is_primary.desc().nullslast(), Formula.created_at.desc()
                )
                .limit(1)
            )
            formula = self.db.execute(formula_stmt).scalar_one_or_none()

            # If no formula, try to get Assembly (legacy)
            if not formula:
                assembly_stmt = (
                    select(Assembly)
                    .where(
                        Assembly.parent_product_id == product_id,
                        Assembly.is_active.is_(True),
                        Assembly.is_primary.is_(True),
                    )
                    .order_by(Assembly.effective_from.desc())
                    .limit(1)
                )
                assembly = self.db.execute(assembly_stmt).scalar_one_or_none()

                # If no primary, get any active assembly
                if not assembly:
                    assembly_stmt = (
                        select(Assembly)
                        .where(
                            Assembly.parent_product_id == product_id,
                            Assembly.is_active.is_(True),
                        )
                        .order_by(Assembly.effective_from.desc())
                        .limit(1)
                    )
                    assembly = self.db.execute(assembly_stmt).scalar_one_or_none()

                if assembly:
                    assembly_id = assembly.id
                else:
                    raise ValueError(
                        f"No active formula or assembly found for product {product_id}. "
                        f"Please create a formula (recipe definition) first."
                    )
            else:
                # Use formula_id as assembly_id for backward compatibility
                assembly_id = formula.id
        else:
            # Check if it's a Formula first
            formula = self.db.get(Formula, assembly_id)
            if formula:
                # Validate formula is for this product
                if formula.product_id != product_id:
                    raise ValueError(
                        f"Formula {assembly_id} is for product {formula.product_id}, "
                        f"not {product_id}"
                    )
            else:
                # Try Assembly (legacy)
                assembly = self.db.get(Assembly, assembly_id)
                if not assembly:
                    raise ValueError(f"Formula or Assembly {assembly_id} not found")

                # Validate assembly is for this product
                if assembly.parent_product_id != product_id:
                    raise ValueError(
                        f"Assembly {assembly_id} is for product {assembly.parent_product_id}, "
                        f"not {product_id}"
                    )

        # Ensure we have a formula when using the new system
        # If we're using Assembly (legacy), we still need to find/create a formula or use a placeholder
        if not formula and not assembly:
            raise ValueError(
                "No formula or assembly found. Cannot create work order without a recipe."
            )

        # If we have an assembly but no formula, try to find or create a formula for it
        # For now, we'll require a formula to exist
        if assembly and not formula:
            # Try to find a formula for this assembly's product
            formula_stmt = (
                select(Formula)
                .where(
                    Formula.product_id == product_id,
                    Formula.is_active.is_(True),
                )
                .order_by(
                    Formula.is_primary.desc().nullslast(), Formula.created_at.desc()
                )
                .limit(1)
            )
            formula = self.db.execute(formula_stmt).scalar_one_or_none()

            if not formula:
                raise ValueError(
                    f"Assembly {assembly_id} found but no active formula exists for product {product_id}. "
                    f"Please create a formula first."
                )

        # Generate work order code in format WOYY0000 (e.g., WO250001)
        now = datetime.utcnow()
        year_2digit = now.strftime("%y")  # e.g., "25" for 2025

        # Find the highest sequence number for this year
        year_prefix = f"WO{year_2digit}"
        existing_wo_codes = (
            self.db.execute(
                select(WorkOrder).where(WorkOrder.code.like(f"{year_prefix}%"))
            )
            .scalars()
            .all()
        )

        max_seq = 0
        for wo in existing_wo_codes:
            if wo.code and wo.code.startswith(year_prefix):
                try:
                    # Extract sequence from WO code (last 4 digits)
                    seq_part = wo.code[-4:]
                    seq_num = int(seq_part)
                    max_seq = max(max_seq, seq_num)
                except (ValueError, IndexError):
                    pass

        # Start from max_seq + 1, or 1 if no existing work orders
        seq = max_seq + 1

        # Format: WO + YY + 0000 (e.g., WO250001)
        wo_code = f"WO{year_2digit}{seq:04d}"

        # Generate batch code placeholder
        batch_code = self.batch_code_gen.generate_batch_code(product_id)

        # Determine formula_id - must have a formula when using the new system
        if not formula:
            raise ValueError("Formula is required for work order creation")
        formula_id_val = formula.id

        # Calculate estimated cost from assembly/formula
        estimated_cost = None
        if formula:
            # Calculate total cost from formula lines
            formula_lines = (
                self.db.execute(
                    select(FormulaLine).where(
                        FormulaLine.formula_id == formula.id,
                        FormulaLine.deleted_at.is_(None),  # Only active lines
                    )
                )
                .scalars()
                .all()
            )

            total_cost = Decimal("0")
            for line in formula_lines:
                if line.quantity_kg and line.raw_material_id:
                    # Get product cost
                    line_product = self.db.get(Product, line.raw_material_id)
                    if line_product:
                        # Use usage_cost_ex_gst or purchase_cost_ex_gst
                        unit_cost = (
                            line_product.usage_cost_ex_gst
                            or line_product.purchase_cost_ex_gst
                            or Decimal("0")
                        )
                        line_cost = round_money(line.quantity_kg * unit_cost)
                        total_cost += line_cost

            # Scale by planned_qty (formula is typically for 1 unit)
            estimated_cost = (
                round_money(total_cost * planned_qty) if total_cost > 0 else None
            )
        elif assembly:
            # Calculate from assembly lines (legacy)
            assembly_lines = (
                self.db.execute(
                    select(AssemblyLine).where(AssemblyLine.assembly_id == assembly.id)
                )
                .scalars()
                .all()
            )

            total_cost = Decimal("0")
            for line in assembly_lines:
                if line.quantity and line.component_product_id:
                    component_product = self.db.get(Product, line.component_product_id)
                    if component_product:
                        unit_cost = (
                            component_product.usage_cost_ex_gst
                            or component_product.purchase_cost_ex_gst
                            or Decimal("0")
                        )
                        # Convert quantity to kg if needed
                        qty_kg = line.quantity  # Assuming already in kg
                        line_cost = round_money(qty_kg * unit_cost)
                        total_cost += line_cost

            estimated_cost = (
                round_money(total_cost * planned_qty) if total_cost > 0 else None
            )

        # Determine output UOM and canonical planned quantity in kg
        output_product = product  # already fetched earlier
        output_uom = (
            (uom or "").strip()
            or (output_product.usage_unit if output_product else None)
            or (output_product.base_unit if output_product else None)
            or (output_product.purchase_unit if output_product else None)
            or "KG"
        )
        output_uom_upper = output_uom.upper()
        density = output_product.density_kg_per_l if output_product else None

        try:
            planned_conversion = to_kg(planned_qty, output_uom_upper, density)
            planned_qty_kg = planned_conversion.quantity_kg
        except ValueError:
            if output_uom_upper != "KG":
                raise ValueError(
                    f"Cannot convert planned quantity from {output_uom} without density for product {product_id}"
                )
            planned_qty_kg = planned_qty

        # Create work order
        work_order = WorkOrder(
            id=str(uuid4()),
            code=wo_code,
            product_id=product_id,
            assembly_id=assembly_id,
            formula_id=formula_id_val,  # Set to formula ID if using formula, otherwise None
            quantity_kg=round_quantity(planned_qty_kg),
            planned_qty=round_quantity(planned_qty),
            uom=output_uom_upper,
            work_center=work_center,
            status="draft",
            batch_code=batch_code,
            estimated_cost=estimated_cost,
            notes=notes,
        )

        self.db.add(work_order)
        self.db.flush()

        # Explode assembly to inputs
        self.explode_assembly_to_inputs(work_order.id)

        return work_order

    def explode_assembly_to_inputs(self, work_order_id: str) -> None:
        """
        Populate work_order_inputs from assembly explosion (recipe definition).

        Args:
            work_order_id: Work order ID

        Raises:
            ValueError: If work order not found or assembly missing
        """
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")

        # Get assembly (primary recipe source) - try Formula first, then Assembly
        formula = None
        assembly = None

        # Try to get Formula first (new system)
        if work_order.assembly_id:
            formula = self.db.get(Formula, work_order.assembly_id)

        # If not a Formula, try Assembly (legacy)
        if not formula:
            assembly = work_order.assembly

        if not formula and not assembly:
            raise ValueError(
                f"No formula or assembly found for work order {work_order_id}. "
                f"Work orders must use Formula (recipe definition)."
            )

        # Get assembly lines (components) - from Formula or Assembly
        assembly_lines = []
        yield_factor = Decimal("1.0")

        if formula:
            # Get formula lines
            formula_lines = (
                self.db.execute(
                    select(FormulaLine)
                    .where(
                        FormulaLine.formula_id == formula.id,
                        FormulaLine.deleted_at.is_(None),  # Only active lines
                    )
                    .order_by(FormulaLine.sequence)
                )
                .scalars()
                .all()
            )

            if not formula_lines:
                raise ValueError(
                    f"No formula lines found for formula {formula.formula_code or formula.id}"
                )

            # Create a mock object with the same attributes as AssemblyLine for compatibility
            class MockAssemblyLine:
                def __init__(self, formula_line, db_session):
                    self.raw_material_id = formula_line.raw_material_id
                    self.quantity_kg = formula_line.quantity_kg
                    self.quantity = formula_line.quantity_kg  # For scaling
                    self.sequence = formula_line.sequence
                    self.unit = formula_line.unit or "kg"
                    self.is_energy_or_overhead = False  # Default to material
                    self.notes = formula_line.notes or ""
                    # Get component product
                    self.component_product = (
                        db_session.get(Product, formula_line.raw_material_id)
                        if formula_line.raw_material_id
                        else None
                    )

            assembly_lines = [MockAssemblyLine(fl, self.db) for fl in formula_lines]
            # Get yield_factor from formula, default to 1.0 if not set
            yield_factor = (
                Decimal(str(formula.yield_factor))
                if formula.yield_factor is not None
                else Decimal("1.0")
            )
        else:
            # Get assembly lines (legacy)
            assembly_lines = (
                self.db.execute(
                    select(AssemblyLine)
                    .where(AssemblyLine.assembly_id == assembly.id)
                    .order_by(AssemblyLine.sequence)
                )
                .scalars()
                .all()
            )

            if not assembly_lines:
                raise ValueError(
                    f"No assembly lines found for assembly {assembly.assembly_code}"
                )

            yield_factor = assembly.yield_factor or Decimal("1.0")

        # Calculate scale factor (planned_qty / assembly base qty)
        # Assembly base is typically 1 unit, so scale by planned_qty
        # Apply yield_factor if present
        scale_factor = work_order.planned_qty * yield_factor

        # Create work order input lines from assembly components
        for idx, assembly_line in enumerate(assembly_lines):
            # For Formula lines (MockAssemblyLine), component_product is already set
            if hasattr(assembly_line, "component_product"):
                component_product = assembly_line.component_product
            else:
                component_product = assembly_line.component_product

            if not component_product:
                # For Formula lines, try to get product by raw_material_id
                if (
                    hasattr(assembly_line, "raw_material_id")
                    and assembly_line.raw_material_id
                ):
                    component_product = self.db.get(
                        Product, assembly_line.raw_material_id
                    )
                if not component_product:
                    continue

            # Calculate required quantity: assembly_line.quantity * scale_factor
            # Assembly line quantity is per unit of parent product
            # For Formula lines, use quantity_kg; for Assembly lines, use quantity
            if hasattr(assembly_line, "quantity_kg"):
                qty_base = assembly_line.quantity_kg
            else:
                qty_base = assembly_line.quantity
            planned_qty_display = round_quantity(qty_base * scale_factor)

            # Get UOM from assembly line or default
            uom = assembly_line.unit or "KG"
            uom_upper = (uom or "").upper()

            # Determine canonical kg quantity for storage/reservations
            density = component_product.density_kg_per_l if component_product else None
            qty_canonical_kg = planned_qty_display
            try:
                qty_canonical_kg = round_quantity(
                    to_kg(planned_qty_display, uom_upper, density).quantity_kg
                )
            except ValueError:
                # Unsupported conversion (e.g., EA) - fall back to original behaviour
                qty_canonical_kg = planned_qty_display

            # Determine line type (material vs overhead)
            if hasattr(assembly_line, "is_energy_or_overhead"):
                line_type = (
                    "overhead" if assembly_line.is_energy_or_overhead else "material"
                )
            else:
                line_type = "material"  # Default for Formula lines

            # Create input line
            input_line = WorkOrderLine(
                id=str(uuid4()),
                work_order_id=work_order_id,
                component_product_id=component_product.id,
                ingredient_product_id=component_product.id,  # Legacy compatibility
                required_quantity_kg=qty_canonical_kg,
                planned_qty=planned_qty_display,
                actual_qty=None,
                uom=uom,
                line_type=line_type,
                sequence=assembly_line.sequence or (idx + 1),
                note=assembly_line.notes,
            )

            self.db.add(input_line)

        self.db.flush()

        # Reserve inventory for material lines (optional - can be done on release)
        # For now, we'll reserve on creation to show availability
        material_lines = (
            self.db.execute(
                select(WorkOrderLine).where(
                    WorkOrderLine.work_order_id == work_order_id,
                    WorkOrderLine.line_type == "material",
                )
            )
            .scalars()
            .all()
        )

        for line in material_lines:
            if not line.component_product_id or not line.required_quantity_kg:
                continue

            try:
                self.inventory_service.reserve_inventory(
                    product_id=line.component_product_id,
                    qty_kg=line.required_quantity_kg,
                    source="internal",
                    reference_id=work_order_id,
                )
            except ValueError as e:
                print(
                    f"Warning: Could not reserve inventory for {line.component_product_id}: {e}"
                )
            except Exception as e:
                print(
                    f"Warning: Error reserving inventory for {line.component_product_id}: {e}"
                )

    def release_work_order(self, work_order_id: str) -> WorkOrder:
        """
        Release work order: validate availability, lock recipe.

        Args:
            work_order_id: Work order ID

        Returns:
            Updated WorkOrder

        Raises:
            ValueError: If work order not found or invalid status
        """
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")

        # Validate status transition
        validate_wo_status_transition(work_order.status, "released")

        # Validate ingredients available (soft constraint - can be made hard)
        input_lines = (
            self.db.execute(
                select(WorkOrderLine).where(
                    WorkOrderLine.work_order_id == work_order_id,
                    WorkOrderLine.line_type == "material",
                )
            )
            .scalars()
            .all()
        )

        for line in input_lines:
            if not line.component_product_id:
                continue

            lots = self.inventory_service.get_lots_fifo(line.component_product_id)
            available = sum(lot.quantity_kg for lot in lots if lot.quantity_kg > 0)

            required_qty = line.required_quantity_kg or Decimal("0")
            if available < required_qty:
                # Soft validation - just log warning
                # Could raise here for hard constraint
                pass

        # Lock assembly/formula version (already selected, just validate it's still active)
        formula = None
        assembly = None
        if work_order.assembly_id:
            formula = self.db.get(Formula, work_order.assembly_id)
        if not formula:
            assembly = work_order.assembly

        if formula and not formula.is_active:
            raise ValueError(
                f"Formula {formula.formula_code or formula.id} is no longer active"
            )
        elif assembly and not assembly.is_active:
            raise ValueError(
                f"Assembly {assembly.assembly_code if hasattr(assembly, 'assembly_code') else assembly.id} is no longer active"
            )

        # Update status
        work_order.status = "released"
        work_order.released_at = datetime.utcnow()

        self.db.flush()
        return work_order

    def start_work_order(self, work_order_id: str) -> WorkOrder:
        """
        Start production: set start_time, status=in_progress.

        Args:
            work_order_id: Work order ID

        Returns:
            Updated WorkOrder

        Raises:
            ValueError: If work order not found or invalid status
        """
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")

        # Validate status transition
        validate_wo_status_transition(work_order.status, "in_progress")

        work_order.status = "in_progress"
        work_order.start_time = datetime.utcnow()

        self.db.flush()
        return work_order

    def issue_material(
        self,
        work_order_id: str,
        component_product_id: str,
        qty: Decimal,
        source_batch_id: Optional[str] = None,
        uom: Optional[str] = None,
    ) -> str:
        """
        Issue material: post inventory_moves, update actual_qty.

        Args:
            work_order_id: Work order ID
            component_product_id: Component product ID
            qty: Quantity to issue
            source_batch_id: Optional source batch ID
            uom: Unit of measure (defaults to input line UOM)

        Returns:
            Move ID

        Raises:
            ValueError: If work order not found, invalid status, or insufficient stock
        """
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")

        if work_order.status not in ["released", "in_progress"]:
            raise ValueError(
                f"Cannot issue materials when work order status is '{work_order.status}'"
            )

        # Find input line (check both component_product_id and ingredient_product_id for compatibility)
        input_line = (
            self.db.execute(
                select(WorkOrderLine).where(
                    WorkOrderLine.work_order_id == work_order_id,
                    (
                        (WorkOrderLine.component_product_id == component_product_id)
                        | (WorkOrderLine.ingredient_product_id == component_product_id)
                    ),
                )
            )
            .scalars()
            .first()
        )

        if not input_line:
            raise ValueError(
                f"Input line not found for component {component_product_id} in work order {work_order_id}"
            )

        # Get UOM
        issue_uom = uom or input_line.uom or "KG"

        # Convert to kg if needed
        product = self.db.get(Product, component_product_id)
        density = product.density_kg_per_l if product else None
        allow_negative_inventory = bool(
            getattr(product, "allow_negative_inventory", False) if product else False
        )

        if issue_uom.upper() in ["L", "ML", "LITRE", "LITER"]:
            if not density:
                raise ValueError(
                    f"Density required for liquid conversion from {issue_uom}"
                )
            conversion_result = to_kg(qty, issue_uom, density)
            qty_kg = conversion_result.quantity_kg
        else:
            # Assume mass unit
            qty_kg = round_quantity(qty)

        # Get FIFO cost
        lots = self.inventory_service.get_lots_fifo(component_product_id)
        if source_batch_id:
            unit_cost = fifo_peek_cost(lots, source_batch_id)
        else:
            unit_cost = fifo_peek_cost(lots)

        if unit_cost is None:
            unit_cost = Decimal("0")

        # Issue from inventory using FIFO
        self.inventory_service.consume_lots_fifo(
            product_id=component_product_id,
            qty_kg=qty_kg,
            reason=f"Work order {work_order.code} material issue",
            ref_type="work_orders",
            ref_id=work_order_id,
            allow_negative=allow_negative_inventory,
        )

        # Create inventory movement
        move = InventoryMovement(
            id=str(uuid4()),
            ts=datetime.utcnow(),
            timestamp=datetime.utcnow(),
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            product_id=component_product_id,
            batch_id=source_batch_id,
            qty=-abs(qty_kg),  # Negative for issues
            unit=issue_uom or input_line.uom or "KG",
            uom=issue_uom or input_line.uom or "KG",
            direction="OUT",
            move_type="wo_issue",
            ref_table="work_orders",
            ref_id=work_order_id,
            unit_cost=unit_cost,
            note=f"Material issue for WO {work_order.code}",
        )

        self.db.add(move)

        # Update input line
        if input_line.actual_qty is None:
            input_line.actual_qty = Decimal("0")
        input_line.actual_qty += qty_kg
        input_line.allocated_quantity_kg = input_line.actual_qty
        input_line.unit_cost = unit_cost
        if source_batch_id:
            input_line.source_batch_id = source_batch_id

        self.db.flush()

        return move.id

    def record_qc(
        self,
        work_order_id: str,
        test_type_id: Optional[str] = None,
        test_type: Optional[str] = None,
        result_value: Optional[Decimal] = None,
        result_text: Optional[str] = None,
        unit: Optional[str] = None,
        status: str = "pending",
        tester: Optional[str] = None,
        note: Optional[str] = None,
    ) -> WoQcTest:
        """
        Record QC test result.

        Args:
            work_order_id: Work order ID
            test_type_id: ID of QC test type
            test_type: Test type code/name (fallback if ID not provided)
            result_value: Numeric result
            result_text: Text result (for non-numeric)
            unit: Unit override (will default from QC test type if available)
            status: Test status (pending, pass, fail)
            tester: Tester name
            note: Optional note

        Returns:
            Created WoQcTest

        Raises:
            ValueError: If work order not found
        """
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")

        qc_type: Optional[QcTestType] = None
        if test_type_id:
            qc_type = self.db.get(QcTestType, test_type_id)
            if not qc_type or qc_type.deleted_at is not None:
                raise ValueError("QC test type not found")
            if not qc_type.is_active:
                raise ValueError("QC test type is inactive")
            test_type = qc_type.code or qc_type.name
            unit = qc_type.unit or unit

        if not test_type:
            raise ValueError("QC test type is required")

        qc_test = WoQcTest(
            id=str(uuid4()),
            work_order_id=work_order_id,
            test_type=test_type,
            test_type_id=qc_type.id if qc_type else test_type_id,
            result_value=result_value,
            result_text=result_text,
            unit=unit,
            status=status,
            tested_at=datetime.utcnow() if status != "pending" else None,
            tester=tester,
            note=note,
        )

        self.db.add(qc_test)
        self.db.flush()

        return qc_test

    def update_qc_test(
        self,
        qc_test_id: str,
        work_order_id: str,
        test_type_id: Optional[str] = None,
        result_value: Optional[Decimal] = None,
        result_text: Optional[str] = None,
        status: Optional[str] = None,
        tester: Optional[str] = None,
        note: Optional[str] = None,
    ) -> WoQcTest:
        """Update an existing QC test."""

        qc_test = self.db.get(WoQcTest, qc_test_id)
        if not qc_test or qc_test.deleted_at is not None:
            raise ValueError("QC test not found")

        if qc_test.work_order_id != work_order_id:
            raise ValueError("QC test does not belong to this work order")

        if test_type_id:
            qc_type = self.db.get(QcTestType, test_type_id)
            if not qc_type or qc_type.deleted_at is not None:
                raise ValueError("QC test type not found")
            if not qc_type.is_active:
                raise ValueError("QC test type is inactive")
            qc_test.test_type_id = qc_type.id
            qc_test.test_type = qc_type.code or qc_type.name
            qc_test.unit = qc_type.unit

        if result_value is not None:
            qc_test.result_value = result_value
        if result_text is not None:
            qc_test.result_text = result_text
        if tester is not None:
            qc_test.tester = tester
        if note is not None:
            qc_test.note = note
        if status is not None:
            qc_test.status = status
            qc_test.tested_at = datetime.utcnow() if status != "pending" else None

        self.db.flush()
        return qc_test

    def soft_delete_qc_test(self, qc_test_id: str, work_order_id: str) -> None:
        """Soft delete a QC test result."""

        qc_test = self.db.get(WoQcTest, qc_test_id)
        if not qc_test or qc_test.deleted_at is not None:
            raise ValueError("QC test not found")

        if qc_test.work_order_id != work_order_id:
            raise ValueError("QC test does not belong to this work order")

        qc_test.deleted_at = datetime.utcnow()
        self.db.flush()

    def list_qc_test_types(self, include_inactive: bool = False) -> List[QcTestType]:
        """Return configured QC test types."""

        stmt = select(QcTestType).where(QcTestType.deleted_at.is_(None))
        if not include_inactive:
            stmt = stmt.where(QcTestType.is_active.is_(True))
        stmt = stmt.order_by(QcTestType.code)
        return self.db.execute(stmt).scalars().all()

    def apply_overhead(
        self,
        work_order_id: str,
        rate_code: str,
        basis_qty: Optional[Decimal] = None,
        seconds: Optional[int] = None,
    ) -> str:
        """
        Apply overhead cost (as pseudo-component or timer-based).

        Args:
            work_order_id: Work order ID
            rate_code: Rate code (e.g., 'CANNING_LINE_STD_HOURLY')
            basis_qty: Basis quantity for per-unit rates
            seconds: Seconds for hourly rates

        Returns:
            Input line ID or timer ID

        Raises:
            ValueError: If work order or rate not found
        """
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")

        # Get rate
        rate = (
            self.db.execute(
                select(ProductCostRate).where(
                    ProductCostRate.rate_code == rate_code,
                    ProductCostRate.effective_from <= datetime.utcnow(),
                    (ProductCostRate.effective_to.is_(None))
                    | (ProductCostRate.effective_to >= datetime.utcnow()),
                )
            )
            .scalars()
            .first()
        )

        if not rate:
            raise ValueError(f"Cost rate {rate_code} not found or not effective")

        if rate.rate_type == "hourly" and seconds:
            # Create timer-based overhead
            cost = round_money((Decimal(seconds) / Decimal("3600")) * rate.rate_value)

            timer = WoTimer(
                id=str(uuid4()),
                work_order_id=work_order_id,
                timer_type=rate_code,
                seconds=seconds,
                rate_per_hour=rate.rate_value,
                cost=cost,
            )

            self.db.add(timer)
            self.db.flush()
            return timer.id

        else:
            # Create overhead input line
            if not basis_qty:
                raise ValueError(f"basis_qty required for rate type '{rate.rate_type}'")

            cost = round_money(basis_qty * rate.rate_value)

            input_line = WorkOrderLine(
                id=str(uuid4()),
                work_order_id=work_order_id,
                component_product_id=None,  # Overhead has no product
                ingredient_product_id=None,
                required_quantity_kg=Decimal("0"),
                planned_qty=basis_qty,
                actual_qty=basis_qty,
                uom=rate.uom or "HOUR",
                unit_cost=rate.rate_value,
                line_type="overhead",
                sequence=999,  # Overheads at end
                note=f"Overhead: {rate_code}",
            )

            self.db.add(input_line)
            self.db.flush()
            return input_line.id

    def complete_work_order(
        self,
        work_order_id: str,
        qty_produced: Decimal,
        batch_attrs: Optional[Dict] = None,
    ) -> tuple[str, str]:
        """
        Complete work order: cost roll-up, post output, set status=complete.

        Args:
            work_order_id: Work order ID
            qty_produced: Actual quantity produced
            batch_attrs: Optional batch attributes (mfg_date, exp_date, meta)

        Returns:
            Tuple of (output_move_id, batch_id)

        Raises:
            ValueError: If work order not found, QC not passed, or invalid status
        """
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")

        if work_order.status != "in_progress":
            raise ValueError(
                f"Cannot complete work order with status '{work_order.status}'"
            )

        # Check required QC tests passed
        qc_tests = (
            self.db.execute(
                select(WoQcTest).where(WoQcTest.work_order_id == work_order_id)
            )
            .scalars()
            .all()
        )

        # Check if any required tests are pending or failed
        for test in qc_tests:
            if test.status == "pending":
                raise ValueError(
                    f"Required QC test '{test.test_type}' is still pending"
                )
            if test.status == "fail":
                raise ValueError(
                    f"Required QC test '{test.test_type}' failed - cannot complete"
                )

        # Determine output UOM and convert to kg for inventory/batch tracking
        output_product = self.db.get(Product, work_order.product_id)
        output_uom = (
            (work_order.uom or "").strip()
            or (output_product.usage_unit if output_product else None)
            or (output_product.base_unit if output_product else None)
            or (output_product.purchase_unit if output_product else None)
            or "KG"
        )
        output_uom = output_uom.upper()
        density = output_product.density_kg_per_l if output_product else None

        try:
            conversion = to_kg(qty_produced, output_uom, density)
            qty_produced_kg = conversion.quantity_kg
        except ValueError:
            if output_uom != "KG":
                raise
            qty_produced_kg = round_quantity(qty_produced)

        # Cost roll-up
        # Material cost
        input_lines = (
            self.db.execute(
                select(WorkOrderLine).where(
                    WorkOrderLine.work_order_id == work_order_id,
                    WorkOrderLine.line_type == "material",
                )
            )
            .scalars()
            .all()
        )

        material_cost = Decimal("0")
        for line in input_lines:
            if line.actual_qty and line.unit_cost:
                material_cost += round_money(abs(line.actual_qty) * line.unit_cost)

        # Overhead cost (from input lines and timers)
        overhead_lines = (
            self.db.execute(
                select(WorkOrderLine).where(
                    WorkOrderLine.work_order_id == work_order_id,
                    WorkOrderLine.line_type == "overhead",
                )
            )
            .scalars()
            .all()
        )

        overhead_cost = Decimal("0")
        for line in overhead_lines:
            if line.actual_qty and line.unit_cost:
                overhead_cost += round_money(abs(line.actual_qty) * line.unit_cost)

        # Timer costs
        timers = (
            self.db.execute(
                select(WoTimer).where(WoTimer.work_order_id == work_order_id)
            )
            .scalars()
            .all()
        )

        for timer in timers:
            if timer.cost:
                overhead_cost += timer.cost

        # Total cost and unit cost
        total_cost = material_cost + overhead_cost
        unit_cost = (
            round_money(total_cost / qty_produced) if qty_produced > 0 else Decimal("0")
        )

        # Create batch
        batch = Batch(
            id=str(uuid4()),
            product_id=work_order.product_id,
            work_order_id=work_order_id,
            batch_code=work_order.batch_code
            or work_order.code
            or self.batch_code_gen.generate_batch_code(work_order.product_id),
            quantity_kg=round_quantity(qty_produced_kg),
            mfg_date=(batch_attrs or {}).get("mfg_date") or date.today(),
            exp_date=(batch_attrs or {}).get("exp_date"),
            status="released",
            meta=json.dumps(batch_attrs.get("meta") if batch_attrs else {}),
        )

        self.db.add(batch)
        self.db.flush()

        # Create work order output
        output = WorkOrderOutput(
            id=str(uuid4()),
            work_order_id=work_order_id,
            product_id=work_order.product_id,
            qty_produced=round_quantity(qty_produced),
            uom=output_uom,
            batch_id=batch.id,
            unit_cost=unit_cost,
            note="Work order completion",
        )

        self.db.add(output)

        # Post inventory movement (positive)
        move = InventoryMovement(
            id=str(uuid4()),
            ts=datetime.utcnow(),
            timestamp=datetime.utcnow(),
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            product_id=work_order.product_id,
            batch_id=batch.id,
            qty=abs(qty_produced_kg),
            unit=output_uom,
            uom=output_uom,
            direction="IN",
            move_type="wo_completion",
            ref_table="work_orders",
            ref_id=work_order_id,
            unit_cost=unit_cost,
            note=f"Work order {work_order.code} completion",
        )

        self.db.add(move)

        # Store genealogy in batch meta
        genealogy = []
        for line in input_lines:
            if line.source_batch_id:
                genealogy.append(line.source_batch_id)

        if genealogy:
            meta = batch.meta or "{}"
            meta_dict = json.loads(meta) if isinstance(meta, str) else meta
            meta_dict["genealogy"] = genealogy
            batch.meta = json.dumps(meta_dict)

        # Update work order status and costs
        work_order.status = "complete"
        work_order.end_time = datetime.utcnow()
        work_order.completed_at = datetime.utcnow()
        work_order.actual_qty = round_quantity(qty_produced)
        work_order.actual_cost = round_money(total_cost)

        self.db.flush()

        return move.id, batch.id

    def void_work_order(self, work_order_id: str, reason: str) -> WorkOrder:
        """
        Void work order: create compensating moves, set status=void.

        Args:
            work_order_id: Work order ID
            reason: Reason for voiding

        Returns:
            Updated WorkOrder

        Raises:
            ValueError: If work order not found or already completed/voided
        """
        work_order = self.db.get(WorkOrder, work_order_id)
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")

        if work_order.status in ["complete", "void"]:
            raise ValueError(
                f"Cannot void work order with status '{work_order.status}'"
            )

        # Create compensating inventory moves for any issues
        moves = (
            self.db.execute(
                select(InventoryMovement).where(
                    InventoryMovement.ref_table == "work_orders",
                    InventoryMovement.ref_id == work_order_id,
                    InventoryMovement.move_type == "wo_issue",
                )
            )
            .scalars()
            .all()
        )

        for move in moves:
            # Create compensating move (reverse the issue)
            compensating_move = InventoryMovement(
                id=str(uuid4()),
                ts=datetime.utcnow(),
                timestamp=datetime.utcnow(),
                date=datetime.utcnow().strftime("%Y-%m-%d"),
                product_id=move.product_id,
                batch_id=move.batch_id,
                qty=-move.qty,  # Reverse the sign
                unit=move.unit,
                uom=move.uom,
                direction="IN" if -move.qty > 0 else "OUT",
                move_type="wo_void",
                ref_table="work_orders",
                ref_id=work_order_id,
                unit_cost=move.unit_cost,
                note=f"Void compensation for {move.id}: {reason}",
            )

            self.db.add(compensating_move)

        # Update status
        work_order.status = "void"
        work_order.notes = (
            f"{work_order.notes or ''}\nVOIDED: {reason}"
            if work_order.notes
            else f"VOIDED: {reason}"
        )

        self.db.flush()

        return work_order
