"""Look up addresses and coordinates via OpenStreetMap Nominatim."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import List, Optional

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "VNDManuf-Sales/1.0 (customer location enrichment)"
MIN_REQUEST_INTERVAL_SEC = 1.1

_AU_STATE_ABBR = {
    "new south wales": "NSW",
    "victoria": "VIC",
    "queensland": "QLD",
    "south australia": "SA",
    "western australia": "WA",
    "tasmania": "TAS",
    "northern territory": "NT",
    "australian capital territory": "ACT",
}

_last_request_at: float = 0.0


@dataclass
class GeocodeResult:
    query: str
    lat: float
    lon: float
    display_name: str
    address_line1: Optional[str] = None
    suburb: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    confidence: float = 0.0


def build_search_query(
    name: str,
    *,
    suburb: Optional[str] = None,
    state: Optional[str] = None,
    country: str = "Australia",
) -> str:
    """Build a Nominatim search string from a customer/business name."""
    parts = [p.strip() for p in [name, suburb, state, country] if p and p.strip()]
    return ", ".join(parts)


def _throttle() -> None:
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < MIN_REQUEST_INTERVAL_SEC:
        time.sleep(MIN_REQUEST_INTERVAL_SEC - elapsed)
    _last_request_at = time.monotonic()


def _state_abbr(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    text = raw.strip()
    if len(text) <= 3 and text.isalpha():
        return text.upper()
    return _AU_STATE_ABBR.get(text.lower(), text[:8].upper())


def _parse_address(
    address: dict,
) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    house = address.get("house_number")
    road = address.get("road") or address.get("pedestrian") or address.get("footway")
    line1 = None
    if house and road:
        line1 = f"{house} {road}"
    elif road:
        line1 = road

    suburb = (
        address.get("suburb")
        or address.get("town")
        or address.get("city")
        or address.get("village")
        or address.get("hamlet")
    )
    state = _state_abbr(address.get("state"))
    postcode = address.get("postcode")
    country = address.get("country")
    return line1, suburb, state, postcode, country


def _score_result(name: str, item: dict) -> float:
    """Rough relevance score — prefer shop/retail matches in Australia."""
    score = 0.5
    display = (item.get("display_name") or "").lower()
    name_l = name.lower()
    if name_l in display:
        score += 0.25
    type_ = item.get("type") or ""
    category = item.get("category") or ""
    if type_ in ("shop", "retail", "commercial", "alcohol") or category == "shop":
        score += 0.15
    if item.get("class") == "amenity":
        score += 0.05
    if "australia" in display:
        score += 0.1
    try:
        importance = float(item.get("importance") or 0)
        score += min(importance, 0.2)
    except (TypeError, ValueError):
        pass
    return score


def geocode_query(
    query: str, *, country_codes: str = "au", limit: int = 3
) -> Optional[GeocodeResult]:
    """Search Nominatim for a single query string. Returns best AU match or None."""
    cleaned = (query or "").strip()
    if not cleaned:
        return None

    _throttle()
    params = {
        "q": cleaned,
        "format": "json",
        "addressdetails": 1,
        "limit": limit,
        "countrycodes": country_codes,
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        with httpx.Client(timeout=20.0, headers=headers) as client:
            response = client.get(NOMINATIM_URL, params=params)
            response.raise_for_status()
            items = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    if not isinstance(items, list) or not items:
        return None

    best = max(items, key=lambda item: _score_result(cleaned, item))
    try:
        lat = float(best["lat"])
        lon = float(best["lon"])
    except (KeyError, TypeError, ValueError):
        return None

    addr = best.get("address") if isinstance(best.get("address"), dict) else {}
    line1, suburb, state, postcode, country = _parse_address(addr)

    return GeocodeResult(
        query=cleaned,
        lat=lat,
        lon=lon,
        display_name=best.get("display_name") or cleaned,
        address_line1=line1,
        suburb=suburb,
        state=state,
        postcode=postcode,
        country=country or "Australia",
        confidence=_score_result(cleaned, best),
    )


def geocode_address(
    *,
    line1: Optional[str] = None,
    suburb: Optional[str] = None,
    state: Optional[str] = None,
    postcode: Optional[str] = None,
    country: str = "Australia",
) -> Optional[GeocodeResult]:
    """Geocode a structured postal address."""
    parts = [
        p.strip() for p in [line1, suburb, state, postcode, country] if p and p.strip()
    ]
    if len(parts) < 2:
        return None
    return geocode_query(", ".join(parts))


def geocode_customer_address(customer) -> Optional[GeocodeResult]:
    """Geocode from whatever address fields exist on a customer."""
    line1 = (customer.delivery_address_line1 or "").strip() or (
        customer.billing_address_line1 or ""
    ).strip()
    suburb = customer.delivery_suburb or customer.billing_suburb
    state = customer.delivery_state or customer.billing_state
    postcode = customer.delivery_postcode or customer.billing_postcode
    country = customer.delivery_country or customer.billing_country or "Australia"
    if line1 or suburb:
        result = geocode_address(
            line1=line1 or None,
            suburb=suburb,
            state=state,
            postcode=postcode,
            country=country,
        )
        if result:
            return result
    legacy = (customer.address or "").strip()
    if legacy:
        return geocode_query(f"{legacy}, {country}")
    return None


def geocode_business_name(
    name: str,
    *,
    suburb: Optional[str] = None,
    state: Optional[str] = None,
    country: str = "Australia",
) -> Optional[GeocodeResult]:
    """Try progressively broader queries until a match is found."""
    name = (name or "").strip()
    if not name:
        return None

    queries: List[str] = []
    primary = build_search_query(name, suburb=suburb, state=state, country=country)
    queries.append(primary)
    if suburb or state:
        queries.append(build_search_query(name, country=country))
    # Strip common suffixes for bottle shops / venues
    simplified = re.sub(
        r"\s+(pty\s+ltd|at\s+.+|#\d+)$",
        "",
        name,
        flags=re.IGNORECASE,
    ).strip()
    if simplified and simplified != name:
        queries.append(build_search_query(simplified, country=country))

    seen = set()
    best: Optional[GeocodeResult] = None
    for q in queries:
        if q in seen:
            continue
        seen.add(q)
        result = geocode_query(q)
        if result and (best is None or result.confidence > best.confidence):
            best = result
            if result.confidence >= 0.85:
                break
    return best
