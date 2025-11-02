"""add_unified_contacts_table

Revision ID: 5809474d8078
Revises: 94253da44e13
Create Date: 2025-11-01 08:22:22.274514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5809474d8078'
down_revision: Union[str, None] = '94253da44e13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unified contacts table for customers, suppliers, and other contacts."""
    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        
        # Contact type flags (can be multiple)
        sa.Column('is_customer', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_supplier', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_other', sa.Boolean(), nullable=False, server_default='0'),
        
        # Additional fields
        sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('xero_contact_id', sa.String(length=100), nullable=True),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_contact_code', 'contacts', ['code'], unique=True)
    op.create_index('ix_contact_type', 'contacts', ['is_customer', 'is_supplier', 'is_other'])
    op.create_index('ix_contacts_is_customer', 'contacts', ['is_customer'])
    op.create_index('ix_contacts_is_supplier', 'contacts', ['is_supplier'])


def downgrade() -> None:
    """Remove contacts table."""
    op.drop_index('ix_contacts_is_supplier', table_name='contacts')
    op.drop_index('ix_contacts_is_customer', table_name='contacts')
    op.drop_index('ix_contact_type', table_name='contacts')
    op.drop_index('ix_contact_code', table_name='contacts')
    op.drop_table('contacts')
