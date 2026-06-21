"""Add contact_id to customers (link to Contact for sales customer list).

Revision ID: 20250223_cust_contact
Revises: 20250223_merge
Create Date: 2025-02-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250223_cust_contact"
down_revision: Union[str, None] = "20250223_merge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "customers" not in insp.get_table_names():
        return
    if _has_column(insp, "customers", "contact_id"):
        return

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("customers", schema=None) as batch_op:
            batch_op.add_column(sa.Column("contact_id", sa.String(36), nullable=True))
            batch_op.create_foreign_key(
                "fk_customers_contact_id_contacts",
                "contacts",
                ["contact_id"],
                ["id"],
            )
            batch_op.create_index(
                "ix_customers_contact_id", ["contact_id"], unique=False
            )
    else:
        op.add_column(
            "customers", sa.Column("contact_id", sa.String(36), nullable=True)
        )
        op.create_foreign_key(
            "fk_customers_contact_id_contacts",
            "customers",
            "contacts",
            ["contact_id"],
            ["id"],
        )
        op.create_index(
            "ix_customers_contact_id", "customers", ["contact_id"], unique=False
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "customers" not in insp.get_table_names():
        return
    if not _has_column(insp, "customers", "contact_id"):
        return

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("customers", schema=None) as batch_op:
            batch_op.drop_index("ix_customers_contact_id")
            batch_op.drop_constraint(
                "fk_customers_contact_id_contacts", type_="foreignkey"
            )
            batch_op.drop_column("contact_id")
    else:
        op.drop_index("ix_customers_contact_id", table_name="customers")
        op.drop_constraint(
            "fk_customers_contact_id_contacts", "customers", type_="foreignkey"
        )
        op.drop_column("customers", "contact_id")
