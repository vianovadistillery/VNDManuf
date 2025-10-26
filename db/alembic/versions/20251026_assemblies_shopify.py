"""assemblies + shopify mapping

Revision ID: rev_assemblies_shopify
Revises: b7a47f197d45
Create Date: 2025-10-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "rev_assemblies_shopify"
down_revision = "b7a47f197d45"
branch_labels = None
depends_on = None

def upgrade():
    # Use SQLite-compatible UUID columns (String) for compatibility
    op.create_table(
        "assemblies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("parent_product_id", sa.String(36), nullable=False),
        sa.Column("child_product_id", sa.String(36), nullable=False),
        sa.Column("ratio", sa.Numeric(18,6), nullable=False, server_default="1"),
        sa.Column("direction", sa.String(32), nullable=False, server_default="MAKE_FROM_CHILDREN"),
        sa.Column("loss_factor", sa.Numeric(6,4), nullable=False, server_default="0"),
    )
    op.create_index("ix_assemblies_parent", "assemblies", ["parent_product_id"])
    op.create_index("ix_assemblies_child", "assemblies", ["child_product_id"])

    op.create_table(
        "product_channel_links",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False, server_default="shopify"),
        sa.Column("shopify_product_id", sa.String(64), nullable=True),
        sa.Column("shopify_variant_id", sa.String(64), nullable=True),
        sa.Column("shopify_location_id", sa.String(64), nullable=True),
        sa.UniqueConstraint("product_id", "channel", name="uq_product_channel"),
    )
    op.create_index("ix_product_channel_links_product", "product_channel_links", ["product_id"])

    # Optional: lightweight reservations for order→fulfilment gap
    op.create_table(
        "inventory_reservations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), nullable=False),
        sa.Column("qty_canonical", sa.Numeric(18,6), nullable=False),  # store in canonical units
        sa.Column("source", sa.String(16), nullable=False),            # 'shopify'|'internal'
        sa.Column("reference_id", sa.String(128), nullable=True),      # e.g., Shopify order id
        sa.Column("status", sa.String(16), nullable=False, server_default="ACTIVE"), # ACTIVE|RELEASED|COMMITTED
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_inventory_reservations_product", "inventory_reservations", ["product_id"])


def downgrade():
    op.drop_index("ix_inventory_reservations_product", table_name="inventory_reservations")
    op.drop_table("inventory_reservations")

    op.drop_index("ix_product_channel_links_product", table_name="product_channel_links")
    op.drop_table("product_channel_links")

    op.drop_index("ix_assemblies_parent", table_name="assemblies")
    op.drop_index("ix_assemblies_child", table_name="assemblies")
    op.drop_table("assemblies")


