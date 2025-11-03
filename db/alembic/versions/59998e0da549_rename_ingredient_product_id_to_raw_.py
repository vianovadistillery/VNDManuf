"""rename_ingredient_product_id_to_raw_material_id_in_formula_lines

Revision ID: 59998e0da549
Revises: 4e5525d232e0
Create Date: 2025-10-26 21:44:43.704899

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "59998e0da549"
down_revision: Union[str, None] = "4e5525d232e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operation for SQLite compatibility
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Check if formula_lines table exists and get its structure
    try:
        columns = [col["name"] for col in inspector.get_columns("formula_lines")]

        if "ingredient_product_id" in columns:
            # SQLite doesn't support ALTER COLUMN, so we need to use batch_alter_table
            with op.batch_alter_table("formula_lines", schema=None) as batch_op:
                batch_op.alter_column(
                    "ingredient_product_id", new_column_name="raw_material_id"
                )
    except Exception as e:
        print(f"Table may not exist or structure is different: {e}")


def downgrade() -> None:
    # Rename back if needed
    with op.batch_alter_table("formula_lines", schema=None) as batch_op:
        batch_op.alter_column(
            "raw_material_id", new_column_name="ingredient_product_id"
        )
