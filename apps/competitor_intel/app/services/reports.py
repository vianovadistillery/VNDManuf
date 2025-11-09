from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from statistics import median
from typing import Optional

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from ..models import (
    SKU,
    Brand,
    Company,
    Location,
    PackageSpec,
    PriceObservation,
    Product,
    PurchasePrice,
)
from .dedupe import find_duplicate_groups


@dataclass(slots=True)
class ObservationFilters:
    brand_ids: list[str] = field(default_factory=list)
    product_ids: list[str] = field(default_factory=list)
    sku_ids: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    package_types: list[str] = field(default_factory=list)
    can_form_factors: list[str] = field(default_factory=list)
    carton_units: list[int] = field(default_factory=list)
    channels: list[str] = field(default_factory=list)
    price_bases: list[str] = field(default_factory=list)
    company_ids: list[str] = field(default_factory=list)
    location_ids: list[str] = field(default_factory=list)
    price_contexts: list[str] = field(default_factory=list)
    availability: list[str] = field(default_factory=list)
    states: list[str] = field(default_factory=list)
    suburbs: list[str] = field(default_factory=list)
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None
    search: Optional[str] = None


def _observation_select(*columns) -> Select:
    if not columns:
        columns = (PriceObservation.id,)
    stmt = (
        select(*columns)
        .select_from(PriceObservation)
        .join(SKU, PriceObservation.sku)
        .join(Product, SKU.product)
        .join(Brand, Product.brand)
        .join(PackageSpec, SKU.package_spec)
        .join(Company, PriceObservation.company)
        .outerjoin(Location, PriceObservation.location)
        .where(PriceObservation.deleted_at.is_(None))
    )
    return stmt


def _apply_filters(stmt: Select, filters: ObservationFilters) -> Select:
    if filters.brand_ids:
        stmt = stmt.where(Brand.id.in_(filters.brand_ids))
    if filters.product_ids:
        stmt = stmt.where(Product.id.in_(filters.product_ids))
    if filters.sku_ids:
        stmt = stmt.where(SKU.id.in_(filters.sku_ids))
    if filters.categories:
        stmt = stmt.where(Product.category.in_(filters.categories))
    if filters.package_types:
        stmt = stmt.where(PackageSpec.type.in_(filters.package_types))
    if filters.can_form_factors:
        stmt = stmt.where(PackageSpec.can_form_factor.in_(filters.can_form_factors))
    if filters.carton_units:
        stmt = stmt.where(PriceObservation.carton_units.in_(filters.carton_units))
    if filters.channels:
        stmt = stmt.where(PriceObservation.channel.in_(filters.channels))
    if filters.price_bases:
        stmt = stmt.where(PriceObservation.price_basis.in_(filters.price_bases))
    if filters.company_ids:
        stmt = stmt.where(Company.id.in_(filters.company_ids))
    if filters.location_ids:
        stmt = stmt.where(Location.id.in_(filters.location_ids))
    if filters.price_contexts:
        stmt = stmt.where(PriceObservation.price_context.in_(filters.price_contexts))
    if filters.availability:
        stmt = stmt.where(PriceObservation.availability.in_(filters.availability))
    if filters.states:
        stmt = stmt.where(Location.state.in_(filters.states))
    if filters.suburbs:
        stmt = stmt.where(Location.suburb.in_(filters.suburbs))
    if filters.start_dt:
        stmt = stmt.where(PriceObservation.observation_dt >= filters.start_dt)
    if filters.end_dt:
        stmt = stmt.where(PriceObservation.observation_dt <= filters.end_dt)
    if filters.search:
        pattern = f"%{filters.search.lower()}%"
        stmt = stmt.where(
            func.lower(Brand.name).like(pattern)
            | func.lower(Product.name).like(pattern)
        )
    return stmt


