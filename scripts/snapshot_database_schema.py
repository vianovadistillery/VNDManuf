"""Extract complete database schema snapshot for documentation and alignment.

This script captures:
- All tables with columns, types, constraints
- All indexes
- All foreign key relationships
- Alembic version state
- Exports to JSON (structured) and SQL (DDL format)
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


def get_database_path():
    """Get database path from environment or default."""
    import os
    db_url = os.getenv("DB_DATABASE_URL", "sqlite:///./tpmanuf.db")
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "")
    return "tpmanuf.db"


def extract_table_info(cursor, table_name):
    """Extract complete information about a table."""
    info = {}
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = []
    for col in cursor.fetchall():
        col_info = {
            "name": col[1],
            "type": col[2],
            "notnull": bool(col[3]),
            "default": col[4],
            "primary_key": bool(col[5]),
        }
        columns.append(col_info)
    info["columns"] = columns
    
    # Get indexes (including unique constraints)
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = []
    for idx in cursor.fetchall():
        idx_name = idx[1]
        is_unique = bool(idx[2])
        is_primary = bool(idx[3]) if len(idx) > 3 else False
        
        # Get index columns
        cursor.execute(f"PRAGMA index_info({idx_name})")
        idx_cols = [row[2] for row in cursor.fetchall()]
        
        indexes.append({
            "name": idx_name,
            "unique": is_unique,
            "columns": idx_cols,
            "is_primary": is_primary,
        })
    info["indexes"] = indexes
    
    # Get foreign keys
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = []
    for fk in cursor.fetchall():
        foreign_keys.append({
            "id": fk[0],
            "sequence": fk[1],
            "from_column": fk[2],
            "to_table": fk[3],
            "to_column": fk[4],
            "on_update": fk[5] if len(fk) > 5 else None,
            "on_delete": fk[6] if len(fk) > 6 else None,
        })
    info["foreign_keys"] = foreign_keys
    
    # Get table creation SQL (includes constraints)
    cursor.execute(
        f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    result = cursor.fetchone()
    info["ddl"] = result[0] if result else None
    
    return info


def extract_alembic_version(cursor):
    """Extract Alembic version information."""
    try:
        cursor.execute("SELECT version_num FROM alembic_version")
        versions = cursor.fetchall()
        return [v[0] for v in versions]
    except sqlite3.OperationalError:
        return []


def generate_sql_export(schema_data):
    """Generate SQL DDL from schema data."""
    sql_lines = []
    sql_lines.append("-- Database Schema Snapshot")
    sql_lines.append(f"-- Generated: {datetime.now().isoformat()}")
    sql_lines.append("")
    
    # Export table DDLs
    for table_name, info in sorted(schema_data["tables"].items()):
        if info.get("ddl"):
            sql_lines.append(f"-- Table: {table_name}")
            sql_lines.append(info["ddl"])
            sql_lines.append(";")
            sql_lines.append("")
    
    # Export indexes (those not in table DDL)
    for table_name, info in sorted(schema_data["tables"].items()):
        for idx in info.get("indexes", []):
            if idx.get("ddl"):
                sql_lines.append(f"-- Index: {idx['name']} on {table_name}")
                sql_lines.append(idx["ddl"])
                sql_lines.append(";")
                sql_lines.append("")
    
    return "\n".join(sql_lines)


def main():
    """Main execution."""
    db_path = get_database_path()
    
    if not Path(db_path).exists():
        print(f"Error: Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Filter out system tables
    user_tables = [
        t for t in tables
        if t != "sqlite_sequence" and not t.startswith("sqlite_")
    ]
    
    # Extract schema information
    schema_data = {
        "metadata": {
            "database_path": db_path,
            "snapshot_date": datetime.now().isoformat(),
            "total_tables": len(user_tables),
        },
        "tables": {},
        "alembic_versions": extract_alembic_version(cursor),
    }
    
    for table in user_tables:
        schema_data["tables"][table] = extract_table_info(cursor, table)
    
    conn.close()
    
    # Create output directory
    output_dir = Path("docs/snapshot")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export JSON
    json_path = output_dir / "db_schema.json"
    with open(json_path, "w") as f:
        json.dump(schema_data, f, indent=2)
    print(f"[OK] Exported JSON schema to {json_path}")
    
    # Export SQL
    sql_path = output_dir / "db_schema.sql"
    sql_content = generate_sql_export(schema_data)
    with open(sql_path, "w") as f:
        f.write(sql_content)
    print(f"[OK] Exported SQL schema to {sql_path}")
    
    # Summary
    print(f"\nSnapshot Summary:")
    print(f"  - Tables: {len(user_tables)}")
    print(f"  - Alembic versions: {len(schema_data['alembic_versions'])}")
    if schema_data["alembic_versions"]:
        print(f"    Applied: {', '.join(schema_data['alembic_versions'])}")


if __name__ == "__main__":
    main()

