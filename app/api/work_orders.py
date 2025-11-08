# app/api/work_orders.py
"""Work Orders API router."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import (
    Batch,
    WorkOrder,
    WorkOrderLine,
    WorkOrderOutput,
    WoTimer,
)
from app.api.dto import (
    GenealogyResponse,
    QcTestTypeResponse,
    WorkOrderCompleteRequest,
    WorkOrderCostResponse,
    WorkOrderCreate,
    WorkOrderInputResponse,
    WorkOrderIssueRequest,
    WorkOrderOutputResponse,
    WorkOrderOverheadRequest,
    WorkOrderQcRequest,
    WorkOrderQcResponse,
    WorkOrderQcUpdateRequest,
    WorkOrderReleaseRequest,
    WorkOrderResponse,
    WorkOrderStartRequest,
    WorkOrderVoidRequest,
)
from app.services.work_orders import WorkOrderService

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


def work_order_to_response(work_order: WorkOrder) -> WorkOrderResponse:
    """Convert WorkOrder model to response DTO."""
    inputs = [
        WorkOrderInputResponse(
            id=line.id,
            component_product_id=line.component_product_id
            or line.ingredient_product_id
            or "",
            planned_qty=line.planned_qty or line.required_quantity_kg,
            actual_qty=line.actual_qty or line.allocated_quantity_kg,
            uom=line.uom,
            source_batch_id=line.source_batch_id,
            unit_cost=line.unit_cost,
            line_type=line.line_type or "material",
            sequence=line.sequence,
            required_quantity_kg=line.required_quantity_kg,
            allocated_quantity_kg=line.allocated_quantity_kg,
        )
        for line in work_order.lines
    ]

    outputs = [
        WorkOrderOutputResponse(
            id=output.id,
            product_id=output.product_id,
            qty_produced=output.qty_produced,
            uom=output.uom,
            batch_id=output.batch_id,
            unit_cost=output.unit_cost,
            scrap_qty=output.scrap_qty,
            note=output.note,
        )
        for output in work_order.outputs
    ]

    qc_tests = [
        WorkOrderQcResponse(
            id=qc.id,
            work_order_id=qc.work_order_id,
            test_type=qc.test_type,
            test_type_id=qc.test_type_id,
            result_value=qc.result_value,
            result_text=qc.result_text,
            unit=qc.unit,
            status=qc.status,
            tested_at=qc.tested_at,
            tester=qc.tester,
            note=qc.note,
        )
        for qc in work_order.qc_tests
        if qc.deleted_at is None
    ]

    return WorkOrderResponse(
        id=work_order.id,
        code=work_order.code,
        product_id=work_order.product_id,
        assembly_id=work_order.assembly_id,  # Primary recipe
        formula_id=work_order.formula_id,  # Legacy
        planned_qty=work_order.planned_qty or work_order.quantity_kg,
        quantity_kg=work_order.quantity_kg,
        uom=work_order.uom,
        work_center=work_order.work_center,
        status=work_order.status,
        start_time=work_order.start_time,
        end_time=work_order.end_time,
        released_at=work_order.released_at,  # Issued date
        completed_at=work_order.completed_at,  # Completed date
        actual_qty=work_order.actual_qty,
        estimated_cost=work_order.estimated_cost,
        actual_cost=work_order.actual_cost,
        batch_code=work_order.batch_code,
        notes=work_order.notes,
        created_at=work_order.created_at or datetime.utcnow(),
        inputs=inputs,
        outputs=outputs,
        qc_tests=qc_tests,
    )


@router.post("/", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    wo_data: WorkOrderCreate,
    db: Session = Depends(get_db),
):
    """Create a new work order."""
    try:
        service = WorkOrderService(db)
        work_order = service.create_work_order(
            product_id=wo_data.product_id,
            planned_qty=wo_data.planned_qty,
            work_center=wo_data.work_center,
            assembly_id=wo_data.assembly_id,  # Use Assembly instead of Formula
            uom=wo_data.uom,
            notes=wo_data.notes,
        )
        db.commit()
        db.refresh(work_order)
        return work_order_to_response(work_order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create work order: {str(e)}",
        )


@router.get("/", response_model=List[WorkOrderResponse])
async def list_work_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    product_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List work orders with optional filters."""
    stmt = select(WorkOrder)

    if status_filter:
        stmt = stmt.where(WorkOrder.status == status_filter.lower())

    if product_id:
        stmt = stmt.where(WorkOrder.product_id == product_id)

    if date_from:
        stmt = stmt.where(WorkOrder.created_at >= datetime.fromisoformat(date_from))

    if date_to:
        stmt = stmt.where(WorkOrder.created_at <= datetime.fromisoformat(date_to))

    stmt = stmt.order_by(WorkOrder.created_at.desc())

    work_orders = db.execute(stmt).scalars().all()

    return [work_order_to_response(wo) for wo in work_orders]


