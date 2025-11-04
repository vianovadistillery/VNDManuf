#!/usr/bin/env python3
"""
Analyze and document Contact vs Customer/Supplier model conflict.

The database has:
- contacts table (unified model)
- customers table (separate)
- suppliers table (separate)

We need to decide on the approach and create a migration plan.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect, text

from app.adapters.db.session import get_engine

engine = get_engine()
inspector = inspect(engine)

# Check what tables exist
tables = inspector.get_table_names()
has_contacts = "contacts" in tables
has_customers = "customers" in tables
has_suppliers = "suppliers" in tables

print("=" * 60)
print("Contact Model Analysis")
print("=" * 60)
print(f"contacts table exists: {has_contacts}")
print(f"customers table exists: {has_customers}")
print(f"suppliers table exists: {has_suppliers}")

# Check foreign key usage
print("\nForeign Key Analysis:")
print("-" * 60)

fk_usage = {
    "contacts": 0,
    "customers": 0,
    "suppliers": 0,
}

for table_name in tables:
    for fk in inspector.get_foreign_keys(table_name):
        referred = fk.get("referred_table", "")
        if referred == "contacts":
            fk_usage["contacts"] += 1
            print(f"  {table_name} -> contacts")
        elif referred == "customers":
            fk_usage["customers"] += 1
            print(f"  {table_name} -> customers")
        elif referred == "suppliers":
            fk_usage["suppliers"] += 1
            print(f"  {table_name} -> suppliers")

print("\nFK Usage Summary:")
print(f"  contacts: {fk_usage['contacts']} references")
print(f"  customers: {fk_usage['customers']} references")
print(f"  suppliers: {fk_usage['suppliers']} references")

# Recommendation
print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("=" * 60)
if fk_usage["customers"] > 0 or fk_usage["suppliers"] > 0:
    print("Keep separate Customer and Supplier models for now.")
    print("Contacts table exists but is not being used by FKs.")
    print("Migration strategy: Gradually migrate FKs to contacts over time.")
else:
    print("Contacts table can be used as primary model.")
    print("Customer and Supplier can be deprecated.")

# Check data
print("\n" + "=" * 60)
print("Data Counts:")
print("=" * 60)
conn = engine.connect()
try:
    if has_contacts:
        result = conn.execute(text("SELECT COUNT(*) FROM contacts"))
        print(f"contacts: {result.scalar()} rows")
    if has_customers:
        result = conn.execute(text("SELECT COUNT(*) FROM customers"))
        print(f"customers: {result.scalar()} rows")
    if has_suppliers:
        result = conn.execute(text("SELECT COUNT(*) FROM suppliers"))
        print(f"suppliers: {result.scalar()} rows")
finally:
    conn.close()

print("\n[OK] Analysis complete.")
