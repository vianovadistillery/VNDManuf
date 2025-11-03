"""remove_legacy_columns

Revision ID: 94253da44e13
Revises: e4a5484fc3f6
Create Date: 2025-10-31 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision: str = "94253da44e13"
down_revision: Union[str, None] = "e4a5484fc3f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove legacy columns after all code has been migrated.

    WARNING: Only run this migration after:
    - All code uses unified product_id references
    - Backward compatibility properties no longer needed
    - Database backup created
    """
    connection = op.get_bind()
    inspector = inspect(connection)

    # Remove formula_lines.raw_material_id
    if "formula_lines" in inspector.get_table_names():
        formula_columns = [
            col["name"] for col in inspector.get_columns("formula_lines")
        ]

        if "raw_material_id" in formula_columns:
            # Safety check: verify all formula_lines have product_id
            null_product_ids = connection.execute(
                text(
                    """
                SELECT COUNT(*) FROM formula_lines WHERE product_id IS NULL
            """
                )
            ).scalar()

            if null_product_ids > 0:
                raise ValueError(
                    f"{null_product_ids} formula_lines have NULL product_id. "
                    "Cannot remove raw_material_id until all rows have product_id."
                )

            print("Dropping formula_lines.raw_material_id column...")
            with op.batch_alter_table("formula_lines", schema=None) as batch_op:
                batch_op.drop_column("raw_material_id")
            print("   [OK] formula_lines.raw_material_id dropped")

    # Remove inventory_movements.item_type and item_id
    if "inventory_movements" in inspector.get_table_names():
        movement_columns = [
            col["name"] for col in inspector.get_columns("inventory_movements")
        ]

        # Safety check: verify all movements have product_id
        null_product_ids = connection.execute(
            text(
                """
            SELECT COUNT(*) FROM inventory_movements WHERE product_id IS NULL
        """
            )
        ).scalar()

        if null_product_ids > 0:
            raise ValueError(
                f"{null_product_ids} inventory_movements have NULL product_id. "
                "Cannot remove item_type/item_id until all rows have product_id."
            )

        # Check if both columns exist - if so, need to drop them together
        if "item_type" in movement_columns and "item_id" in movement_columns:
            # Drop the index first if it exists
            indexes = inspector.get_indexes("inventory_movements")
            for idx in indexes:
                if idx["name"] == "ix_movements_item":
                    print("Dropping ix_movements_item index...")
                    op.drop_index("ix_movements_item", table_name="inventory_movements")
                    print("   [OK] ix_movements_item index dropped")
                    break

            print("Dropping inventory_movements.item_type and item_id columns...")
            with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
                batch_op.drop_column("item_type")
                batch_op.drop_column("item_id")
            print("   [OK] inventory_movements item_type and item_id columns dropped")


def downgrade() -> None:
    """
    Rollback: Recreate legacy columns.

    Note: Column data will be NULL - original data must be restored from backup.
    """
    # Recreate formula_lines.raw_material_id
    with op.batch_alter_table("formula_lines", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("raw_material_id", sa.String(length=36), nullable=True)
        )
        # Copy product_id to raw_material_id for backward compatibility
        op.execute(
            text(
                """
            UPDATE formula_lines
            SET raw_material_id = product_id
            WHERE product_id IS NOT NULL
        """
            )
        )

    # Recreate inventory_movements.item_type and item_id
    with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
        batch_op.add_column(sa.Column("item_type", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("item_id", sa.String(length=36), nullable=True))
        # Set item_type based on product type
        op.execute(
            text(
                """
            UPDATE inventory_movements im
            SET item_type = (
                SELECT CASE
                    WHEN p.product_type = 'RAW' THEN 'RAW_MATERIAL'
                    WHEN p.product_type = 'WIP' THEN 'WIP'
                    WHEN p.product_type = 'FINISHED' THEN 'FINISHED_GOOD'
                    ELSE 'PRODUCT'
                END
                FROM products p
                WHERE p.id = im.product_id
            ),
            item_id = product_id
            WHERE product_id IS NOT NULL
        """
            )
        )

    print("Legacy columns recreated (data restored from product_id)")
