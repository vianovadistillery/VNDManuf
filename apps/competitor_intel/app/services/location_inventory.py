from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Optional

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from ..models import (
    SKU,
    Brand,
    Location,
    LocationSKU,
    PriceObservation,
    Product,
)
from .costs import get_active_cost


@dataclass(slots=True)
class ObservationSummary:
    observation_id: str
    observed_at: datetime
    channel: str
    price_context: str
    price_basis: str
    price_inc_gst: Optional[float]
    price_ex_gst: Optional[float]
    unit_price_inc_gst: Optional[float]


@dataclass(slots=True)
class CostSummary:
    cost_id: str
    effective_date: date
    cost_type: str
    currency: str
    cost_per_unit: Optional[float]
    cost_per_pack: Optional[float]
    cost_per_carton: Optional[float]


@dataclass(slots=True)
class InventoryItem:
    location_sku_id: str
    sku_id: str
    sku_label: str
    brand_name: str
    product_name: str
    category: str
    is_manual: bool
    notes: Optional[str]
    first_observed_dt: Optional[datetime]
    last_observed_dt: Optional[datetime]
    latest_observation: Optional[ObservationSummary]
    latest_cost: Optional[CostSummary]
    history: list[ObservationSummary]


def ensure_location_sku(
    session: Session,
    *,
    location_id: str,
    sku_id: str,
    observation_dt: Optional[datetime] = None,
    is_manual: bool = False,
    notes: Optional[str] = None,
) -> LocationSKU:
    """Create or update a location ↔ SKU link, tracking first/last observation timestamps."""

    stmt = select(LocationSKU).where(
        LocationSKU.location_id == location_id,
        LocationSKU.sku_id == sku_id,
        LocationSKU.deleted_at.is_(None),
    )
    link = session.execute(stmt).scalar_one_or_none()
    if link is None:
        link = LocationSKU(
            location_id=location_id,
            sku_id=sku_id,
            is_manual=is_manual,
            notes=notes,
            first_observed_dt=observation_dt,
            last_observed_dt=observation_dt,
        )
        session.add(link)
        session.flush([link])
        return link

    if observation_dt is not None:
        if link.first_observed_dt is None or observation_dt < link.first_observed_dt:
            link.first_observed_dt = observation_dt
        if link.last_observed_dt is None or observation_dt > link.last_observed_dt:
            link.last_observed_dt = observation_dt
    if is_manual and not link.is_manual:
        link.is_manual = True
    if notes:
        if not link.notes:
            link.notes = notes
    session.flush([link])
    return link


def fetch_location_inventory(
    session: Session,
    *,
    location_id: str,
    include_history: bool = False,
    history_limit: int = 50,
) -> dict:
    """Return a structured view of the products available at a location."""

    location = session.get(Location, location_id)
    if location is None or location.deleted_at is not None:
        return {"location": None, "items": []}

    base_stmt: Select = (
        select(LocationSKU, SKU, Product, Brand)
        .join(LocationSKU.sku)
        .join(SKU.product)
        .join(Product.brand)
        .where(
            LocationSKU.location_id == location_id,
            LocationSKU.deleted_at.is_(None),
            SKU.deleted_at.is_(None),
            Product.deleted_at.is_(None),
            Brand.deleted_at.is_(None),
        )
        .order_by(Brand.name, Product.name, SKU.gtin)
    )
    rows = session.execute(base_stmt).all()
    if not rows:
        return {
            "location": _location_snapshot(location),
            "items": [],
        }

    sku_ids = [row[1].id for row in rows]
    unique_sku_ids = list(dict.fromkeys(sku_ids))
    latest_map = _latest_observations(session, location_id, unique_sku_ids)
    cost_map = _cost_summary(session, unique_sku_ids)
    history_map = (
        _observation_history(session, location_id, unique_sku_ids, history_limit)
        if include_history
        else {}
    )

    items: list[InventoryItem] = []
    for link, sku, product, brand in rows:
        latest = latest_map.get(sku.id)
        latest_cost = cost_map.get(sku.id)
        history = history_map.get(sku.id, []) if include_history else []
        items.append(
            InventoryItem(
                location_sku_id=link.id,
                sku_id=sku.id,
                sku_label=_format_sku_label(sku, brand, product),
                brand_name=brand.name,
                product_name=product.name,
                category=product.category,
                is_manual=link.is_manual,
                notes=link.notes,
                first_observed_dt=link.first_observed_dt,
                last_observed_dt=link.last_observed_dt,
                latest_observation=latest,
                latest_cost=latest_cost,
                history=history,
            )
        )

    return {
        "location": _location_snapshot(location),
        "items": items,
    }


