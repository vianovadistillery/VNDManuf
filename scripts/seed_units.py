#!/usr/bin/env python3
"""Seed the Units table with standard units of measure and conversion formulas."""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import Unit


def seed_units(db: Session, dry_run: bool = False) -> None:
    """Seed the Units table with standard units."""

    units_data = [
        # Mass Units
        {
            "code": "TON",
            "name": "Metric Ton",
            "symbol": "t",
            "unit_type": "MASS",
            "description": "Metric ton (1,000 kg). Base unit for large mass measurements.",
            "conversion_formula": "To kg: qty_ton * 1000 = qty_kg\nFrom kg: qty_kg / 1000 = qty_ton",
            "is_active": True,
        },
        {
            "code": "KG",
            "name": "Kilogram",
            "symbol": "kg",
            "unit_type": "MASS",
            "description": "Kilogram - canonical storage unit for mass. Base unit for mass conversions.",
            "conversion_formula": "To g: qty_kg * 1000 = qty_g\nTo ton: qty_kg / 1000 = qty_ton\nTo mg: qty_kg * 1,000,000 = qty_mg",
            "is_active": True,
        },
        {
            "code": "K",
            "name": "Kilogram (abbreviated)",
            "symbol": "k",
            "unit_type": "MASS",
            "description": "Kilogram abbreviated as 'k'. Equivalent to KG.",
            "conversion_formula": "Same as KG: To g: qty_k * 1000 = qty_g\nTo ton: qty_k / 1000 = qty_ton",
            "is_active": True,
        },
        {
            "code": "G",
            "name": "Gram",
            "symbol": "g",
            "unit_type": "MASS",
            "description": "Gram - 1/1000 of a kilogram.",
            "conversion_formula": "To kg: qty_g / 1000 = qty_kg\nTo mg: qty_g * 1000 = qty_mg",
            "is_active": True,
        },
        {
            "code": "MG",
            "name": "Milligram",
            "symbol": "mg",
            "unit_type": "MASS",
            "description": "Milligram - 1/1,000,000 of a kilogram.",
            "conversion_formula": "To kg: qty_mg / 1,000,000 = qty_kg\nTo g: qty_mg / 1000 = qty_g",
            "is_active": True,
        },
        # Volume Units
        {
            "code": "KL",
            "name": "Kiloliter",
            "symbol": "kL",
            "unit_type": "VOLUME",
            "description": "Kiloliter (1,000 L). Base unit for large volume measurements.",
            "conversion_formula": "To L: qty_kl * 1000 = qty_l\nTo mL: qty_kl * 1,000,000 = qty_ml",
            "is_active": True,
        },
        {
            "code": "L",
            "name": "Liter",
            "symbol": "L",
            "unit_type": "VOLUME",
            "description": "Liter - base unit for volume measurements.",
            "conversion_formula": "To mL: qty_l * 1000 = qty_ml\nTo kL: qty_l / 1000 = qty_kl\nTo kg (requires density): qty_l * density_kg_per_l = qty_kg",
            "is_active": True,
        },
        {
            "code": "ML",
            "name": "Milliliter",
            "symbol": "mL",
            "unit_type": "VOLUME",
            "description": "Milliliter - 1/1000 of a liter.",
            "conversion_formula": "To L: qty_ml / 1000 = qty_l\nTo kL: qty_ml / 1,000,000 = qty_kl\nTo kg (requires density): (qty_ml / 1000) * density_kg_per_l = qty_kg",
            "is_active": True,
        },
        # Density Units
        {
            "code": "KG_L",
            "name": "Kilograms per Liter",
            "symbol": "kg/L",
            "unit_type": "DENSITY",
            "description": "Density expressed as kilograms per liter. Used for converting between volume and mass.",
            "conversion_formula": "Volume to Mass: volume_l * density_kg_per_l = mass_kg\nMass to Volume: mass_kg / density_kg_per_l = volume_l\nTo g/cm³: density_kg_per_l * 1 = density_g_per_cm3 (numerically equivalent)",
            "is_active": True,
        },
        {
            "code": "G_CM3",
            "name": "Grams per Cubic Centimeter",
            "symbol": "g/cm³",
            "unit_type": "DENSITY",
            "description": "Density expressed as grams per cubic centimeter. Numerically equivalent to kg/L.",
            "conversion_formula": "To kg/L: density_g_per_cm3 * 1 = density_kg_per_l (numerically equivalent)\nVolume to Mass: volume_l * density_g_per_cm3 = mass_kg",
            "is_active": True,
        },
        {
            "code": "KG_M3",
            "name": "Kilograms per Cubic Meter",
            "symbol": "kg/m³",
            "unit_type": "DENSITY",
            "description": "Density expressed as kilograms per cubic meter.",
            "conversion_formula": "To kg/L: density_kg_per_m3 / 1000 = density_kg_per_l\nFrom kg/L: density_kg_per_l * 1000 = density_kg_per_m3",
            "is_active": True,
        },
        # Concentration Units
        {
            "code": "ABV",
            "name": "Alcohol by Volume",
            "symbol": "% ABV",
            "unit_type": "CONCENTRATION",
            "description": "Alcohol by volume expressed as percentage (v/v). Used for excise calculations.",
            "conversion_formula": "Alcohol volume from solution volume: solution_volume_l * (abv_percent / 100) = alcohol_volume_l\nAlcohol mass from solution volume: solution_volume_l * (abv_percent / 100) * 0.789 = alcohol_mass_kg\nAlcohol mass from solution mass: (solution_mass_kg / solution_density_kg_per_l) * (abv_percent / 100) * 0.789 = alcohol_mass_kg\nNote: 0.789 kg/L is the density of pure ethanol at 20°C",
            "is_active": True,
        },
        {
            "code": "ABV_PCT",
            "name": "Alcohol by Volume Percentage",
            "symbol": "% v/v",
            "unit_type": "CONCENTRATION",
            "description": "Alcohol by volume as percentage (v/v). Same as ABV but explicitly percentage.",
            "conversion_formula": "Same as ABV: solution_volume_l * (abv_pct / 100) * 0.789 = alcohol_mass_kg",
            "is_active": True,
        },
        {
            "code": "WT_PCT",
            "name": "Weight Percentage",
            "symbol": "% w/w",
            "unit_type": "CONCENTRATION",
            "description": "Weight percentage (w/w). Concentration expressed as mass of solute per mass of solution.",
            "conversion_formula": "To ABV (requires solution density): wt_pct * solution_density_kg_per_l / 0.789 * 100 = abv_pct\nFrom ABV (requires solution density): abv_pct * 0.789 / solution_density_kg_per_l * 100 = wt_pct",
            "is_active": True,
        },
        # Count Units
        {
            "code": "EA",
            "name": "Each",
            "symbol": "ea",
            "unit_type": "COUNT",
            "description": "Each - unit of count for discrete items. No conversion needed (1 ea = 1 ea).",
            "conversion_formula": "No conversion: 1 ea = 1 ea\nCount units are discrete and do not convert to mass or volume.",
            "is_active": True,
        },
    ]

    print(f"{'[DRY RUN] ' if dry_run else ''}Seeding Units table...")
    created_count = 0
    updated_count = 0
    skipped_count = 0

    for unit_data in units_data:
        code = unit_data["code"]

        # Check if unit already exists
        existing = db.execute(
            select(Unit).where(Unit.code == code)
        ).scalar_one_or_none()

        if existing:
            # Update existing unit
            print(f"  Updating existing unit: {code}")
            if not dry_run:
                existing.name = unit_data["name"]
                existing.symbol = unit_data.get("symbol")
                existing.unit_type = unit_data.get("unit_type")
                existing.description = unit_data.get("description")
                existing.conversion_formula = unit_data.get("conversion_formula")
                existing.is_active = unit_data.get("is_active", True)
            updated_count += 1
        else:
            # Create new unit
            print(f"  Creating new unit: {code} - {unit_data['name']}")
            if not dry_run:
                unit = Unit(
                    code=code,
                    name=unit_data["name"],
                    symbol=unit_data.get("symbol"),
                    unit_type=unit_data.get("unit_type"),
                    description=unit_data.get("description"),
                    conversion_formula=unit_data.get("conversion_formula"),
                    is_active=unit_data.get("is_active", True),
                )
                db.add(unit)
            created_count += 1

        if not dry_run:
            db.flush()

    if not dry_run:
        db.commit()
        print("\n[SUCCESS] Units table seeded successfully!")
    else:
        print(
            f"\n[DRY RUN] Would create {created_count} units, update {updated_count} units"
        )

    print(f"  Created: {created_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed the Units table")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes",
    )
    args = parser.parse_args()

    db: Session = next(get_db())
    try:
        seed_units(db, dry_run=args.dry_run)
    except Exception as e:
        print(f"Error seeding units: {e}", file=sys.stderr)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
