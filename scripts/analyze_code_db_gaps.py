"""Compare database schema vs code models to identify misalignments.

This script:
- Loads database schema snapshot
- Loads code models snapshot
- Compares tables, columns, types, constraints
- Identifies gaps and misalignments
"""

import json
from pathlib import Path


def normalize_type(db_type):
    """Normalize database type string for comparison."""
    if not db_type:
        return None
    
    db_type = db_type.upper().strip()
    
    # SQLite type mappings
    type_map = {
        "VARCHAR": "STRING",
        "TEXT": "TEXT",
        "INTEGER": "INTEGER",
        "NUMERIC": "NUMERIC",
        "REAL": "REAL",
        "BLOB": "BLOB",
        "BOOLEAN": "BOOLEAN",
        "DATETIME": "DATETIME",
        "DATE": "DATE",
    }
    
    # Extract base type (before length/precision)
    base_type = db_type.split("(")[0].strip()
    return type_map.get(base_type, base_type)


def normalize_code_type(code_type):
    """Normalize code type string for comparison."""
    if not code_type:
        return None
    
    code_type = str(code_type).upper()
    
    # SQLAlchemy type mappings
    type_map = {
        "VARCHAR": "STRING",
        "STRING": "STRING",
        "TEXT": "TEXT",
        "INTEGER": "INTEGER",
        "NUMERIC": "NUMERIC",
        "REAL": "REAL",
        "BOOLEAN": "BOOLEAN",
        "DATETIME": "DATETIME",
        "DATE": "DATE",
    }
    
    # Handle SQLAlchemy type classes (e.g., "VARCHAR(50)")
    base_type = code_type.split("(")[0].strip()
    return type_map.get(base_type, base_type)


def load_snapshots():
    """Load both snapshots."""
    snapshot_dir = Path("docs/snapshot")
    
    # Load DB schema
    db_schema_path = snapshot_dir / "db_schema.json"
    with open(db_schema_path, "r") as f:
        db_schema = json.load(f)
    
    # Load code models
    code_models_path = snapshot_dir / "code_models.json"
    with open(code_models_path, "r") as f:
        code_models = json.load(f)
    
    return db_schema, code_models


def compare_columns(db_col, code_col):
    """Compare a database column with a code column."""
    differences = []
    
    # Type comparison
    db_type_norm = normalize_type(db_col.get("type"))
    code_type_norm = normalize_code_type(code_col.get("type", ""))
    
    if db_type_norm != code_type_norm:
        differences.append({
            "field": "type",
            "database": db_col.get("type"),
            "code": str(code_col.get("type", "")),
        })
    
    # Nullable comparison
    db_nullable = db_col.get("notnull", True) == 0
    code_nullable = code_col.get("nullable")
    
    if code_nullable is not None and db_nullable != code_nullable:
        differences.append({
            "field": "nullable",
            "database": db_nullable,
            "code": code_nullable,
        })
    
    # Primary key comparison
    db_pk = bool(db_col.get("primary_key", False))
    code_pk = bool(code_col.get("primary_key", False))
    
    if db_pk != code_pk:
        differences.append({
            "field": "primary_key",
            "database": db_pk,
            "code": code_pk,
        })
    
    return differences


def analyze_gaps():
    """Perform gap analysis."""
    db_schema, code_models = load_snapshots()
    
    db_tables = set(db_schema.get("tables", {}).keys())
    code_tables = set(code_models.get("models", {}).keys())
    
    # Filter out system tables
    db_tables = {t for t in db_tables if not t.startswith("sqlite_") and t != "alembic_version"}
    
    gaps = {
        "metadata": {
            "analysis_date": db_schema.get("metadata", {}).get("snapshot_date"),
            "database_tables": len(db_tables),
            "code_tables": len(code_tables),
        },
        "tables_in_db_not_in_code": sorted(list(db_tables - code_tables)),
        "tables_in_code_not_in_db": sorted(list(code_tables - db_tables)),
        "table_differences": {},
    }
    
    # Compare common tables
    common_tables = db_tables & code_tables
    
    for table_name in sorted(common_tables):
        db_table = db_schema["tables"][table_name]
        code_table_data = code_models["models"].get(table_name, {})
        code_table = code_table_data.get("table_info", {})
        
        db_columns = {col["name"]: col for col in db_table.get("columns", [])}
        code_columns = {col["name"]: col for col in code_table.get("columns", [])}
        
        table_diff = {
            "columns_in_db_not_in_code": [],
            "columns_in_code_not_in_db": [],
            "column_differences": {},
        }
        
        # Check columns in DB but not in code
        for col_name in set(db_columns.keys()) - set(code_columns.keys()):
            table_diff["columns_in_db_not_in_code"].append({
                "name": col_name,
                "type": db_columns[col_name].get("type"),
                "notnull": db_columns[col_name].get("notnull"),
            })
        
        # Check columns in code but not in DB
        for col_name in set(code_columns.keys()) - set(db_columns.keys()):
            table_diff["columns_in_code_not_in_db"].append({
                "name": col_name,
                "type": str(code_columns[col_name].get("type", "")),
            })
        
        # Compare common columns
        common_columns = set(db_columns.keys()) & set(code_columns.keys())
        
        for col_name in common_columns:
            db_col = db_columns[col_name]
            code_col = code_columns[col_name]
            
            differences = compare_columns(db_col, code_col)
            if differences:
                table_diff["column_differences"][col_name] = differences
        
        # Only include table if there are differences
        if (
            table_diff["columns_in_db_not_in_code"]
            or table_diff["columns_in_code_not_in_db"]
            or table_diff["column_differences"]
        ):
            gaps["table_differences"][table_name] = table_diff
    
    return gaps


def main():
    """Main execution."""
    print("Loading snapshots...")
    
    try:
        gaps = analyze_gaps()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run snapshot scripts first:")
        print("  python scripts/snapshot_database_schema.py")
        print("  python scripts/snapshot_code_models.py")
        return
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Create output directory
    output_dir = Path("docs/snapshot")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export JSON
    json_path = output_dir / "alignment_gaps.json"
    with open(json_path, "w") as f:
        json.dump(gaps, f, indent=2, default=str)
    print(f"[OK] Exported gap analysis to {json_path}")
    
    # Summary
    print(f"\nGap Analysis Summary:")
    print(f"  - DB tables: {gaps['metadata']['database_tables']}")
    print(f"  - Code tables: {gaps['metadata']['code_tables']}")
    print(f"  - Tables in DB but not in code: {len(gaps['tables_in_db_not_in_code'])}")
    if gaps['tables_in_db_not_in_code']:
        print(f"    {', '.join(gaps['tables_in_db_not_in_code'])}")
    print(f"  - Tables in code but not in DB: {len(gaps['tables_in_code_not_in_db'])}")
    if gaps['tables_in_code_not_in_db']:
        print(f"    {', '.join(gaps['tables_in_code_not_in_db'])}")
    print(f"  - Tables with differences: {len(gaps['table_differences'])}")
    
    if gaps['table_differences']:
        print(f"\nTables with misalignments:")
        for table_name, diff in gaps['table_differences'].items():
            issues = []
            if diff['columns_in_db_not_in_code']:
                issues.append(f"{len(diff['columns_in_db_not_in_code'])} missing columns")
            if diff['columns_in_code_not_in_db']:
                issues.append(f"{len(diff['columns_in_code_not_in_db'])} extra columns")
            if diff['column_differences']:
                issues.append(f"{len(diff['column_differences'])} type/nullable differences")
            print(f"  - {table_name}: {', '.join(issues)}")


if __name__ == "__main__":
    main()

