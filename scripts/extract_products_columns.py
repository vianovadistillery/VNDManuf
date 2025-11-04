#!/usr/bin/env python3
"""Extract products table columns for model generation."""

import json
from pathlib import Path

project_root = Path(__file__).parent.parent
schema_path = project_root / "docs" / "snapshot" / "complete_schema.json"

with open(schema_path, "r", encoding="utf-8") as f:
    schema = json.load(f)

products = schema["tables"]["products"]
print(f"Primary Keys: {products['primary_keys']}")
print(f"Total Columns: {len(products['columns'])}")
print("\nColumns:")
for i, col in enumerate(products["columns"], 1):
    print(f"{i:3d}. {col['name']:40s} {col['type']:20s} nullable={col['nullable']}")
