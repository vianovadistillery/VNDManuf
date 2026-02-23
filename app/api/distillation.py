"""Distillation API router."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import (
    DistillationEvent,
    DistillationMaterial,
    DistillationRun,
)
from app.api.dto import (
    DistillationEventCreate,
    DistillationEventResponse,
    DistillationMaterialResponse,
    DistillationPeriodResponse,
    DistillationRunCreate,
    DistillationRunResponse,
    DistillationRunUpdate,
)
from app.services.distillation import RUN_STATUS_CLOSED, DistillationService

router = APIRouter(prefix="/distillation", tags=["distillation"])


def _safe_load_json(raw: Optional[str]) -> Optional[Dict]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def _material_to_response(
    material: DistillationMaterial,
) -> DistillationMaterialResponse:
    return DistillationMaterialResponse(
        id=material.id,
        run_id=material.run_id,
        period_id=material.period_id,
        product_id=material.product_id,
        direction=material.direction,
        inventory_movement_id=material.inventory_movement_id,
        qty_kg=material.qty_kg,
        uom=material.uom,
        unit_cost=material.unit_cost,
        note=material.note,
    )


def _event_to_response(
    event: DistillationEvent,
    material: Optional[DistillationMaterial] = None,
) -> DistillationEventResponse:
    material_resp = _material_to_response(material) if material else None
    return DistillationEventResponse(
        id=event.id,
        run_id=event.run_id,
        period_id=event.period_id,
        event_type=event.event_type,  # Pydantic will coerce to Enum
        occurred_at=event.occurred_at,
        source=event.source,
        payload=_safe_load_json(event.payload_json),
        external_id=event.external_id,
        note=event.note,
        material=material_resp,
    )


def _run_to_response(run: DistillationRun) -> DistillationRunResponse:
    periods = [
        DistillationPeriodResponse(
            id=period.id,
            run_id=period.run_id,
            botanical_product_id=period.botanical_product_id,
            started_at=period.started_at,
            ended_at=period.ended_at,
            duration_seconds=period.duration_seconds,
            avg_feed_rate_lph=period.avg_feed_rate_lph,
            avg_product_rate_lph=period.avg_product_rate_lph,
            feed_mass_kg=period.feed_mass_kg,
            product_mass_kg=period.product_mass_kg,
            record_source=period.record_source,
            note=period.note,
        )
        for period in run.periods
    ]

    events = [
        DistillationEventResponse(
            id=event.id,
            run_id=event.run_id,
            period_id=event.period_id,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            source=event.source,
            payload=_safe_load_json(event.payload_json),
            external_id=event.external_id,
            note=event.note,
            material=None,
        )
        for event in run.events
    ]

    materials = [_material_to_response(material) for material in run.materials]

    return DistillationRunResponse(
        id=run.id,
        code=run.code,
        status=run.status,
        still_code=run.still_code,
        product_id=run.product_id,
        external_run_code=run.external_run_code,
        open_at=run.open_at,
        close_at=run.close_at,
        actual_cost=run.actual_cost,
        notes=run.notes,
        created_at=run.created_at,
        periods=periods,
        events=events,
        materials=materials,
    )


@router.post(
    "/runs",
    response_model=DistillationRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_distillation_run(
    payload: DistillationRunCreate, db: Session = Depends(get_db)
):
    """Create/open a new distillation run."""
    service = DistillationService(db)
    try:
        run = service.open_run(
            still_code=payload.still_code,
            product_id=payload.product_id,
            code=payload.code,
            external_run_code=payload.external_run_code,
            notes=payload.notes,
            initial_botanical_product_id=payload.initial_botanical_product_id,
            started_at=payload.started_at,
        )
        db.commit()
        run = service.get_run(run.id)
        return _run_to_response(run)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    except Exception as exc:  # pragma: no cover - unexpected failure
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create distillation run: {exc}",
        )


@router.get("/runs", response_model=List[DistillationRunResponse])
def list_distillation_runs(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List distillation runs."""
    service = DistillationService(db)
    runs = service.list_runs(status=status_filter, limit=limit)
    return [_run_to_response(run) for run in runs]


@router.get("/runs/{run_id}", response_model=DistillationRunResponse)
def get_distillation_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific distillation run."""
    service = DistillationService(db)
    try:
        run = service.get_run(run_id)
        return _run_to_response(run)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/runs/{run_id}", response_model=DistillationRunResponse)
def update_distillation_run(
    run_id: str,
    payload: DistillationRunUpdate,
    db: Session = Depends(get_db),
):
    """Update run status or details."""
    service = DistillationService(db)
    try:
        run = service.update_run(
            run_id,
            status=payload.status.value if payload.status else None,
            close_at=payload.close_at,
            notes=payload.notes,
            still_code=payload.still_code,
            product_id=payload.product_id,
            open_at=payload.open_at,
            external_run_code=payload.external_run_code,
            code=payload.code,
        )
        db.commit()
        run = service.get_run(run.id)
        return _run_to_response(run)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_distillation_run(
    run_id: str,
    force: bool = Query(False),
    db: Session = Depends(get_db),
) -> Response:
    """Delete a distillation run."""
    service = DistillationService(db)
    try:
        service.delete_run(run_id, force=force)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )


@router.post(
    "/runs/{run_id}/events",
    response_model=DistillationEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_distillation_event(
    run_id: str,
    payload: DistillationEventCreate,
    db: Session = Depends(get_db),
):
    """Record an event (and optional material movement) against a run."""
    service = DistillationService(db)
    try:
        event, material = service.record_event(
            run_id,
            event_type=payload.event_type.value,
            timestamp=payload.timestamp,
            period_id=payload.period_id,
            period_ref=payload.period_ref,
            botanical_product_id=payload.botanical_product_id,
            metrics=payload.metrics,
            notes=payload.notes,
            external_id=payload.external_id,
            source=payload.source,
            inventory_payload=payload.inventory.dict() if payload.inventory else None,
        )
        db.commit()
        return _event_to_response(event, material)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    except Exception as exc:  # pragma: no cover - unexpected failure
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record event: {exc}",
        )


@router.post(
    "/runs/{run_id}/close",
    response_model=DistillationRunResponse,
    status_code=status.HTTP_200_OK,
)
def close_distillation_run(
    run_id: str,
    db: Session = Depends(get_db),
):
    """Convenience endpoint to close a run."""
    service = DistillationService(db)
    try:
        run = service.update_run(
            run_id, status=RUN_STATUS_CLOSED, close_at=datetime.utcnow()
        )
        db.commit()
        run = service.get_run(run.id)
        return _run_to_response(run)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
