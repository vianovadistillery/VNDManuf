"""add location metadata and inventory link table

Revision ID: 20251109_231500
Revises: 20251109_223800
Create Date: 2025-11-09 23:15:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251109_231500"
down_revision = "20251109_223800"
branch_labels = None
depends_on = None


def _has_table(insp, name: str) -> bool:
    return name in insp.get_table_names()


def _get_column_names(insp, table: str) -> set[str]:
    return {col["name"] for col in insp.get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if _has_table(insp, "locations"):
        existing_cols = _get_column_names(insp, "locations")
        required_cols = {
            "address",
            "chain_alignment",
            "main_contact",
            "decision_maker",
        }
        if not required_cols.issubset(existing_cols):
            with op.batch_alter_table("locations", recreate="always") as batch:
                if "address" not in existing_cols:
                    batch.add_column(sa.Column("address", sa.String(length=255)))
                if "chain_alignment" not in existing_cols:
                    batch.add_column(
                        sa.Column("chain_alignment", sa.String(length=128))
                    )
                if "main_contact" not in existing_cols:
                    batch.add_column(sa.Column("main_contact", sa.String(length=255)))
                if "decision_maker" not in existing_cols:
                    batch.add_column(sa.Column("decision_maker", sa.String(length=255)))

    if not _has_table(insp, "location_skus"):
        op.create_table(
            "location_skus",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("location_id", sa.String(length=36), nullable=False),
            sa.Column("sku_id", sa.String(length=36), nullable=False),
            sa.Column(
                "is_manual", sa.Boolean(), nullable=False, server_default=sa.text("0")
            ),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("first_observed_dt", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_observed_dt", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["location_id"],
                ["locations.id"],
                name=op.f("fk_location_skus__location_id__locations"),
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["sku_id"],
                ["skus.id"],
                name=op.f("fk_location_skus__sku_id__skus"),
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_location_skus")),
            sa.UniqueConstraint(
                "location_id", "sku_id", name=op.f("uq_location_skus_location_sku")
            ),
        )
        op.create_index(
            op.f("ix_location_skus_location_id"),
            "location_skus",
            ["location_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_location_skus_sku_id"),
            "location_skus",
            ["sku_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if _has_table(insp, "location_skus"):
        op.drop_index(op.f("ix_location_skus_sku_id"), table_name="location_skus")
        op.drop_index(op.f("ix_location_skus_location_id"), table_name="location_skus")
        op.drop_table("location_skus")

    if _has_table(insp, "locations"):
        existing_cols = _get_column_names(insp, "locations")
        drop_cols = {
            "address",
            "chain_alignment",
            "main_contact",
            "decision_maker",
        }.intersection(existing_cols)
        if drop_cols:
            with op.batch_alter_table("locations", recreate="always") as batch:
                if "decision_maker" in drop_cols:
                    batch.drop_column("decision_maker")
                if "main_contact" in drop_cols:
                    batch.drop_column("main_contact")
                if "chain_alignment" in drop_cols:
                    batch.drop_column("chain_alignment")
                if "address" in drop_cols:
                    batch.drop_column("address")