def _location_snapshot(location: Location) -> dict:
    return {
        "id": location.id,
        "company_id": location.company_id,
        "store_name": location.store_name,
        "address": location.address,
        "suburb": location.suburb,
        "state": location.state,
        "postcode": location.postcode,
        "chain_alignment": location.chain_alignment,
        "main_contact": location.main_contact,
        "decision_maker": location.decision_maker,
    }


def _latest_observations(
    session: Session, location_id: str, sku_ids: Iterable[str]
) -> dict[str, ObservationSummary]:
    if not sku_ids:
        return {}
    stmt = (
        select(
            PriceObservation.sku_id,
            PriceObservation.id,
            PriceObservation.observation_dt,
            PriceObservation.channel,
            PriceObservation.price_context,
            PriceObservation.price_basis,
            PriceObservation.price_inc_gst_norm,
            PriceObservation.price_ex_gst_norm,
            PriceObservation.unit_price_inc_gst,
        )
        .where(
            PriceObservation.location_id == location_id,
            PriceObservation.sku_id.in_(sku_ids),
            PriceObservation.deleted_at.is_(None),
        )
        .order_by(
            PriceObservation.sku_id,
            PriceObservation.observation_dt.desc(),
            PriceObservation.created_at.desc(),
        )
    )
    rows = session.execute(stmt).all()
    latest: dict[str, ObservationSummary] = {}
    for (
        sku_id,
        obs_id,
        observed_at,
        channel,
        price_context,
        price_basis,
        price_inc,
        price_ex,
        unit_price,
    ) in rows:
        if sku_id in latest:
            continue
        latest[sku_id] = ObservationSummary(
            observation_id=obs_id,
            observed_at=observed_at,
            channel=channel,
            price_context=price_context,
            price_basis=price_basis,
            price_inc_gst=float(price_inc) if price_inc is not None else None,
            price_ex_gst=float(price_ex) if price_ex is not None else None,
            unit_price_inc_gst=float(unit_price) if unit_price is not None else None,
        )
    return latest


def _observation_history(
    session: Session,
    location_id: str,
    sku_ids: Iterable[str],
    history_limit: int,
) -> dict[str, list[ObservationSummary]]:
    if not sku_ids or history_limit <= 0:
        return {}

    stmt = (
        select(
            PriceObservation.sku_id,
            PriceObservation.id,
            PriceObservation.observation_dt,
            PriceObservation.channel,
            PriceObservation.price_context,
            PriceObservation.price_basis,
            PriceObservation.price_inc_gst_norm,
            PriceObservation.price_ex_gst_norm,
            PriceObservation.unit_price_inc_gst,
        )
        .where(
            PriceObservation.location_id == location_id,
            PriceObservation.sku_id.in_(sku_ids),
            PriceObservation.deleted_at.is_(None),
        )
        .order_by(PriceObservation.observation_dt.desc())
        .limit(history_limit * max(len(set(sku_ids)), 1))
    )
    rows = session.execute(stmt).all()

    history: dict[str, list[ObservationSummary]] = defaultdict(list)
    for (
        sku_id,
        obs_id,
        observed_at,
        channel,
        price_context,
        price_basis,
        price_inc,
        price_ex,
        unit_price,
    ) in rows:
        bucket = history[sku_id]
        if len(bucket) >= history_limit:
            continue
        bucket.append(
            ObservationSummary(
                observation_id=obs_id,
                observed_at=observed_at,
                channel=channel,
                price_context=price_context,
                price_basis=price_basis,
                price_inc_gst=float(price_inc) if price_inc is not None else None,
                price_ex_gst=float(price_ex) if price_ex is not None else None,
                unit_price_inc_gst=float(unit_price)
                if unit_price is not None
                else None,
            )
        )
    return history


def _cost_summary(
    session: Session, sku_ids: Iterable[str]
) -> dict[str, Optional[CostSummary]]:
    result: dict[str, Optional[CostSummary]] = {}
    for sku_id in sku_ids:
        cost = get_active_cost(session, sku_id, prefer_known=True)
        if not cost:
            result[sku_id] = None
            continue
        result[sku_id] = CostSummary(
            cost_id=cost.id,
            effective_date=cost.effective_date,
            cost_type=cost.cost_type,
            currency=cost.cost_currency,
            cost_per_unit=float(cost.cost_per_unit)
            if cost.cost_per_unit is not None
            else None,
            cost_per_pack=float(cost.cost_per_pack)
            if cost.cost_per_pack is not None
            else None,
            cost_per_carton=float(cost.cost_per_carton)
            if cost.cost_per_carton is not None
            else None,
        )
    return result


def _format_sku_label(sku: SKU, brand: Brand, product: Product) -> str:
    parts = [brand.name, product.name]
    if sku.gtin:
        parts.append(f"GTIN {sku.gtin}")
    return " • ".join(parts)


__all__ = [
    "InventoryItem",
    "ObservationSummary",
    "CostSummary",
    "ensure_location_sku",
    "fetch_location_inventory",
]
