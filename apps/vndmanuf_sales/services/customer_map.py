"""Customer map data for the sales overview dashboard."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.adapters.db.models import (
    BuyingGroup,
    Contact,
    Customer,
    CustomerRepAssignment,
    Pricebook,
    SalesOrder,
    SalesRep,
)
from apps.vndmanuf_sales.models import SalesOrderStatus
from apps.vndmanuf_sales.services.totals import _dec, _quantize

STATE_COORDS: Dict[str, Tuple[float, float]] = {
    "NSW": (-33.8688, 151.2093),
    "VIC": (-37.8136, 144.9631),
    "QLD": (-27.4698, 153.0251),
    "SA": (-34.9285, 138.6007),
    "WA": (-31.9505, 115.8605),
    "TAS": (-42.8821, 147.3272),
    "NT": (-12.4634, 130.8456),
    "ACT": (-35.2809, 149.1300),
}

VOLUME_BANDS = (
    ("under_1000", "Under $1,000", 0, 1000),
    ("1000_5000", "$1,000 – $5,000", 1000, 5000),
    ("5000_15000", "$5,000 – $15,000", 5000, 15000),
    ("over_15000", "$15,000+", 15000, None),
)

RELATIONSHIP_STATUSES = (
    ("active", "Active"),
    ("prospective", "Prospective"),
    ("lapsed", "Lapsed"),
)

_NONE_GROUP_COLOR = "#9E9E9E"

LOCATION_SOURCE_LABELS = {
    "customer": "Exact coordinates",
    "contact": "Contact coordinates",
    "site": "Site coordinates",
    "state_estimate": "Approximate (state centre)",
    "site_state_estimate": "Approximate (site state)",
    "unmapped": "No location",
}


def format_customer_address(customer: Customer) -> Optional[str]:
    parts = []
    line1 = (
        customer.delivery_address_line1 or customer.billing_address_line1 or ""
    ).strip()
    if line1:
        parts.append(line1)
    suburb = customer.delivery_suburb or customer.billing_suburb
    state = customer.delivery_state or customer.billing_state
    postcode = customer.delivery_postcode or customer.billing_postcode
    locality = ", ".join(p for p in [suburb, state, postcode] if p)
    if locality:
        parts.append(locality)
    if not parts and (customer.address or "").strip():
        return (customer.address or "").strip()[:200]
    return ", ".join(parts) if parts else None


@dataclass
class CustomerMapPoint:
    customer_id: str
    name: str
    code: str
    lat: float
    lon: float
    buying_group_id: Optional[str]
    buying_group_name: str
    buying_group_color: str
    relationship_status: str
    price_level: Optional[str]
    sales_rep_name: Optional[str]
    period_revenue: Decimal
    volume_band: str
    location_source: str
    location_label: str
    address_display: Optional[str] = None
    suburb: Optional[str] = None
    state: Optional[str] = None


@dataclass
class CustomerMapSummary:
    points: List[dict] = field(default_factory=list)
    legend: List[dict] = field(default_factory=list)
    total_customers: int = 0
    mapped_customers: int = 0
    unmapped_customers: int = 0


def _as_datetime_start(d: date) -> datetime:
    return datetime(d.year, d.month, d.day)


def _as_datetime_end(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, 23, 59, 59)


def _jitter(entity_id: str, scale: float = 0.35) -> Tuple[float, float]:
    digest = hashlib.md5(entity_id.encode()).digest()
    return (
        (digest[0] - 128) / 128 * scale,
        (digest[1] - 128) / 128 * scale,
    )


def _state_from_postcode(postcode: Optional[str]) -> Optional[str]:
    pc = re.sub(r"\D", "", (postcode or "").strip())
    if not pc:
        return None
    if pc.startswith("08") or pc.startswith("09"):
        return "NT"
    if pc.startswith("26") or pc.startswith("29"):
        return "ACT"
    first = pc[0]
    if first == "2":
        return "NSW"
    if first == "3":
        return "VIC"
    if first == "4":
        return "QLD"
    if first == "5":
        return "SA"
    if first == "6":
        return "WA"
    if first == "7":
        return "TAS"
    return None


def _volume_band(revenue: Decimal) -> str:
    value = float(revenue)
    for band_id, _, low, high in VOLUME_BANDS:
        if high is None and value >= low:
            return band_id
        if high is not None and low <= value < high:
            return band_id
    return "under_1000"


def _normalize_price_level(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    return raw.replace("_", " ").strip().title()


class CustomerMapService:
    def __init__(self, db: Session):
        self.db = db

    def filter_options(self) -> dict:
        reps = (
            self.db.execute(
                select(SalesRep)
                .where(
                    SalesRep.deleted_at.is_(None),
                    SalesRep.is_active.is_(True),
                )
                .order_by(SalesRep.name)
            )
            .scalars()
            .all()
        )
        groups = (
            self.db.execute(
                select(BuyingGroup)
                .where(BuyingGroup.deleted_at.is_(None))
                .order_by(BuyingGroup.name)
            )
            .scalars()
            .all()
        )
        pricebooks = (
            self.db.execute(
                select(Pricebook)
                .where(Pricebook.deleted_at.is_(None))
                .order_by(Pricebook.name)
            )
            .scalars()
            .all()
        )
        price_levels = (
            self.db.execute(
                select(Contact.default_pricing_level)
                .where(
                    Contact.deleted_at.is_(None),
                    Contact.is_customer.is_(True),
                    Contact.default_pricing_level.isnot(None),
                    Contact.default_pricing_level != "",
                )
                .distinct()
                .order_by(Contact.default_pricing_level)
            )
            .scalars()
            .all()
        )
        return {
            "sales_reps": [{"label": r.name, "value": str(r.id)} for r in reps],
            "buying_groups": [
                {
                    "label": g.name,
                    "value": str(g.id),
                    "color": g.map_color or _NONE_GROUP_COLOR,
                }
                for g in groups
            ],
            "price_levels": [
                {"label": _normalize_price_level(p) or p, "value": p}
                for p in price_levels
                if p
            ],
            "pricebooks": [{"label": p.name, "value": str(p.id)} for p in pricebooks],
            "volume_bands": [
                {"label": label, "value": band_id}
                for band_id, label, _, _ in VOLUME_BANDS
            ],
            "relationship_statuses": [
                {"label": label, "value": value}
                for value, label in RELATIONSHIP_STATUSES
            ],
        }

    def get_map(
        self,
        *,
        start_date: date,
        end_date: date,
        sales_rep_id: Optional[str] = None,
        buying_group_id: Optional[str] = None,
        price_level: Optional[str] = None,
        pricebook_id: Optional[str] = None,
        volume_band: Optional[str] = None,
        relationship_status: Optional[str] = None,
    ) -> CustomerMapSummary:
        start_dt = _as_datetime_start(start_date)
        end_dt = _as_datetime_end(end_date)

        revenue_rows = self.db.execute(
            select(
                SalesOrder.customer_id,
                func.coalesce(func.sum(SalesOrder.total_inc_gst), 0).label("revenue"),
            )
            .where(
                SalesOrder.deleted_at.is_(None),
                SalesOrder.status != SalesOrderStatus.CANCELLED.value,
                SalesOrder.order_date >= start_dt,
                SalesOrder.order_date <= end_dt,
            )
            .group_by(SalesOrder.customer_id)
        ).all()
        revenue_by_customer = {
            row.customer_id: _quantize(_dec(row.revenue)) for row in revenue_rows
        }

        stmt = (
            select(Customer)
            .where(Customer.deleted_at.is_(None))
            .options(
                joinedload(Customer.buying_group),
                joinedload(Customer.contact),
                joinedload(Customer.customer_sites),
                joinedload(Customer.rep_assignments).joinedload(
                    CustomerRepAssignment.sales_rep
                ),
            )
        )
        if relationship_status:
            stmt = stmt.where(Customer.relationship_status == relationship_status)
        if buying_group_id:
            stmt = stmt.where(Customer.buying_group_id == buying_group_id)

        customers = list(self.db.execute(stmt).unique().scalars().all())

        if sales_rep_id:
            customers = [
                c
                for c in customers
                if any(
                    str(a.sales_rep_id) == sales_rep_id
                    for a in (c.rep_assignments or [])
                    if a.deleted_at is None
                )
            ]

        pricebook_by_customer = self._latest_pricebook_by_customer(
            [c.id for c in customers], start_dt, end_dt
        )

        points: List[CustomerMapPoint] = []
        legend_colors: Dict[str, dict] = {}

        for customer in customers:
            period_revenue = revenue_by_customer.get(customer.id, Decimal("0"))
            band = _volume_band(period_revenue)
            if volume_band and band != volume_band:
                continue

            price_lvl = None
            if customer.contact and customer.contact.default_pricing_level:
                price_lvl = customer.contact.default_pricing_level
            pb_name = pricebook_by_customer.get(customer.id)
            if not price_lvl and pb_name:
                price_lvl = pb_name

            if price_level and (price_lvl or "").lower() != price_level.lower():
                continue
            if pricebook_id:
                customer_pb = pricebook_by_customer.get(f"{customer.id}_pb_id")
                if customer_pb != pricebook_id:
                    continue

            coords, location_source, suburb, state = self._resolve_coordinates(customer)
            if coords is None:
                continue

            bg = customer.buying_group
            bg_name = bg.name if bg else "None"
            bg_color = bg.map_color if bg and bg.map_color else _NONE_GROUP_COLOR
            bg_id = str(bg.id) if bg else None

            primary_rep = None
            for assignment in customer.rep_assignments or []:
                if assignment.deleted_at is None and assignment.role == "primary":
                    if assignment.sales_rep:
                        primary_rep = assignment.sales_rep.name
                    break

            point = CustomerMapPoint(
                customer_id=str(customer.id),
                name=customer.name,
                code=customer.code,
                lat=coords[0],
                lon=coords[1],
                buying_group_id=bg_id,
                buying_group_name=bg_name,
                buying_group_color=bg_color,
                relationship_status=getattr(customer, "relationship_status", None)
                or "active",
                price_level=_normalize_price_level(price_lvl),
                sales_rep_name=primary_rep,
                period_revenue=period_revenue,
                volume_band=band,
                location_source=location_source,
                location_label=LOCATION_SOURCE_LABELS.get(
                    location_source, location_source
                ),
                address_display=format_customer_address(customer),
                suburb=suburb,
                state=state,
            )
            points.append(point)
            legend_key = bg_id or "none"
            if legend_key not in legend_colors:
                legend_colors[legend_key] = {
                    "buying_group_id": bg_id,
                    "name": bg_name,
                    "color": bg_color,
                }

        point_dicts = [
            {
                "customer_id": p.customer_id,
                "name": p.name,
                "code": p.code,
                "lat": p.lat,
                "lon": p.lon,
                "buying_group_id": p.buying_group_id,
                "buying_group_name": p.buying_group_name,
                "buying_group_color": p.buying_group_color,
                "relationship_status": p.relationship_status,
                "price_level": p.price_level or "—",
                "sales_rep_name": p.sales_rep_name or "—",
                "period_revenue": float(p.period_revenue),
                "volume_band": p.volume_band,
                "location_source": p.location_source,
                "location_label": p.location_label,
                "address_display": p.address_display,
                "suburb": p.suburb,
                "state": p.state,
            }
            for p in points
        ]

        total = len(customers)
        mapped = len(points)
        return CustomerMapSummary(
            points=point_dicts,
            legend=sorted(legend_colors.values(), key=lambda x: x["name"]),
            total_customers=total,
            mapped_customers=mapped,
            unmapped_customers=max(0, total - mapped),
        )

    def _latest_pricebook_by_customer(
        self,
        customer_ids: List[str],
        start_dt: datetime,
        end_dt: datetime,
    ) -> Dict[str, str]:
        if not customer_ids:
            return {}
        rows = self.db.execute(
            select(
                SalesOrder.customer_id,
                SalesOrder.pricebook_id,
                Pricebook.name,
                SalesOrder.order_date,
            )
            .outerjoin(Pricebook, Pricebook.id == SalesOrder.pricebook_id)
            .where(
                SalesOrder.deleted_at.is_(None),
                SalesOrder.status != SalesOrderStatus.CANCELLED.value,
                SalesOrder.customer_id.in_(customer_ids),
                SalesOrder.order_date >= start_dt,
                SalesOrder.order_date <= end_dt,
            )
            .order_by(SalesOrder.customer_id, SalesOrder.order_date.desc())
        ).all()
        result: Dict[str, str] = {}
        for row in rows:
            cid = row.customer_id
            if cid not in result:
                result[cid] = row.name
                result[f"{cid}_pb_id"] = row.pricebook_id
        return result

    def _resolve_coordinates(
        self, customer: Customer
    ) -> Tuple[Optional[Tuple[float, float]], str, Optional[str], Optional[str]]:
        if customer.latitude is not None and customer.longitude is not None:
            return (
                (float(customer.latitude), float(customer.longitude)),
                "customer",
                customer.delivery_suburb,
                customer.delivery_state,
            )

        if customer.contact_id and customer.contact:
            contact = customer.contact
            if contact.deleted_at is None:
                if contact.latitude is not None and contact.longitude is not None:
                    return (
                        (float(contact.latitude), float(contact.longitude)),
                        "contact",
                        contact.delivery_suburb,
                        contact.delivery_state,
                    )

        for site in customer.customer_sites or []:
            if site.deleted_at is not None:
                continue
            if site.latitude is not None and site.longitude is not None:
                return (
                    (float(site.latitude), float(site.longitude)),
                    "site",
                    site.suburb,
                    site.state,
                )

        suburb = customer.delivery_suburb or customer.billing_suburb
        state = (customer.delivery_state or customer.billing_state or "").upper()
        postcode = customer.delivery_postcode or customer.billing_postcode
        if not state:
            state = _state_from_postcode(postcode) or ""

        if state and state in STATE_COORDS:
            lat, lon = STATE_COORDS[state]
            jlat, jlon = _jitter(str(customer.id))
            return (
                (lat + jlat, lon + jlon),
                "state_estimate",
                suburb,
                state,
            )

        for site in customer.customer_sites or []:
            if site.deleted_at is not None:
                continue
            st = (site.state or "").upper()
            if st in STATE_COORDS:
                lat, lon = STATE_COORDS[st]
                jlat, jlon = _jitter(str(customer.id))
                return (
                    (lat + jlat, lon + jlon),
                    "site_state_estimate",
                    site.suburb,
                    st,
                )

        return None, "unmapped", suburb, state or None
