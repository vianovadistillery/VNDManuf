#!/usr/bin/env python3
"""
Import QuickBASIC TPManuf legacy data files.
Parses MSF binary files and imports into SQLAlchemy models.
"""

import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.adapters.qb_parser import QBFileParser
from app.adapters.db import get_db
from app.adapters.db.qb_models import (
    RawMaterialGroup, RawMaterial, FormulaClass,
    Markup, ConditionType, Dataset, ManufacturingConfig
)
import uuid
from decimal import Decimal
from datetime import datetime

ROOT = Path(__file__).parent.parent
LEGACY_DIR = ROOT / "legacy_data"


def import_raw_material_groups(db) -> Dict[int, str]:
    """
    Import raw material groups from MSRMGP.DAT or similar.
    Returns dict mapping group code to group id.
    """
    # Hardcode common groups based on QB code
    groups = [
        {'code': '1.1.1', 'name': 'Solvents'},
        {'code': '1.2.1', 'name': 'Resins'},
        {'code': '1.3.1', 'name': 'Pigments'},
        {'code': '1.4.1', 'name': 'Additives'},
        {'code': '1.5.1', 'name': 'Thinners'},
    ]
    
    group_map = {}
    for grp_data in groups:
        # Check if group exists
        existing = db.query(RawMaterialGroup).filter(RawMaterialGroup.code == grp_data['code']).first()
        
        if not existing:
            group = RawMaterialGroup(
                id=str(uuid.uuid4()),
                code=grp_data['code'],
                name=grp_data['name'],
                is_active=True
            )
            db.add(group)
            db.flush()
            group_map[int(grp_data['code'].replace('.', ''))] = group.id
        else:
            # Map group code number to UUID
            code_num = int(grp_data['code'].replace('.', ''))
            group_map[code_num] = existing.id
    
    return group_map


