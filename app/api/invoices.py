# app/api/invoices.py
"""Invoices API router."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.adapters.db import get_db
from app.adapters.db.models import Invoice, InvoiceLine, Customer, SalesOrder, Product
from app.api.dto import (
    InvoiceCreate, InvoiceResponse, InvoiceLineResponse, InvoiceIssueRequest,
    PrintResponse, ErrorResponse
)
from app.domain.rules import calculate_line_totals, round_money
from app.reports.invoice import generate_invoice_text

router = APIRouter(prefix="/invoices", tags=["invoices"])


def invoice_to_response(invoice: Invoice) -> InvoiceResponse:
    """Convert Invoice model to response DTO."""
    return InvoiceResponse(
        id=invoice.id,
        customer_id=invoice.customer_id,
        sales_order_id=invoice.sales_order_id,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        status=invoice.status,
        subtotal_ex_tax=invoice.subtotal_ex_tax,
        total_tax=invoice.total_tax,
        total_inc_tax=invoice.total_inc_tax,
        notes=invoice.notes,
        lines=[
            InvoiceLineResponse(
                id=line.id,
                product_id=line.product_id,
                quantity_kg=line.quantity_kg,
                unit_price_ex_tax=line.unit_price_ex_tax,
                tax_rate=line.tax_rate,
                line_total_ex_tax=line.line_total_ex_tax,
                line_total_inc_tax=line.line_total_inc_tax,
                sequence=line.sequence
            ) for line in invoice.lines
        ]
    )


def generate_invoice_number(db: Session) -> str:
    """Generate next invoice number."""
    # Get the highest existing invoice number
    stmt = select(func.max(Invoice.invoice_number)).where(
        Invoice.invoice_number.like("INV-%")
    )
    max_number = db.execute(stmt).scalar()
    
    if max_number:
        # Extract number and increment
        try:
            number_part = max_number.split("-")[1]
            next_number = int(number_part) + 1
        except (IndexError, ValueError):
            next_number = 1
    else:
        next_number = 1
    
    return f"INV-{next_number:08d}"


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_data: InvoiceCreate, db: Session = Depends(get_db)):
    """Create a new invoice."""
    # Validate customer exists
    customer = db.get(Customer, invoice_data.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Validate sales order if provided
    if invoice_data.sales_order_id:
        sales_order = db.get(SalesOrder, invoice_data.sales_order_id)
        if not sales_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
    
    # Validate all products exist
    product_ids = [line.product_id for line in invoice_data.lines]
    products_stmt = select(Product).where(Product.id.in_(product_ids))
    products = {p.id: p for p in db.execute(products_stmt).scalars().all()}
    
    missing_products = set(product_ids) - set(products.keys())
    if missing_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Products not found: {', '.join(missing_products)}"
        )
    
    # Generate invoice number
    invoice_number = generate_invoice_number(db)
    
    # Create invoice
    invoice = Invoice(
        id=str(uuid4()),
        customer_id=invoice_data.customer_id,
        sales_order_id=invoice_data.sales_order_id,
        invoice_number=invoice_number,
        invoice_date=invoice_data.invoice_date or datetime.utcnow(),
        due_date=invoice_data.due_date,
        status="DRAFT",
        subtotal_ex_tax=Decimal("0"),
        total_tax=Decimal("0"),
        total_inc_tax=Decimal("0"),
        notes=invoice_data.notes
    )
    
    db.add(invoice)
    db.flush()  # Get the invoice ID
    
    # Create invoice lines
    subtotal_ex_tax = Decimal("0")
    total_tax = Decimal("0")
    
    for i, line_data in enumerate(invoice_data.lines):
        product = products[line_data.product_id]
        
        # Calculate line totals
        line_total_ex_tax, tax_amount, line_total_inc_tax = calculate_line_totals(
            line_data.quantity_kg,
            line_data.unit_price_ex_tax,
            line_data.tax_rate
        )
        
        invoice_line = InvoiceLine(
            id=str(uuid4()),
            invoice_id=invoice.id,
            product_id=line_data.product_id,
            quantity_kg=line_data.quantity_kg,
            unit_price_ex_tax=line_data.unit_price_ex_tax,
            tax_rate=line_data.tax_rate,
            line_total_ex_tax=line_total_ex_tax,
            line_total_inc_tax=line_total_inc_tax,
            sequence=i + 1
        )
        
        db.add(invoice_line)
        
        subtotal_ex_tax += line_total_ex_tax
        total_tax += tax_amount
    
    # Update invoice totals
    invoice.subtotal_ex_tax = round_money(subtotal_ex_tax)
    invoice.total_tax = round_money(total_tax)
    invoice.total_inc_tax = round_money(subtotal_ex_tax + total_tax)
    
    db.commit()
    db.refresh(invoice)
    
    return invoice_to_response(invoice)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    """Get invoice by ID."""
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return invoice_to_response(invoice)


@router.post("/{invoice_id}/issue", response_model=InvoiceResponse)
async def issue_invoice(
    invoice_id: str,
    issue_data: InvoiceIssueRequest,
    db: Session = Depends(get_db)
):
    """Issue an invoice (change status from DRAFT to SENT)."""
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if invoice.status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot issue invoice with status '{invoice.status}'"
        )
    
    invoice.status = "SENT"
    if issue_data.notes:
        invoice.notes = (invoice.notes or "") + f"\nIssue notes: {issue_data.notes}"
    
    db.commit()
    db.refresh(invoice)
    
    return invoice_to_response(invoice)


@router.get("/{invoice_id}/print", response_model=PrintResponse)
async def print_invoice(
    invoice_id: str,
    format: str = Query("text", regex="^(text|pdf)$"),
    db: Session = Depends(get_db)
):
    """Print invoice in specified format."""
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if format == "text":
        content = generate_invoice_text(invoice.invoice_number)
    else:
        # PDF not implemented yet
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF format not implemented yet"
        )
    
    return PrintResponse(
        content=content,
        format=format,
        generated_at=datetime.utcnow()
    )
