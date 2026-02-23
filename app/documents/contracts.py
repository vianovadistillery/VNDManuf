"""Data contract: exact Python dict schema passed to docxtpl (Jinja2-in-DOCX)."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, List, Optional


@dataclass
class LineItemContext:
    """One row in the line-items table (product/quantity/price)."""

    description: str
    sku: str
    quantity: str  # Ordered qty (formatted)
    uom: str
    unit_price: str
    line_total: str
    sequence: int = 0
    oqty: str = (
        ""  # Ordered qty (use {{ item.oqty }} in template); set same as quantity
    )
    # Delivered qty and line totals (for delivery dockets: ordered vs delivered)
    dqty: str = "0"  # Delivered quantity
    toqty: str = "0.00"  # Ordered line total (quantity * unit_price)
    tdqty: str = "0.00"  # Delivered line total (dqty * unit_price)
    # Optional for templates that need them
    product_name: Optional[str] = None
    quantity_raw: Optional[Decimal] = None
    unit_price_raw: Optional[Decimal] = None
    line_total_raw: Optional[Decimal] = None
    dqty_raw: Optional[Decimal] = None
    toqty_raw: Optional[Decimal] = None
    tdqty_raw: Optional[Decimal] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "sku": self.sku,
            "quantity": self.quantity,
            "oqty": self.oqty,
            "uom": self.uom,
            "unit_price": self.unit_price,
            "line_total": self.line_total,
            "sequence": self.sequence,
            "dqty": self.dqty,
            "toqty": self.toqty,
            "tdqty": self.tdqty,
            "product_name": self.product_name,
            "quantity_raw": float(self.quantity_raw)
            if self.quantity_raw is not None
            else None,
            "unit_price_raw": float(self.unit_price_raw)
            if self.unit_price_raw is not None
            else None,
            "line_total_raw": float(self.line_total_raw)
            if self.line_total_raw is not None
            else None,
            "dqty_raw": float(self.dqty_raw) if self.dqty_raw is not None else None,
            "toqty_raw": float(self.toqty_raw) if self.toqty_raw is not None else None,
            "tdqty_raw": float(self.tdqty_raw) if self.tdqty_raw is not None else None,
        }


def _format_address_block(
    line1: Optional[str] = None,
    line2: Optional[str] = None,
    suburb: Optional[str] = None,
    state: Optional[str] = None,
    postcode: Optional[str] = None,
    country: Optional[str] = None,
) -> str:
    """Build a single collected address string from parts (e.g. for contact.address / contact.daddress)."""
    parts = [
        p
        for p in (line1, line2, suburb, state, postcode, country)
        if p and str(p).strip()
    ]
    return "\n".join(parts) if parts else ""


@dataclass
class ContactContext:
    """Contact/customer block for header and address."""

    name: str
    code: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None  # Collected contact/primary address (single block)
    daddress: Optional[str] = None  # Collected delivery address (single block)
    # Billing/delivery (optional; individual fields for templates that need them)
    billing_address_line1: Optional[str] = None
    billing_address_line2: Optional[str] = None
    billing_suburb: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postcode: Optional[str] = None
    billing_country: Optional[str] = None
    delivery_address_line1: Optional[str] = None
    delivery_address_line2: Optional[str] = None
    delivery_suburb: Optional[str] = None
    delivery_state: Optional[str] = None
    delivery_postcode: Optional[str] = None
    delivery_country: Optional[str] = None
    abn: Optional[str] = None
    notes: Optional[str] = None
    alm_account_number: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "code": self.code,
            "contact_person": self.contact_person or "",
            "email": self.email or "",
            "phone": self.phone or "",
            "address": self.address or "",
            "daddress": self.daddress or "",
            "billing_address_line1": self.billing_address_line1 or "",
            "billing_address_line2": self.billing_address_line2 or "",
            "billing_suburb": self.billing_suburb or "",
            "billing_state": self.billing_state or "",
            "billing_postcode": self.billing_postcode or "",
            "billing_country": self.billing_country or "",
            "delivery_address_line1": self.delivery_address_line1 or "",
            "delivery_address_line2": self.delivery_address_line2 or "",
            "delivery_suburb": self.delivery_suburb or "",
            "delivery_state": self.delivery_state or "",
            "delivery_postcode": self.delivery_postcode or "",
            "delivery_country": self.delivery_country or "",
            "abn": self.abn or "",
            "notes": self.notes or "",
            "alm_account_number": self.alm_account_number or "",
        }


@dataclass
class DocumentHeaderContext:
    """Document-level fields (dates, totals, notes, terms)."""

    doc_type: str
    doc_number: str
    date: str  # Formatted (e.g. YYYY-MM-DD or DD/MM/YYYY)
    quote_date: Optional[str] = None
    delivery_date: Optional[str] = None
    notes: Optional[str] = None
    shipping: Optional[str] = None
    payment_terms: Optional[str] = None
    discount_percent: Optional[str] = None
    subtotal: str = "0.00"
    tax: str = "0.00"
    total: str = "0.00"
    total_ordered: str = "0.00"  # Sum of line toqty (ordered)
    total_delivered: str = "0.00"  # Sum of line tdqty (delivered)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_type": self.doc_type,
            "doc_number": self.doc_number,
            "date": self.date,
            "quote_date": self.quote_date or "",
            "delivery_date": self.delivery_date or "",
            "notes": self.notes or "",
            "shipping": self.shipping or "",
            "payment_terms": self.payment_terms or "",
            "discount_percent": self.discount_percent or "",
            "subtotal": self.subtotal,
            "tax": self.tax,
            "total": self.total,
            "total_ordered": self.total_ordered,
            "total_delivered": self.total_delivered,
        }


@dataclass
class DocumentOverrides:
    """Runtime overrides (quote date, discount, notes, shipping, payment terms)."""

    quote_date: Optional[date] = None
    delivery_date: Optional[date] = None
    notes: Optional[str] = None
    shipping: Optional[str] = None
    payment_terms: Optional[str] = None
    discount_percent: Optional[Decimal] = None


@dataclass
class DocumentContext:
    """Full context passed to docxtpl. Template uses: {{ contact.name }}, {{ document.doc_number }}, {% for item in line_items %}...{% endfor %}."""

    contact: ContactContext
    document: DocumentHeaderContext
    line_items: List[LineItemContext] = field(default_factory=list)
    overrides: Optional[DocumentOverrides] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "contact": self.contact.to_dict(),
            "document": self.document.to_dict(),
            "line_items": [li.to_dict() for li in self.line_items],
        }


def build_document_context(
    contact: ContactContext,
    document: DocumentHeaderContext,
    line_items: List[LineItemContext],
    overrides: Optional[DocumentOverrides] = None,
) -> DocumentContext:
    """Build the full context for docxtpl."""
    return DocumentContext(
        contact=contact,
        document=document,
        line_items=line_items,
        overrides=overrides,
    )
