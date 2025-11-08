from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha1
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import PriceObservation


@dataclass(frozen=True)
class DuplicateGroup:
    hash_key: str
    observation_ids: list[str]
    count: int


def compute_observation_hash(
    *,
    sku_id: str,
    company_id: str,
    location_id: Optional[str],
    observation_dt: datetime,
    channel: str,
    price_inc_gst_norm: str | float | int,
    is_carton_price: bool,
    carton_units: Optional[int],
    price_context: str,
) -> str:
    cartons = str(carton_units or 0)
    parts = [
        sku_id,
        company_id,
        location_id or "",
        observation_dt.date().isoformat(),
        channel,
        f"{Decimal(str(price_inc_gst_norm)):.2f}",
        "1" if is_carton_price else "0",
        cartons,
        price_context,
    ]
    return sha1("|".join(parts).encode("utf-8")).hexdigest()


def find_duplicate_groups(
    session: Session, limit: Optional[int] = None
) -> list[DuplicateGroup]:
    stmt = (
        select(
            PriceObservation.hash_key,
            func.count().label("dup_count"),
            func.group_concat(PriceObservation.id, ",").label("id_concat"),
        )
        .where(PriceObservation.deleted_at.is_(None))
        .group_by(PriceObservation.hash_key)
        .having(func.count() > 1)
        .order_by(func.count().desc())
    )
    if limit:
        stmt = stmt.limit(limit)

    results = session.execute(stmt).all()
    groups: list[DuplicateGroup] = []
    for hash_key, count, id_concat in results:
        id_list = id_concat.split(",") if id_concat else []
        groups.append(
            DuplicateGroup(hash_key=hash_key, observation_ids=id_list, count=count)
        )
    return groups


def apply_hash_to_observation(observation: PriceObservation) -> None:
    observation.hash_key = compute_observation_hash(
        sku_id=observation.sku_id,
        company_id=observation.company_id,
        location_id=observation.location_id,
        observation_dt=observation.observation_dt,
        channel=observation.channel,
        price_inc_gst_norm=observation.price_inc_gst_norm,
        is_carton_price=observation.is_carton_price,
        carton_units=observation.carton_units,
        price_context=observation.price_context,
    )
