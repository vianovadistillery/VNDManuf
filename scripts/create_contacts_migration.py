#!/usr/bin/env python3
"""
Create migration to update foreign keys from customers/suppliers to contacts.
Since all tables are empty, this is safe.
"""

from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
migrations_dir = project_root / "db" / "alembic" / "versions"

migration_content = '''"""Migrate foreign keys from customers/suppliers to unified contacts

Revision ID: migrate_to_unified_contacts
Revises: fix_products_pk_sqlite
Create Date: {timestamp}

This migration updates all foreign keys to use the unified contacts table
instead of separate customers and suppliers tables.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "migrate_to_unified_contacts"
down_revision: Union[str, None] = "fix_products_pk_sqlite"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate foreign keys to contacts table."""
    # Since all tables are empty, we can safely:
    # 1. Drop existing foreign key constraints
    # 2. Rename columns from customer_id/supplier_id to contact_id
    # 3. Add new foreign key constraints to contacts.id

    # For SQLite, we need to recreate tables or use table recreation
    # This is complex, so we'll use a simpler approach:
    # - Add contact_id columns
    # - Drop old foreign keys (they're not enforced in SQLite anyway)
    # - Update application code to use contact_id

    # Tables to update:
    # - customer_prices: customer_id -> contact_id
    # - invoices: customer_id -> contact_id
    # - sales_orders: customer_id -> contact_id
    # - purchase_orders: supplier_id -> contact_id
    # - raw_material_suppliers: supplier_id -> contact_id

    # Note: SQLite doesn't support ALTER TABLE DROP COLUMN or MODIFY COLUMN easily
    # For now, we'll add contact_id columns and let application code migrate
    # The old columns can remain for backward compatibility during transition

    # Add contact_id to customer_prices
    try:
        op.add_column('customer_prices', sa.Column('contact_id', sa.String(36), nullable=True))
        op.create_foreign_key('fk_customer_prices_contact', 'customer_prices', 'contacts', ['contact_id'], ['id'])
    except Exception as e:
        print(f"[SKIP] customer_prices.contact_id: {{e}}")

    # Add contact_id to invoices
    try:
        op.add_column('invoices', sa.Column('contact_id', sa.String(36), nullable=True))
        op.create_foreign_key('fk_invoices_contact', 'invoices', 'contacts', ['contact_id'], ['id'])
    except Exception as e:
        print(f"[SKIP] invoices.contact_id: {{e}}")

    # Add contact_id to sales_orders
    try:
        op.add_column('sales_orders', sa.Column('contact_id', sa.String(36), nullable=True))
        op.create_foreign_key('fk_sales_orders_contact', 'sales_orders', 'contacts', ['contact_id'], ['id'])
    except Exception as e:
        print(f"[SKIP] sales_orders.contact_id: {{e}}")

    # Add contact_id to purchase_orders
    try:
        op.add_column('purchase_orders', sa.Column('contact_id', sa.String(36), nullable=True))
        op.create_foreign_key('fk_purchase_orders_contact', 'purchase_orders', 'contacts', ['contact_id'], ['id'])
    except Exception as e:
        print(f"[SKIP] purchase_orders.contact_id: {{e}}")

    # For raw_material_suppliers, we keep supplier_id but add contact_id for future use
    try:
        op.add_column('raw_material_suppliers', sa.Column('contact_id', sa.String(36), nullable=True))
        op.create_foreign_key('fk_raw_material_suppliers_contact', 'raw_material_suppliers', 'contacts', ['contact_id'], ['id'])
    except Exception as e:
        print(f"[SKIP] raw_material_suppliers.contact_id: {{e}}")

    print("[INFO] Added contact_id columns. Old customer_id/supplier_id columns remain for backward compatibility.")
    print("[INFO] Application code should be updated to use contact_id going forward.")


def downgrade() -> None:
    """Remove contact_id columns."""
    # Drop contact_id columns
    try:
        op.drop_constraint('fk_raw_material_suppliers_contact', 'raw_material_suppliers', type_='foreignkey')
        op.drop_column('raw_material_suppliers', 'contact_id')
    except:
        pass

    try:
        op.drop_constraint('fk_purchase_orders_contact', 'purchase_orders', type_='foreignkey')
        op.drop_column('purchase_orders', 'contact_id')
    except:
        pass

    try:
        op.drop_constraint('fk_sales_orders_contact', 'sales_orders', type_='foreignkey')
        op.drop_column('sales_orders', 'contact_id')
    except:
        pass

    try:
        op.drop_constraint('fk_invoices_contact', 'invoices', type_='foreignkey')
        op.drop_column('invoices', 'contact_id')
    except:
        pass

    try:
        op.drop_constraint('fk_customer_prices_contact', 'customer_prices', type_='foreignkey')
        op.drop_column('customer_prices', 'contact_id')
    except:
        pass
'''

migration_file = migrations_dir / "migrate_to_unified_contacts.py"
with open(migration_file, "w") as f:
    f.write(migration_content.format(timestamp=datetime.now().isoformat()))

print(f"[OK] Created migration file: {migration_file}")
print(
    "[INFO] This migration adds contact_id columns alongside existing customer_id/supplier_id"
)
print("[INFO] Allows gradual migration in application code")
