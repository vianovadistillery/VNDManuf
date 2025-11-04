#!/usr/bin/env python3
"""
Generate complete Product model with all columns from database schema.

This script reads the complete schema and generates the correct Product model
with all 72+ missing columns properly typed.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def sqlite_to_sqlalchemy_type(db_type: str, nullable: bool = True):
    """Convert SQLite type to SQLAlchemy type."""
    db_type_lower = str(db_type).lower()

    if "varchar" in db_type_lower or "text" in db_type_lower or db_type_lower == "text":
        return "String"
    if "integer" in db_type_lower or db_type_lower == "int":
        return "Integer"
    if "numeric" in db_type_lower or db_type_lower == "num":
        # Try to extract precision/scale
        if "(" in db_type:
            return f"Numeric({db_type.split('(')[1].rstrip(')')})"
        return "Numeric(10, 2)"  # Default
    if "boolean" in db_type_lower or db_type_lower == "bool":
        return "Boolean"
    if "datetime" in db_type_lower:
        return "DateTime"
    if db_type_lower == "null" or db_type_lower == "":
        return "String"  # Default for unknown

    return "String"  # Safe default


def generate_product_model():
    """Generate complete Product model."""
    schema_path = project_root / "docs" / "snapshot" / "complete_schema.json"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    products_table = schema["tables"]["products"]
    columns = products_table["columns"]
    products_table["primary_keys"]

    # Group columns logically
    model_lines = []
    model_lines.append("class Product(Base):")
    model_lines.append('    __tablename__ = "products"')
    model_lines.append("")
    model_lines.append("    # Primary Key - CRITICAL: Must be defined")
    if "id" in [col["name"] for col in columns]:
        next(c for c in columns if c["name"] == "id")
        model_lines.append("    id = uuid_column()  # Primary key")
    else:
        model_lines.append("    id = uuid_column()  # Primary key (adding)")
    model_lines.append("")

    # Core identification
    model_lines.append("    # Core Identification")
    core_fields = ["sku", "name", "description", "ean13"]
    for field in core_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            index = ", index=True" if field == "sku" else ""
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable}{index})"
            )
    model_lines.append("")

    # Product Type and Classification
    model_lines.append("    # Product Type and Classification")
    type_fields = [
        "product_type",
        "is_purchase",
        "is_sell",
        "is_assemble",
        "is_tracked",
        "sellable",
        "is_archived",
        "archived_at",
    ]
    for field in type_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            default = get_default_value(col, col_type)
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable}{default})"
            )
    model_lines.append("")

    # Raw Material Fields (for RAW product type)
    model_lines.append("    # Raw Material Fields (RAW product type)")
    rm_fields = [
        "raw_material_code",
        "raw_material_group_id",
        "raw_material_search_key",
        "raw_material_search_ext",
        "specific_gravity",
        "vol_solid",
        "solid_sg",
        "wt_solid",
        "usage_cost",
        "usage_unit",
        "restock_level",
        "used_ytd",
        "hazard",
        "condition",
        "msds_flag",
        "altno1",
        "altno2",
        "altno3",
        "altno4",
        "altno5",
        "last_movement_date",
        "last_purchase_date",
        "ean13_raw",
        "xero_account",
    ]
    for field in rm_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            index = (
                ", index=True"
                if field in ["raw_material_code", "raw_material_group_id"]
                else ""
            )
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable}{index})"
            )
    model_lines.append("")

    # Finished Goods Fields (for FINISHED product type)
    model_lines.append("    # Finished Goods Fields (FINISHED product type)")
    fg_fields = ["formula_id", "formula_revision"]
    for field in fg_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Physical Properties
    model_lines.append("    # Physical Properties")
    phys_fields = ["size", "base_unit", "pack", "density_kg_per_l", "abv_percent"]
    for field in phys_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Purchase Information
    model_lines.append("    # Purchase Information")
    purchase_fields = [
        "supplier_id",
        "purchase_unit_id",
        "purchase_volume",
        "purchase_cost_ex_gst",
        "purchase_cost_inc_gst",
        "purchase_tax_included",
        "purchase_tax_included_bool",
        "purcost",
        "purtax",
    ]
    for field in purchase_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            if field == "supplier_id":
                model_lines.append(
                    f'    {field} = Column(String(36), ForeignKey("suppliers.id"), nullable=True)'
                )
            else:
                col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
                nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
                model_lines.append(
                    f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
                )
    model_lines.append("")

    # Usage Information
    model_lines.append("    # Usage Information")
    usage_fields = ["usage_cost_ex_gst", "usage_cost_inc_gst", "usage_tax_included"]
    for field in usage_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Costing Information
    model_lines.append("    # Costing Information")
    costing_fields = [
        "standard_cost",
        "estimated_cost",
        "estimate_reason",
        "estimated_by",
        "estimated_at",
        "manufactured_cost_ex_gst",
        "manufactured_cost_inc_gst",
        "manufactured_tax_included",
        "wholesalecost",
    ]
    for field in costing_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Pricing - Retail
    model_lines.append("    # Pricing - Retail")
    retail_fields = [
        "retail_price_ex_gst",
        "retail_price_inc_gst",
        "retail_excise",
        "retailcde",
    ]
    for field in retail_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Pricing - Wholesale
    model_lines.append("    # Pricing - Wholesale")
    wholesale_fields = [
        "wholesale_price_ex_gst",
        "wholesale_price_inc_gst",
        "wholesale_excise",
        "wholesalecde",
    ]
    for field in wholesale_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Pricing - Counter
    model_lines.append("    # Pricing - Counter")
    counter_fields = [
        "counter_price_ex_gst",
        "counter_price_inc_gst",
        "counter_excise",
        "countercde",
    ]
    for field in counter_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Pricing - Trade
    model_lines.append("    # Pricing - Trade")
    trade_fields = [
        "trade_price_ex_gst",
        "trade_price_inc_gst",
        "trade_excise",
        "tradecde",
    ]
    for field in trade_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Pricing - Contract
    model_lines.append("    # Pricing - Contract")
    contract_fields = [
        "contract_price_ex_gst",
        "contract_price_inc_gst",
        "contract_excise",
        "contractcde",
    ]
    for field in contract_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Pricing - Industrial
    model_lines.append("    # Pricing - Industrial")
    industrial_fields = [
        "industrial_price_ex_gst",
        "industrial_price_inc_gst",
        "industrial_excise",
        "industrialcde",
    ]
    for field in industrial_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Pricing - Distributor
    model_lines.append("    # Pricing - Distributor")
    distributor_fields = [
        "distributor_price_ex_gst",
        "distributor_price_inc_gst",
        "distributor_excise",
        "distributorcde",
    ]
    for field in distributor_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Product Flags
    model_lines.append("    # Product Flags")
    flag_fields = ["dgflag", "form", "pkge", "label", "manu", "taxinc", "salestaxcde"]
    for field in flag_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Discount Codes
    model_lines.append("    # Discount Codes")
    disc_fields = ["disccdeone", "disccdetwo"]
    for field in disc_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Xero Integration
    model_lines.append("    # Xero Integration")
    xero_fields = ["xero_item_id", "last_sync"]
    for field in xero_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable})"
            )
    model_lines.append("")

    # Status and Timestamps
    model_lines.append("    # Status and Timestamps")
    status_fields = ["is_active", "created_at", "updated_at"]
    for field in status_fields:
        col = next((c for c in columns if c["name"] == field), None)
        if col:
            col_type = sqlite_to_sqlalchemy_type(col["type"], col["nullable"])
            nullable = ", nullable=True" if col["nullable"] else ", nullable=False"
            default = get_default_value(col, col_type)
            model_lines.append(
                f"    {field} = Column({col_type}({get_type_args(col['type'])}){nullable}{default})"
            )
    model_lines.append("")

    # Indexes
    model_lines.append("    __table_args__ = (")
    model_lines.append('        Index("ix_products_sku", "sku"),')
    model_lines.append('        Index("ix_products_product_type", "product_type"),')
    model_lines.append(
        '        Index("ix_products_raw_material_code", "raw_material_code"),'
    )
    model_lines.append(
        '        Index("ix_products_raw_material_group", "raw_material_group_id"),'
    )
    model_lines.append("    )")

    return "\n".join(model_lines)


def get_type_args(db_type: str) -> str:
    """Extract type arguments from database type string."""
    if "(" in str(db_type):
        return db_type.split("(")[1].rstrip(")")
    if db_type.upper() in ["TEXT", "NUMERIC", "INTEGER", "BOOLEAN", "DATETIME"]:
        return ""
    # Default sizes for common types
    if "varchar" in db_type.lower():
        return "50"  # Default
    return ""


def get_default_value(col: dict, col_type: str) -> str:
    """Get default value string for column."""
    if col.get("default"):
        default_str = str(col["default"]).strip("'\"")
        if col_type == "Boolean" and default_str in ["1", "0", "True", "False"]:
            return f", default={default_str.lower() == '1' or default_str.lower() == 'true'}"
        if col_type == "Integer" and default_str.isdigit():
            return f", default={default_str}"
        if col_type == "DateTime":
            if "now" in default_str.lower() or "current" in default_str.lower():
                return ", default=datetime.utcnow"
        return f', default="{default_str}"'
    return ""


if __name__ == "__main__":
    print("Generating complete Product model...")
    model_code = generate_product_model()

    output_path = project_root / "docs" / "snapshot" / "product_model_complete.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Complete Product Model (Generated from Database Schema)\n")
        f.write("# This model includes all 72+ columns from the database\n\n")
        f.write("from datetime import datetime\n")
        f.write(
            "from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Index\n"
        )
        f.write("from app.adapters.db.base import Base\n")
        f.write("from app.adapters.db.models import uuid_column\n\n")
        f.write(model_code)

    print(f"[OK] Complete Product model saved to: {output_path}")
    print("[OK] Model generation complete!")
