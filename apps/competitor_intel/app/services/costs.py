from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from ..models import ManufacturingCost


@dataclass(slots=True)
class CostRecord:
    id: str
    sku_id: str
    cost_type: str
    cost_currency: str
    cost_per_unit: Optional[Decimal]
    cost_per_pack: Optional[Decimal]
    cost_per_carton: Optional[Decimal]
    effective_date: date
    notes: Optional[str]


def _active_costs_query(sku_id: str, *, include_deleted: bool = False) -> Select:
    stmt = select(ManufacturingCost).where(ManufacturingCost.sku_id == sku_id)
    if not include_deleted:
        stmt = stmt.where(ManufacturingCost.deleted_at.is_(None))
    return stmt


def list_costs(
    session: Session, sku_id: str, *, include_deleted: bool = False
) -> list[CostRecord]:
    rows: Iterable[ManufacturingCost] = session.scalars(
        _active_costs_query(sku_id, include_deleted=include_deleted).order_by(
            ManufacturingCost.effective_date.desc(), ManufacturingCost.cost_type.desc()
        )
    )
    return [
        CostRecord(
            id=row.id,
            sku_id=row.sku_id,
            cost_type=row.cost_type,
            cost_currency=row.cost_currency,
            cost_per_unit=row.cost_per_unit,
            cost_per_pack=row.cost_per_pack,
            cost_per_carton=row.cost_per_carton,
            effective_date=row.effective_date,
            notes=row.notes,
        )
        for row in rows
    ]


def get_active_cost(
    session: Session,
    sku_id: str,
    *,
    as_of: Optional[date] = None,
    prefer_known: bool = True,
) -> Optional[ManufacturingCost]:
    stmt = _active_costs_query(sku_id)
    if as_of is not None:
        stmt = stmt.where(ManufacturingCost.effective_date <= as_of)
    costs: list[ManufacturingCost] = list(
        session.scalars(
            stmt.order_by(
                ManufacturingCost.effective_date.desc(),
                ManufacturingCost.cost_type.desc(),
            )
        )
    )
    if not costs:
        return None
    if not prefer_known:
        return costs[0]
    for row in costs:
        if row.cost_type == "known":
            return row
    return costs[0]


def upsert_cost(
    session: Session,
    *,
    sku_id: str,
    cost_type: str,
    effective_date: date,
    cost_currency: str,
    cost_per_unit: Optional[Decimal],
    cost_per_pack: Optional[Decimal],
    cost_per_carton: Optional[Decimal],
    notes: Optional[str] = None,
) -> ManufacturingCost:
    cost_type = cost_type.lower()
    if cost_type not in {"estimated", "known"}:
        raise ValueError("cost_type must be 'estimated' or 'known'")
    stmt = _active_costs_query(sku_id, include_deleted=True).where(
        ManufacturingCost.cost_type == cost_type,
        ManufacturingCost.effective_date == effective_date,
    )
    instance = session.scalars(stmt).first()
    if instance is None:
        instance = ManufacturingCost(
            sku_id=sku_id,
            cost_type=cost_type,
            effective_date=effective_date,
        )
        session.add(instance)
    instance.cost_currency = cost_currency
    instance.cost_per_unit = cost_per_unit
    instance.cost_per_pack = cost_per_pack
    instance.cost_per_carton = cost_per_carton
    instance.notes = notes
    instance.deleted_at = None
    return instance


def soft_delete_cost(session: Session, cost_id: str) -> bool:
    instance = session.get(ManufacturingCost, cost_id)
    if instance is None or instance.deleted_at is not None:
        return False
    instance.deleted_at = datetime.now(timezone.utc)
    return True


__all__ = [
    "CostRecord",
    "list_costs",
    "get_active_cost",
    "upsert_cost",
    "soft_delete_cost",
]
