"""Seed script to populate units table with standard metric units."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.adapters.db import get_session
from app.adapters.db.models import Unit
from sqlalchemy import select

# Define units to seed
UNITS_DATA = [
    # Mass units
    {"code": "G", "name": "Gram", "symbol": "g", "unit_type": "MASS", "description": "Gram - metric unit of mass"},
    {"code": "KG", "name": "Kilogram", "symbol": "kg", "unit_type": "MASS", "description": "Kilogram - base metric unit of mass (canonical storage unit)"},
    {"code": "TON", "name": "Metric Ton", "symbol": "t", "unit_type": "MASS", "description": "Metric ton (1000 kg)"},
    
    # Volume units
    {"code": "ML", "name": "Milliliter", "symbol": "mL", "unit_type": "VOLUME", "description": "Milliliter - metric unit of volume"},
    {"code": "L", "name": "Liter", "symbol": "L", "unit_type": "VOLUME", "description": "Liter - metric unit of volume"},
    
    # Density units
    {"code": "G_CM3", "name": "Grams per Cubic Centimeter", "symbol": "g/cm³", "unit_type": "DENSITY", "description": "Density in grams per cubic centimeter (equivalent to kg/L)"},
    {"code": "KG_L", "name": "Kilograms per Liter", "symbol": "kg/L", "unit_type": "DENSITY", "description": "Density in kilograms per liter"},
    {"code": "KG_M3", "name": "Kilograms per Cubic Meter", "symbol": "kg/m³", "unit_type": "DENSITY", "description": "Density in kilograms per cubic meter"},
    
    # Concentration units
    {"code": "ABV_VOL_VOL", "name": "ABV Volume/Volume", "symbol": "ABV %", "unit_type": "CONCENTRATION", "description": "Alcohol by Volume - percentage volume/volume"},
    {"code": "WT_PCT", "name": "Weight Percentage", "symbol": "wt%", "unit_type": "CONCENTRATION", "description": "Weight percentage concentration"},
    {"code": "SOLIDS_PCT", "name": "Solids Percentage", "symbol": "solids%", "unit_type": "CONCENTRATION", "description": "Solids percentage concentration"},
    
    # Additional units for completeness
    {"code": "MG", "name": "Milligram", "symbol": "mg", "unit_type": "MASS", "description": "Milligram - metric unit of mass"},
    {"code": "EA", "name": "Each", "symbol": "ea", "unit_type": "COUNT", "description": "Each - count unit"},
    {"code": "PK", "name": "Pack", "symbol": "pk", "unit_type": "COUNT", "description": "Pack - count unit"},
]


def seed_units(db: Session, overwrite: bool = False):
    """Seed units table with standard units."""
    print("Seeding units table...")
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for unit_data in UNITS_DATA:
        code = unit_data["code"]
        
        # Check if unit already exists
        existing = db.execute(select(Unit).where(Unit.code == code)).scalar_one_or_none()
        
        if existing:
            if overwrite:
                # Update existing unit
                for key, value in unit_data.items():
                    setattr(existing, key, value)
                updated_count += 1
                print(f"  Updated: {code}")
            else:
                skipped_count += 1
                print(f"  Skipped (exists): {code}")
        else:
            # Create new unit
            unit = Unit(**unit_data)
            db.add(unit)
            created_count += 1
            print(f"  Created: {code}")
    
    db.commit()
    
    print(f"\nUnits seeding complete:")
    print(f"  Created: {created_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total processed: {len(UNITS_DATA)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed units table with standard units")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing units")
    args = parser.parse_args()
    
    db = get_session()
    try:
        seed_units(db, overwrite=args.overwrite)
    finally:
        db.close()

