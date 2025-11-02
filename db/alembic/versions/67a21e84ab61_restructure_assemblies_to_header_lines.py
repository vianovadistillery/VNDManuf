"""restructure_assemblies_to_header_lines

Revision ID: 67a21e84ab61
Revises: 0afdf02085a6
Create Date: 2025-11-02 21:05:34.249982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '67a21e84ab61'
down_revision: Union[str, None] = '0afdf02085a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if assembly_lines table exists
    connection = op.get_bind()
    inspector = inspect(connection)
    tables = inspector.get_table_names()
    assemblies_columns = [col['name'] for col in inspector.get_columns('assemblies')]
    
    # Create assembly_lines table for line items if not exists
    if 'assembly_lines' not in tables:
        op.create_table('assembly_lines',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('assembly_id', sa.String(length=36), nullable=False),
        sa.Column('component_product_id', sa.String(length=36), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('unit', sa.String(length=10), nullable=True),
        sa.Column('is_energy_or_overhead', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['assembly_id'], ['assemblies.id'], name=op.f('fk_assembly_lines__assembly_id__assemblies')),
        sa.ForeignKeyConstraint(['component_product_id'], ['products.id'], name=op.f('fk_assembly_lines__component_product_id__products')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_assembly_lines')),
        sa.UniqueConstraint('assembly_id', 'sequence', name='uq_assembly_line_sequence')
        )
        op.create_index('ix_assembly_line_assembly', 'assembly_lines', ['assembly_id'], unique=False)
    
    # Add new columns if they don't exist
    with op.batch_alter_table('assemblies') as batch_op:
        if 'assembly_code' not in assemblies_columns:
            batch_op.add_column(sa.Column('assembly_code', sa.String(length=50), nullable=True))
        if 'assembly_name' not in assemblies_columns:
            batch_op.add_column(sa.Column('assembly_name', sa.String(length=200), nullable=True))
        if 'notes' in assemblies_columns:
            # Check current type and only alter if needed
            current_col = next(col for col in inspector.get_columns('assemblies') if col['name'] == 'notes')
            if hasattr(current_col['type'], 'length') and current_col['type'].length == 255:
                batch_op.alter_column('notes', type_=sa.Text(), existing_type=sa.VARCHAR(length=255))
    
    # Migrate existing data: create assembly from old single-child structure
    op.execute("""
        UPDATE assemblies 
        SET assembly_code = 'MIGRATED-1',
            assembly_name = 'Migrated Assembly'
        WHERE assembly_code IS NULL OR assembly_code = ''
    """)
    
    # Make columns NOT NULL
    with op.batch_alter_table('assemblies') as batch_op:
        batch_op.alter_column('assembly_code', nullable=False)
        batch_op.alter_column('assembly_name', nullable=False)
        if 'version' in assemblies_columns:
            batch_op.alter_column('version', nullable=False)
        if 'is_primary' in assemblies_columns:
            batch_op.alter_column('is_primary', nullable=False)
        if 'is_active' in assemblies_columns:
            batch_op.alter_column('is_active', nullable=False)
    
    # Migrate old single-child data to assembly_lines
    op.execute("""
        INSERT OR IGNORE INTO assembly_lines (id, assembly_id, component_product_id, quantity, sequence, unit, is_energy_or_overhead, notes)
        SELECT 
            lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))), 1, 1) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))), 1, 1) || '-' || lower(hex(randomblob(12))) as id,
            a.id as assembly_id,
            a.child_product_id as component_product_id,
            a.ratio as quantity,
            1 as sequence,
            NULL as unit,
            COALESCE(a.is_energy_or_overhead, 0) as is_energy_or_overhead,
            NULL as notes
        FROM assemblies a
        WHERE a.child_product_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM assembly_lines al 
            WHERE al.assembly_id = a.id
        )
    """)
    
    # Drop old columns
    with op.batch_alter_table('assemblies') as batch_op:
        if 'direction' in assemblies_columns:
            batch_op.drop_column('direction')
        if 'child_product_id' in assemblies_columns:
            batch_op.drop_column('child_product_id')
        if 'ratio' in assemblies_columns:
            batch_op.drop_column('ratio')
        if 'is_energy_or_overhead' in assemblies_columns:
            batch_op.drop_column('is_energy_or_overhead')
        if 'sequence' in assemblies_columns:
            batch_op.drop_column('sequence')
        if 'loss_factor' in assemblies_columns:
            batch_op.drop_column('loss_factor')
    
    # Create new indexes and constraints
    indexes = [idx['name'] for idx in inspector.get_indexes('assemblies')]
    if 'ix_assemblies_primary' not in indexes:
        op.create_index('ix_assemblies_primary', 'assemblies', ['parent_product_id', 'is_primary', 'is_active'], unique=False)
    
    # Note: Unique constraint will be added in a follow-up migration using batch_alter_table
    # as SQLite doesn't support ADD CONSTRAINT directly


def downgrade() -> None:
    # Drop constraints and indexes
    inspector = inspect(op.get_bind())
    
    constraints = [c['name'] for c in inspector.get_unique_constraints('assemblies')]
    if 'uq_assembly_version' in constraints:
        op.drop_constraint('uq_assembly_version', 'assemblies', type_='unique')
    
    indexes = [idx['name'] for idx in inspector.get_indexes('assemblies')]
    if 'ix_assemblies_primary' in indexes:
        op.drop_index('ix_assemblies_primary', table_name='assemblies')
    
    # Add back old columns
    with op.batch_alter_table('assemblies') as batch_op:
        batch_op.add_column(sa.Column('direction', sa.VARCHAR(length=32), server_default="MAKE_FROM_CHILDREN", nullable=False))
        batch_op.add_column(sa.Column('child_product_id', sa.VARCHAR(length=36), nullable=True))
        batch_op.add_column(sa.Column('ratio', sa.Numeric(precision=18, scale=6), nullable=True))
        batch_op.add_column(sa.Column('is_energy_or_overhead', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('sequence', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('loss_factor', sa.NUMERIC(precision=6, scale=4), nullable=True))
        batch_op.alter_column('notes', type_=sa.VARCHAR(length=255), existing_type=sa.Text())
        batch_op.alter_column('is_active', nullable=True)
        batch_op.alter_column('is_primary', nullable=True)
        batch_op.alter_column('version', nullable=True)
    
    # Migrate line data back (take first line if multiple)
    op.execute("""
        UPDATE assemblies a
        SET child_product_id = (
            SELECT al.component_product_id 
            FROM assembly_lines al 
            WHERE al.assembly_id = a.id 
            ORDER BY al.sequence 
            LIMIT 1
        ),
        ratio = (
            SELECT al.quantity 
            FROM assembly_lines al 
            WHERE al.assembly_id = a.id 
            ORDER BY al.sequence 
            LIMIT 1
        ),
        is_energy_or_overhead = (
            SELECT al.is_energy_or_overhead 
            FROM assembly_lines al 
            WHERE al.assembly_id = a.id 
            ORDER BY al.sequence 
            LIMIT 1
        ),
        sequence = 1,
        loss_factor = 0
        WHERE EXISTS (SELECT 1 FROM assembly_lines al WHERE al.assembly_id = a.id)
    """)
    
    # Make ratio not null after migration
    with op.batch_alter_table('assemblies') as batch_op:
        batch_op.alter_column('ratio', nullable=False)
        batch_op.alter_column('loss_factor', nullable=False)
        batch_op.alter_column('direction', nullable=False)
    
    # Drop new columns
    with op.batch_alter_table('assemblies') as batch_op:
        batch_op.drop_column('assembly_name')
        batch_op.drop_column('assembly_code')
    
    # Drop assembly_lines table
    op.drop_index('ix_assembly_line_assembly', table_name='assembly_lines')
    op.drop_table('assembly_lines')