def get_kpis(session: Session) -> dict[str, int]:
    brands = session.query(Brand).filter(Brand.deleted_at.is_(None)).count()
    skus = session.query(SKU).filter(SKU.deleted_at.is_(None)).count()
    observations = (
        session.query(PriceObservation)
        .filter(PriceObservation.deleted_at.is_(None))
        .count()
    )
    known_costs = session.execute(
        select(func.count(func.distinct(PurchasePrice.sku_id))).where(
            PurchasePrice.deleted_at.is_(None),
            PurchasePrice.cost_type == "known",
        )
    ).scalar_one()
    estimated_costs = session.execute(
        select(func.count(func.distinct(PurchasePrice.sku_id))).where(
            PurchasePrice.deleted_at.is_(None),
            PurchasePrice.cost_type == "estimated",
        )
    ).scalar_one()
    return {
        "brands": int(brands or 0),
        "skus": int(skus or 0),
        "observations": int(observations or 0),
        "skus_with_known_costs": int(known_costs or 0),
        "skus_with_estimated_costs": int(estimated_costs or 0),
    }


def get_filtered_counts(
    session: Session, filters: ObservationFilters
) -> dict[str, int]:
    base = _apply_filters(
        _observation_select(
            func.count(func.distinct(Brand.id)),
            func.count(func.distinct(SKU.id)),
            func.count(),
        ),
        filters,
    )
    row = session.execute(base).one()
    return {
        "brands": int(row[0] or 0),
        "skus": int(row[1] or 0),
        "observations": int(row[2] or 0),
    }


def get_recent_observations(session: Session, limit: int = 15) -> list[dict]:
    stmt = (
        _apply_filters(
            _observation_select(
                PriceObservation,
                SKU,
                Product,
                Brand,
                Company,
                Location,
                PackageSpec,
            ),
            ObservationFilters(),
        )
        .order_by(PriceObservation.observation_dt.desc())
        .limit(limit)
    )

    rows = session.execute(stmt).all()
    return [_row_to_dict(row) for row in rows]


def count_observations(session: Session, filters: ObservationFilters) -> int:
    stmt = _apply_filters(_observation_select(), filters)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    return session.execute(count_stmt).scalar_one()


def fetch_observations(
    session: Session,
    filters: ObservationFilters,
    *,
    page: int,
    page_size: int,
) -> dict:
    stmt = _apply_filters(
        _observation_select(
            PriceObservation,
            SKU,
            Product,
            Brand,
            Company,
            Location,
            PackageSpec,
        ),
        filters,
    ).order_by(PriceObservation.observation_dt.desc())

    offset = max(page - 1, 0) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    rows = session.execute(stmt).all()
    total = count_observations(session, filters)
    return {
        "items": [_row_to_dict(row) for row in rows],
        "total": total,
    }


def get_price_time_series(session: Session, filters: ObservationFilters) -> list[dict]:
    time_bucket = func.strftime("%Y-%W", PriceObservation.observation_dt).label(
        "period"
    )
    stmt = (
        _apply_filters(
            _observation_select(
                time_bucket,
                SKU.id.label("sku_id"),
                Product.name.label("product_name"),
                Brand.name.label("brand_name"),
                func.avg(PriceObservation.price_inc_gst_norm).label("avg_price"),
                func.avg(PriceObservation.gp_unit_pct).label("avg_gp_pct"),
                func.count().label("samples"),
            ),
            filters,
        )
        .group_by(time_bucket, SKU.id, Product.name, Brand.name)
        .order_by(time_bucket, Brand.name, Product.name)
    )

    rows = session.execute(stmt).all()
    return [
        {
            "period": period,
            "sku_id": sku_id,
            "sku_label": f"{brand_name} - {product_name}",
            "avg_price": float(avg_price) if avg_price is not None else None,
            "avg_gp_pct": float(avg_gp_pct) * 100 if avg_gp_pct is not None else None,
            "samples": samples,
        }
        for period, sku_id, product_name, brand_name, avg_price, avg_gp_pct, samples in rows
    ]


def get_price_distribution(session: Session, filters: ObservationFilters) -> list[dict]:
    stmt = (
        _apply_filters(
            _observation_select(
                Company.name,
                func.avg(PriceObservation.price_per_litre),
                func.avg(PriceObservation.gp_unit_pct),
                func.count(),
            ),
            filters,
        )
        .group_by(Company.name)
        .order_by(Company.name)
    )
    rows = session.execute(stmt).all()
    return [
        {
            "company": company or "Unknown",
            "avg_price_per_litre": float(avg_price) if avg_price is not None else None,
            "avg_gp_pct": float(avg_gp_pct) * 100 if avg_gp_pct is not None else None,
            "samples": samples,
        }
        for company, avg_price, avg_gp_pct, samples in rows
    ]


