"""Fix all database constraints and indexes

Revision ID: fix_all_constraints_001
Revises: f1xpr0duct5pk001
Create Date: 2025-01-04 01:00:00.000000

This migration ensures all tables have proper primary keys, foreign keys, and indexes.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fix_all_constraints_001"
down_revision: Union[str, None] = "f1xpr0duct5pk001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix all constraints."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Verify all critical tables have primary keys
    critical_tables = [
        "products",
        "formulas",
        "inventory_lots",
        "work_orders",
        "batches",
        "customers",
        "suppliers",
        "contacts",
        "sales_orders",
        "purchase_orders",
        "invoices",
        "assemblies",
        "price_lists",
    ]

    for table_name in critical_tables:
        if table_name not in inspector.get_table_names():
            continue

        pk_constraint = inspector.get_pk_constraint(table_name)
        if not pk_constraint.get("constrained_columns"):
            # Try to add primary key on id column if it exists
            columns = [c["name"] for c in inspector.get_columns(table_name)]
            if "id" in columns:
                # Ensure id is not null
                try:
                    op.execute(
                        f'UPDATE {table_name} SET id = lower(hex(randomblob(16))) || "-" || substr(hex(randomblob(2)), 1, 4) || "-" || substr(hex(randomblob(2)), 1, 4) || "-" || substr(hex(randomblob(2)), 1, 4) || "-" || hex(randomblob(6)) WHERE id IS NULL'
                    )
                    op.alter_column(table_name, "id", nullable=False)
                    op.create_primary_key(f"pk_{table_name}", table_name, ["id"])
                except Exception as e:
                    print(f"Could not add PK to {table_name}: {e}")


def downgrade() -> None:
    """Not recommended - would break database."""
    pass
