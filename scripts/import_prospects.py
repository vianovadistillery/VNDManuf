#!/usr/bin/env python3
"""Import prospect contacts + customers from JSON (CRM relationship_status=prospective)."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import or_, select

from app.adapters.db.models import BuyingGroup, Contact, Customer
from app.adapters.db.session import get_session


def _load_records(path: Path) -> List[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit(
            "JSON root must be an array of {contact, customer, research?} objects"
        )
    return payload


def _resolve_buying_group(session, name: Optional[str]) -> Optional[str]:
    if not name or not str(name).strip():
        return None
    clean = str(name).strip()
    bg = session.execute(
        select(BuyingGroup).where(
            BuyingGroup.deleted_at.is_(None),
            BuyingGroup.name == clean,
        )
    ).scalar_one_or_none()
    if bg:
        return str(bg.id)
    bg = session.execute(
        select(BuyingGroup).where(
            BuyingGroup.deleted_at.is_(None),
            BuyingGroup.name.ilike(clean),
        )
    ).scalar_one_or_none()
    return str(bg.id) if bg else None


def _research_note(research: Optional[dict]) -> Optional[str]:
    if not research:
        return None
    parts = [
        research.get("segment_label"),
        research.get("source"),
        f"confidence={research.get('confidence')}"
        if research.get("confidence")
        else None,
    ]
    text = " | ".join(p for p in parts if p)
    return f"[Prospect research: {text}]" if text else None


def _append_note(base: Optional[str], extra: Optional[str]) -> Optional[str]:
    if not extra:
        return base
    if not base:
        return extra
    if extra in base:
        return base
    return f"{base}\n\n{extra}"


def _geocode_note(precision: Optional[str]) -> Optional[str]:
    if not precision:
        return None
    return f"[Geocode precision: {precision}]"


def _coords(data: dict) -> dict:
    out: dict = {}
    if data.get("latitude") is not None:
        out["latitude"] = data["latitude"]
    if data.get("longitude") is not None:
        out["longitude"] = data["longitude"]
    return out


def _contact_fields(data: dict) -> dict:
    keys = (
        "name",
        "contact_person",
        "email",
        "phone",
        "address",
        "billing_address_line1",
        "billing_address_line2",
        "billing_suburb",
        "billing_state",
        "billing_postcode",
        "billing_country",
        "delivery_address_line1",
        "delivery_address_line2",
        "delivery_suburb",
        "delivery_state",
        "delivery_postcode",
        "delivery_country",
        "latitude",
        "longitude",
        "abn",
        "alm_account_number",
        "payment_method",
        "paramount_number",
        "default_pricing_level",
        "is_customer",
        "is_supplier",
        "is_other",
        "tax_rate",
        "is_active",
    )
    return {k: data.get(k) for k in keys if k in data}


def _customer_address_fields(contact: dict) -> dict:
    return {
        "billing_address_line1": contact.get("billing_address_line1")
        or contact.get("delivery_address_line1"),
        "billing_address_line2": contact.get("billing_address_line2")
        or contact.get("delivery_address_line2"),
        "billing_suburb": contact.get("billing_suburb")
        or contact.get("delivery_suburb"),
        "billing_state": contact.get("billing_state") or contact.get("delivery_state"),
        "billing_postcode": contact.get("billing_postcode")
        or contact.get("delivery_postcode"),
        "billing_country": contact.get("billing_country")
        or contact.get("delivery_country")
        or "Australia",
        "delivery_address_line1": contact.get("delivery_address_line1"),
        "delivery_address_line2": contact.get("delivery_address_line2"),
        "delivery_suburb": contact.get("delivery_suburb"),
        "delivery_state": contact.get("delivery_state"),
        "delivery_postcode": contact.get("delivery_postcode"),
        "delivery_country": contact.get("delivery_country") or "Australia",
    }


def import_prospects(
    records: List[dict],
    *,
    dry_run: bool = False,
    skip_existing: bool = False,
) -> Dict[str, int]:
    session = get_session()
    stats = {
        "created_contacts": 0,
        "updated_contacts": 0,
        "created_customers": 0,
        "updated_customers": 0,
        "skipped": 0,
        "errors": 0,
        "missing_buying_group": 0,
        "geocoded": 0,
    }
    missing_groups: set[str] = set()

    try:
        for row in records:
            contact_data = row.get("contact") or {}
            customer_data = row.get("customer") or {}
            research = row.get("research")

            code = (contact_data.get("code") or customer_data.get("code") or "").strip()
            if not code:
                print("SKIP: record missing code")
                stats["errors"] += 1
                continue

            existing_contact = session.execute(
                select(Contact).where(
                    Contact.deleted_at.is_(None),
                    Contact.code == code,
                )
            ).scalar_one_or_none()

            if skip_existing and existing_contact:
                stats["skipped"] += 1
                continue

            research_line = _research_note(research)
            geocode_line = _geocode_note(contact_data.get("geocode_precision"))
            contact_notes = _append_note(
                contact_data.get("notes"),
                _append_note(research_line, geocode_line),
            )

            contact_fields = _contact_fields(contact_data)
            contact_fields["notes"] = contact_notes
            contact_fields.setdefault("is_customer", True)
            contact_fields.setdefault("is_supplier", False)
            contact_fields.setdefault("is_other", False)
            contact_fields.setdefault("is_active", True)

            if existing_contact:
                for key, value in contact_fields.items():
                    if value is not None:
                        setattr(existing_contact, key, value)
                contact = existing_contact
                stats["updated_contacts"] += 1
                action = "update contact"
            else:
                contact = Contact(
                    id=str(uuid.uuid4()),
                    code=code,
                    **{k: v for k, v in contact_fields.items() if v is not None},
                )
                session.add(contact)
                stats["created_contacts"] += 1
                action = "create contact"

            session.flush()

            existing_customer = session.execute(
                select(Customer).where(
                    Customer.deleted_at.is_(None),
                    or_(Customer.code == code, Customer.contact_id == str(contact.id)),
                )
            ).scalar_one_or_none()

            buying_group_name = customer_data.get("buying_group_name")
            buying_group_id = _resolve_buying_group(session, buying_group_name)
            if buying_group_name and not buying_group_id:
                missing_groups.add(str(buying_group_name))
                stats["missing_buying_group"] += 1

            customer_notes = _append_note(customer_data.get("notes"), research_line)
            addr = _customer_address_fields(contact_data)

            cust_payload = {
                "name": customer_data.get("name") or contact_data.get("name"),
                "customer_type": customer_data.get("customer_type") or "other",
                "contact_person": contact_data.get("contact_person"),
                "contact_name": contact_data.get("contact_person")
                or customer_data.get("name")
                or contact_data.get("name"),
                "email": contact_data.get("email"),
                "phone": contact_data.get("phone"),
                "address": contact_data.get("address"),
                "abn": contact_data.get("abn"),
                "tax_rate": contact_data.get("tax_rate") or 10.0,
                "contact_id": str(contact.id),
                "buying_group_id": buying_group_id,
                "relationship_status": customer_data.get("relationship_status")
                or "prospective",
                "visit_frequency_target_days": customer_data.get(
                    "visit_frequency_target_days"
                ),
                "preferred_contact_method": customer_data.get(
                    "preferred_contact_method"
                ),
                "notes": customer_notes,
                "is_active": contact_fields.get("is_active", True),
                **addr,
                **_coords(contact_data),
            }

            if contact_data.get("latitude") is not None:
                stats["geocoded"] += 1

            if existing_customer:
                for key, value in cust_payload.items():
                    if value is not None:
                        setattr(existing_customer, key, value)
                stats["updated_customers"] += 1
                cust_action = "update customer"
            else:
                session.add(
                    Customer(
                        id=str(uuid.uuid4()),
                        code=code,
                        **{k: v for k, v in cust_payload.items() if v is not None},
                    )
                )
                stats["created_customers"] += 1
                cust_action = "create customer"

            print(
                f"{'[dry-run] ' if dry_run else ''}{code}: {action}, {cust_action}"
                + (
                    f" (lat={contact_data.get('latitude')}, lon={contact_data.get('longitude')})"
                    if contact_data.get("latitude") is not None
                    else ""
                )
            )

        if dry_run:
            session.rollback()
        else:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    if missing_groups:
        print("\nUnresolved buying groups (import continued without group):")
        for name in sorted(missing_groups):
            print(f"  - {name}")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Import CRM prospects from JSON")
    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to prospects JSON array",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print actions without committing",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip records whose contact code already exists",
    )
    args = parser.parse_args()

    if not args.json_file.is_file():
        raise SystemExit(f"File not found: {args.json_file}")

    records = _load_records(args.json_file)
    print(f"Loaded {len(records)} prospect records from {args.json_file}")
    stats = import_prospects(
        records,
        dry_run=args.dry_run,
        skip_existing=args.skip_existing,
    )
    print("\nSummary:", json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
