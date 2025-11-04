#!/usr/bin/env python3
"""
Generate detailed alignment report comparing SQLAlchemy models against actual database schema.

This script:
1. Inspects the actual database schema
2. Inspects SQLAlchemy models from Base.metadata
3. Compares them and generates a detailed report
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

from sqlalchemy import inspect
from sqlalchemy.engine import Inspector

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.adapters.db import Base
from app.adapters.db.session import get_engine
from app.settings import settings


def get_db_table_info(inspector: Inspector, table_name: str) -> Dict[str, Any]:
    """Get table information from actual database."""
    columns = {}
    for col in inspector.get_columns(table_name):
        col_name = col["name"]
        columns[col_name] = {
            "type": str(col["type"]),
            "nullable": col.get("nullable", True),
            "default": (
                str(col.get("default", "")) if col.get("default") is not None else None
            ),
            "autoincrement": col.get("autoincrement", False),
        }

    pk_constraint = inspector.get_pk_constraint(table_name)
    primary_keys = pk_constraint.get("constrained_columns", []) if pk_constraint else []

    foreign_keys = []
    for fk in inspector.get_foreign_keys(table_name):
        foreign_keys.append(
            {
                "name": fk.get("name"),
                "constrained_columns": fk.get("constrained_columns", []),
                "referred_table": fk.get("referred_table"),
                "referred_columns": fk.get("referred_columns", []),
            }
        )

    indexes = []
    for idx in inspector.get_indexes(table_name):
        indexes.append(
            {
                "name": idx.get("name"),
                "unique": idx.get("unique", False),
                "column_names": idx.get("column_names", []),
            }
        )

    unique_constraints = []
    for uq in inspector.get_unique_constraints(table_name):
        unique_constraints.append(
            {
                "name": uq.get("name"),
                "column_names": uq.get("column_names", []),
            }
        )

    return {
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "indexes": indexes,
        "unique_constraints": unique_constraints,
    }


def get_model_table_info(table: Any) -> Dict[str, Any]:
    """Get table information from SQLAlchemy model."""
    columns = {}
    for col in table.columns:
        columns[col.name] = {
            "type": str(col.type),
            "nullable": col.nullable,
            "default": (
                str(col.default.arg)
                if col.default and col.default.arg is not None
                else None
            ),
            "autoincrement": col.autoincrement,
        }

    primary_keys = [col.name for col in table.primary_key.columns]

    foreign_keys = []
    for fk in table.foreign_keys:
        foreign_keys.append(
            {
                "name": fk.name if hasattr(fk, "name") else None,
                "constrained_columns": [fk.parent.name],
                "referred_table": fk.column.table.name,
                "referred_columns": [fk.column.name],
            }
        )

    indexes = []
    for idx in table.indexes:
        indexes.append(
            {
                "name": idx.name,
                "unique": idx.unique,
                "column_names": [col.name for col in idx.columns],
            }
        )

    unique_constraints = []
    for constraint in table.constraints:
        if hasattr(constraint, "columns"):
            col_names = [col.name for col in constraint.columns]
            if len(col_names) > 1:  # Multi-column unique constraint
                unique_constraints.append(
                    {
                        "name": (
                            constraint.name if hasattr(constraint, "name") else None
                        ),
                        "column_names": col_names,
                    }
                )

    return {
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "indexes": indexes,
        "unique_constraints": unique_constraints,
    }


def compare_tables(
    db_info: Dict[str, Any], model_info: Dict[str, Any], table_name: str
) -> Dict[str, Any]:
    """Compare database table with model."""
    comparison = {
        "table_name": table_name,
        "exists_in_db": True,
        "exists_in_models": True,
        "column_differences": {},
        "columns_in_db_not_in_model": [],
        "columns_in_model_not_in_db": [],
        "primary_key_differences": [],
        "foreign_key_differences": [],
        "index_differences": [],
        "unique_constraint_differences": [],
    }

    # Compare columns
    db_cols = set(db_info["columns"].keys())
    model_cols = set(model_info["columns"].keys())

    comparison["columns_in_db_not_in_model"] = sorted(list(db_cols - model_cols))
    comparison["columns_in_model_not_in_db"] = sorted(list(model_cols - db_cols))

    # Compare common columns
    common_cols = db_cols & model_cols
    for col_name in common_cols:
        db_col = db_info["columns"][col_name]
        model_col = model_info["columns"][col_name]
        differences = []

        # Type comparison (simplified)
        db_type = str(db_col["type"]).upper()
        model_type = str(model_col["type"]).upper()
        if db_type != model_type:
            # Normalize for comparison
            if "VARCHAR" in db_type or "TEXT" in db_type:
                db_type_norm = "STRING"
            elif "INTEGER" in db_type or "INT" in db_type:
                db_type_norm = "INTEGER"
            elif "NUMERIC" in db_type or "NUM" in db_type or "DECIMAL" in db_type:
                db_type_norm = "NUMERIC"
            elif "DATETIME" in db_type:
                db_type_norm = "DATETIME"
            elif "BOOLEAN" in db_type:
                db_type_norm = "BOOLEAN"
            else:
                db_type_norm = db_type

            if (
                "VARCHAR" in model_type
                or "TEXT" in model_type
                or "STRING" in model_type
            ):
                model_type_norm = "STRING"
            elif "INTEGER" in model_type or "INT" in model_type:
                model_type_norm = "INTEGER"
            elif (
                "NUMERIC" in model_type
                or "NUM" in model_type
                or "DECIMAL" in model_type
            ):
                model_type_norm = "NUMERIC"
            elif "DATETIME" in model_type or "TIMESTAMP" in model_type:
                model_type_norm = "DATETIME"
            elif "BOOLEAN" in model_type:
                model_type_norm = "BOOLEAN"
            else:
                model_type_norm = model_type

            if db_type_norm != model_type_norm:
                differences.append(
                    {
                        "field": "type",
                        "database": db_type,
                        "model": model_type,
                    }
                )

        # Nullable comparison
        if db_col["nullable"] != model_col["nullable"]:
            differences.append(
                {
                    "field": "nullable",
                    "database": db_col["nullable"],
                    "model": model_col["nullable"],
                }
            )

        if differences:
            comparison["column_differences"][col_name] = differences

    # Compare primary keys
    if set(db_info["primary_keys"]) != set(model_info["primary_keys"]):
        comparison["primary_key_differences"] = {
            "database": db_info["primary_keys"],
            "model": model_info["primary_keys"],
        }

    return comparison


def main():
    """Main function."""
    print("Generating alignment report...")
    print(f"Database URL: {settings.database.database_url}")

    # Connect to database
    engine = get_engine()
    inspector = inspect(engine)

    # Get all tables from database
    db_tables = set(inspector.get_table_names())

    # Get all tables from models
    model_tables = set(Base.metadata.tables.keys())

    # Compare
    alignment_report = {
        "metadata": {
            "generated_at": str(Path(__file__).stat().st_mtime),
            "database_url": settings.database.database_url,
            "total_db_tables": len(db_tables),
            "total_model_tables": len(model_tables),
        },
        "tables_in_db_not_in_models": sorted(list(db_tables - model_tables)),
        "tables_in_models_not_in_db": sorted(list(model_tables - db_tables)),
        "table_comparisons": {},
    }

    # Compare each table
    common_tables = db_tables & model_tables
    for table_name in sorted(common_tables):
        db_info = get_db_table_info(inspector, table_name)
        model_table = Base.metadata.tables[table_name]
        model_info = get_model_table_info(model_table)
        comparison = compare_tables(db_info, model_info, table_name)
        alignment_report["table_comparisons"][table_name] = comparison

    # Save report
    report_path = project_root / "docs" / "snapshot" / "alignment_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(alignment_report, f, indent=2, default=str)
    print(f"[OK] Alignment report saved to: {report_path}")

    # Generate summary
    print("\n" + "=" * 60)
    print("Alignment Report Summary")
    print("=" * 60)
    print(
        f"Tables in DB but not in models: {len(alignment_report['tables_in_db_not_in_models'])}"
    )
    if alignment_report["tables_in_db_not_in_models"]:
        for table in alignment_report["tables_in_db_not_in_models"]:
            print(f"  - {table}")

    print(
        f"\nTables in models but not in DB: {len(alignment_report['tables_in_models_not_in_db'])}"
    )
    if alignment_report["tables_in_models_not_in_db"]:
        for table in alignment_report["tables_in_models_not_in_db"]:
            print(f"  - {table}")

    print(
        f"\nTables with column differences: {sum(1 for c in alignment_report['table_comparisons'].values() if c['columns_in_db_not_in_model'] or c['columns_in_model_not_in_db'] or c['column_differences'])}"
    )

    critical_issues = []
    for table_name, comparison in alignment_report["table_comparisons"].items():
        if comparison["primary_key_differences"]:
            critical_issues.append(f"{table_name}: Missing/inconsistent primary key")
        if comparison["columns_in_db_not_in_model"]:
            count = len(comparison["columns_in_db_not_in_model"])
            if count > 10:
                critical_issues.append(
                    f"{table_name}: {count} missing columns in model"
                )

    if critical_issues:
        print("\nCritical Issues:")
        for issue in critical_issues:
            print(f"  [WARNING] {issue}")

    print("\n[OK] Alignment report generation complete!")


if __name__ == "__main__":
    main()
