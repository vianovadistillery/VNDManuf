"""Seed script to populate units table with standard metric units."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_session
from app.adapters.db.models import Unit

# Define units to seed
# Units include: ton, kg, k, kL, L, mL, density (kg/L), ABV
UNITS_DATA = [
    # Mass units - Canonical storage is in kg
    {
        "code": "TON",
        "name": "Metric Ton",
        "symbol": "t",
        "unit_type": "MASS",
        "description": "Metric ton (1000 kg). Base unit for mass storage is kg. All mass quantities are stored in kg in the database.",
        "conversion_formula": "to_kg(ton) = ton × 1000; to_ton(kg) = kg ÷ 1000; Example: 2.5 ton = 2500 kg; 1500 kg = 1.5 ton; Use for bulk mass measurements.",
    },
    {
        "code": "KG",
        "name": "Kilogram",
        "symbol": "kg",
        "unit_type": "MASS",
        "description": "Kilogram - base metric unit of mass (canonical storage unit). All mass quantities are stored in kg in the database. This is the standard unit for inventory tracking.",
        "conversion_formula": "kg = kg (base unit, no conversion needed for storage). Display conversions: kg → ton = kg ÷ 1000; kg → g = kg × 1000; kg → mg = kg × 1,000,000; kg → k (kilo) = kg × 1 (identical).",
    },
    {
        "code": "K",
        "name": "Kilo (shorthand)",
        "symbol": "k",
        "unit_type": "MASS",
        "description": "Kilo - shorthand for kilogram (same as KG). 1 k = 1 kg = 1000 g. Used interchangeably with kg in forms and displays.",
        "conversion_formula": "k = kg (identical to KG). to_kg(k) = k × 1; to_k(kg) = kg × 1; Example: 5 k = 5 kg = 5000 g; 3.2 k = 3.2 kg. No conversion needed - just display preference.",
    },
    {
        "code": "G",
        "name": "Gram",
        "symbol": "g",
        "unit_type": "MASS",
        "description": "Gram - metric unit of mass. 1 kg = 1000 g. For storage convert to kg: g ÷ 1000 = kg. Use for small quantities.",
        "conversion_formula": "to_kg(g) = g ÷ 1000; to_g(kg) = kg × 1000; Example: 2500 g = 2.5 kg; 3.5 kg = 3500 g; 500 g = 0.5 kg.",
    },
    {
        "code": "MG",
        "name": "Milligram",
        "symbol": "mg",
        "unit_type": "MASS",
        "description": "Milligram - metric unit of mass. 1 kg = 1,000,000 mg. For storage convert to kg: mg ÷ 1,000,000 = kg. Use for very small quantities.",
        "conversion_formula": "to_kg(mg) = mg ÷ 1,000,000; to_mg(kg) = kg × 1,000,000; Example: 500000 mg = 0.5 kg; 0.001 kg = 1000 mg; 2500 mg = 0.0025 kg.",
    },
    # Volume units - Base unit is Liter (L)
    {
        "code": "KL",
        "name": "Kiloliter",
        "symbol": "kL",
        "unit_type": "VOLUME",
        "description": "Kiloliter - 1000 liters. 1 kL = 1000 L. For mass conversion: use density. mass_kg = volume_kL × 1000 × density_kg_per_L. Use for bulk volume measurements.",
        "conversion_formula": "to_L(kL) = kL × 1000; to_kL(L) = L ÷ 1000; to_kg(kL, density_kg_per_L) = kL × 1000 × density_kg_per_L; to_kL(kg, density_kg_per_L) = kg ÷ (1000 × density_kg_per_L); Example: 2.5 kL = 2500 L; 5000 L = 5 kL; 2 kL × 0.8 kg/L = 1600 kg.",
    },
    {
        "code": "L",
        "name": "Liter",
        "symbol": "L",
        "unit_type": "VOLUME",
        "description": "Liter - base metric unit of volume. For mass conversion: use product density. mass_kg = volume_L × density_kg_per_L. Standard unit for liquid volume measurements.",
        "conversion_formula": "L = L (base volume unit). Mass conversion: to_kg(L, density_kg_per_L) = L × density_kg_per_L; to_L(kg, density_kg_per_L) = kg ÷ density_kg_per_L; Example: 100 L × 0.8 kg/L = 80 kg; 200 kg ÷ 1.2 kg/L = 166.67 L; 50 L × 1.0 kg/L = 50 kg.",
    },
    {
        "code": "ML",
        "name": "Milliliter",
        "symbol": "mL",
        "unit_type": "VOLUME",
        "description": "Milliliter - metric unit of volume. 1 L = 1000 mL. For mass conversion: mass_kg = volume_mL × density_kg_per_L ÷ 1000. Use for small volume measurements.",
        "conversion_formula": "to_L(mL) = mL ÷ 1000; to_mL(L) = L × 1000; to_kg(mL, density_kg_per_L) = mL × density_kg_per_L ÷ 1000; to_mL(kg, density_kg_per_L) = kg × 1000 ÷ density_kg_per_L; Example: 5000 mL = 5 L; 250 mL × 0.9 kg/L ÷ 1000 = 0.225 kg; 100 mL = 0.1 L.",
    },
    # Density units - kg/L is the canonical density unit
    {
        "code": "DENSITY",
        "name": "Density (Kilograms per Liter)",
        "symbol": "kg/L",
        "unit_type": "DENSITY",
        "description": "Density in kilograms per liter (canonical density unit). Used for converting between mass and volume. Store on product records for L ⇄ kg conversions. Essential for alcohol and liquid products.",
        "conversion_formula": "density_kg_per_L = mass_kg ÷ volume_L; volume_L = mass_kg ÷ density_kg_per_L; mass_kg = volume_L × density_kg_per_L; Example: 100 kg ÷ 125 L = 0.8 kg/L; 200 L × 1.2 kg/L = 240 kg; 150 kg ÷ 0.9 kg/L = 166.67 L; Pure water = 1.0 kg/L; Ethanol = 0.79 kg/L.",
    },
    {
        "code": "KG_L",
        "name": "Kilograms per Liter",
        "symbol": "kg/L",
        "unit_type": "DENSITY",
        "description": "Density in kilograms per liter (same as DENSITY, alternative code). Used for converting between mass and volume. Store on product records for L ⇄ kg conversions.",
        "conversion_formula": "density_kg_per_L = mass_kg ÷ volume_L; volume_L = mass_kg ÷ density_kg_per_L; mass_kg = volume_L × density_kg_per_L; Example: 100 kg ÷ 125 L = 0.8 kg/L; 200 L × 1.2 kg/L = 240 kg.",
    },
    {
        "code": "G_CM3",
        "name": "Grams per Cubic Centimeter",
        "symbol": "g/cm³",
        "unit_type": "DENSITY",
        "description": "Density in grams per cubic centimeter (numerically equivalent to kg/L: 1 g/cm³ = 1 kg/L). Alternative density unit.",
        "conversion_formula": "to_kg_per_L(g_per_cm3) = g_per_cm3 (same value); to_g_per_cm3(kg_per_L) = kg_per_L (same value); Example: 0.8 g/cm³ = 0.8 kg/L; 1.2 kg/L = 1.2 g/cm³.",
    },
    {
        "code": "KG_M3",
        "name": "Kilograms per Cubic Meter",
        "symbol": "kg/m³",
        "unit_type": "DENSITY",
        "description": "Density in kilograms per cubic meter. 1 kg/L = 1000 kg/m³. Convert to kg/L for storage: kg/m³ ÷ 1000 = kg/L.",
        "conversion_formula": "to_kg_per_L(kg_per_m3) = kg_per_m3 ÷ 1000; to_kg_per_m3(kg_per_L) = kg_per_L × 1000; Example: 800 kg/m³ = 0.8 kg/L; 1.2 kg/L = 1200 kg/m³.",
    },
    # ABV - Alcohol by Volume percentage
    {
        "code": "ABV",
        "name": "ABV - Alcohol by Volume",
        "symbol": "ABV %",
        "unit_type": "CONCENTRATION",
        "description": "Alcohol by Volume - percentage volume/volume. Stored as % (v/v) on products. Used to calculate alcohol quantity from total volume or mass using density. Essential for excise calculations.",
        "conversion_formula": "alcohol_volume_L = total_volume_L × (ABV_percent ÷ 100); alcohol_mass_kg = alcohol_volume_L × density_kg_per_L; ABV_from_mass = (alcohol_mass_kg ÷ density_kg_per_L) ÷ total_volume_L × 100; Example: 100 L × 40% ABV = 40 L alcohol; 40 L × 0.79 kg/L = 31.6 kg alcohol; For excise: excise_tax = alcohol_volume_L × excise_rate_per_L_ABV.",
    },
    {
        "code": "ABV_VOL_VOL",
        "name": "ABV Volume/Volume (Legacy)",
        "symbol": "ABV %",
        "unit_type": "CONCENTRATION",
        "description": "Alcohol by Volume - percentage volume/volume (legacy code, use ABV instead). Maintained for backward compatibility.",
        "conversion_formula": "ABV % = (volume_alcohol_L ÷ volume_total_L) × 100; Same as ABV unit; Example: 40 L alcohol ÷ 100 L total × 100 = 40% ABV.",
    },
    # Additional concentration units
    {
        "code": "WT_PCT",
        "name": "Weight Percentage",
        "symbol": "wt%",
        "unit_type": "CONCENTRATION",
        "description": "Weight percentage concentration - mass of component per 100 mass units of total. Used for solid concentrations.",
        "conversion_formula": "wt_percent = (mass_component_kg ÷ mass_total_kg) × 100; mass_component_kg = mass_total_kg × (wt_percent ÷ 100); Example: 25 kg ÷ 100 kg × 100 = 25 wt%; 100 kg × 0.15 = 15 kg component.",
    },
    {
        "code": "SOLIDS_PCT",
        "name": "Solids Percentage",
        "symbol": "solids%",
        "unit_type": "CONCENTRATION",
        "description": "Solids percentage concentration - mass of solids per 100 mass units of total. Used in paint and coating formulations.",
        "conversion_formula": "solids_percent = (mass_solids_kg ÷ mass_total_kg) × 100; mass_solids_kg = mass_total_kg × (solids_percent ÷ 100); Example: 40 kg solids ÷ 100 kg total × 100 = 40% solids.",
    },
    # Additional units for completeness
    {
        "code": "EA",
        "name": "Each",
        "symbol": "ea",
        "unit_type": "COUNT",
        "description": "Each - count unit (1 each = 1). No conversion factor. Used for discrete items counted individually.",
        "conversion_formula": "ea = ea (no conversion). Used for discrete items counted individually. Example: 5 ea = 5 items.",
    },
    {
        "code": "PK",
        "name": "Pack",
        "symbol": "pk",
        "unit_type": "COUNT",
        "description": "Pack - count unit. Conversion factor depends on product-specific pack_conversion table.",
        "conversion_formula": "pk = pk (conversion factor from pack_conversion table). Look up product-specific conversion: pk_to_ea = pack_conversion_factor; ea_to_pk = 1 ÷ pack_conversion_factor.",
    },
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
        existing = db.execute(
            select(Unit).where(Unit.code == code)
        ).scalar_one_or_none()

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

    print("\nUnits seeding complete:")
    print(f"  Created: {created_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total processed: {len(UNITS_DATA)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed units table with standard units")
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing units"
    )
    args = parser.parse_args()

    db = get_session()
    try:
        seed_units(db, overwrite=args.overwrite)
    finally:
        db.close()
