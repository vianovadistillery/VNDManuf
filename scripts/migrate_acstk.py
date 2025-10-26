"""Migration script for legacy acstk file data.

This script imports all data from the legacy QuickBASIC acstk file,
preserving everything in both the normalized modern schema and
the legacy preservation table.
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.adapters.legacy_acstk import AcstkParser, AcstkRecord
from app.adapters.db.session import get_session
from app.adapters.db.models import (
    Product, InventoryLot, InventoryTxn, PriceListItem, PriceList,
    PackUnit, PackConversion, LegacyAcstkData, Supplier
)
from sqlalchemy import select
from decimal import Decimal


def get_db_session():
    """Get database session."""
    return get_session()


def create_legacy_legacy_impl(session, record: AcstkRecord, product: Product):
    """Create LegacyAcstkData record to preserve all legacy fields."""
    legacy_data = LegacyAcstkData(
        product_id=product.id,
        legacy_no=record.no,
        
        # Product Description
        legacy_search=record.search,
        ean13=Decimal(str(record.ean13)) if record.ean13 else None,
        desc1=record.desc1,
        desc2=record.desc2,
        legacy_suplr=record.suplr,
        size=record.size,
        legacy_unit=record.unit,
        pack=record.pack,
        dgflag=record.dgflag,
        form=record.form,
        pkge=record.pkge,
        label=record.label,
        manu=record.manu,
        legacy_active=record.active,
        
        # Financial
        taxinc=record.taxinc,
        salestaxcde=record.salestaxcde,
        purcost=Decimal(str(record.purcost)) if record.purcost else None,
        purtax=Decimal(str(record.purtax)) if record.purtax else None,
        wholesalecost=Decimal(str(record.wholesalecost)) if record.wholesalecost else None,
        disccdeone=record.disccdeone,
        disccdetwo=record.disccdetwo,
        
        # Price Codes
        wholesalecde=record.wholesalecde,
        retailcde=record.retailcde,
        countercde=record.countercde,
        tradecde=record.tradecde,
        contractcde=record.contractcde,
        industrialcde=record.industrialcde,
        distributorcde=record.distributorcde,
        
        # Prices
        retail=Decimal(str(record.retail)) if record.retail else None,
        counter=Decimal(str(record.counter)) if record.counter else None,
        trade=Decimal(str(record.trade)) if record.trade else None,
        contract=Decimal(str(record.contract)) if record.contract else None,
        industrial=Decimal(str(record.industrial)) if record.industrial else None,
        distributor=Decimal(str(record.distributor)) if record.distributor else None,
        
        # Standard Cost References
        suplr4stdcost=record.suplr4stdcost,
        search4stdcost=record.search4stdcost,
        
        # Stock Holding
        cogs=Decimal(str(record.cogs)) if record.cogs else None,
        gpc=Decimal(str(record.gpc)) if record.gpc else None,
        rmc=Decimal(str(record.rmc)) if record.rmc else None,
        gpr=Decimal(str(record.gpr)) if record.gpr else None,
        soh=record.soh,
        sohv=Decimal(str(record.sohv)) if record.sohv else None,
        sip=record.sip,
        soo=record.soo,
        sold=record.sold,
        legacy_date=record.date,
        
        # Additional
        bulk=Decimal(str(record.bulk)) if record.bulk else None,
        lid=record.lid,
        pbox=record.pbox,
        boxlbl=record.boxlbl,
        notes=f"Migrated from legacy acstk file"
    )
    
    session.add(legacy_data)
    return legacy_data


def find_or_create_supplier(session, supplier_code: str) -> Optional[str]:
    """Find or create supplier and return ID."""
    if not supplier_code or supplier_code.strip() == "":
        return None
    
    # Try to find existing supplier
    stmt = select(Supplier).where(Supplier.code == supplier_code)
    supplier = session.execute(stmt).scalar_one_or_none()
    
    if not supplier:
        # Create supplier
        supplier = Supplier(
            code=supplier_code,
            name=f"Legacy Supplier {supplier_code}",
            is_active=True
        )
        session.add(supplier)
        session.flush()
    
    return supplier.id


def create_price_list_items(session, record: AcstkRecord, product: Product):
    """Create price list items for all pricing tiers."""
    
    # Create different price lists
    price_lists = {}
    for tier in ['retail', 'counter', 'trade', 'contract', 'industrial', 'distributor']:
        tier_code = tier.upper()
        price_value = getattr(record, tier, None)
        
        if price_value and price_value > 0:
            # Create or get price list
            if tier_code not in price_lists:
                stmt = select(PriceList).where(PriceList.code == tier_code)
                price_list = session.execute(stmt).scalar_one_or_none()
                
                if not price_list:
                    price_list = PriceList(
                        code=tier_code,
                        name=f"{tier.title()} Price List",
                        is_active=True
                    )
                    session.add(price_list)
                    session.flush()
                
                price_lists[tier_code] = price_list
            
            # Create price list item
            price_list_item = PriceListItem(
                price_list_id=price_lists[tier_code].id,
                product_id=product.id,
                unit_price_ex_tax=Decimal(str(price_value)),
                is_active=True
            )
            session.add(price_list_item)


def create_inventory_lots(session, record: AcstkRecord, product: Product):
    """Create inventory lots from legacy stock data."""
    if not record.soh or record.soh <= 0:
        return
    
    # Create a single lot for the legacy stock
    lot_code = f"LEGACY-{record.search}"
    
    # Get unit cost from purcost
    unit_cost = Decimal(str(record.purcost)) if record.purcost else None
    
    lot = InventoryLot(
        product_id=product.id,
        lot_code=lot_code,
        quantity_kg=Decimal(str(record.soh)),  # Assume 'kg' for now
        unit_cost=unit_cost,
        is_active=True
    )
    
    session.add(lot)
    session.flush()
    
    # Create initial transaction
    if record.date and len(record.date) >= 8:
        try:
            from datetime import datetime
            received_date = datetime.strptime(record.date, "%Y%m%d")
        except:
            received_date = None
    else:
        received_date = None
    
    txn = InventoryTxn(
        lot_id=lot.id,
        transaction_type="RECEIPT",
        quantity_kg=Decimal(str(record.soh)),
        unit_cost=unit_cost,
        reference_type="LEGACY_MIGRATION",
        notes=f"Migrated from legacy stock: {record.search}"
    )
    
    if received_date:
        txn.created_at = received_date
    
    session.add(txn)
    
    return lot


def create_pack_units_and_conversions(session, record: AcstkRecord, product: Product):
    """Create pack units and conversions."""
    if not record.unit or record.unit.strip() == "":
        return
    
    # Create or get pack unit
    stmt = select(PackUnit).where(PackUnit.code == record.unit)
    pack_unit = session.execute(stmt).scalar_one_or_none()
    
    if not pack_unit:
        pack_unit = PackUnit(
            code=record.unit,
            name=f"{record.unit}",
            description=f"Legacy unit {record.unit}",
            is_active=True
        )
        session.add(pack_unit)
        session.flush()
    
    # Create conversion from kg to this unit
    # This is a placeholder - actual conversion depends on product
    conversion = PackConversion(
        product_id=product.id,
        from_unit_id=pack_unit.id,  # Assuming a 'kg' unit exists
        to_unit_id=pack_unit.id,
        conversion_factor=Decimal("1.0"),
        is_active=True
    )
    session.add(conversion)


def migrate_acstk_file(filepath: str):
    """Main migration function."""
    print(f"Starting migration from {filepath}")
    
    # Parse legacy file
    records = AcstkParser.parse_file(filepath)
    print(f"Parsed {len(records)} records from legacy file")
    
    # Process each record
    db = get_db_session()
    
    try:
        for i, record in enumerate(records, 1):
            try:
                print(f"Processing record {i}/{len(records)}: {record.search}")
                
                # Check if product already exists
                stmt = select(Product).where(Product.sku == record.search)
                product = db.execute(stmt).scalar_one_or_none()
                
                if not product:
                    # Create product
                    product = Product(
                        sku=record.search,
                        name=record.product_name,
                        description=f"Size: {record.size}, Form: {record.form}, Unit: {record.unit}",
                        is_active=record.is_active
                    )
                    db.add(product)
                    db.flush()
                    print(f"  Created product: {product.sku}")
                else:
                    print(f"  Product exists: {product.sku}")
                
                # Create legacy data preservation record
                create_legacy_legacy_impl(db, record, product)
                
                # Create price list items
                create_price_list_items(db, record, product)
                
                # Create inventory lot
                create_inventory_lots(db, record, product)
                
                # Create pack units
                create_pack_units_and_conversions(db, record, product)
                
                # Commit every 10 records
                if i % 10 == 0:
                    db.commit()
                    print(f"  Committed {i} records")
            
            except Exception as e:
                print(f"  Error processing record {i}: {e}")
                import traceback
                traceback.print_exc()
                db.rollback()
                continue
        
        # Final commit
        db.commit()
        print(f"Migration completed successfully!")
    
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_acstk.py <path_to_acstk_file>")
        print("Example: python migrate_acstk.py legacy_data/acstk.acf")
        sys.exit(1)
    
    filepath = sys.argv[1]
    migrate_acstk_file(filepath)

