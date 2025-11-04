#!/usr/bin/env python3
"""
Generate complete database schema documentation.

This script connects to the database and extracts:
- All tables
- All columns with types, nullability, defaults
- Primary keys
- Foreign keys and relationships
- Indexes
- Unique constraints
- Check constraints

Outputs both JSON (machine-readable) and Markdown (human-readable) formats.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import inspect
from sqlalchemy.engine import Inspector

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.adapters.db.session import get_engine
from app.settings import settings


def get_table_info(inspector: Inspector, table_name: str) -> Dict[str, Any]:
    """Get complete information about a table."""
    # Get columns
    columns_info = []
    for column in inspector.get_columns(table_name):
        col_info = {
            "name": column["name"],
            "type": str(column["type"]),
            "nullable": column.get("nullable", True),
            "default": (
                str(column.get("default", ""))
                if column.get("default") is not None
                else None
            ),
            "autoincrement": column.get("autoincrement", False),
        }
        columns_info.append(col_info)

    # Get primary keys
    pk_constraint = inspector.get_pk_constraint(table_name)
    primary_keys = pk_constraint.get("constrained_columns", []) if pk_constraint else []

    # Get foreign keys
    foreign_keys = []
    for fk in inspector.get_foreign_keys(table_name):
        fk_info = {
            "name": fk.get("name"),
            "constrained_columns": fk.get("constrained_columns", []),
            "referred_table": fk.get("referred_table"),
            "referred_columns": fk.get("referred_columns", []),
            "onupdate": fk.get("onupdate"),
            "ondelete": fk.get("ondelete"),
        }
        foreign_keys.append(fk_info)

    # Get indexes
    indexes = []
    for idx in inspector.get_indexes(table_name):
        idx_info = {
            "name": idx.get("name"),
            "unique": idx.get("unique", False),
            "column_names": idx.get("column_names", []),
        }
        indexes.append(idx_info)

    # Get unique constraints
    unique_constraints = []
    for uq in inspector.get_unique_constraints(table_name):
        uq_info = {
            "name": uq.get("name"),
            "column_names": uq.get("column_names", []),
        }
        unique_constraints.append(uq_info)

    # Get check constraints (if supported)
    check_constraints = []
    try:
        for ck in inspector.get_check_constraints(table_name):
            ck_info = {
                "name": ck.get("name"),
                "sqltext": ck.get("sqltext"),
            }
            check_constraints.append(ck_info)
    except NotImplementedError:
        # SQLite doesn't support get_check_constraints
        pass

    return {
        "table_name": table_name,
        "columns": columns_info,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "indexes": indexes,
        "unique_constraints": unique_constraints,
        "check_constraints": check_constraints,
    }


def generate_json_documentation(
    inspector: Inspector, tables: List[str]
) -> Dict[str, Any]:
    """Generate JSON documentation."""
    schema_doc = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "database_url": settings.database.database_url,
            "total_tables": len(tables),
            "database_type": (
                "sqlite"
                if settings.database.database_url.startswith("sqlite")
                else "postgresql"
            ),
        },
        "tables": {},
    }

    for table_name in sorted(tables):
        schema_doc["tables"][table_name] = get_table_info(inspector, table_name)

    return schema_doc


def generate_markdown_documentation(schema_doc: Dict[str, Any]) -> str:
    """Generate Markdown documentation."""
    md = []
    md.append("# Complete Database Schema Documentation\n")
    md.append(f"Generated: {schema_doc['metadata']['generated_at']}\n")
    md.append(f"Database: {schema_doc['metadata']['database_url']}\n")
    md.append(f"Total Tables: {schema_doc['metadata']['total_tables']}\n\n")
    md.append("---\n\n")

    # Group tables by domain
    domains = {
        "Product Hierarchy": [
            "products",
            "product_variants",
            "product_migration_map",
            "product_channel_links",
        ],
        "Manufacturing Core": [
            "formulas",
            "formula_lines",
            "work_orders",
            "work_order_lines",
            "batches",
            "batch_components",
            "batch_lines",
            "qc_results",
        ],
        "Inventory Management": [
            "inventory_lots",
            "inventory_txns",
            "inventory_movements",
            "inventory_reservations",
        ],
        "Assembly Operations": [
            "assemblies",
            "assembly_lines",
            "assembly_cost_dependencies",
        ],
        "Sales & Purchasing": [
            "customers",
            "suppliers",
            "contacts",
            "sales_orders",
            "so_lines",
            "purchase_orders",
            "po_lines",
            "invoices",
            "invoice_lines",
        ],
        "Pricing & Packaging": [
            "price_lists",
            "price_list_items",
            "customer_prices",
            "pack_units",
            "pack_conversions",
            "units",
        ],
        "External Integrations": ["xero_tokens", "xero_sync_log"],
        "Reference Data": [
            "excise_rates",
            "quality_test_definitions",
            "raw_material_groups",
            "condition_types",
            "markups",
            "datasets",
            "manufacturing_config",
        ],
        "Legacy Preservation": [
            "legacy_acstk_data",
            "raw_materials",
            "finished_goods",
            "finished_goods_inventory",
        ],
        "Other": [],
    }

    # Categorize tables
    categorized = {domain: [] for domain in domains}
    for table_name in schema_doc["tables"].keys():
        found = False
        for domain, table_list in domains.items():
            if table_name in table_list:
                categorized[domain].append(table_name)
                found = True
                break
        if not found:
            categorized["Other"].append(table_name)

    # Generate documentation by domain
    for domain, table_names in categorized.items():
        if not table_names:
            continue

        md.append(f"## {domain}\n\n")

        for table_name in sorted(table_names):
            table_info = schema_doc["tables"][table_name]
            md.append(f"### Table: `{table_name}`\n\n")

            # Columns
            md.append("#### Columns\n\n")
            md.append("| Name | Type | Nullable | Default | Auto Increment |\n")
            md.append("|------|------|----------|---------|----------------|\n")
            for col in table_info["columns"]:
                pk_marker = "[PK]" if col["name"] in table_info["primary_keys"] else ""
                md.append(
                    f"| {pk_marker} {col['name']} | {col['type']} | "
                    f"{'Yes' if col['nullable'] else 'No'} | "
                    f"{col['default'] or 'NULL'} | "
                    f"{'Yes' if col['autoincrement'] else 'No'} |\n"
                )
            md.append("\n")

            # Primary Keys
            if table_info["primary_keys"]:
                md.append("#### Primary Keys\n\n")
                md.append(", ".join(f"`{pk}`" for pk in table_info["primary_keys"]))
                md.append("\n\n")
            else:
                md.append("#### Primary Keys\n\n")
                md.append("**WARNING**: No primary key defined!\n\n")

            # Foreign Keys
            if table_info["foreign_keys"]:
                md.append("#### Foreign Keys\n\n")
                md.append("| Name | Columns | References | On Update | On Delete |\n")
                md.append("|------|---------|-----------|-----------|-----------|\n")
                for fk in table_info["foreign_keys"]:
                    cols = ", ".join(fk["constrained_columns"])
                    ref = f"{fk['referred_table']}({', '.join(fk['referred_columns'])})"
                    md.append(
                        f"| {fk['name'] or 'N/A'} | {cols} | {ref} | "
                        f"{fk['onupdate'] or 'N/A'} | {fk['ondelete'] or 'N/A'} |\n"
                    )
                md.append("\n")

            # Unique Constraints
            if table_info["unique_constraints"]:
                md.append("#### Unique Constraints\n\n")
                for uq in table_info["unique_constraints"]:
                    cols = ", ".join(f"`{col}`" for col in uq["column_names"])
                    md.append(f"- {uq['name'] or 'Unnamed'}: ({cols})\n")
                md.append("\n")

            # Indexes
            if table_info["indexes"]:
                md.append("#### Indexes\n\n")
                md.append("| Name | Unique | Columns |\n")
                md.append("|------|--------|---------|\n")
                for idx in table_info["indexes"]:
                    cols = ", ".join(idx["column_names"])
                    unique = "Yes" if idx["unique"] else "No"
                    md.append(f"| {idx['name']} | {unique} | {cols} |\n")
                md.append("\n")

            md.append("---\n\n")

    return "".join(md)


def main():
    """Main function."""
    print("Generating database schema documentation...")
    print(f"Database URL: {settings.database.database_url}")

    # Create engine and inspector
    engine = get_engine()
    inspector = inspect(engine)

    # Get all tables
    tables = inspector.get_table_names()
    print(f"Found {len(tables)} tables")

    # Generate documentation
    schema_doc = generate_json_documentation(inspector, tables)

    # Output JSON
    json_path = project_root / "docs" / "snapshot" / "complete_schema.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(schema_doc, f, indent=2, default=str)
    print(f"[OK] JSON documentation saved to: {json_path}")

    # Output Markdown
    md_content = generate_markdown_documentation(schema_doc)
    md_path = project_root / "docs" / "snapshot" / "complete_schema.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[OK] Markdown documentation saved to: {md_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Schema Documentation Summary")
    print("=" * 60)
    print(f"Total tables: {len(tables)}")
    print("\nTables without primary keys:")
    no_pk = [
        name for name, info in schema_doc["tables"].items() if not info["primary_keys"]
    ]
    if no_pk:
        for table in no_pk:
            print(f"  [WARNING] {table}")
    else:
        print("  [OK] All tables have primary keys")

    print(
        f"\nTables with foreign keys: {sum(1 for t in schema_doc['tables'].values() if t['foreign_keys'])}"
    )
    print(
        f"Total foreign key relationships: {sum(len(t['foreign_keys']) for t in schema_doc['tables'].values())}"
    )
    print(
        f"Total indexes: {sum(len(t['indexes']) for t in schema_doc['tables'].values())}"
    )

    print("\n[OK] Documentation generation complete!")


if __name__ == "__main__":
    main()
