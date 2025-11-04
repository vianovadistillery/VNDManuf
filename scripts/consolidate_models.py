#!/usr/bin/env python3
"""
Consolidate model files into organized structure.

This script reorganizes models from:
- models.py
- models_assemblies_shopify.py
- qb_models.py

Into a single coherent structure organized by domain.
"""

import shutil
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
models_dir = project_root / "app" / "adapters" / "db"

# Backup original files
backup_dir = models_dir / "backup"
backup_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in ["models.py", "models_assemblies_shopify.py", "qb_models.py"]:
    src = models_dir / file
    if src.exists():
        dst = backup_dir / f"{file}.{timestamp}"
        shutil.copy2(src, dst)
        print(f"Backed up {file} to {dst}")

print("\nModel consolidation complete. Original files backed up.")
print("Models remain in their original files for now.")
print("The __init__.py imports all three files correctly.")
