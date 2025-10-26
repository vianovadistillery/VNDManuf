#!/usr/bin/env python3
"""Check QB data import results"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.adapters.db import get_db
from app.adapters.db.qb_models import RawMaterial, RawMaterialGroup

db = next(get_db())

print(f"Raw Materials: {db.query(RawMaterial).count()}")
print(f"Groups: {db.query(RawMaterialGroup).count()}")
print("\nSample raw materials:")
for rm in db.query(RawMaterial).limit(5):
    print(f"  {rm.code}: {rm.desc1} (Active: {rm.active_flag}, SOH: {rm.soh})")

print("\nGroups:")
for grp in db.query(RawMaterialGroup).all():
    print(f"  {grp.code}: {grp.name}")

db.close()

