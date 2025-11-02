#!/usr/bin/env python3
"""Idempotent migration from legacy files to the new database."""
import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from decimal import Decimal
import uuid
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.adapters.db import get_db, create_tables
from app.adapters.db.models import (
    Product, ProductVariant, Customer, Supplier, Contact, PackUnit, PackConversion,
    PriceList, PriceListItem, CustomerPrice, WorkOrder, Batch, BatchComponent,
    Invoice, InvoiceLine, InventoryLot, Formula, FormulaLine
)
from app.adapters.legacy_io import (
    FixedWidthParser, LegacyDataMapper,
    create_sample_products_data, create_sample_customers_data,
    create_sample_pack_units_data, create_sample_batch_data,
    create_sample_invoice_data
)


class LegacyMigrator:
    """Handles migration of legacy data to the modern database."""
    
    def __init__(self, db: Session, dry_run: bool = False, allow_anomalies: bool = False):
        self.db = db
        self.dry_run = dry_run
        self.allow_anomalies = allow_anomalies
        self.audit_records = []
        self.anomalies = []
        self.stats = {
            'products': 0,
            'customers': 0,
            'suppliers': 0,
            'contacts': 0,
            'pack_units': 0,
            'price_lists': 0,
            'work_orders': 0,
            'batches': 0,
            'invoices': 0,
            'inventory_lots': 0,
            'anomalies': 0
        }
    
    def migrate_all(self) -> Dict[str, Any]:
        """Run the complete migration process."""
        print("Starting legacy data migration...")
        
        if self.dry_run:
            print("DRY RUN MODE - No data will be written to database")
        
        # Migration order as specified in brief.md
        self.migrate_products()
        self.migrate_customers()
        self.migrate_suppliers()
        self.migrate_contacts()
        self.migrate_pack_units()
        self.migrate_pricing()
        self.migrate_inventory_lots()
        self.migrate_work_orders()
        self.migrate_batches()
        self.migrate_sales_orders()
        self.migrate_invoices()
        
        # Commit if not dry run
        if not self.dry_run:
            self.db.commit()
            print("Migration committed to database")
        else:
            self.db.rollback()
            print("Dry run completed - no changes committed")
        
        return self.stats
    
    def migrate_products(self) -> None:
        """Migrate product data."""
        print("Migrating products...")
        
        # For now, use sample data. In production, this would read from legacy files
        products_data = create_sample_products_data()
        
        for product_data in products_data:
            try:
                # Check if product already exists (upsert by SKU)
                existing = self.db.execute(
                    select(Product).where(Product.sku == product_data['sku'])
                ).scalar_one_or_none()
                
                if existing:
                    # Update existing product
                    for key, value in product_data.items():
                        if key != 'sku':  # Don't update the key field
                            setattr(existing, key, value)
                    product = existing
                    action = "updated"
                else:
                    # Create new product
                    product = Product(**product_data)
                    self.db.add(product)
                    action = "created"
                
                if not self.dry_run:
                    self.db.flush()  # Get the ID
                
                self.audit_records.append({
                    'table': 'products',
                    'action': action,
                    'key': product_data['sku'],
                    'id': str(product.id) if hasattr(product, 'id') else 'new',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                self.stats['products'] += 1
                
            except Exception as e:
                self._handle_anomaly('products', product_data, str(e))
    
    def migrate_customers(self) -> None:
        """Migrate customer data."""
        print("Migrating customers...")
        
        customers_data = create_sample_customers_data()
        
        for customer_data in customers_data:
            try:
                # Upsert by customer code
                existing = self.db.execute(
                    select(Customer).where(Customer.code == customer_data['code'])
                ).scalar_one_or_none()
                
                if existing:
                    for key, value in customer_data.items():
                        if key != 'code':
                            setattr(existing, key, value)
                    customer = existing
                    action = "updated"
                else:
                    customer = Customer(**customer_data)
                    self.db.add(customer)
                    action = "created"
                
                if not self.dry_run:
                    self.db.flush()
                
                self.audit_records.append({
                    'table': 'customers',
                    'action': action,
                    'key': customer_data['code'],
                    'id': str(customer.id) if hasattr(customer, 'id') else 'new',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                self.stats['customers'] += 1
                
            except Exception as e:
                self._handle_anomaly('customers', customer_data, str(e))
    
    def migrate_suppliers(self) -> None:
        """Migrate supplier data."""
        print("Migrating suppliers...")
        
        # Sample supplier data
        suppliers_data = [
            {
                'code': 'SUPP-001',
                'name': 'Raw Materials Co',
                'contact_person': 'Bob Supplier',
                'email': 'bob@rawmaterials.com.au',
                'phone': '+61 3 9999 8888',
                'address': '456 Industrial Blvd\nMELBOURNE 3000\nAU',
                'is_active': True
            }
        ]
        
        for supplier_data in suppliers_data:
            try:
                existing = self.db.execute(
                    select(Supplier).where(Supplier.code == supplier_data['code'])
                ).scalar_one_or_none()
                
                if existing:
                    for key, value in supplier_data.items():
                        if key != 'code':
                            setattr(existing, key, value)
                    supplier = existing
                    action = "updated"
                else:
                    supplier = Supplier(**supplier_data)
                    self.db.add(supplier)
                    action = "created"
                
                if not self.dry_run:
                    self.db.flush()
                
                self.audit_records.append({
                    'table': 'suppliers',
                    'action': action,
                    'key': supplier_data['code'],
                    'id': str(supplier.id) if hasattr(supplier, 'id') else 'new',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                self.stats['suppliers'] += 1
                
            except Exception as e:
                self._handle_anomaly('suppliers', supplier_data, str(e))
    
    def migrate_contacts(self) -> None:
        """Migrate supplier and customer data to contacts."""
        print("Migrating contacts...")
        
        # Sample contact data
        contacts_data = [
            {
                'code': 'CONT-001',
                'name': 'Acme Chemicals',
                'contact_person': 'John Smith',
                'email': 'john@acme.com',
                'phone': '555-0101',
                'address': '123 Main St',
                'is_customer': False,
                'is_supplier': True,
                'is_other': False,
                'tax_rate': 10.0,
                'is_active': True
            },
            {
                'code': 'CONT-002',
                'name': 'Paint Distributors Inc',
                'contact_person': 'Jane Customer',
                'email': 'jane@paintdist.com',
                'phone': '555-0202',
                'address': '456 Oak Ave',
                'is_customer': True,
                'is_supplier': False,
                'is_other': False,
                'tax_rate': 10.0,
                'is_active': True
            },
            {
                'code': 'CONT-003',
                'name': 'Global Materials Ltd',
                'contact_person': 'Bob Johnson',
                'email': 'bob@global.com',
                'phone': '555-0303',
                'address': '789 Pine Rd',
                'is_customer': False,
                'is_supplier': True,
                'is_other': False,
                'tax_rate': 10.0,
                'is_active': True
            }
        ]
        
        for contact_data in contacts_data:
            try:
                existing = self.db.execute(
                    select(Contact).where(Contact.code == contact_data['code'])
                ).scalar_one_or_none()
                
                if existing:
                    for key, value in contact_data.items():
                        if key != 'code':
                            setattr(existing, key, value)
                    contact = existing
                    action = "updated"
                else:
                    contact = Contact(**contact_data)
                    self.db.add(contact)
                    action = "created"
                
                if not self.dry_run:
                    self.db.flush()
                
                self.audit_records.append({
                    'table': 'contacts',
                    'action': action,
                    'key': contact_data['code'],
                    'id': str(contact.id) if hasattr(contact, 'id') else 'new',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                self.stats['contacts'] += 1
                
            except Exception as e:
                self._handle_anomaly('contacts', contact_data, str(e))
    
    def migrate_pack_units(self) -> None:
        """Migrate pack unit data."""
        print("Migrating pack units...")
        
        pack_units_data = create_sample_pack_units_data()
        
        for pack_unit_data in pack_units_data:
            try:
                existing = self.db.execute(
                    select(PackUnit).where(PackUnit.code == pack_unit_data['code'])
                ).scalar_one_or_none()
                
                if existing:
                    for key, value in pack_unit_data.items():
                        if key != 'code':
                            setattr(existing, key, value)
                    pack_unit = existing
                    action = "updated"
                else:
                    pack_unit = PackUnit(**pack_unit_data)
                    self.db.add(pack_unit)
                    action = "created"
                
                if not self.dry_run:
                    self.db.flush()
                
                self.audit_records.append({
                    'table': 'pack_units',
                    'action': action,
                    'key': pack_unit_data['code'],
                    'id': str(pack_unit.id) if hasattr(pack_unit, 'id') else 'new',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                self.stats['pack_units'] += 1
                
            except Exception as e:
                self._handle_anomaly('pack_units', pack_unit_data, str(e))
    
    def migrate_pricing(self) -> None:
        """Migrate pricing data."""
        print("Migrating pricing...")
        
        # Create a default price list
        price_list_data = {
            'code': 'DEFAULT',
            'name': 'Default Price List',
            'effective_date': datetime.utcnow(),
            'expiry_date': None,
            'is_active': True
        }
        
        try:
            existing = self.db.execute(
                select(PriceList).where(PriceList.code == price_list_data['code'])
            ).scalar_one_or_none()
            
            if existing:
                price_list = existing
            else:
                price_list = PriceList(**price_list_data)
                self.db.add(price_list)
                if not self.dry_run:
                    self.db.flush()
            
            # Add price list items for products
            products = self.db.execute(select(Product)).scalars().all()
            for product in products:
                price_item_data = {
                    'price_list_id': price_list.id,
                    'product_id': product.id,
                    'pack_unit_code': 'CAN',
                    'unit_price_ex_tax': Decimal('25.00'),
                    'min_quantity': Decimal('1.0'),
                    'is_active': True
                }
                
                existing_item = self.db.execute(
                    select(PriceListItem).where(
                        and_(
                            PriceListItem.price_list_id == price_list.id,
                            PriceListItem.product_id == product.id,
                            PriceListItem.pack_unit_code == 'CAN'
                        )
                    )
                ).scalar_one_or_none()
                
                if not existing_item:
                    price_item = PriceListItem(**price_item_data)
                    self.db.add(price_item)
            
            self.stats['price_lists'] += 1
            
        except Exception as e:
            self._handle_anomaly('price_lists', price_list_data, str(e))
    
    def migrate_inventory_lots(self) -> None:
        """Migrate inventory lot data."""
        print("Migrating inventory lots...")
        
        # Sample inventory lots
        lots_data = [
            {
                'lot_code': 'LOT-001',
                'product_id': 'PAINT-001',  # Will be resolved to actual product ID
                'quantity_kg': Decimal('1000.0'),
                'unit_cost': Decimal('15.50'),
                'received_at': datetime.utcnow(),
                'expires_at': None,
                'is_active': True
            }
        ]
        
        for lot_data in lots_data:
            try:
                # Resolve product_id to actual product
                product = self.db.execute(
                    select(Product).where(Product.sku == lot_data['product_id'])
                ).scalar_one_or_none()
                
                if not product:
                    raise ValueError(f"Product {lot_data['product_id']} not found")
                
                lot_data['product_id'] = product.id
                
                existing = self.db.execute(
                    select(InventoryLot).where(InventoryLot.lot_code == lot_data['lot_code'])
                ).scalar_one_or_none()
                
                if existing:
                    for key, value in lot_data.items():
                        if key != 'lot_code':
                            setattr(existing, key, value)
                    lot = existing
                    action = "updated"
                else:
                    lot = InventoryLot(**lot_data)
                    self.db.add(lot)
                    action = "created"
                
                if not self.dry_run:
                    self.db.flush()
                
                self.audit_records.append({
                    'table': 'inventory_lots',
                    'action': action,
                    'key': lot_data['lot_code'],
                    'id': str(lot.id) if hasattr(lot, 'id') else 'new',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                self.stats['inventory_lots'] += 1
                
            except Exception as e:
                self._handle_anomaly('inventory_lots', lot_data, str(e))
    
    def migrate_work_orders(self) -> None:
        """Migrate work order data."""
        print("Migrating work orders...")
        
        # Sample work order
        wo_data = {
            'code': 'WO-001',
            'product_id': 'PAINT-001',  # Will be resolved
            'planned_quantity_kg': Decimal('370.0'),
            'status': 'completed',
            'created_at': datetime.utcnow(),
            'completed_at': datetime.utcnow()
        }
        
        try:
            # Resolve product_id
            product = self.db.execute(
                select(Product).where(Product.sku == wo_data['product_id'])
            ).scalar_one_or_none()
            
            if not product:
                raise ValueError(f"Product {wo_data['product_id']} not found")
            
            wo_data['product_id'] = product.id
            
            existing = self.db.execute(
                select(WorkOrder).where(WorkOrder.code == wo_data['code'])
            ).scalar_one_or_none()
            
            if existing:
                for key, value in wo_data.items():
                    if key != 'code':
                        setattr(existing, key, value)
                wo = existing
                action = "updated"
            else:
                wo = WorkOrder(**wo_data)
                self.db.add(wo)
                action = "created"
            
            if not self.dry_run:
                self.db.flush()
            
            self.audit_records.append({
                'table': 'work_orders',
                'action': action,
                'key': wo_data['code'],
                'id': str(wo.id) if hasattr(wo, 'id') else 'new',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            self.stats['work_orders'] += 1
            
        except Exception as e:
            self._handle_anomaly('work_orders', wo_data, str(e))
    
    def migrate_batches(self) -> None:
        """Migrate batch data."""
        print("Migrating batches...")
        
        batches_data = create_sample_batch_data()
        
        for batch_data in batches_data:
            try:
                # Resolve work_order_id
                work_order = self.db.execute(
                    select(WorkOrder).where(WorkOrder.code == batch_data['work_order_id'])
                ).scalar_one_or_none()
                
                if not work_order:
                    raise ValueError(f"Work order {batch_data['work_order_id']} not found")
                
                batch_data['work_order_id'] = work_order.id
                
                # Resolve product_id
                product = self.db.execute(
                    select(Product).where(Product.sku == batch_data['product_id'])
                ).scalar_one_or_none()
                
                if not product:
                    raise ValueError(f"Product {batch_data['product_id']} not found")
                
                batch_data['product_id'] = product.id
                
                existing = self.db.execute(
                    select(Batch).where(Batch.batch_code == batch_data['batch_code'])
                ).scalar_one_or_none()
                
                if existing:
                    for key, value in batch_data.items():
                        if key != 'batch_code':
                            setattr(existing, key, value)
                    batch = existing
                    action = "updated"
                else:
                    batch = Batch(**batch_data)
                    self.db.add(batch)
                    action = "created"
                
                if not self.dry_run:
                    self.db.flush()
                
                self.audit_records.append({
                    'table': 'batches',
                    'action': action,
                    'key': batch_data['batch_code'],
                    'id': str(batch.id) if hasattr(batch, 'id') else 'new',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                self.stats['batches'] += 1
                
            except Exception as e:
                self._handle_anomaly('batches', batch_data, str(e))
    
    def migrate_sales_orders(self) -> None:
        """Migrate sales order data."""
        print("Migrating sales orders...")
        
        # This would typically read from legacy files
        # For now, we'll skip as it's not in the sample data
        pass
    
    def migrate_invoices(self) -> None:
        """Migrate invoice data."""
        print("Migrating invoices...")
        
        invoices_data = create_sample_invoice_data()
        
        for invoice_data in invoices_data:
            try:
                # Resolve customer_id
                customer = self.db.execute(
                    select(Customer).where(Customer.code == invoice_data['customer_id'])
                ).scalar_one_or_none()
                
                if not customer:
                    raise ValueError(f"Customer {invoice_data['customer_id']} not found")
                
                invoice_data['customer_id'] = customer.id
                
                existing = self.db.execute(
                    select(Invoice).where(Invoice.invoice_number == invoice_data['invoice_number'])
                ).scalar_one_or_none()
                
                if existing:
                    for key, value in invoice_data.items():
                        if key != 'invoice_number':
                            setattr(existing, key, value)
                    invoice = existing
                    action = "updated"
                else:
                    invoice = Invoice(**invoice_data)
                    self.db.add(invoice)
                    action = "created"
                
                if not self.dry_run:
                    self.db.flush()
                
                self.audit_records.append({
                    'table': 'invoices',
                    'action': action,
                    'key': invoice_data['invoice_number'],
                    'id': str(invoice.id) if hasattr(invoice, 'id') else 'new',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                self.stats['invoices'] += 1
                
            except Exception as e:
                self._handle_anomaly('invoices', invoice_data, str(e))
    
    def _handle_anomaly(self, table: str, data: Dict[str, Any], error: str) -> None:
        """Handle migration anomalies."""
        anomaly = {
            'table': table,
            'data': data,
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.anomalies.append(anomaly)
        self.stats['anomalies'] += 1
        
        if not self.allow_anomalies:
            raise Exception(f"Migration failed due to anomaly in {table}: {error}")
        
        print(f"WARNING: Anomaly in {table}: {error}")
    
    def write_audit_report(self, output_dir: Path) -> None:
        """Write audit report and anomaly files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write main audit CSV
        audit_csv = output_dir / "audit.csv"
        with audit_csv.open("w", newline="", encoding="utf-8") as f:
            if self.audit_records:
                writer = csv.DictWriter(f, fieldnames=self.audit_records[0].keys())
                writer.writeheader()
                writer.writerows(self.audit_records)
        
        print(f"Wrote audit report to {audit_csv}")
        
        # Write anomaly files
        if self.anomalies:
            anomalies_dir = output_dir / "anomalies"
            anomalies_dir.mkdir(exist_ok=True)
            
            for i, anomaly in enumerate(self.anomalies):
                anomaly_file = anomalies_dir / f"anomaly_{i+1:03d}.csv"
                with anomaly_file.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=['table', 'error', 'timestamp'])
                    writer.writeheader()
                    writer.writerow({
                        'table': anomaly['table'],
                        'error': anomaly['error'],
                        'timestamp': anomaly['timestamp']
                    })
            
            print(f"Wrote {len(self.anomalies)} anomaly files to {anomalies_dir}")


def main():
    ap = argparse.ArgumentParser(description="Migrate legacy data to modern database")
    ap.add_argument("--dry-run", action="store_true", help="Don't write to database, just report")
    ap.add_argument("--allow-anomalies", action="store_true", help="Continue migration despite anomalies")
    ap.add_argument("--output", default="out", help="Output directory for audit reports")
    
    args = ap.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    create_tables()
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        migrator = LegacyMigrator(db, dry_run=args.dry_run, allow_anomalies=args.allow_anomalies)
        stats = migrator.migrate_all()
        
        # Write audit reports
        migrator.write_audit_report(output_dir)
        
        # Print summary
        print("\nMigration Summary:")
        print("=" * 50)
        for table, count in stats.items():
            if count > 0:
                print(f"{table:20}: {count:4d} records")
        
        if args.dry_run:
            print("\nThis was a DRY RUN - no data was written to the database")
        else:
            print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()