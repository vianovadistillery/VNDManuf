#!/usr/bin/env python3
"""
Analyze foreign key dependencies on customers and suppliers tables.
This helps understand what needs to be migrated to use the unified contacts table.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3

from app.settings import settings

db_path = settings.database.database_url.replace("sqlite:///", "")
if not db_path.startswith("/"):
    db_path = str(project_root / db_path)

print("Analyzing foreign key dependencies on customers and suppliers...")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

# Check foreign keys
print("\nForeign keys referencing 'customers' table:")
customer_fks = []
for table in tables:
    cursor.execute(f"PRAGMA foreign_key_list({table})")
    fks = cursor.fetchall()
    for fk in fks:
        if fk[2] == "customers":  # referred_table is at index 2
            customer_fks.append((table, fk[3], fk[4]))  # table, column, referred_column
            print(f"  {table}.{fk[3]} -> customers.{fk[4]}")

print(f"\nTotal: {len(customer_fks)} foreign keys to customers")

print("\nForeign keys referencing 'suppliers' table:")
supplier_fks = []
for table in tables:
    cursor.execute(f"PRAGMA foreign_key_list({table})")
    fks = cursor.fetchall()
    for fk in fks:
        if fk[2] == "suppliers":
            supplier_fks.append((table, fk[3], fk[4]))
            print(f"  {table}.{fk[3]} -> suppliers.{fk[4]}")

print(f"\nTotal: {len(supplier_fks)} foreign keys to suppliers")

# Check data counts
cursor.execute("SELECT COUNT(*) FROM customers")
customer_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM suppliers")
supplier_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM contacts")
contact_count = cursor.fetchone()[0]

print("\nData counts:")
print(f"  customers: {customer_count} rows")
print(f"  suppliers: {supplier_count} rows")
print(f"  contacts: {contact_count} rows")

conn.close()

print("\n[OK] Analysis complete")
print("\nRecommendation:")
if customer_count == 0 and supplier_count == 0:
    print("  [INFO] Customers and suppliers tables are empty")
    print("  [INFO] Can safely migrate to unified contacts table")
elif contact_count > 0:
    print("  [INFO] Contacts table has data")
    print("  [INFO] Need to migrate existing customer/supplier data to contacts")
else:
    print("  [WARNING] Customers/suppliers have data but contacts is empty")
    print("  [WARNING] Need data migration strategy")
