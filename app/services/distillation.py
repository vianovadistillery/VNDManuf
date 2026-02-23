"""Distillation service - manages continuous run lifecycle, events, and material flows."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db.models import (
    DistillationEvent,
    DistillationMaterial,
    DistillationParameter,
    DistillationPeriod,
    DistillationRun,
    InventoryMovement,
    Product,
)
from app.domain.rules import round_money, round_quantity
from app.services.batch_codes import BatchCodeGenerator
from app.services.inventory import InventoryService

RUN_STATUS_OPEN = "open"
RUN_STATUS_RUNNING = "running"
RUN_STATUS_PAUSED = "paused"
RUN_STATUS_CLOSED = "closed"

EVENT_RUN_OPEN = "run_open"
EVENT_FEED_CHARGE = "feed_charge"
EVENT_BOTANICAL_SWAP = "botanical_swap"
EVENT_PARAMETER_SNAPSHOT = "parameter_snapshot"
EVENT_PRODUCT_DRAW = "product_draw"
EVENT_RUN_CLOSE = "run_close"
EVENT_NOTE = "note"


class DistillationService:
    """Encapsulates distillation operations including inventory movements."""

    def __init__(self, db: Session):
        self.db = db
        self.inventory_service = InventoryService(db)
        self.batch_code_gen = BatchCodeGenerator(db)

    # ------------------------------------------------------------------ #
    # Run lifecycle
    # ------------------------------------------------------------------ #
    def list_runs(
        self, status: Optional[str] = None, limit: int = 100
    ) -> list[DistillationRun]:
        """List runs filtered by status."""
        stmt = select(DistillationRun).order_by(DistillationRun.open_at.desc())
        if status:
            stmt = stmt.where(DistillationRun.status == status)
        if limit:
            stmt = stmt.limit(limit)
        return self.db.execute(stmt).scalars().all()

    def get_run(self, run_id: str) -> DistillationRun:
        """Load a run or raise."""
        run = self.db.get(DistillationRun, run_id)
        if not run:
            raise ValueError(f"Distillation run {run_id} not found")
        return run

    def open_run(
        self,
        *,
        still_code: Optional[str],
        product_id: Optional[str],
        code: Optional[str],
        external_run_code: Optional[str],
        notes: Optional[str],
        initial_botanical_product_id: Optional[str],
        started_at: Optional[datetime],
    ) -> DistillationRun:
        """Create a new distillation run and prime an initial period/event."""
        if still_code:
            self._ensure_no_active_run(still_code)

        run_code = code or self._generate_run_code()
        if self._run_code_exists(run_code):
            raise ValueError(f"Distillation run code {run_code} already exists")

        opened_at = started_at or datetime.utcnow()

        run = DistillationRun(
            code=run_code,
            status=RUN_STATUS_RUNNING if started_at else RUN_STATUS_OPEN,
            still_code=still_code,
            product_id=product_id,
            external_run_code=external_run_code,
            open_at=opened_at,
            notes=notes,
        )
        self.db.add(run)
        self.db.flush()

        period: Optional[DistillationPeriod] = None
        if initial_botanical_product_id:
            period = DistillationPeriod(
                run_id=run.id,
                botanical_product_id=initial_botanical_product_id,
                started_at=opened_at,
                record_source="manual",
            )
            self.db.add(period)
            self.db.flush()

        self._log_event(
            run=run,
            period=period,
            event_type=EVENT_RUN_OPEN,
            occurred_at=opened_at,
            source="manual",
            payload={},
            external_id=None,
            note=notes,
        )

        return run

    def update_run(
        self,
        run_id: str,
        *,
        status: Optional[str] = None,
        close_at: Optional[datetime] = None,
        notes: Optional[str] = None,
        still_code: Optional[str] = None,
        product_id: Optional[str] = None,
        open_at: Optional[datetime] = None,
        external_run_code: Optional[str] = None,
        code: Optional[str] = None,
    ) -> DistillationRun:
        """Update run status/details."""
        run = self.get_run(run_id)

        if code and code != run.code:
            if self._run_code_exists(code):
                raise ValueError(f"Distillation run code {code} already exists")
            run.code = code

        if still_code and still_code != run.still_code:
            self._ensure_no_active_run(still_code, exclude_run_id=run.id)
            run.still_code = still_code

        if product_id and product_id != run.product_id:
            if product_id and not self.db.get(Product, product_id):
                raise ValueError(f"Product {product_id} not found")
            run.product_id = product_id

        if open_at:
            run.open_at = open_at

        if external_run_code is not None:
            run.external_run_code = external_run_code

        if status:
            if status not in {
                RUN_STATUS_OPEN,
                RUN_STATUS_RUNNING,
                RUN_STATUS_PAUSED,
                RUN_STATUS_CLOSED,
            }:
                raise ValueError(f"Invalid status '{status}' for distillation run")
            run.status = status
        if notes is not None:
            run.notes = notes

        if status == RUN_STATUS_CLOSED:
            closed_at = close_at or datetime.utcnow()
            run.close_at = closed_at
            self._close_active_period(run, closed_at)
            self._recalculate_cost(run)
            self._log_event(
                run=run,
                period=None,
                event_type=EVENT_RUN_CLOSE,
                occurred_at=closed_at,
                source="manual",
                payload={},
                external_id=None,
                note=notes,
            )

        return run

    def delete_run(self, run_id: str, *, force: bool = False) -> None:
        """Delete a distillation run."""
        run = self.get_run(run_id)

        if run.materials and not force:
            raise ValueError(
                "Cannot delete distillation run with recorded material movements. "
                "Use force delete if you are sure."
            )

        if run.materials and force:
            # Prevent deleting when materials exist to avoid orphaned inventory moves
            raise ValueError(
                "Force delete is not supported when material movements exist. "
                "Reverse inventory adjustments first."
            )

        self.db.delete(run)

    # ------------------------------------------------------------------ #
    # Event ingestion
    # ------------------------------------------------------------------ #
    def record_event(
        self,
        run_id: str,
        *,
        event_type: str,
        timestamp: Optional[datetime],
        period_id: Optional[str],
        period_ref: Optional[str],
        botanical_product_id: Optional[str],
        metrics: Optional[Dict[str, Any]],
        notes: Optional[str],
        external_id: Optional[str],
        source: Optional[str],
        inventory_payload: Optional[Dict[str, Any]],
    ) -> Tuple[DistillationEvent, Optional[DistillationMaterial]]:
        """Record an operational event and optional material movement."""
        run = self.get_run(run_id)
        occurred_at = timestamp or datetime.utcnow()
        event_source = source or "manual"

        period = None
        if period_id:
            period = self.db.get(DistillationPeriod, period_id)
            if not period or period.run_id != run.id:
                raise ValueError("Invalid period_id for this run")
        else:
            period = self._resolve_period(
                run=run,
                event_type=event_type,
                botanical_product_id=botanical_product_id,
                occurred_at=occurred_at,
                record_source=event_source,
            )

        payload: Dict[str, Any] = {}
        if metrics:
            payload["metrics"] = metrics
        if period_ref:
            payload["period_ref"] = period_ref
        if botanical_product_id:
            payload["botanical_product_id"] = botanical_product_id
        if inventory_payload:
            payload["inventory"] = inventory_payload

        event = self._log_event(
            run=run,
            period=period,
            event_type=event_type,
            occurred_at=occurred_at,
            source=event_source,
            payload=payload,
            external_id=external_id,
            note=notes,
        )

        material: Optional[DistillationMaterial] = None
        if inventory_payload:
            material = self._record_material_movement(
                run=run,
                period=period,
                event_type=event_type,
                occurred_at=occurred_at,
                inventory_payload=inventory_payload,
                note=notes,
            )

        if event_type == EVENT_PARAMETER_SNAPSHOT and metrics:
            self._record_parameter_snapshots(
                run=run,
                period=period,
                occurred_at=occurred_at,
                metrics=metrics,
            )

        if event_type == EVENT_RUN_CLOSE:
            run.status = RUN_STATUS_CLOSED
            run.close_at = occurred_at
            self._close_active_period(run, occurred_at)
            self._recalculate_cost(run)

        return event, material

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _ensure_no_active_run(
        self, still_code: str, exclude_run_id: Optional[str] = None
    ) -> None:
        stmt = select(DistillationRun).where(
            DistillationRun.still_code == still_code,
            DistillationRun.status.in_(
                [RUN_STATUS_OPEN, RUN_STATUS_RUNNING, RUN_STATUS_PAUSED]
            ),
        )
        existing = self.db.execute(stmt).scalars().first()
        if existing:
            if exclude_run_id and existing.id == exclude_run_id:
                return
            raise ValueError(
                f"Still {still_code} already has active run {existing.code} ({existing.status})"
            )

    def _generate_run_code(self) -> str:
        batch_code = self.batch_code_gen.generate_batch_code()
        return f"DST-{batch_code}"

    def _resolve_period(
        self,
        *,
        run: DistillationRun,
        event_type: str,
        botanical_product_id: Optional[str],
        occurred_at: datetime,
        record_source: str,
    ) -> Optional[DistillationPeriod]:
        if event_type == EVENT_BOTANICAL_SWAP:
            return self._swap_botanical_period(
                run=run,
                botanical_product_id=botanical_product_id,
                occurred_at=occurred_at,
                record_source=record_source,
            )

        active = self._get_active_period(run)
        if active:
            return active

        if botanical_product_id:
            period = DistillationPeriod(
                run_id=run.id,
                botanical_product_id=botanical_product_id,
                started_at=occurred_at,
                record_source=record_source,
            )
            self.db.add(period)
            self.db.flush()
            return period

        return None

    def _get_active_period(self, run: DistillationRun) -> Optional[DistillationPeriod]:
        for period in sorted(run.periods, key=lambda p: p.started_at or datetime.min):
            if period.ended_at is None:
                return period
        return None

    def _close_active_period(self, run: DistillationRun, ended_at: datetime) -> None:
        period = self._get_active_period(run)
        if period and period.started_at:
            period.ended_at = ended_at
            period.duration_seconds = int(
                (ended_at - period.started_at).total_seconds()
            )

    def _swap_botanical_period(
        self,
        *,
        run: DistillationRun,
        botanical_product_id: Optional[str],
        occurred_at: datetime,
        record_source: str,
    ) -> Optional[DistillationPeriod]:
        self._close_active_period(run, occurred_at)
        if botanical_product_id:
            new_period = DistillationPeriod(
                run_id=run.id,
                botanical_product_id=botanical_product_id,
                started_at=occurred_at,
                record_source=record_source,
            )
            self.db.add(new_period)
            self.db.flush()
            return new_period
        return None

    def _log_event(
        self,
        *,
        run: DistillationRun,
        period: Optional[DistillationPeriod],
        event_type: str,
        occurred_at: datetime,
        source: str,
        payload: Dict[str, Any],
        external_id: Optional[str],
        note: Optional[str],
    ) -> DistillationEvent:
        payload_json = (
            json.dumps(payload, default=self._json_serializer) if payload else None
        )
        event = DistillationEvent(
            run_id=run.id,
            period_id=period.id if period else None,
            event_type=event_type,
            occurred_at=occurred_at,
            source=source,
            payload_json=payload_json,
            external_id=external_id,
            note=note,
        )
        self.db.add(event)
        self.db.flush()
        return event

    def _record_material_movement(
        self,
        *,
        run: DistillationRun,
        period: Optional[DistillationPeriod],
        event_type: str,
        occurred_at: datetime,
        inventory_payload: Dict[str, Any],
        note: Optional[str],
    ) -> DistillationMaterial:
        product_id = inventory_payload.get("product_id")
        if not product_id:
            raise ValueError("Inventory payload requires product_id")

        qty_raw = inventory_payload.get("qty_kg")
        if qty_raw is None:
            raise ValueError("Inventory payload requires qty_kg")

        qty_kg = round_quantity(Decimal(str(qty_raw)))
        if qty_kg == 0:
            raise ValueError("qty_kg must be non-zero")

        direction = (inventory_payload.get("direction") or "").lower()
        if direction not in {"input", "output"}:
            if event_type == EVENT_PRODUCT_DRAW:
                direction = "output"
            else:
                direction = "input"

        uom = inventory_payload.get("uom", "KG")
        unit_cost = (
            round_money(Decimal(str(inventory_payload["unit_cost"])))
            if inventory_payload.get("unit_cost") is not None
            else None
        )
        batch_id = inventory_payload.get("batch_id")
        move_note = note or inventory_payload.get("note")

        signed_qty = qty_kg if direction == "output" else -qty_kg
        movement = InventoryMovement(
            id=str(uuid4()),
            ts=occurred_at,
            timestamp=occurred_at,
            date=occurred_at.strftime("%Y-%m-%d"),
            product_id=product_id,
            batch_id=batch_id,
            qty=signed_qty,
            unit=uom,
            uom=uom,
            direction="IN" if direction == "output" else "OUT",
            move_type=f"distillation_{direction}",
            ref_table="distillation_runs",
            ref_id=run.id,
            unit_cost=unit_cost,
            note=move_note,
        )
        self.db.add(movement)
        self.db.flush()

        material = DistillationMaterial(
            run_id=run.id,
            period_id=period.id if period else None,
            product_id=product_id,
            direction=direction,
            inventory_movement_id=movement.id,
            qty_kg=qty_kg,
            uom=uom,
            unit_cost=unit_cost,
            note=move_note,
        )
        self.db.add(material)

        if period:
            if direction == "input":
                period.feed_mass_kg = (period.feed_mass_kg or Decimal("0")) + qty_kg
            else:
                period.product_mass_kg = (
                    period.product_mass_kg or Decimal("0")
                ) + qty_kg

        self._recalculate_cost(run)

        return material

    def _record_parameter_snapshots(
        self,
        *,
        run: DistillationRun,
        period: Optional[DistillationPeriod],
        occurred_at: datetime,
        metrics: Dict[str, Any],
    ) -> None:
        for name, value in metrics.items():
            numeric_value: Optional[Decimal] = None
            text_value: Optional[str] = None
            try:
                numeric_value = round_quantity(Decimal(str(value)))
            except Exception:
                text_value = str(value)

            param = DistillationParameter(
                run_id=run.id,
                period_id=period.id if period else None,
                parameter_name=str(name),
                unit=None,
                recorded_at=occurred_at,
                value_numeric=numeric_value,
                value_text=text_value,
            )
            self.db.add(param)

    def _recalculate_cost(self, run: DistillationRun) -> Decimal:
        total_cost = Decimal("0")
        for material in run.materials:
            if material.direction == "input" and material.unit_cost is not None:
                qty = Decimal(str(material.qty_kg))
                cost = Decimal(str(material.unit_cost))
                total_cost += qty * cost
        run.actual_cost = round_money(total_cost)
        return run.actual_cost

    def _run_code_exists(self, code: str) -> bool:
        stmt = select(DistillationRun.id).where(DistillationRun.code == code)
        return self.db.execute(stmt).first() is not None

    @staticmethod
    def _json_serializer(value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
