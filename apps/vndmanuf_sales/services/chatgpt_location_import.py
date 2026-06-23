"""Import ChatGPT-filled address/coordinate CSV into customers and contacts."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db.models import Contact, Customer

SKIP_CODES = frozenset({"CASHR", "TEST-CUST-001", "VND"})


@dataclass
class ImportRowResult:
    code: str
    status: str
    message: str = ""


@dataclass
class ImportSummary:
    updated: int = 0
    skipped: int = 0
    not_found: int = 0
    results: List[ImportRowResult] = field(default_factory=list)


def _parse_float(value: Optional[str]) -> Optional[float]:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _append_note(existing: Optional[str], note: Optional[str]) -> Optional[str]:
    note = (note or "").strip()
    if not note:
        return existing
    if note.lower().startswith("skipped"):
        return existing
    prefix = (existing or "").strip()
    if prefix and note in prefix:
        return existing
    return f"{prefix}\n{note}".strip() if prefix else note


def _apply_address_fields(
    entity,
    *,
    line1: Optional[str],
    suburb: Optional[str],
    state: Optional[str],
    postcode: Optional[str],
    country: str = "Australia",
) -> None:
    if line1 and not (getattr(entity, "delivery_address_line1", None) or "").strip():
        entity.delivery_address_line1 = line1[:200]
        if (
            hasattr(entity, "billing_address_line1")
            and not (entity.billing_address_line1 or "").strip()
        ):
            entity.billing_address_line1 = line1[:200]
    if suburb and not (getattr(entity, "delivery_suburb", None) or "").strip():
        entity.delivery_suburb = suburb[:100]
        if (
            hasattr(entity, "billing_suburb")
            and not (entity.billing_suburb or "").strip()
        ):
            entity.billing_suburb = suburb[:100]
    if state and not (getattr(entity, "delivery_state", None) or "").strip():
        entity.delivery_state = state[:50]
        if (
            hasattr(entity, "billing_state")
            and not (entity.billing_state or "").strip()
        ):
            entity.billing_state = state[:50]
    if postcode and not (getattr(entity, "delivery_postcode", None) or "").strip():
        entity.delivery_postcode = str(postcode)[:20]
        if (
            hasattr(entity, "billing_postcode")
            and not (entity.billing_postcode or "").strip()
        ):
            entity.billing_postcode = str(postcode)[:20]
    if not (getattr(entity, "delivery_country", None) or "").strip():
        entity.delivery_country = country[:100]
    if (
        hasattr(entity, "billing_country")
        and not (entity.billing_country or "").strip()
    ):
        entity.billing_country = country[:100]


def _apply_coordinates(entity, lat: float, lon: float) -> None:
    entity.latitude = Decimal(str(round(lat, 6)))
    entity.longitude = Decimal(str(round(lon, 6)))


def _sync_contact_for_customer(db: Session, customer: Customer) -> Optional[Contact]:
    if customer.contact_id:
        contact = db.get(Contact, customer.contact_id)
        if contact and contact.deleted_at is None:
            return contact
    contact = db.execute(
        select(Contact).where(
            Contact.code == customer.code,
            Contact.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    return contact


def import_chatgpt_locations_csv(
    db: Session,
    csv_path: Path,
    *,
    dry_run: bool = False,
) -> ImportSummary:
    summary = ImportSummary()
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            code = (row.get("Code") or "").strip()
            if not code:
                continue
            if code in SKIP_CODES:
                summary.skipped += 1
                summary.results.append(
                    ImportRowResult(
                        code, "skipped", row.get("chatgpt_notes") or "Skipped"
                    )
                )
                continue

            customer = db.execute(
                select(Customer).where(
                    Customer.code == code,
                    Customer.deleted_at.is_(None),
                )
            ).scalar_one_or_none()
            if not customer:
                summary.not_found += 1
                summary.results.append(
                    ImportRowResult(code, "not_found", "No customer")
                )
                continue

            lat = _parse_float(row.get("chatgpt_latitude"))
            lon = _parse_float(row.get("chatgpt_longitude"))
            line1 = (row.get("chatgpt_line1") or "").strip() or None
            suburb = (row.get("chatgpt_suburb") or "").strip() or None
            state = (row.get("chatgpt_state") or "").strip() or None
            postcode = (row.get("chatgpt_postcode") or "").strip() or None
            notes = (row.get("chatgpt_notes") or "").strip() or None

            if not any([lat, lon, line1, suburb, state, postcode]):
                summary.skipped += 1
                summary.results.append(ImportRowResult(code, "skipped", "No data"))
                continue

            if line1 or suburb or state or postcode:
                _apply_address_fields(
                    customer,
                    line1=line1,
                    suburb=suburb,
                    state=state,
                    postcode=postcode,
                )
            if lat is not None and lon is not None:
                _apply_coordinates(customer, lat, lon)
            if notes:
                customer.notes = _append_note(customer.notes, notes)

            contact = _sync_contact_for_customer(db, customer)
            if contact:
                if line1 or suburb or state or postcode:
                    _apply_address_fields(
                        contact,
                        line1=line1,
                        suburb=suburb,
                        state=state,
                        postcode=postcode,
                    )
                if lat is not None and lon is not None:
                    _apply_coordinates(contact, lat, lon)
                if notes:
                    contact.notes = _append_note(contact.notes, notes)

            summary.updated += 1
            summary.results.append(
                ImportRowResult(
                    code,
                    "updated",
                    f"lat={lat}, lon={lon}" if lat is not None else "address only",
                )
            )

    if not dry_run and summary.updated:
        db.commit()
    return summary
