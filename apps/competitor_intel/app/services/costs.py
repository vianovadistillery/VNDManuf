from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from ..models import PurchasePrice


@dataclass(slots=True)
class PurchasePriceRecord:
    id: str
    sku_id: str
    price_type: str
    currency: str
    price_per_unit: Optional[Decimal]
    price_per_pack: Optional[Decimal]
    price_per_carton: Optional[Decimal]
    effective_date: date
    notes: Optional[str]


def _active_costs_query(sku_id: str, *, include_deleted: bool = False) -> Select:
    stmt = select(PurchasePrice).where(PurchasePrice.sku_id == sku_id)
    if not include_deleted:
        stmt = stmt.where(PurchasePrice.deleted_at.is_(None))
    return stmt


def list_costs(
    session: Session, sku_id: str, *, include_deleted: bool = False
) -> list[PurchasePriceRecord]:
    rows: Iterable[PurchasePrice] = session.scalars(
        _active_costs_query(sku_id, include_deleted=include_deleted).order_by(
            PurchasePrice.effective_date.desc(), PurchasePrice.cost_type.desc()
        )
    )
    return [
        PurchasePriceRecord(
            id=row.id,
            sku_id=row.sku_id,
            price_type=row.cost_type,
            currency=row.cost_currency,
            price_per_unit=row.cost_per_unit,
            price_per_pack=row.cost_per_pack,
            price_per_carton=row.cost_per_carton,
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
) -> Optional[PurchasePrice]:
    stmt = _active_costs_query(sku_id)
    if as_of is not None:
        stmt = stmt.where(PurchasePrice.effective_date <= as_of)
    costs: list[PurchasePrice] = list(
        session.scalars(
            stmt.order_by(
                PurchasePrice.effective_date.desc(),
                PurchasePrice.cost_type.desc(),
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


def create_purchase_price(
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
) -> PurchasePrice:
    cost_type = cost_type.lower()
    if cost_type not in {"estimated", "known"}:
        raise ValueError("cost_type must be 'estimated' or 'known'")
    instance = PurchasePrice(
        sku_id=sku_id,
        cost_type=cost_type,
        effective_date=effective_date,
        cost_currency=cost_currency,
        cost_per_unit=cost_per_unit,
        cost_per_pack=cost_per_pack,
        cost_per_carton=cost_per_carton,
        notes=notes,
    )
    session.add(instance)
    return instance


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
) -> PurchasePrice:
    cost_type = cost_type.lower()
    if cost_type not in {"estimated", "known"}:
        raise ValueError("cost_type must be 'estimated' or 'known'")
    stmt = _active_costs_query(sku_id, include_deleted=True).where(
        PurchasePrice.cost_type == cost_type,
        PurchasePrice.effective_date == effective_date,
    )
    instance = session.scalars(stmt).first()
    if instance is None:
        instance = create_purchase_price(
            session,
            sku_id=sku_id,
            cost_type=cost_type,
            effective_date=effective_date,
            cost_currency=cost_currency,
            cost_per_unit=cost_per_unit,
            cost_per_pack=cost_per_pack,
            cost_per_carton=cost_per_carton,
            notes=notes,
        )
    else:
        instance.cost_currency = cost_currency
        instance.cost_per_unit = cost_per_unit
        instance.cost_per_pack = cost_per_pack
        instance.cost_per_carton = cost_per_carton
        instance.notes = notes
        instance.deleted_at = None
    return instance


def soft_delete_cost(session: Session, cost_id: str) -> bool:
    instance = session.get(PurchasePrice, cost_id)
    if instance is None or instance.deleted_at is not None:
        return False
    instance.deleted_at = datetime.now(timezone.utc)
    return True


__all__ = [
    "PurchasePriceRecord",
    "list_costs",
    "get_active_cost",
    "create_purchase_price",
    "upsert_cost",
    "soft_delete_cost",
]
