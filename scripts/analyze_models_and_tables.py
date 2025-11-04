#!/usr/bin/env python3
"""
Analyze models in code vs tables in database.
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

print(f"Analyzing database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print(f"\nFound {len(tables)} tables in database:")
for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = cursor.fetchall()
    pk_cols = [c[1] for c in cols if c[5] == 1]
    print(f"  {table}: {len(cols)} columns, PK: {pk_cols if pk_cols else 'NONE'}")

# Check for Contact vs Customer/Supplier
if "contacts" in tables:
    print("\n[INFO] 'contacts' table exists")
if "customers" in tables:
    print("[INFO] 'customers' table exists")
if "suppliers" in tables:
    print("[INFO] 'suppliers' table exists")

conn.close()

# Now check models
print("\nChecking models...")
from app.adapters.db import models

model_classes = [
    name
    for name in dir(models)
    if name[0].isupper() and hasattr(getattr(models, name), "__tablename__")
]
print(f"\nFound {len(model_classes)} model classes:")
for cls_name in sorted(model_classes):
    cls = getattr(models, cls_name)
    print(f"  {cls_name}: {cls.__tablename__}")

print("\n[OK] Analysis complete")
