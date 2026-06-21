"""Seed customer/site import mappings and delivery sites from historic DD CSV.

Usage:
    python scripts/seed_dd_import_mappings.py "c:/Users/pduxs/Downloads/dd_output.csv"
    python scripts/seed_dd_import_mappings.py path/to.csv --dry-run
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select

from app.adapters.db import get_session
from app.adapters.db.models import Customer, CustomerImportAlias, CustomerSite
from apps.vndmanuf_sales.services.customer_mapping import (
    CustomerMappingService,
    names_refer_to_same_entity,
    normalize_import_key,
)

# CSV site label -> canonical CustomerSite.site_name for known customers
SITE_CANONICAL_OVERRIDES: dict[tuple[str, str], str] = {
    ("Cellarbrations Bannockburn", "Bannockburn Cellarbrations"): "Store",
}

# Extra customer aliases if missing (csv label -> canonical customer name)
CUSTOMER_ALIASES: dict[str, str] = {
    "Bannockburn Cellarbrations": "Cellarbrations Bannockburn",
    "CBN AT CHAS COLE": "Cellarbrations at Chas Cole",
    "CBN AT FOXXYS DAYLESFORD X": "Cellarbrations at Foxxy's Daylesford",
    "TBO CENTRAL LIQUOR BARN X": "Cellarbrations Swan Hill Central Liquor Barn",
    "GEELONG WEST LIQUOR LEGENDS": "Geelong West Liquor Legends",
    "CBN AT NARDIS HIGHTON X": "Cellarbrations Nardi Highton",
    "MURPHY'S GEELONG": "Murphy's",
    "GEELONG PERFORMING ARTS CENTRE": "Geelong Performing Arts Centre",
    "Piano Bar": "Piano Bar Geelong",
    "CELLARBRATIONS AT JACKS X": "Cellarbrations at Jacks",
    "TBO HIGHTON (CORP)": "The Bottle-O Highton",
    "GROVEDALE HOTEL X": "Grovedale Hotel",
    "Corks Crew Cellars": "Corks Crew Cellars Torquay",
}


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _find_customer_by_name(session, name: str) -> Customer | None:
    return session.execute(
        select(Customer).where(
            Customer.deleted_at.is_(None),
            Customer.name == name,
        )
    ).scalar_one_or_none()


def _find_site(session, customer_id: str, site_name: str) -> CustomerSite | None:
    key = normalize_import_key(site_name)
    sites = (
        session.execute(
            select(CustomerSite).where(
                CustomerSite.customer_id == customer_id,
                CustomerSite.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )
    for site in sites:
        if normalize_import_key(site.site_name) == key:
            return site
        if names_refer_to_same_entity(site.site_name, site_name):
            return site
    return None


def _get_or_create_site(
    session,
    customer: Customer,
    site_name: str,
    *,
    suburb: str | None,
    state: str | None,
    postcode: str | None,
    dry_run: bool,
) -> CustomerSite | None:
    existing = _find_site(session, customer.id, site_name)
    if existing:
        return existing
    if dry_run:
        print(f"    [dry-run] would create site {site_name!r} for {customer.name}")
        return None
    site = CustomerSite(
        customer_id=customer.id,
        site_name=site_name.strip(),
        state=(state or "UNKNOWN").strip().upper()[:8],
        suburb=(suburb or "").strip() or None,
        postcode=(postcode or "").strip() or None,
    )
    session.add(site)
    session.flush()
    return site


def _resolve_customer(
    session,
    mapping: CustomerMappingService,
    customer_csv: str,
) -> Customer | None:
    customer = mapping.resolve_customer(customer_csv)
    if customer:
        return customer
    canonical = CUSTOMER_ALIASES.get(customer_csv)
    if canonical:
        return _find_customer_by_name(session, canonical)
    return _find_customer_by_name(session, customer_csv)


def seed_mappings(csv_path: Path, *, dry_run: bool = False) -> None:
    rows = _load_csv_rows(csv_path)
    if not rows:
        print("No rows in CSV.")
        return

    site_groups: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in rows:
        customer_csv = (row.get("customer") or "").strip()
        site_name = (row.get("site_name") or "").strip()
        suburb = (row.get("site_suburb") or "").strip()
        state = (row.get("site_state") or "").strip()
        postcode = (row.get("site_postcode") or "").strip()
        if not customer_csv:
            continue
        key = (customer_csv, site_name, suburb, state, postcode)
        site_groups[key] = row

    session = get_session()
    mapping = CustomerMappingService(session)
    created_customer_aliases = 0
    created_site_aliases = 0
    created_sites = 0
    skipped_site = 0

    try:
        print("=== Customer aliases ===")
        for alias_label, canonical_name in sorted(CUSTOMER_ALIASES.items()):
            customer = _find_customer_by_name(session, canonical_name)
            if not customer:
                print(
                    f"  SKIP customer alias {alias_label!r}: customer {canonical_name!r} not found"
                )
                continue
            key = normalize_import_key(alias_label)
            existing = session.execute(
                select(CustomerImportAlias).where(
                    CustomerImportAlias.alias_key == key,
                    CustomerImportAlias.deleted_at.is_(None),
                )
            ).scalar_one_or_none()
            if existing:
                cust = session.get(Customer, existing.customer_id)
                print(
                    f"  OK  {alias_label!r} -> {cust.name if cust else canonical_name!r} (already mapped)"
                )
                continue
            if dry_run:
                print(
                    f"  [dry-run] would add customer alias {alias_label!r} -> {customer.name!r}"
                )
            else:
                mapping.add_alias(
                    alias_label, customer.id, notes="seed from dd_output.csv"
                )
                print(f"  ADD {alias_label!r} -> {customer.name!r}")
            created_customer_aliases += 1

        print("\n=== Sites and site aliases ===")
        for (customer_csv, site_csv, suburb, state, postcode), _row in sorted(
            site_groups.items()
        ):
            customer = _resolve_customer(session, mapping, customer_csv)
            if not customer:
                print(f"  SKIP site for unknown customer {customer_csv!r}")
                continue

            if not site_csv:
                continue

            override_key = (customer.name, site_csv)
            canonical_name = SITE_CANONICAL_OVERRIDES.get(override_key, site_csv)

            if names_refer_to_same_entity(
                site_csv, customer.name
            ) and not SITE_CANONICAL_OVERRIDES.get(override_key):
                skipped_site += 1
                continue

            site_before = _find_site(session, customer.id, canonical_name)
            site = _get_or_create_site(
                session,
                customer,
                canonical_name,
                suburb=suburb,
                state=state,
                postcode=postcode,
                dry_run=dry_run,
            )
            if site is None and dry_run:
                resolved_site_name = canonical_name
            elif site is not None:
                resolved_site_name = site.site_name
                if site_before is None:
                    created_sites += 1
            else:
                resolved_site_name = canonical_name
            existing_alias = mapping.resolve_site_alias(customer.id, site_csv)
            if existing_alias:
                print(f"  OK  [{customer.name}] {site_csv!r} -> {existing_alias!r}")
                continue

            if dry_run:
                print(
                    f"  [dry-run] site alias [{customer.name}] {site_csv!r} -> {resolved_site_name!r}"
                )
                created_site_aliases += 1
                if site is None:
                    created_sites += 1
                continue

            if site and normalize_import_key(site.site_name) == normalize_import_key(
                canonical_name
            ):
                created_sites += 1
            mapping.add_site_alias(
                site_csv,
                customer.id,
                resolved_site_name,
                notes="seed from dd_output.csv",
            )
            print(
                f"  ADD [{customer.name}] site {site_csv!r} -> {resolved_site_name!r}"
            )
            created_site_aliases += 1

        if dry_run:
            session.rollback()
            print("\n[dry-run] No changes committed.")
        else:
            session.commit()
            print(
                f"\nDone. Customer aliases added: {created_customer_aliases}, "
                f"site aliases added: {created_site_aliases}, sites touched/created: {created_sites}, "
                f"site rows skipped (same as customer): {skipped_site}"
            )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Path to delivery docket CSV")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()
    if not args.csv_path.exists():
        raise SystemExit(f"File not found: {args.csv_path}")
    seed_mappings(args.csv_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