@router.get("/qc-test-types", response_model=List[QcTestTypeResponse])
async def list_qc_test_types(
    include_inactive: bool = False, db: Session = Depends(get_db)
):
    """List available QC test types."""
    service = WorkOrderService(db)
    qc_types = service.list_qc_test_types(include_inactive=include_inactive)
    return qc_types


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(
    work_order_id: str,
    db: Session = Depends(get_db),
):
    """Get work order detail."""
    work_order = db.get(WorkOrder, work_order_id)
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found"
        )

    return work_order_to_response(work_order)


@router.post("/{work_order_id}/release", response_model=WorkOrderResponse)
async def release_work_order(
    work_order_id: str,
    request: WorkOrderReleaseRequest,
    db: Session = Depends(get_db),
):
    """Release work order."""
    try:
        service = WorkOrderService(db)
        work_order = service.release_work_order(work_order_id)
        db.commit()
        db.refresh(work_order)
        return work_order_to_response(work_order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to release work order: {str(e)}",
        )


@router.post("/{work_order_id}/start", response_model=WorkOrderResponse)
async def start_work_order(
    work_order_id: str,
    request: WorkOrderStartRequest,
    db: Session = Depends(get_db),
):
    """Start work order production."""
    try:
        service = WorkOrderService(db)
        work_order = service.start_work_order(work_order_id)
        db.commit()
        db.refresh(work_order)
        return work_order_to_response(work_order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start work order: {str(e)}",
        )


@router.post("/{work_order_id}/issues", status_code=status.HTTP_201_CREATED)
async def issue_material(
    work_order_id: str,
    issue_data: WorkOrderIssueRequest,
    db: Session = Depends(get_db),
):
    """Issue material for work order."""
    try:
        service = WorkOrderService(db)
        move_id = service.issue_material(
            work_order_id=work_order_id,
            component_product_id=issue_data.component_product_id,
            qty=issue_data.qty,
            source_batch_id=issue_data.source_batch_id,
            uom=issue_data.uom,
        )
        db.commit()
        return {"move_id": move_id, "message": "Material issued successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to issue material: {str(e)}",
        )


