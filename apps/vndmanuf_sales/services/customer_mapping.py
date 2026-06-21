"""Resolve CSV customer and site names to canonical records via aliases."""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.db.models import (
    Customer,
    CustomerImportAlias,
    CustomerSite,
    CustomerSiteImportAlias,
)


def normalize_import_key(name: str) -> str:
    """Normalize a name for alias lookup (case/whitespace/punctuation insensitive)."""
    text = (name or "").strip().lower()
    text = text.replace("'", "'").replace("'", "'").replace("–", "-").replace("—", "-")
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"\s+x$", "", text.strip())
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_customer_key(name: str) -> str:
    """Backwards-compatible alias for customer normalization."""
    return normalize_import_key(name)


def name_token_set(name: str) -> frozenset[str]:
    tokens = [t for t in normalize_import_key(name).split() if t]
    if tokens and tokens[-1] == "x":
        tokens = tokens[:-1]
    return frozenset(tokens)


def names_refer_to_same_entity(a: str, b: str) -> bool:
    """True when two labels likely refer to the same store (reordered/extra words)."""
    left = name_token_set(a)
    right = name_token_set(b)
    if not left or not right:
        return False
    if left == right:
        return True
    if (
        len(left) >= 2
        and len(right) >= 2
        and (left.issubset(right) or right.issubset(left))
    ):
        return True
    return False


