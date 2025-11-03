"""add_excise_rates_table_and_product_pricing_fields

Revision ID: bf78b64511f2
Revises: 788e64e924f6
Create Date: 2025-11-02 15:09:18.021047

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bf78b64511f2"
down_revision: Union[str, None] = "788e64e924f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create excise_rates table
    op.create_table(
        "excise_rates",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("date_active_from", sa.DateTime(), nullable=False),
        sa.Column("rate_per_l_abv", sa.Numeric(10, 4), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_excise_rates_date_active_from"),
        "excise_rates",
        ["date_active_from"],
        unique=False,
    )

    # Add new pricing fields to products for each price tier (incGST, exGST, excise)
    # Retail price tier
    op.add_column(
        "products",
        sa.Column(
            "retail_price_inc_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "retail_price_ex_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column("retail_excise", sa.Numeric(precision=10, scale=2), nullable=True),
    )

    # Wholesale price tier
    op.add_column(
        "products",
        sa.Column(
            "wholesale_price_inc_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "wholesale_price_ex_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column("wholesale_excise", sa.Numeric(precision=10, scale=2), nullable=True),
    )

    # Distributor price tier
    op.add_column(
        "products",
        sa.Column(
            "distributor_price_inc_gst",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "distributor_price_ex_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "distributor_excise", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )

    # Counter price tier
    op.add_column(
        "products",
        sa.Column(
            "counter_price_inc_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "counter_price_ex_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column("counter_excise", sa.Numeric(precision=10, scale=2), nullable=True),
    )

    # Trade price tier
    op.add_column(
        "products",
        sa.Column(
            "trade_price_inc_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "trade_price_ex_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column("trade_excise", sa.Numeric(precision=10, scale=2), nullable=True),
    )

    # Contract price tier
    op.add_column(
        "products",
        sa.Column(
            "contract_price_inc_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "contract_price_ex_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column("contract_excise", sa.Numeric(precision=10, scale=2), nullable=True),
    )

    # Industrial price tier
    op.add_column(
        "products",
        sa.Column(
            "industrial_price_inc_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "industrial_price_ex_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "industrial_excise", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )

    # Add purchase cost fields (incGST, exGST)
    op.add_column(
        "products",
        sa.Column(
            "purchase_cost_inc_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "purchase_cost_ex_gst", sa.Numeric(precision=10, scale=2), nullable=True
        ),
    )


def downgrade() -> None:
    # Remove purchase cost fields
    op.drop_column("products", "purchase_cost_ex_gst")
    op.drop_column("products", "purchase_cost_inc_gst")

    # Remove industrial price tier fields
    op.drop_column("products", "industrial_excise")
    op.drop_column("products", "industrial_price_ex_gst")
    op.drop_column("products", "industrial_price_inc_gst")

    # Remove contract price tier fields
    op.drop_column("products", "contract_excise")
    op.drop_column("products", "contract_price_ex_gst")
    op.drop_column("products", "contract_price_inc_gst")

    # Remove trade price tier fields
    op.drop_column("products", "trade_excise")
    op.drop_column("products", "trade_price_ex_gst")
    op.drop_column("products", "trade_price_inc_gst")

    # Remove counter price tier fields
    op.drop_column("products", "counter_excise")
    op.drop_column("products", "counter_price_ex_gst")
    op.drop_column("products", "counter_price_inc_gst")

    # Remove distributor price tier fields
    op.drop_column("products", "distributor_excise")
    op.drop_column("products", "distributor_price_ex_gst")
    op.drop_column("products", "distributor_price_inc_gst")

    # Remove wholesale price tier fields
    op.drop_column("products", "wholesale_excise")
    op.drop_column("products", "wholesale_price_ex_gst")
    op.drop_column("products", "wholesale_price_inc_gst")

    # Remove retail price tier fields
    op.drop_column("products", "retail_excise")
    op.drop_column("products", "retail_price_ex_gst")
    op.drop_column("products", "retail_price_inc_gst")

    # Drop excise_rates table
    op.drop_index(op.f("ix_excise_rates_date_active_from"), table_name="excise_rates")
    op.drop_table("excise_rates")
