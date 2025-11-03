"""add_costing_fields_and_tables

Revision ID: 2b0eead645b5
Revises: add_archiving_fields
Create Date: 2025-11-02 09:47:15.346830

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b0eead645b5"
down_revision: Union[str, None] = "add_archiving_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add costing fields and tables for inventory management and costing system."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Step 1: Add fields to products table
    products_columns = [col["name"] for col in inspector.get_columns("products")]

    with op.batch_alter_table("products", schema=None) as batch_op:
        if "is_tracked" not in products_columns:
            batch_op.add_column(
                sa.Column("is_tracked", sa.Boolean(), nullable=True, server_default="1")
            )
        if "sellable" not in products_columns:
            batch_op.add_column(
                sa.Column("sellable", sa.Boolean(), nullable=True, server_default="0")
            )
        if "standard_cost" not in products_columns:
            batch_op.add_column(
                sa.Column("standard_cost", sa.Numeric(10, 2), nullable=True)
            )
        if "estimated_cost" not in products_columns:
            batch_op.add_column(
                sa.Column("estimated_cost", sa.Numeric(10, 2), nullable=True)
            )
        if "estimate_reason" not in products_columns:
            batch_op.add_column(sa.Column("estimate_reason", sa.Text(), nullable=True))
        if "estimated_by" not in products_columns:
            batch_op.add_column(
                sa.Column("estimated_by", sa.String(100), nullable=True)
            )
        if "estimated_at" not in products_columns:
            batch_op.add_column(sa.Column("estimated_at", sa.DateTime(), nullable=True))

    # Step 2: Add fields to inventory_lots table
    lots_columns = [col["name"] for col in inspector.get_columns("inventory_lots")]

    with op.batch_alter_table("inventory_lots", schema=None) as batch_op:
        if "original_unit_cost" not in lots_columns:
            batch_op.add_column(
                sa.Column("original_unit_cost", sa.Numeric(10, 2), nullable=True)
            )
        if "current_unit_cost" not in lots_columns:
            batch_op.add_column(
                sa.Column("current_unit_cost", sa.Numeric(10, 2), nullable=True)
            )

    # Step 3: Add fields to inventory_txns table
    txns_columns = [col["name"] for col in inspector.get_columns("inventory_txns")]

    with op.batch_alter_table("inventory_txns", schema=None) as batch_op:
        if "cost_source" not in txns_columns:
            batch_op.add_column(sa.Column("cost_source", sa.String(20), nullable=True))
        if "extended_cost" not in txns_columns:
            batch_op.add_column(
                sa.Column("extended_cost", sa.Numeric(12, 2), nullable=True)
            )
        if "estimate_flag" not in txns_columns:
            batch_op.add_column(
                sa.Column(
                    "estimate_flag", sa.Boolean(), nullable=True, server_default="0"
                )
            )
        if "estimate_reason" not in txns_columns:
            batch_op.add_column(sa.Column("estimate_reason", sa.Text(), nullable=True))

    # Step 4: Extend assemblies table
    assemblies_columns = [col["name"] for col in inspector.get_columns("assemblies")]

    with op.batch_alter_table("assemblies", schema=None) as batch_op:
        if "is_energy_or_overhead" not in assemblies_columns:
            batch_op.add_column(
                sa.Column(
                    "is_energy_or_overhead",
                    sa.Boolean(),
                    nullable=True,
                    server_default="0",
                )
            )
        if "effective_from" not in assemblies_columns:
            batch_op.add_column(
                sa.Column("effective_from", sa.DateTime(), nullable=True)
            )
        if "effective_to" not in assemblies_columns:
            batch_op.add_column(sa.Column("effective_to", sa.DateTime(), nullable=True))
        if "version" not in assemblies_columns:
            batch_op.add_column(
                sa.Column("version", sa.Integer(), nullable=True, server_default="1")
            )
        if "is_active" not in assemblies_columns:
            batch_op.add_column(
                sa.Column("is_active", sa.Boolean(), nullable=True, server_default="1")
            )
        if "yield_factor" not in assemblies_columns:
            batch_op.add_column(
                sa.Column(
                    "yield_factor",
                    sa.Numeric(6, 4),
                    nullable=True,
                    server_default="1.0",
                )
            )

    # Step 5: Create revaluations table
    tables = inspector.get_table_names()

    if "revaluations" not in tables:
        op.create_table(
            "revaluations",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("item_id", sa.String(36), nullable=False),
            sa.Column("lot_id", sa.String(36), nullable=True),
            sa.Column("old_unit_cost", sa.Numeric(10, 2), nullable=False),
            sa.Column("new_unit_cost", sa.Numeric(10, 2), nullable=False),
            sa.Column("delta_extended_cost", sa.Numeric(12, 2), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("revalued_by", sa.String(100), nullable=False),
            sa.Column(
                "revalued_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.current_timestamp(),
            ),
            sa.Column(
                "propagated_to_assemblies",
                sa.Boolean(),
                nullable=True,
                server_default="0",
            ),
            sa.ForeignKeyConstraint(["item_id"], ["products.id"], name="fk_reval_item"),
            sa.ForeignKeyConstraint(
                ["lot_id"], ["inventory_lots.id"], name="fk_reval_lot"
            ),
        )
        op.create_index("ix_reval_item_ts", "revaluations", ["item_id", "revalued_at"])
        op.create_index("ix_reval_lot", "revaluations", ["lot_id"])

    # Step 6: Create assembly_cost_dependencies table
    if "assembly_cost_dependencies" not in tables:
        op.create_table(
            "assembly_cost_dependencies",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("consumed_lot_id", sa.String(36), nullable=False),
            sa.Column("produced_lot_id", sa.String(36), nullable=False),
            sa.Column("consumed_txn_id", sa.String(36), nullable=False),
            sa.Column("produced_txn_id", sa.String(36), nullable=False),
            sa.Column(
                "dependency_ts",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.current_timestamp(),
            ),
            sa.ForeignKeyConstraint(
                ["consumed_lot_id"], ["inventory_lots.id"], name="fk_dep_consumed_lot"
            ),
            sa.ForeignKeyConstraint(
                ["produced_lot_id"], ["inventory_lots.id"], name="fk_dep_produced_lot"
            ),
            sa.ForeignKeyConstraint(
                ["consumed_txn_id"], ["inventory_txns.id"], name="fk_dep_consumed_txn"
            ),
            sa.ForeignKeyConstraint(
                ["produced_txn_id"], ["inventory_txns.id"], name="fk_dep_produced_txn"
            ),
        )
        op.create_index(
            "ix_dep_consumed", "assembly_cost_dependencies", ["consumed_lot_id"]
        )
        op.create_index(
            "ix_dep_produced", "assembly_cost_dependencies", ["produced_lot_id"]
        )
        op.create_index(
            "ix_dep_consumed_txn", "assembly_cost_dependencies", ["consumed_txn_id"]
        )
        op.create_index(
            "ix_dep_produced_txn", "assembly_cost_dependencies", ["produced_txn_id"]
        )


def downgrade() -> None:
    """Remove costing fields and tables."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    # Drop tables
    if "assembly_cost_dependencies" in tables:
        op.drop_table("assembly_cost_dependencies")

    if "revaluations" in tables:
        op.drop_table("revaluations")

    # Remove fields from assemblies
    assemblies_columns = [col["name"] for col in inspector.get_columns("assemblies")]
    with op.batch_alter_table("assemblies", schema=None) as batch_op:
        if "yield_factor" in assemblies_columns:
            batch_op.drop_column("yield_factor")
        if "is_active" in assemblies_columns:
            batch_op.drop_column("is_active")
        if "version" in assemblies_columns:
            batch_op.drop_column("version")
        if "effective_to" in assemblies_columns:
            batch_op.drop_column("effective_to")
        if "effective_from" in assemblies_columns:
            batch_op.drop_column("effective_from")
        if "is_energy_or_overhead" in assemblies_columns:
            batch_op.drop_column("is_energy_or_overhead")

    # Remove fields from inventory_txns
    txns_columns = [col["name"] for col in inspector.get_columns("inventory_txns")]
    with op.batch_alter_table("inventory_txns", schema=None) as batch_op:
        if "estimate_reason" in txns_columns:
            batch_op.drop_column("estimate_reason")
        if "estimate_flag" in txns_columns:
            batch_op.drop_column("estimate_flag")
        if "extended_cost" in txns_columns:
            batch_op.drop_column("extended_cost")
        if "cost_source" in txns_columns:
            batch_op.drop_column("cost_source")

    # Remove fields from inventory_lots
    lots_columns = [col["name"] for col in inspector.get_columns("inventory_lots")]
    with op.batch_alter_table("inventory_lots", schema=None) as batch_op:
        if "current_unit_cost" in lots_columns:
            batch_op.drop_column("current_unit_cost")
        if "original_unit_cost" in lots_columns:
            batch_op.drop_column("original_unit_cost")

    # Remove fields from products
    products_columns = [col["name"] for col in inspector.get_columns("products")]
    with op.batch_alter_table("products", schema=None) as batch_op:
        if "estimated_at" in products_columns:
            batch_op.drop_column("estimated_at")
        if "estimated_by" in products_columns:
            batch_op.drop_column("estimated_by")
        if "estimate_reason" in products_columns:
            batch_op.drop_column("estimate_reason")
        if "estimated_cost" in products_columns:
            batch_op.drop_column("estimated_cost")
        if "standard_cost" in products_columns:
            batch_op.drop_column("standard_cost")
        if "sellable" in products_columns:
            batch_op.drop_column("sellable")
        if "is_tracked" in products_columns:
            batch_op.drop_column("is_tracked")