def get_map_summary(session: Session, filters: ObservationFilters) -> list[dict]:
    stmt = _apply_filters(
        _observation_select(
            Location.state,
            Location.suburb,
            Location.lat,
            Location.lon,
            PriceObservation.price_inc_gst_norm,
            PriceObservation.gp_unit_pct,
        ).where(Location.id.is_not(None)),
        filters,
    )
    rows = session.execute(stmt).all()

    accumulator: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(
        lambda: {"prices": [], "gps": [], "lats": [], "lons": []}
    )
    for state, suburb, lat, lon, price, gp in rows:
        if state is None or suburb is None or price is None:
            continue
        bucket = accumulator[(state, suburb)]
        bucket["prices"].append(float(price))
        if gp is not None:
            bucket["gps"].append(float(gp * Decimal("100")))
        if lat is not None and lon is not None:
            bucket["lats"].append(float(lat))
            bucket["lons"].append(float(lon))

    summary = []
    for (state, suburb), values in accumulator.items():
        prices = values["prices"]
        summary.append(
            {
                "state": state,
                "suburb": suburb,
                "median_price_inc_gst": median(prices),
                "samples": len(prices),
                "lat": sum(values["lats"]) / len(values["lats"])
                if values["lats"]
                else None,
                "lon": sum(values["lons"]) / len(values["lons"])
                if values["lons"]
                else None,
                "median_gp_pct": median(values["gps"]) if values["gps"] else None,
            }
        )
    summary.sort(key=lambda item: (item["state"], item["suburb"]))
    return summary


def get_duplicate_overview(session: Session, limit: int = 25) -> list[dict]:
    groups = find_duplicate_groups(session, limit=limit)
    return [
        {
            "hash_key": group.hash_key,
            "count": group.count,
            "observation_ids": group.observation_ids,
        }
        for group in groups
    ]


def get_missing_gtins(session: Session) -> list[dict]:
    rows = session.execute(
        select(SKU, Product.name, Brand.name)
        .join(SKU.product)
        .join(Product.brand)
        .where(
            SKU.deleted_at.is_(None),
            Product.deleted_at.is_(None),
            Brand.deleted_at.is_(None),
            or_(SKU.gtin.is_(None), func.trim(SKU.gtin) == ""),
        )
        .order_by(Brand.name, Product.name)
    ).all()
    return [
        {
            "brand": brand_name,
            "product": product_name,
            "sku_id": sku.id,
            "is_active": sku.is_active,
        }
        for sku, product_name, brand_name in rows
    ]


def get_price_outliers(
    session: Session, filters: ObservationFilters, z_threshold: float = 3.0
) -> list[dict]:
    stmt = _apply_filters(
        _observation_select(
            PriceObservation.id,
            SKU.id,
            Product.name,
            Brand.name,
            Company.name,
            PriceObservation.price_per_litre,
            PriceObservation.gp_unit_pct,
            PriceObservation.observation_dt,
        ),
        filters,
    )
    rows = session.execute(stmt).all()

    grouped: dict[str, list[dict]] = defaultdict(list)
    for (
        obs_id,
        sku_id,
        product_name,
        brand_name,
        company_name,
        price_per_litre,
        gp_pct,
        obs_dt,
    ) in rows:
        price = float(price_per_litre)
        grouped[sku_id].append(
            {
                "observation_id": obs_id,
                "price_per_litre": price,
                "brand": brand_name,
                "product": product_name,
                "company": company_name,
                "gp_unit_pct": float(gp_pct * Decimal("100"))
                if gp_pct is not None
                else None,
                "observation_dt": obs_dt,
            }
        )

    outliers: list[dict] = []
    for sku_id, observations in grouped.items():
        if len(observations) < 5:
            continue
        values = [obs["price_per_litre"] for obs in observations]
        mean_value = sum(values) / len(values)
        variance = sum((v - mean_value) ** 2 for v in values) / len(values)
        std_dev = variance**0.5
        if std_dev == 0:
            continue
        for obs in observations:
            z_score = (obs["price_per_litre"] - mean_value) / std_dev
            if abs(z_score) >= z_threshold:
                outliers.append(
                    {
                        "observation_id": obs["observation_id"],
                        "sku_id": sku_id,
                        "brand": obs["brand"],
                        "product": obs["product"],
                        "company": obs["company"],
                        "price_per_litre": obs["price_per_litre"],
                        "gp_unit_pct": obs["gp_unit_pct"],
                        "z_score": round(z_score, 2),
                        "observation_dt": obs["observation_dt"].isoformat(),
                    }
                )

    return sorted(outliers, key=lambda item: abs(item["z_score"]), reverse=True)


