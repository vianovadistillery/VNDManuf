#!/usr/bin/env python3
"""Extract products table schema from complete_schema.json"""

import json
from pathlib import Path

project_root = Path(__file__).parent.parent
schema_path = project_root / "docs" / "snapshot" / "complete_schema.json"

with open(schema_path) as f:
    data = json.load(f)

products = data["tables"]["products"]
print(f"Primary keys: {products['primary_keys']}")
print(f"Total columns: {len(products['columns'])}")
print("\nColumns:")
for col in products["columns"]:
    print(f"  {col['name']:40} {col['type']:20} nullable={col['nullable']}")
