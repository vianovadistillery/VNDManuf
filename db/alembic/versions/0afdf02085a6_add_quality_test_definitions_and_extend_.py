"""add_quality_test_definitions_and_extend_workorders

Revision ID: 0afdf02085a6
Revises: 4c76f70220c2
Create Date: 2025-11-02 20:31:25.535835

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0afdf02085a6"
down_revision: Union[str, None] = "4c76f70220c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create quality test definitions table
    op.create_table(
        "quality_test_definitions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("test_type", sa.String(length=50), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("min_value", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("max_value", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("target_value", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quality_test_definitions")),
    )
    op.create_index(
        op.f("ix_quality_test_definitions_code"),
        "quality_test_definitions",
        ["code"],
        unique=True,
    )

    # Extend assemblies table
    with op.batch_alter_table("assemblies") as batch_op:
        batch_op.add_column(
            sa.Column("sequence", sa.Integer(), nullable=False, server_default="1")
        )
        batch_op.add_column(
            sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="0")
        )
        batch_op.add_column(sa.Column("notes", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))

    # Add instructions to formulas
    op.add_column("formulas", sa.Column("instructions", sa.Text(), nullable=True))

    # Add QC results link to test definitions
    with op.batch_alter_table("qc_results") as batch_op:
        batch_op.add_column(
            sa.Column("test_definition_id", sa.String(length=36), nullable=True)
        )
        batch_op.create_foreign_key(
            op.f("fk_qc_results__test_definition_id__quality_test_definitions"),
            "quality_test_definitions",
            ["test_definition_id"],
            ["id"],
        )

    # Add instructions and actual quantities to work orders
    op.add_column("work_orders", sa.Column("instructions", sa.Text(), nullable=True))
    op.add_column(
        "work_order_lines",
        sa.Column(
            "actual_quantity_kg", sa.Numeric(precision=12, scale=3), nullable=True
        ),
    )


def downgrade() -> None:
    # Drop new columns and table
    op.drop_column("work_order_lines", "actual_quantity_kg")
    op.drop_column("work_orders", "instructions")
    with op.batch_alter_table("qc_results") as batch_op:
        batch_op.drop_constraint(
            op.f("fk_qc_results__test_definition_id__quality_test_definitions"),
            type_="foreignkey",
        )
        batch_op.drop_column("test_definition_id")
    op.drop_column("formulas", "instructions")
    op.drop_column("assemblies", "updated_at")
    op.drop_column("assemblies", "created_at")
    op.drop_column("assemblies", "notes")
    op.drop_column("assemblies", "is_primary")
    op.drop_column("assemblies", "sequence")
    op.drop_index(
        op.f("ix_quality_test_definitions_code"), table_name="quality_test_definitions"
    )
    op.drop_table("quality_test_definitions")