def _pack_info(sku: SKU) -> Optional[dict]:
    assignment = getattr(sku, "pack_assignment", None)
    if not assignment or assignment.pack_spec is None:
        return None
    spec = assignment.pack_spec
    return {
        "pack_spec_id": spec.id,
        "units_per_pack": spec.units_per_pack,
        "gtin": spec.gtin,
        "notes": spec.notes,
    }


def _carton_info(sku: SKU) -> list[dict]:
    details: list[dict] = []
    for link in getattr(sku, "carton_links", []) or []:
        spec = getattr(link, "carton_spec", None)
        if spec is None:
            continue
        details.append(
            {
                "carton_spec_id": spec.id,
                "units_per_carton": spec.units_per_carton,
                "pack_count": spec.pack_count,
                "gtin": spec.gtin,
                "mode": "pack" if spec.pack_spec_id else "unit",
                "notes": spec.notes,
            }
        )
    return sorted(details, key=lambda item: (item["mode"], item["units_per_carton"]))


def _row_to_dict(row) -> dict:
    (
        observation,
        sku,
        product,
        brand,
        company,
        location,
        package_spec,
    ) = row
    return {
        "id": observation.id,
        "sku_id": sku.id,
        "brand": brand.name,
        "product": product.name,
        "category": product.category,
        "package": {
            "type": package_spec.type,
            "container_ml": package_spec.container_ml,
            "can_form_factor": package_spec.can_form_factor,
        },
        "gtin": sku.gtin,
        "pack": _pack_info(sku),
        "cartons": _carton_info(sku),
        "company": company.name,
        "location": {
            "state": location.state if location else None,
            "suburb": location.suburb if location else None,
            "store_name": location.store_name if location else None,
        },
        "channel": observation.channel,
        "price_context": observation.price_context,
        "promo_name": observation.promo_name,
        "availability": observation.availability,
        "price_inc_gst_norm": float(observation.price_inc_gst_norm),
        "unit_price_inc_gst": float(observation.unit_price_inc_gst),
        "pack_price_inc_gst": float(observation.pack_price_inc_gst)
        if observation.pack_price_inc_gst is not None
        else None,
        "carton_price_inc_gst": float(observation.carton_price_inc_gst)
        if observation.carton_price_inc_gst is not None
        else None,
        "price_per_litre": float(observation.price_per_litre),
        "price_per_unit_pure_alcohol": float(observation.price_per_unit_pure_alcohol),
        "standard_drinks": float(observation.standard_drinks),
        "price_basis": (observation.price_basis or "unit").title(),
        "gp_unit_abs": float(observation.gp_unit_abs)
        if observation.gp_unit_abs is not None
        else None,
        "gp_unit_pct": round(float(observation.gp_unit_pct * Decimal("100")), 2)
        if observation.gp_unit_pct is not None
        else None,
        "gp_pack_abs": float(observation.gp_pack_abs)
        if observation.gp_pack_abs is not None
        else None,
        "gp_pack_pct": round(float(observation.gp_pack_pct * Decimal("100")), 2)
        if observation.gp_pack_pct is not None
        else None,
        "gp_carton_abs": float(observation.gp_carton_abs)
        if observation.gp_carton_abs is not None
        else None,
        "gp_carton_pct": round(float(observation.gp_carton_pct * Decimal("100")), 2)
        if observation.gp_carton_pct is not None
        else None,
        "observation_dt": observation.observation_dt.isoformat(),
    }
