"""add_raw_material_suppliers_junction_table

Revision ID: 4e5525d232e0
Revises: adb7b8daaa40
Create Date: 2025-10-26 21:35:16.392621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e5525d232e0'
down_revision: Union[str, None] = 'adb7b8daaa40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create raw_material_suppliers table
    op.create_table('raw_material_suppliers',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('raw_material_id', sa.String(length=36), nullable=False),
    sa.Column('supplier_id', sa.String(length=36), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=True),
    sa.Column('min_qty', sa.Numeric(precision=12, scale=3), nullable=True),
    sa.Column('lead_time_days', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['raw_material_id'], ['raw_materials.id'], name=op.f('fk_raw_material_suppliers__raw_material_id__raw_materials')),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], name=op.f('fk_raw_material_suppliers__supplier_id__suppliers')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_raw_material_suppliers')),
    sa.UniqueConstraint('raw_material_id', 'supplier_id', name='uq_rm_supplier')
    )
    op.create_index('ix_rm_supplier_material', 'raw_material_suppliers', ['raw_material_id'], unique=False)
    op.create_index('ix_rm_supplier_supplier', 'raw_material_suppliers', ['supplier_id'], unique=False)


def downgrade() -> None:
    # Drop raw_material_suppliers table
    op.drop_index('ix_rm_supplier_supplier', table_name='raw_material_suppliers')
    op.drop_index('ix_rm_supplier_material', table_name='raw_material_suppliers')
    op.drop_table('raw_material_suppliers')
