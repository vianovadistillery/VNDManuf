"""expand product categories with vodka and gin rtd rename

Revision ID: 20251109_223800
Revises: 20251108_104900
Create Date: 2025-11-09 22:38:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251109_223800"
down_revision = "20251108_104900"
branch_labels = None
depends_on = None


def _has_table(insp, name: str) -> bool:
    return name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if not _has_table(insp, "products"):
        return

    # Rename existing RTD category to the gin-specific label.
    op.execute(
        sa.text("UPDATE products SET category = 'gin_rtd' WHERE category = 'rtd_can'")
    )

    checks = {ck["name"] for ck in insp.get_check_constraints("products")}
    with op.batch_alter_table("products", recreate="always") as batch:
        if "ck_products_category" in checks:
            batch.drop_constraint("ck_products_category", type_="check")
        batch.create_check_constraint(
            "ck_products_category",
            "category IN ('gin_bottle','gin_rtd','vodka_bottle','vodka_rtd')",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if not _has_table(insp, "products"):
        return

    checks = {ck["name"] for ck in insp.get_check_constraints("products")}
    with op.batch_alter_table("products", recreate="always") as batch:
        if "ck_products_category" in checks:
            batch.drop_constraint("ck_products_category", type_="check")
        batch.create_check_constraint(
            "ck_products_category",
            "category IN ('gin_bottle','rtd_can')",
        )

    # Collapse the expanded categories back into the legacy labels.
    op.execute(
        sa.text(
            """
            UPDATE products
            SET category = CASE
                WHEN category = 'gin_rtd' THEN 'rtd_can'
                WHEN category = 'vodka_bottle' THEN 'gin_bottle'
                WHEN category = 'vodka_rtd' THEN 'rtd_can'
                ELSE category
            END
            """
        )
    )