def import_raw_materials(db, group_map: Dict[int, str], dry_run: bool = False) -> List[Dict]:
    """
    Import raw materials from MSRMNEW.MSF.
    """
    msf_file = LEGACY_DIR / "MSRMNEW.msf"
    
    if not msf_file.exists():
        print(f"[ERROR] MSRMNEW.msf not found at {msf_file}")
        return []
    
    print(f"Parsing {msf_file}...")
    parser = QBFileParser(msf_file)
    qb_records = parser.parse_raw_materials()
    
    print(f"Found {len(qb_records)} raw material records")
    
    imported = []
    anomalies = []
    
    for qb_rec in qb_records[:10]:  # Test with first 10 records
        if qb_rec['no'] <= 0:
            continue
        
        try:
            # Map QB fields to SQLAlchemy model
            rm_data = {
                'id': str(uuid.uuid4()),
                'code': qb_rec['no'],
                'desc1': qb_rec.get('Desc1', '')[:25],
                'desc2': qb_rec.get('Desc2', '')[:25],
                'search_key': qb_rec.get('Search', '')[:5],
                'search_ext': qb_rec.get('searchs', '')[:8],
                'sg': float(qb_rec.get('Sg', 0.0)) if qb_rec.get('Sg') else None,
                'purchase_cost': float(qb_rec.get('PurCost', 0.0)) if qb_rec.get('PurCost') else None,
                'purchase_unit': qb_rec.get('PurUnit', '')[:2],
                'usage_cost': float(qb_rec.get('UseCost', 0.0)) if qb_rec.get('UseCost') else None,
                'usage_unit': qb_rec.get('UseUnit', '')[:2],
                'deal_cost': float(qb_rec.get('Dealcost', 0.0)) if qb_rec.get('Dealcost') else None,
                'sup_unit': qb_rec.get('SupUnit', '')[:2],
                'sup_qty': float(qb_rec.get('supqty', 0.0)) if qb_rec.get('supqty') else None,
                'active_flag': qb_rec.get('Active', 'A')[:1],
                'soh': float(qb_rec.get('soh', 0.0)) if qb_rec.get('soh') else None,
                'opening_soh': float(qb_rec.get('Osoh', 0.0)) if qb_rec.get('Osoh') else None,
                'soh_value': float(qb_rec.get('sohv', 0.0)) if qb_rec.get('sohv') else None,
                'so_on_order': int(qb_rec.get('soo', 0)) if qb_rec.get('soo') else None,
                'so_in_process': float(qb_rec.get('sip', 0.0)) if qb_rec.get('sip') else None,
                'restock_level': float(qb_rec.get('restock', 0.0)) if qb_rec.get('restock') else None,
                'used_ytd': float(qb_rec.get('used', 0.0)) if qb_rec.get('used') else None,
                'hazard': qb_rec.get('hazard', '')[:1],
                'condition': qb_rec.get('cond', '')[:1],
                'msds_flag': qb_rec.get('msdsflag', '')[:1],
                'altno1': int(qb_rec.get('altno1', 0)) if qb_rec.get('altno1') else None,
                'altno2': int(qb_rec.get('altno2', 0)) if qb_rec.get('altno2') else None,
                'altno3': int(qb_rec.get('altno3', 0)) if qb_rec.get('altno3') else None,
                'altno4': int(qb_rec.get('altno4', 0)) if qb_rec.get('altno4') else None,
                'altno5': int(qb_rec.get('altno5', 0)) if qb_rec.get('altno5') else None,
                'last_movement_date': qb_rec.get('Date', '')[:8],
                'last_purchase_date': qb_rec.get('lastpur', '')[:8],
                'notes': qb_rec.get('Notes', '')[:25],
                'ean13': float(qb_rec.get('ean13', 0.0)) if qb_rec.get('ean13') else None,
                'vol_solid': float(qb_rec.get('Volsolid', 0.0)) if qb_rec.get('Volsolid') else None,
                'solid_sg': float(qb_rec.get('Solidsg', 0.0)) if qb_rec.get('Solidsg') else None,
                'wt_solid': float(qb_rec.get('Wtsolid', 0.0)) if qb_rec.get('Wtsolid') else None,
                'group_id': group_map.get(int(qb_rec.get('Group', 0))),
            }
            
            if not dry_run:
                raw_material = RawMaterial(**rm_data)
                db.add(raw_material)
                imported.append(rm_data)
            else:
                imported.append(rm_data)
            
        except Exception as e:
            anomalies.append({
                'record': qb_rec.get('no', 'unknown'),
                'error': str(e),
                'data': qb_rec
            })
    
    if anomalies:
        print(f"[WARNING] {len(anomalies)} records had import errors")
        for anom in anomalies[:5]:  # Show first 5
            print(f"  Record {anom['record']}: {anom['error']}")
    
    return imported


def main():
    """Main import function."""
    import argparse
    parser = argparse.ArgumentParser(description='Import QuickBASIC TPManuf data')
    parser.add_argument('--dry-run', action='store_true', help='Parse files but do not write to database')
    parser.add_argument('--allow-anomalies', action='store_true', help='Continue on anomalies')
    args = parser.parse_args()
    
    print("QuickBASIC TPManuf Data Import")
    print("=" * 50)
    
    if args.dry_run:
        print("[DRY RUN] No data will be written to database")
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Import raw material groups
        print("\n1. Importing raw material groups...")
        group_map = import_raw_material_groups(db)
        print(f"   Imported {len(group_map)} groups")
        
        # 2. Import raw materials
        print("\n2. Importing raw materials...")
        raw_materials = import_raw_materials(db, group_map, dry_run=args.dry_run)
        print(f"   Parsed {len(raw_materials)} raw materials")
        
        if not args.dry_run:
            db.commit()
            print("\n[SUCCESS] Data imported successfully")
        else:
            print("\n[DRY RUN] Would import data (use without --dry-run to import)")
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Import failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