@router.post(
    "/{work_order_id}/qc",
    response_model=WorkOrderQcResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_qc(
    work_order_id: str,
    qc_data: WorkOrderQcRequest,
    db: Session = Depends(get_db),
):
    """Record QC test result."""
    try:
        service = WorkOrderService(db)
        qc_test = service.record_qc(
            work_order_id=work_order_id,
            test_type_id=qc_data.test_type_id,
            test_type=qc_data.test_type,
            result_value=qc_data.result_value,
            result_text=qc_data.result_text,
            status=qc_data.status,
            tester=qc_data.tester,
            note=qc_data.note,
        )
        db.commit()
        db.refresh(qc_test)
        return WorkOrderQcResponse(
            id=qc_test.id,
            work_order_id=qc_test.work_order_id,
            test_type=qc_test.test_type,
            test_type_id=qc_test.test_type_id,
            result_value=qc_test.result_value,
            result_text=qc_test.result_text,
            unit=qc_test.unit,
            status=qc_test.status,
            tested_at=qc_test.tested_at,
            tester=qc_test.tester,
            note=qc_test.note,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record QC: {str(e)}",
        )


@router.patch(
    "/{work_order_id}/qc/{qc_test_id}",
    response_model=WorkOrderQcResponse,
    status_code=status.HTTP_200_OK,
)
async def update_qc_result(
    work_order_id: str,
    qc_test_id: str,
    qc_data: WorkOrderQcUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update an existing QC test result."""
    try:
        service = WorkOrderService(db)
        qc_test = service.update_qc_test(
            qc_test_id=qc_test_id,
            work_order_id=work_order_id,
            test_type_id=qc_data.test_type_id,
            result_value=qc_data.result_value,
            result_text=qc_data.result_text,
            status=qc_data.status,
            tester=qc_data.tester,
            note=qc_data.note,
        )
        db.commit()
        db.refresh(qc_test)
        return WorkOrderQcResponse(
            id=qc_test.id,
            work_order_id=qc_test.work_order_id,
            test_type=qc_test.test_type,
            test_type_id=qc_test.test_type_id,
            result_value=qc_test.result_value,
            result_text=qc_test.result_text,
            unit=qc_test.unit,
            status=qc_test.status,
            tested_at=qc_test.tested_at,
            tester=qc_test.tester,
            note=qc_test.note,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update QC: {str(e)}",
        )


@router.delete(
    "/{work_order_id}/qc/{qc_test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_qc_result(
    work_order_id: str,
    qc_test_id: str,
    db: Session = Depends(get_db),
):
    """Soft delete a QC test result."""
    try:
        service = WorkOrderService(db)
        service.soft_delete_qc_test(qc_test_id=qc_test_id, work_order_id=work_order_id)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete QC: {str(e)}",
        )


@router.post("/{work_order_id}/overheads", status_code=status.HTTP_201_CREATED)
async def apply_overhead(
    work_order_id: str,
    overhead_data: WorkOrderOverheadRequest,
    db: Session = Depends(get_db),
):
    """Apply overhead cost."""
    try:
        service = WorkOrderService(db)
        line_id = service.apply_overhead(
            work_order_id=work_order_id,
            rate_code=overhead_data.rate_code,
            basis_qty=overhead_data.basis_qty,
            seconds=overhead_data.seconds,
        )
        db.commit()
        return {"line_id": line_id, "message": "Overhead applied successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply overhead: {str(e)}",
        )


@router.post("/{work_order_id}/complete", status_code=status.HTTP_200_OK)
async def complete_work_order(
    work_order_id: str,
    complete_data: WorkOrderCompleteRequest,
    db: Session = Depends(get_db),
):
    """Complete work order."""
    try:
        service = WorkOrderService(db)
        move_id, batch_id = service.complete_work_order(
            work_order_id=work_order_id,
            qty_produced=complete_data.qty_produced,
            batch_attrs=complete_data.batch_attrs,
        )
        db.commit()
        return {
            "move_id": move_id,
            "batch_id": batch_id,
            "message": "Work order completed successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete work order: {str(e)}",
        )


@router.post("/{work_order_id}/void", response_model=WorkOrderResponse)
async def void_work_order(
    work_order_id: str,
    void_data: WorkOrderVoidRequest,
    db: Session = Depends(get_db),
):
    """Void work order (admin only)."""
    try:
        service = WorkOrderService(db)
        work_order = service.void_work_order(
            work_order_id=work_order_id, reason=void_data.reason
        )
        db.commit()
        db.refresh(work_order)
        return work_order_to_response(work_order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to void work order: {str(e)}",
        )


@router.get("/{work_order_id}/costs", response_model=WorkOrderCostResponse)
async def get_work_order_costs(
    work_order_id: str,
    db: Session = Depends(get_db),
):
    """Get work order cost breakdown."""
    work_order = db.get(WorkOrder, work_order_id)
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found"
        )

    # Calculate material cost
    material_lines = (
        db.execute(
            select(WorkOrderLine).where(
                WorkOrderLine.work_order_id == work_order_id,
                WorkOrderLine.line_type == "material",
            )
        )
        .scalars()
        .all()
    )

    material_cost = Decimal("0")
    for line in material_lines:
        if line.actual_qty and line.unit_cost:
            material_cost += Decimal(str(line.actual_qty)) * Decimal(
                str(line.unit_cost)
            )

    # Calculate overhead cost
    overhead_lines = (
        db.execute(
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
            overhead_cost += Decimal(str(line.actual_qty)) * Decimal(
                str(line.unit_cost)
            )

    # Timer costs
    timers = (
        db.execute(select(WoTimer).where(WoTimer.work_order_id == work_order_id))
        .scalars()
        .all()
    )

    for timer in timers:
        if timer.cost:
            overhead_cost += Decimal(str(timer.cost))

    total_cost = material_cost + overhead_cost

    # Get qty_produced
    outputs = (
        db.execute(
            select(WorkOrderOutput).where(
                WorkOrderOutput.work_order_id == work_order_id
            )
        )
        .scalars()
        .all()
    )

    qty_produced = sum(output.qty_produced for output in outputs) if outputs else None
    unit_cost = total_cost / qty_produced if qty_produced and qty_produced > 0 else None

    return WorkOrderCostResponse(
        material_cost=material_cost,
        overhead_cost=overhead_cost,
        total_cost=total_cost,
        qty_produced=qty_produced,
        unit_cost=unit_cost,
    )


@router.get("/{work_order_id}/genealogy", response_model=GenealogyResponse)
async def get_work_order_genealogy(
    work_order_id: str,
    db: Session = Depends(get_db),
):
    """Get batch genealogy for work order."""
    work_order = db.get(WorkOrder, work_order_id)
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found"
        )

    # Get output batch
    outputs = (
        db.execute(
            select(WorkOrderOutput).where(
                WorkOrderOutput.work_order_id == work_order_id
            )
        )
        .scalars()
        .all()
    )

    if not outputs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No output batch found for work order",
        )

    output = outputs[0]
    batch = db.get(Batch, output.batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
        )

    # Get input batch IDs from input lines
    input_lines = (
        db.execute(
            select(WorkOrderLine).where(
                WorkOrderLine.work_order_id == work_order_id,
                WorkOrderLine.source_batch_id.isnot(None),
            )
        )
        .scalars()
        .all()
    )

    input_batch_ids = [
        line.source_batch_id for line in input_lines if line.source_batch_id
    ]

    # Get genealogy from batch meta
    genealogy = None
    if batch.meta:
        try:
            import json

            genealogy = (
                json.loads(batch.meta) if isinstance(batch.meta, str) else batch.meta
            )
        except (TypeError, ValueError, json.JSONDecodeError):
            pass

    return GenealogyResponse(
        batch_id=batch.id,
        batch_code=batch.batch_code,
        input_batch_ids=input_batch_ids,
        genealogy=genealogy,
    )
