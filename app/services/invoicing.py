# app/services/invoicing.py
"""Service for invoice reporting and data retrieval."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.adapters.db.models import (
    Invoice, InvoiceLine, Customer, SalesOrder, Product, SoLine
)


class InvoicingService:
    """Service for retrieving invoice data for reporting."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_invoice_data(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get complete invoice data for reporting."""
        # Query invoice with all related data using joinedload for efficiency
        stmt = (
            select(Invoice)
            .where(Invoice.invoice_number == invoice_number)
            .options(
                joinedload(Invoice.customer),
                joinedload(Invoice.sales_order),
                joinedload(Invoice.lines).joinedload(InvoiceLine.product)
            )
        )
        invoice = self.db.execute(stmt).scalar_one_or_none()
        
        if not invoice:
            return None
        
        customer = invoice.customer
        sales_order = invoice.sales_order
        
        # Get sales order lines if available
        sales_order_lines = []
        if sales_order:
            so_lines_stmt = (
                select(SoLine)
                .where(SoLine.sales_order_id == sales_order.id)
                .options(joinedload(SoLine.product))
                .order_by(SoLine.sequence)
            )
            sales_order_lines = self.db.execute(so_lines_stmt).scalars().all()
        
        return {
            'invoice': invoice,
            'customer': customer,
            'sales_order': sales_order,
            'lines': invoice.lines,
            'sales_order_lines': sales_order_lines,
        }
    
    def get_invoice_summary(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get invoice summary data for quick reporting."""
        invoice_data = self.get_invoice_data(invoice_number)
        if not invoice_data:
            return None
        
        invoice = invoice_data['invoice']
        customer = invoice_data['customer']
        lines = invoice_data['lines']
        
        # Calculate line counts and totals
        total_lines = len(lines)
        total_quantity_kg = sum(line.quantity_kg for line in lines)
        
        # Get product summary
        products = set(line.product for line in lines)
        unique_products = len(products)
        
        return {
            'invoice_number': invoice.invoice_number,
            'customer_name': customer.name if customer else 'Unknown',
            'customer_code': customer.code if customer else 'Unknown',
            'invoice_date': invoice.invoice_date,
            'due_date': invoice.due_date,
            'status': invoice.status,
            'subtotal_ex_tax': invoice.subtotal_ex_tax,
            'total_tax': invoice.total_tax,
            'total_inc_tax': invoice.total_inc_tax,
            'total_lines': total_lines,
            'total_quantity_kg': total_quantity_kg,
            'unique_products': unique_products,
        }
    
    def get_customer_invoices(self, customer_code: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent invoices for a customer."""
        stmt = (
            select(Invoice)
            .join(Customer)
            .where(Customer.code == customer_code)
            .options(
                joinedload(Invoice.customer),
                joinedload(Invoice.lines)
            )
            .order_by(Invoice.invoice_date.desc())
            .limit(limit)
        )
        invoices = self.db.execute(stmt).scalars().all()
        
        return [
            {
                'invoice': invoice,
                'customer': invoice.customer,
                'lines': invoice.lines,
            }
            for invoice in invoices
        ]
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice data by ID."""
        stmt = (
            select(Invoice)
            .where(Invoice.id == invoice_id)
            .options(
                joinedload(Invoice.customer),
                joinedload(Invoice.sales_order),
                joinedload(Invoice.lines).joinedload(InvoiceLine.product)
            )
        )
        invoice = self.db.execute(stmt).scalar_one_or_none()
        
        if not invoice:
            return None
        
        return {
            'invoice': invoice,
            'customer': invoice.customer,
            'sales_order': invoice.sales_order,
            'lines': invoice.lines,
        }


def get_invoice_data_for_reporting(invoice_number: str, db: Session) -> Optional[Dict[str, Any]]:
    """Convenience function to get invoice data."""
    service = InvoicingService(db)
    return service.get_invoice_data(invoice_number)


def get_invoice_summary_for_reporting(invoice_number: str, db: Session) -> Optional[Dict[str, Any]]:
    """Convenience function to get invoice summary."""
    service = InvoicingService(db)
    return service.get_invoice_summary(invoice_number)


def get_customer_invoices_for_reporting(customer_code: str, db: Session, limit: int = 100) -> List[Dict[str, Any]]:
    """Convenience function to get customer invoices."""
    service = InvoicingService(db)
    return service.get_customer_invoices(customer_code, limit)