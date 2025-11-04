#!/usr/bin/env python3
"""
Generate ERD diagram from complete schema documentation.
Creates a Mermaid ERD diagram showing all tables and relationships.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def generate_mermaid_erd(schema_doc: dict) -> str:
    """Generate Mermaid ERD diagram from schema documentation."""
    lines = []
    lines.append("erDiagram")
    lines.append("")

    tables = schema_doc["tables"]

    # Group relationships by type
    relationships = []

    # Process each table and its foreign keys
    for table_name, table_info in sorted(tables.items()):
        # Define table with key columns
        pk_cols = table_info["primary_keys"]
        fk_cols = {
            fk["constrained_columns"][0]: fk for fk in table_info["foreign_keys"]
        }

        # Start table definition
        table_def = f"    {table_name} {{"
        lines.append(table_def)

        # Add primary key columns first
        for col in table_info["columns"]:
            col_name = col["name"]
            col_type = (
                col["type"].split("(")[0]
                if "(" in str(col["type"])
                else str(col["type"])
            )
            # Simplify type names
            if "VARCHAR" in col_type or "TEXT" in col_type:
                col_type = "string"
            elif "INTEGER" in col_type or "INT" in col_type:
                col_type = "int"
            elif "NUMERIC" in col_type or "NUM" in col_type or "DECIMAL" in col_type:
                col_type = "decimal"
            elif "DATETIME" in col_type or "TIMESTAMP" in col_type:
                col_type = "datetime"
            elif "BOOLEAN" in col_type:
                col_type = "bool"
            else:
                col_type = "string"

            nullable = "nullable" if col["nullable"] else "not null"
            pk_marker = " PK" if col_name in pk_cols else ""
            fk_marker = " FK" if col_name in fk_cols else ""

            lines.append(
                f'        {col_type} {col_name}{pk_marker}{fk_marker} "{nullable}"'
            )

        lines.append("    }")
        lines.append("")

        # Collect relationships
        for fk in table_info["foreign_keys"]:
            if fk["constrained_columns"] and fk["referred_table"]:
                relationships.append(
                    {
                        "from_table": table_name,
                        "to_table": fk["referred_table"],
                        "from_col": fk["constrained_columns"][0],
                        "to_col": (
                            fk["referred_columns"][0]
                            if fk["referred_columns"]
                            else "id"
                        ),
                    }
                )

    # Add relationships
    lines.append("")
    for rel in relationships:
        # Determine cardinality (simplified: many-to-one for most FKs)
        from_table = rel["from_table"]
        to_table = rel["to_table"]
        from_col = rel["from_col"]
        to_col = rel["to_col"]
        lines.append(f'    {from_table} }}o--|| {to_table} : "{from_col} -> {to_col}"')

    return "\n".join(lines)


def main():
    """Main function."""
    schema_path = project_root / "docs" / "snapshot" / "complete_schema.json"

    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        print("Please run generate_schema_documentation.py first.")
        sys.exit(1)

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_doc = json.load(f)

    # Generate ERD
    erd_diagram = generate_mermaid_erd(schema_doc)

    # Save to file
    erd_path = project_root / "docs" / "snapshot" / "erd_diagram.mmd"
    erd_path.parent.mkdir(parents=True, exist_ok=True)
    with open(erd_path, "w", encoding="utf-8") as f:
        f.write(erd_diagram)
    print(f"[OK] ERD diagram saved to: {erd_path}")

    # Also create a markdown file with embedded diagram
    md_content = f"""# Database ERD Diagram

This diagram shows all tables and relationships in the database.

```mermaid
{erd_diagram}
```

## How to View

1. Install Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`
2. Generate PNG: `mmdc -i docs/snapshot/erd_diagram.mmd -o docs/snapshot/erd_diagram.png`
3. Or view in GitHub/GitLab (renders automatically in markdown)
4. Or use online viewer: https://mermaid.live/
"""
    md_path = project_root / "docs" / "snapshot" / "erd_diagram.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[OK] ERD markdown saved to: {md_path}")


if __name__ == "__main__":
    main()
