"""Build docxtpl context from DB: Customer/Contact, quote or ad-hoc line items, overrides."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Session

from app.documents.contracts import (
    ContactContext,
    DocumentContext,
    DocumentHeaderContext,
    DocumentOverrides,
    LineItemContext,
    _format_address_block,
)

if TYPE_CHECKING:
    from app.adapters.db.models import (
        Contact,
        Customer,
        DeliveryDocket,
        DeliveryDocketLine,
        Product,
        SalesOrder,
        SalesOrderLine,
    )


def _format_date(d: Optional[date | datetime]) -> str:
    if d is None:
        return ""
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime("%Y-%m-%d")


def _format_decimal(v: Optional[Decimal], places: int = 2) -> str:
    if v is None:
        return "0.00"
    return f"{v:.{places}f}"


def _format_int(v: Optional[Decimal]) -> str:
    """Format as integer for quantities and dollar totals (ordered/delivered)."""
    if v is None:
        return "0"
    return str(int(round(v, 0)))


def _slug(s: str, max_len: int = 40) -> str:
    """Safe filesystem slug: alphanumeric and underscore only."""
    out = []
    for c in (s or "").strip():
        if c.isalnum() or c in " _-":
            out.append(c if c != " " else "_")
        if len(out) >= max_len:
            break
    return "".join(out).strip("_") or "unknown"


def contact_from_customer(customer: "Customer") -> ContactContext:
    """Build ContactContext from Customer model; address/daddress are collected single blocks."""
    addr = getattr(customer, "address", None) or ""
    daddr = _format_address_block(
        getattr(customer, "delivery_address_line1", None),
        getattr(customer, "delivery_address_line2", None),
        getattr(customer, "delivery_suburb", None),
        getattr(customer, "delivery_state", None),
        getattr(customer, "delivery_postcode", None),
        getattr(customer, "delivery_country", None),
    )
    return ContactContext(
        name=getattr(customer, "name", None) or "",
        code=getattr(customer, "code", None) or "",
        contact_person=getattr(customer, "contact_person", None),
        email=getattr(customer, "email", None),
        phone=getattr(customer, "phone", None),
        address=addr,
        daddress=daddr,
        billing_address_line1=getattr(customer, "billing_address_line1", None),
        billing_address_line2=getattr(customer, "billing_address_line2", None),
        billing_suburb=getattr(customer, "billing_suburb", None),
        billing_state=getattr(customer, "billing_state", None),
        billing_postcode=getattr(customer, "billing_postcode", None),
        billing_country=getattr(customer, "billing_country", None),
        delivery_address_line1=getattr(customer, "delivery_address_line1", None),
        delivery_address_line2=getattr(customer, "delivery_address_line2", None),
        delivery_suburb=getattr(customer, "delivery_suburb", None),
        delivery_state=getattr(customer, "delivery_state", None),
        delivery_postcode=getattr(customer, "delivery_postcode", None),
        delivery_country=getattr(customer, "delivery_country", None),
        abn=getattr(customer, "abn", None),
        notes=getattr(customer, "notes", None),
        alm_account_number=getattr(customer, "alm_account_number", None),
    )


def contact_from_contact(contact: "Contact") -> ContactContext:
    """Build ContactContext from unified Contact model (with billing/delivery address, ABN, notes)."""
    daddr = _format_address_block(
        getattr(contact, "delivery_address_line1", None),
        getattr(contact, "delivery_address_line2", None),
        getattr(contact, "delivery_suburb", None),
        getattr(contact, "delivery_state", None),
        getattr(contact, "delivery_postcode", None),
        getattr(contact, "delivery_country", None),
    )
    return ContactContext(
        name=contact.name or "",
        code=contact.code or "",
        contact_person=contact.contact_person,
        email=contact.email,
        phone=contact.phone,
        address=contact.address or "",
        daddress=daddr,
        billing_address_line1=getattr(contact, "billing_address_line1", None),
        billing_address_line2=getattr(contact, "billing_address_line2", None),
        billing_suburb=getattr(contact, "billing_suburb", None),
        billing_state=getattr(contact, "billing_state", None),
        billing_postcode=getattr(contact, "billing_postcode", None),
        billing_country=getattr(contact, "billing_country", None),
        delivery_address_line1=getattr(contact, "delivery_address_line1", None),
        delivery_address_line2=getattr(contact, "delivery_address_line2", None),
        delivery_suburb=getattr(contact, "delivery_suburb", None),
        delivery_state=getattr(contact, "delivery_state", None),
        delivery_postcode=getattr(contact, "delivery_postcode", None),
        delivery_country=getattr(contact, "delivery_country", None),
        abn=getattr(contact, "abn", None),
        notes=getattr(contact, "notes", None),
        alm_account_number=getattr(contact, "alm_account_number", None),
    )


def _get_product(
    session: Session, line: "SalesOrderLine | DeliveryDocketLine"
) -> Optional["Product"]:
    from app.adapters.db.models import Product

    product = getattr(line, "product", None)
    if product is not None:
        return product
    pid = getattr(line, "product_id", None)
    return session.get(Product, pid) if pid else None


def line_items_from_sales_order_lines(
    session: Session,
    lines: List["SalesOrderLine"],
) -> List[LineItemContext]:
    """Build line_items from SalesOrderLine list (with Product loaded)."""
    result = []
    for i, line in enumerate(lines, start=1):
        product = _get_product(session, line)
        if product is None:
            continue
        desc = (product.name or product.sku or str(line.product_id))[:200]
        qty = line.qty or Decimal("0")
        dqty_val = getattr(line, "delivered_qty", None) or Decimal("0")
        up = line.unit_price_ex_gst or Decimal("0")
        lt = (
            line.line_total_ex_gst
            if getattr(line, "line_total_ex_gst", None) is not None
            else (qty * up)
        )
        toqty_val = qty * up
        tdqty_val = dqty_val * up
        result.append(
            LineItemContext(
                description=desc,
                sku=product.sku or "",
                quantity=_format_int(qty),
                oqty=_format_int(qty),
                uom=getattr(line, "uom", None) or "unit",
                unit_price=_format_decimal(up),
                line_total=_format_decimal(lt),
                sequence=i,
                dqty=_format_int(dqty_val),
                toqty=_format_int(toqty_val),
                tdqty=_format_int(tdqty_val),
                product_name=product.name,
                quantity_raw=qty,
                unit_price_raw=up,
                line_total_raw=lt,
                dqty_raw=dqty_val,
                toqty_raw=toqty_val,
                tdqty_raw=tdqty_val,
            )
        )
    return result


def line_items_from_delivery_docket_lines(
    session: Session,
    lines: List["DeliveryDocketLine"],
) -> List[LineItemContext]:
    """Build line_items from DeliveryDocketLine list."""
    result = []
    for i, line in enumerate(lines, start=1):
        product = _get_product(session, line)
        if product is None:
            continue
        desc = (product.name or product.sku or str(line.product_id))[:200]
        # Ordered qty (if we have it on line; else use delivered as both for single-column dockets)
        ordered_qty = (
            getattr(line, "ordered_quantity", None) or line.quantity or Decimal("0")
        )
        dqty_val = line.quantity or Decimal("0")
        up = (
            getattr(line, "unit_price", None)
            or getattr(product, "wholesale_price_ex_gst", None)
            or Decimal("0")
        )
        toqty_val = ordered_qty * up
        tdqty_val = dqty_val * up
        lt = tdqty_val  # line_total = delivered total for display
        result.append(
            LineItemContext(
                description=desc,
                sku=product.sku or "",
                quantity=_format_int(ordered_qty),
                oqty=_format_int(ordered_qty),
                uom=getattr(line, "uom", None) or "unit",
                unit_price=_format_decimal(up),
                line_total=_format_decimal(lt),
                sequence=i,
                dqty=_format_int(dqty_val),
                toqty=_format_int(toqty_val),
                tdqty=_format_int(tdqty_val),
                product_name=product.name,
                quantity_raw=ordered_qty,
                unit_price_raw=up,
                line_total_raw=lt,
                dqty_raw=dqty_val,
                toqty_raw=toqty_val,
                tdqty_raw=tdqty_val,
            )
        )
    return result


def empty_line_item_context(sequence: int) -> LineItemContext:
    """One empty row for padding the line-items table."""
    return LineItemContext(
        description="",
        sku="",
        quantity="",
        oqty="",
        uom="",
        unit_price="",
        line_total="",
        sequence=sequence,
        dqty="",
        toqty="",
        tdqty="",
    )


def pad_line_items(
    line_items: List[LineItemContext],
    max_rows: int,
) -> List[LineItemContext]:
    """Pad with empty rows so the table has exactly max_rows rows (filled + empty)."""
    n = len(line_items)
    if n >= max_rows:
        return line_items[:max_rows]
    result = list(line_items)
    for i in range(n + 1, max_rows + 1):
        result.append(empty_line_item_context(i))
    return result


def compute_totals(
    line_items: List[LineItemContext],
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
    """Subtotal, tax, total; total_ordered (sum toqty_raw), total_delivered (sum tdqty_raw)."""
    subtotal = sum((li.line_total_raw or Decimal("0")) for li in line_items)
    tax = Decimal("0")
    total = subtotal + tax
    total_ordered = sum((li.toqty_raw or Decimal("0")) for li in line_items)
    total_delivered = sum((li.tdqty_raw or Decimal("0")) for li in line_items)
    return subtotal, tax, total, total_ordered, total_delivered


def build_context_from_delivery_docket(
    session: Session,
    docket: "DeliveryDocket",
    doc_type: str = "delivery_docket",
    overrides: Optional[DocumentOverrides] = None,
) -> "DocumentContext":
    """Build full DocumentContext from a DeliveryDocket."""
    # Load customer including delivery/billing address when columns exist
    from sqlalchemy import select
    from sqlalchemy.orm import load_only

    from app.adapters.db.models import Customer
    from app.documents.contracts import DocumentContext

    load_columns = [
        Customer.id,
        Customer.name,
        Customer.code,
        Customer.contact_person,
        Customer.email,
        Customer.phone,
        Customer.address,
    ]
    if hasattr(Customer, "delivery_address_line1"):
        load_columns.extend(
            [
                Customer.delivery_address_line1,
                Customer.delivery_address_line2,
                Customer.delivery_suburb,
                Customer.delivery_state,
                Customer.delivery_postcode,
                Customer.delivery_country,
            ]
        )
    if hasattr(Customer, "billing_address_line1"):
        load_columns.extend(
            [
                Customer.billing_address_line1,
                Customer.billing_address_line2,
                Customer.billing_suburb,
                Customer.billing_state,
                Customer.billing_postcode,
                Customer.billing_country,
            ]
        )
    customer = (
        session.execute(
            select(Customer)
            .options(load_only(*load_columns))
            .where(Customer.id == docket.customer_id)
            .limit(1)
        )
        .scalars()
        .first()
    )
    if customer:
        # Collected contact address (single block) and delivery address (single block)
        addr = getattr(customer, "address", None) or ""
        daddr = _format_address_block(
            getattr(customer, "delivery_address_line1", None),
            getattr(customer, "delivery_address_line2", None),
            getattr(customer, "delivery_suburb", None),
            getattr(customer, "delivery_state", None),
            getattr(customer, "delivery_postcode", None),
            getattr(customer, "delivery_country", None),
        )
        contact = ContactContext(
            name=customer.name or "",
            code=customer.code or "",
            contact_person=customer.contact_person,
            email=customer.email,
            phone=customer.phone,
            address=addr,
            daddress=daddr,
            delivery_address_line1=getattr(customer, "delivery_address_line1", None),
            delivery_address_line2=getattr(customer, "delivery_address_line2", None),
            delivery_suburb=getattr(customer, "delivery_suburb", None),
            delivery_state=getattr(customer, "delivery_state", None),
            delivery_postcode=getattr(customer, "delivery_postcode", None),
            delivery_country=getattr(customer, "delivery_country", None),
            billing_address_line1=getattr(customer, "billing_address_line1", None),
            billing_address_line2=getattr(customer, "billing_address_line2", None),
            billing_suburb=getattr(customer, "billing_suburb", None),
            billing_state=getattr(customer, "billing_state", None),
            billing_postcode=getattr(customer, "billing_postcode", None),
            billing_country=getattr(customer, "billing_country", None),
        )
    else:
        contact = ContactContext(name="", code="")

    from app.settings import settings

    lines = list(docket.lines) if docket.lines else []
    line_items = line_items_from_delivery_docket_lines(session, lines)
    subtotal, tax, total, total_ordered, total_delivered = compute_totals(line_items)
    line_items = pad_line_items(line_items, settings.docgen.table_max_rows)

    doc_number = docket.docket_number or str(docket.id)
    doc_date = (
        overrides.quote_date
        if overrides and overrides.quote_date
        else (docket.docket_date and docket.docket_date.date())
    )
    delivery_date = (
        overrides.delivery_date
        if overrides and overrides.delivery_date
        else (
            docket.delivery_date and docket.delivery_date.date()
            if hasattr(docket.delivery_date, "date")
            else docket.delivery_date
        )
    )

    document = DocumentHeaderContext(
        doc_type=doc_type,
        doc_number=doc_number,
        date=_format_date(doc_date or datetime.utcnow()),
        quote_date=_format_date(doc_date),
        delivery_date=_format_date(delivery_date),
        notes=(overrides.notes if overrides and overrides.notes else None)
        or docket.notes,
        shipping=overrides.shipping if overrides else None,
        payment_terms=overrides.payment_terms if overrides else None,
        discount_percent=_format_decimal(overrides.discount_percent, 2)
        if overrides and overrides.discount_percent is not None
        else None,
        subtotal=_format_decimal(subtotal),
        tax=_format_decimal(tax),
        total=_format_decimal(total),
        total_ordered=_format_int(total_ordered),
        total_delivered=_format_int(total_delivered),
    )
    return DocumentContext(
        contact=contact, document=document, line_items=line_items, overrides=overrides
    )


def build_context_from_sales_order(
    session: Session,
    order: "SalesOrder",
    doc_type: str = "quote",
    overrides: Optional[DocumentOverrides] = None,
) -> "DocumentContext":
    """Build full DocumentContext from a SalesOrder (quote)."""
    from app.adapters.db.models import Customer
    from app.documents.contracts import DocumentContext

    customer = order.customer
    if customer is None:
        customer = session.get(Customer, order.customer_id)
    contact = (
        contact_from_customer(customer)
        if customer
        else ContactContext(name="", code="")
    )

    from app.settings import settings

    lines = list(order.lines) if order.lines else []
    line_items = line_items_from_sales_order_lines(session, lines)
    subtotal, tax, total, total_ordered, total_delivered = compute_totals(line_items)
    line_items = pad_line_items(line_items, settings.docgen.table_max_rows)

    doc_number = order.order_ref or str(order.id)
    doc_date = (
        overrides.quote_date
        if overrides and overrides.quote_date
        else (
            order.order_date and order.order_date.date() if order.order_date else None
        )
    )
    requested = order.requested_date and (
        order.requested_date.date()
        if hasattr(order.requested_date, "date")
        else order.requested_date
    )

    document = DocumentHeaderContext(
        doc_type=doc_type,
        doc_number=doc_number,
        date=_format_date(doc_date or datetime.utcnow()),
        quote_date=_format_date(doc_date),
        delivery_date=_format_date(requested),
        notes=(overrides.notes if overrides and overrides.notes else None)
        or order.notes,
        shipping=overrides.shipping if overrides else None,
        payment_terms=overrides.payment_terms if overrides else None,
        discount_percent=_format_decimal(overrides.discount_percent, 2)
        if overrides and overrides.discount_percent is not None
        else None,
        subtotal=_format_decimal(subtotal),
        tax=_format_decimal(tax),
        total=_format_decimal(total),
        total_ordered=_format_int(total_ordered),
        total_delivered=_format_int(total_delivered),
    )
    return DocumentContext(
        contact=contact, document=document, line_items=line_items, overrides=overrides
    )


def build_context_from_contact_and_lines(
    session: Session,
    contact_id: Optional[str],
    customer_id: Optional[str],
    line_specs: List[dict],
    doc_type: str,
    doc_number: str,
    overrides: Optional[DocumentOverrides] = None,
) -> "DocumentContext":
    """Build context from contact/customer id + list of {product_id, quantity} or {product_id, quantity, unit_price}."""
    from app.adapters.db.models import Contact, Customer, Product
    from app.documents.contracts import DocumentContext

    contact_ctx = ContactContext(name="", code="")
    if customer_id:
        customer = session.get(Customer, customer_id)
        if customer:
            contact_ctx = contact_from_customer(customer)
    elif contact_id:
        contact = session.get(Contact, contact_id)
        if contact:
            contact_ctx = contact_from_contact(contact)

    line_items = []
    for i, spec in enumerate(line_specs, start=1):
        pid = spec.get("product_id")
        qty = Decimal(str(spec.get("quantity", 0)))
        unit_price = spec.get("unit_price")
        product = session.get(Product, pid) if pid else None
        if not product:
            continue
        if unit_price is None:
            unit_price = getattr(product, "wholesale_price_ex_gst", None) or Decimal(
                "0"
            )
        else:
            unit_price = Decimal(str(unit_price))
        lt = qty * unit_price
        line_items.append(
            LineItemContext(
                description=(product.name or product.sku or "")[:200],
                sku=product.sku or "",
                quantity=_format_int(qty),
                oqty=_format_int(qty),
                uom=spec.get("uom", "unit"),
                unit_price=_format_decimal(unit_price),
                line_total=_format_decimal(lt),
                sequence=i,
                dqty=_format_int(qty),
                toqty=_format_int(lt),
                tdqty=_format_int(lt),
                product_name=product.name,
                quantity_raw=qty,
                unit_price_raw=unit_price,
                line_total_raw=lt,
                dqty_raw=qty,
                toqty_raw=lt,
                tdqty_raw=lt,
            )
        )
    from app.settings import settings

    subtotal, tax, total, total_ordered, total_delivered = compute_totals(line_items)
    line_items = pad_line_items(line_items, settings.docgen.table_max_rows)

    doc_date = (
        overrides.quote_date if overrides and overrides.quote_date else date.today()
    )
    document = DocumentHeaderContext(
        doc_type=doc_type,
        doc_number=doc_number,
        date=_format_date(doc_date),
        quote_date=_format_date(overrides.quote_date if overrides else None),
        delivery_date=_format_date(overrides.delivery_date if overrides else None),
        notes=overrides.notes if overrides else None,
        shipping=overrides.shipping if overrides else None,
        payment_terms=overrides.payment_terms if overrides else None,
        discount_percent=_format_decimal(overrides.discount_percent, 2)
        if overrides and overrides.discount_percent is not None
        else None,
        subtotal=_format_decimal(subtotal),
        tax=_format_decimal(tax),
        total=_format_decimal(total),
        total_ordered=_format_int(total_ordered),
        total_delivered=_format_int(total_delivered),
    )
    return DocumentContext(
        contact=contact_ctx,
        document=document,
        line_items=line_items,
        overrides=overrides,
    )


def safe_slug_for_filename(
    contact: ContactContext, doc_number: str, doc_type: str
) -> str:
    """Deterministic slug for filename: doc_type_customer_doc_number_YYYYMMDD."""
    from datetime import date

    customer_slug = _slug(contact.name or contact.code or "unknown", 30)
    num_slug = _slug(doc_number, 20)
    return f"{doc_type}_{customer_slug}_{num_slug}_{date.today().strftime('%Y%m%d')}"
