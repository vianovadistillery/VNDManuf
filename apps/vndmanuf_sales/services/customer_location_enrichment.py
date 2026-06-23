"""Enrich customers with addresses and coordinates from web geocoding."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.adapters.db.models import Customer, CustomerSite
from apps.vndmanuf_sales.services.address_geocoding import (
    GeocodeResult,
    geocode_address,
    geocode_business_name,
    geocode_customer_address,
)
from apps.vndmanuf_sales.services.llm_address_lookup import suggest_customer_address


@dataclass
class EnrichmentRow:
    customer_id: str
    customer_name: str
    status: str  # updated, skipped, not_found, error
    query: Optional[str] = None
    message: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    display_name: Optional[str] = None


@dataclass
class EnrichmentSummary:
    processed: int = 0
    updated: int = 0
    skipped: int = 0
    not_found: int = 0
    failed: int = 0
    results: List[EnrichmentRow] = field(default_factory=list)


def customer_has_coordinates(customer: Customer) -> bool:
    if customer.latitude is not None and customer.longitude is not None:
        return True
    for site in customer.customer_sites or []:
        if site.deleted_at is not None:
            continue
        if site.latitude is not None and site.longitude is not None:
            return True
    return False


def customer_has_delivery_address(customer: Customer) -> bool:
    return bool(
        (customer.delivery_address_line1 or "").strip()
        or (customer.delivery_suburb or "").strip()
        or (customer.billing_address_line1 or "").strip()
        or (customer.billing_suburb or "").strip()
        or (customer.address or "").strip()
    )


def customer_needs_enrichment(customer: Customer) -> bool:
    """True when coordinates or a structured delivery address are missing."""
    if customer_has_coordinates(customer):
        if customer_has_delivery_address(customer):
            return False
    return True


def _apply_geocode(customer: Customer, result: GeocodeResult) -> None:
    customer.latitude = Decimal(str(round(result.lat, 6)))
    customer.longitude = Decimal(str(round(result.lon, 6)))

    if not (customer.delivery_address_line1 or "").strip() and result.address_line1:
        customer.delivery_address_line1 = result.address_line1[:200]
    if not (customer.delivery_suburb or "").strip() and result.suburb:
        customer.delivery_suburb = result.suburb[:100]
    if not (customer.delivery_state or "").strip() and result.state:
        customer.delivery_state = result.state[:50]
    if not (customer.delivery_postcode or "").strip() and result.postcode:
        customer.delivery_postcode = str(result.postcode)[:20]
    if not (customer.delivery_country or "").strip():
        customer.delivery_country = (result.country or "Australia")[:100]

    if not (customer.address or "").strip():
        customer.address = result.display_name[:500] if result.display_name else None


def _touch_primary_site(customer: Customer, result: GeocodeResult) -> None:
    site: Optional[CustomerSite] = None
    for s in customer.customer_sites or []:
        if s.deleted_at is None:
            site = s
            break
    if site is None:
        return
    if site.latitude is None:
        site.latitude = Decimal(str(round(result.lat, 6)))
    if site.longitude is None:
        site.longitude = Decimal(str(round(result.lon, 6)))
    if not site.suburb and result.suburb:
        site.suburb = result.suburb[:120]
    if site.state in (None, "", "UNKNOWN") and result.state:
        site.state = result.state[:8]


def _apply_llm_address_hints(customer: Customer, suggestion) -> None:
    if suggestion.line1 and not (customer.delivery_address_line1 or "").strip():
        customer.delivery_address_line1 = suggestion.line1[:200]
    if suggestion.suburb and not (customer.delivery_suburb or "").strip():
        customer.delivery_suburb = suggestion.suburb[:100]
    if suggestion.state and not (customer.delivery_state or "").strip():
        customer.delivery_state = suggestion.state[:50]
    if suggestion.postcode and not (customer.delivery_postcode or "").strip():
        customer.delivery_postcode = str(suggestion.postcode)[:20]
    if not (customer.delivery_country or "").strip():
        customer.delivery_country = (suggestion.country or "Australia")[:100]


class CustomerLocationEnrichmentService:
    def __init__(self, db: Session):
        self.db = db

    def list_candidates(
        self,
        *,
        customer_ids: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.deleted_at.is_(None))
            .options(
                joinedload(Customer.customer_sites),
                joinedload(Customer.buying_group),
            )
            .order_by(Customer.name)
        )
        if customer_ids:
            stmt = stmt.where(Customer.id.in_(customer_ids))
        customers = list(self.db.execute(stmt).unique().scalars().all())
        return [c for c in customers if customer_needs_enrichment(c)][:limit]

    def enrich(
        self,
        *,
        customer_ids: Optional[List[str]] = None,
        limit: int = 20,
        dry_run: bool = False,
        min_confidence: float = 0.55,
        use_llm: bool = False,
    ) -> EnrichmentSummary:
        summary = EnrichmentSummary()
        candidates = self.list_candidates(customer_ids=customer_ids, limit=limit)

        for customer in candidates:
            summary.processed += 1
            suburb = customer.delivery_suburb or customer.billing_suburb
            state = customer.delivery_state or customer.billing_state
            country = (
                customer.delivery_country or customer.billing_country or "Australia"
            )
            search_name = customer.name
            bg = customer.buying_group
            bg_name = None
            if bg and bg.deleted_at is None:
                bg_name = bg.name
                if bg.code != "NONE" and bg.name.lower() != "none":
                    if bg.name.lower() not in search_name.lower():
                        search_name = f"{bg.name} {search_name}"

            result: Optional[GeocodeResult] = None
            try:
                result = geocode_business_name(
                    search_name,
                    suburb=suburb,
                    state=state,
                    country=country,
                )
                if not result and customer_has_delivery_address(customer):
                    result = geocode_customer_address(customer)
                if not result and use_llm:
                    suggestion = suggest_customer_address(
                        customer.name,
                        buying_group=bg_name,
                        suburb=suburb,
                        state=state,
                        country=country,
                    )
                    if suggestion and suggestion.confidence >= 0.45:
                        result = geocode_address(
                            line1=suggestion.line1,
                            suburb=suggestion.suburb,
                            state=suggestion.state,
                            postcode=suggestion.postcode,
                            country=suggestion.country,
                        )
                        if not result and suggestion.line1:
                            result = geocode_business_name(
                                f"{suggestion.line1}, {suggestion.suburb or ''}, "
                                f"{suggestion.state or ''}, Australia"
                            )
                        if result:
                            result = GeocodeResult(
                                query=result.query,
                                lat=result.lat,
                                lon=result.lon,
                                display_name=result.display_name
                                or suggestion.line1
                                or customer.name,
                                address_line1=result.address_line1 or suggestion.line1,
                                suburb=result.suburb or suggestion.suburb,
                                state=result.state or suggestion.state,
                                postcode=result.postcode or suggestion.postcode,
                                country=result.country or suggestion.country,
                                confidence=max(
                                    result.confidence, suggestion.confidence * 0.85
                                ),
                            )
                            if not dry_run:
                                _apply_llm_address_hints(customer, suggestion)
            except Exception as exc:
                summary.failed += 1
                summary.results.append(
                    EnrichmentRow(
                        customer_id=str(customer.id),
                        customer_name=customer.name,
                        status="error",
                        message=str(exc),
                    )
                )
                continue

            if not result:
                summary.not_found += 1
                summary.results.append(
                    EnrichmentRow(
                        customer_id=str(customer.id),
                        customer_name=customer.name,
                        status="not_found",
                        query=customer.name,
                        message="No match found online",
                    )
                )
                continue

            if result.confidence < min_confidence:
                summary.skipped += 1
                summary.results.append(
                    EnrichmentRow(
                        customer_id=str(customer.id),
                        customer_name=customer.name,
                        status="skipped",
                        query=result.query,
                        message=f"Low confidence ({result.confidence:.2f})",
                        lat=result.lat,
                        lon=result.lon,
                        display_name=result.display_name,
                    )
                )
                continue

            if dry_run:
                summary.updated += 1
                summary.results.append(
                    EnrichmentRow(
                        customer_id=str(customer.id),
                        customer_name=customer.name,
                        status="updated",
                        query=result.query,
                        message="Would apply (dry run)",
                        lat=result.lat,
                        lon=result.lon,
                        display_name=result.display_name,
                    )
                )
                continue

            _apply_geocode(customer, result)
            _touch_primary_site(customer, result)
            summary.updated += 1
            summary.results.append(
                EnrichmentRow(
                    customer_id=str(customer.id),
                    customer_name=customer.name,
                    status="updated",
                    query=result.query,
                    message=result.display_name,
                    lat=result.lat,
                    lon=result.lon,
                    display_name=result.display_name,
                )
            )

        if not dry_run and summary.updated:
            self.db.commit()

        return summary