class CustomerMappingService:
    """Map CSV customer/site strings to existing records."""

    def __init__(self, db: Session):
        self.db = db

    def resolve_customer(self, name: str) -> Optional[Customer]:
        """Find customer by exact name or configured import alias."""
        cleaned = (name or "").strip()
        if not cleaned:
            return None

        customer = self.db.execute(
            select(Customer).where(
                func.lower(Customer.name) == cleaned.lower(),
                Customer.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if customer:
            return customer

        alias_key = normalize_import_key(cleaned)
        alias = self.db.execute(
            select(CustomerImportAlias).where(
                CustomerImportAlias.alias_key == alias_key,
                CustomerImportAlias.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if not alias:
            return None

        customer = self.db.get(Customer, alias.customer_id)
        if customer and customer.deleted_at is None:
            return customer
        return None

    def resolve_site_alias(self, customer_id: str, csv_site_name: str) -> Optional[str]:
        """Return canonical site name for a CSV site label under a customer."""
        cleaned = (csv_site_name or "").strip()
        if not cleaned:
            return None
        alias = self.db.execute(
            select(CustomerSiteImportAlias).where(
                CustomerSiteImportAlias.customer_id == customer_id,
                CustomerSiteImportAlias.alias_key == normalize_import_key(cleaned),
                CustomerSiteImportAlias.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        return alias.site_name if alias else None

    def resolve_site(
        self,
        customer: Customer,
        csv_site_name: str,
        *,
        allow_create: bool,
        suburb: Optional[str] = None,
        state: Optional[str] = None,
        postcode: Optional[str] = None,
    ) -> Optional[CustomerSite]:
        """Resolve or create a delivery site; return None if site can be omitted."""
        cleaned = (csv_site_name or suburb or "").strip()
        if not cleaned:
            return None

        if names_refer_to_same_entity(cleaned, customer.name):
            return None

        canonical = self.resolve_site_alias(customer.id, cleaned) or cleaned
        sites = self._customer_sites(customer.id)
        canonical_key = normalize_import_key(canonical)

        for site in sites:
            if normalize_import_key(site.site_name) == canonical_key:
                return self._touch_site(site, suburb, state, postcode)
        for site in sites:
            if names_refer_to_same_entity(site.site_name, canonical):
                return self._touch_site(site, suburb, state, postcode)

        if len(sites) == 1:
            return self._touch_site(sites[0], suburb, state, postcode)

        if allow_create:
            site = CustomerSite(
                customer_id=customer.id,
                site_name=canonical,
                state=(state or "UNKNOWN").upper()[:8],
                suburb=suburb,
                postcode=postcode,
            )
            self.db.add(site)
            self.db.flush()
            return site

        return None

    def _customer_sites(self, customer_id: str) -> List[CustomerSite]:
        stmt = (
            select(CustomerSite)
            .where(
                CustomerSite.customer_id == customer_id,
                CustomerSite.deleted_at.is_(None),
            )
            .order_by(CustomerSite.site_name)
        )
        return list(self.db.execute(stmt).scalars().all())

    @staticmethod
    def _touch_site(
        site: CustomerSite,
        suburb: Optional[str],
        state: Optional[str],
        postcode: Optional[str],
    ) -> CustomerSite:
        if suburb and not site.suburb:
            site.suburb = suburb
        if state and site.state == "UNKNOWN":
            site.state = state
        if postcode and not site.postcode:
            site.postcode = postcode
        return site

    def list_aliases(self) -> List[CustomerImportAlias]:
        stmt = (
            select(CustomerImportAlias)
            .where(CustomerImportAlias.deleted_at.is_(None))
            .order_by(CustomerImportAlias.alias_label)
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_site_aliases(self) -> List[CustomerSiteImportAlias]:
        stmt = (
            select(CustomerSiteImportAlias)
            .where(CustomerSiteImportAlias.deleted_at.is_(None))
            .order_by(CustomerSiteImportAlias.alias_label)
        )
        return list(self.db.execute(stmt).scalars().all())

    def add_alias(
        self,
        alias: str,
        customer_id: str,
        *,
        notes: Optional[str] = None,
    ) -> CustomerImportAlias:
        label = (alias or "").strip()
        if not label:
            raise ValueError("Alias is required")

        customer = self.db.get(Customer, customer_id)
        if not customer or customer.deleted_at:
            raise ValueError(f"Customer '{customer_id}' not found")

        key = normalize_import_key(label)
        existing = self.db.execute(
            select(CustomerImportAlias).where(
                CustomerImportAlias.alias_key == key,
                CustomerImportAlias.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if existing:
            if existing.customer_id == customer_id:
                return existing
            raise ValueError(
                f"Alias '{label}' already maps to another customer "
                f"(id={existing.customer_id})"
            )

        record = CustomerImportAlias(
            alias_key=key,
            alias_label=label,
            customer_id=customer_id,
            notes=notes,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def add_site_alias(
        self,
        alias: str,
        customer_id: str,
        site_name: str,
        *,
        notes: Optional[str] = None,
    ) -> CustomerSiteImportAlias:
        label = (alias or "").strip()
        canonical = (site_name or "").strip()
        if not label:
            raise ValueError("CSV site alias is required")
        if not canonical:
            raise ValueError("Canonical site name is required")

        customer = self.db.get(Customer, customer_id)
        if not customer or customer.deleted_at:
            raise ValueError(f"Customer '{customer_id}' not found")

        key = normalize_import_key(label)
        existing = self.db.execute(
            select(CustomerSiteImportAlias).where(
                CustomerSiteImportAlias.customer_id == customer_id,
                CustomerSiteImportAlias.alias_key == key,
                CustomerSiteImportAlias.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if existing:
            if existing.site_name == canonical:
                return existing
            raise ValueError(
                f"Site alias '{label}' already maps to '{existing.site_name}'"
            )

        record = CustomerSiteImportAlias(
            alias_key=key,
            alias_label=label,
            customer_id=customer_id,
            site_name=canonical,
            notes=notes,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def remove_alias(self, alias_id: str) -> None:
        record = self.db.get(CustomerImportAlias, alias_id)
        if not record or record.deleted_at:
            raise ValueError(f"Alias '{alias_id}' not found")
        record.deleted_at = datetime.utcnow()
        self.db.flush()

    def remove_site_alias(self, alias_id: str) -> None:
        record = self.db.get(CustomerSiteImportAlias, alias_id)
        if not record or record.deleted_at:
            raise ValueError(f"Site alias '{alias_id}' not found")
        record.deleted_at = datetime.utcnow()
        self.db.flush()
