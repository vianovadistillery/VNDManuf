"""change_price_columns_to_numeric

Revision ID: 788e64e924f6
Revises: 2b0eead645b5
Create Date: 2025-11-02 14:48:29.735987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '788e64e924f6'
down_revision: Union[str, None] = '2b0eead645b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change price columns from String(1) to Numeric(10,2)
    # SQLite requires special handling - need to recreate table or use ALTER COLUMN syntax
    
    # For SQLite, we'll use a workaround since ALTER COLUMN is limited
    # For PostgreSQL, we can use ALTER COLUMN directly
    
    # Check database type
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == 'sqlite'
    
    if is_sqlite:
        # SQLite workaround: need to recreate the column
        # First, add new columns with temporary names
        op.add_column('products', sa.Column('wholesalecde_new', sa.Numeric(10, 2), nullable=True))
        op.add_column('products', sa.Column('retailcde_new', sa.Numeric(10, 2), nullable=True))
        op.add_column('products', sa.Column('countercde_new', sa.Numeric(10, 2), nullable=True))
        op.add_column('products', sa.Column('tradecde_new', sa.Numeric(10, 2), nullable=True))
        op.add_column('products', sa.Column('contractcde_new', sa.Numeric(10, 2), nullable=True))
        op.add_column('products', sa.Column('industrialcde_new', sa.Numeric(10, 2), nullable=True))
        op.add_column('products', sa.Column('distributorcde_new', sa.Numeric(10, 2), nullable=True))
        
        # Copy data (attempting to convert string to numeric where possible)
        op.execute("""
            UPDATE products 
            SET wholesalecde_new = CASE 
                WHEN wholesalecde IS NULL OR wholesalecde = '' THEN NULL
                ELSE CAST(wholesalecde AS REAL)
            END
        """)
        op.execute("""
            UPDATE products 
            SET retailcde_new = CASE 
                WHEN retailcde IS NULL OR retailcde = '' THEN NULL
                ELSE CAST(retailcde AS REAL)
            END
        """)
        op.execute("""
            UPDATE products 
            SET countercde_new = CASE 
                WHEN countercde IS NULL OR countercde = '' THEN NULL
                ELSE CAST(countercde AS REAL)
            END
        """)
        op.execute("""
            UPDATE products 
            SET tradecde_new = CASE 
                WHEN tradecde IS NULL OR tradecde = '' THEN NULL
                ELSE CAST(tradecde AS REAL)
            END
        """)
        op.execute("""
            UPDATE products 
            SET contractcde_new = CASE 
                WHEN contractcde IS NULL OR contractcde = '' THEN NULL
                ELSE CAST(contractcde AS REAL)
            END
        """)
        op.execute("""
            UPDATE products 
            SET industrialcde_new = CASE 
                WHEN industrialcde IS NULL OR industrialcde = '' THEN NULL
                ELSE CAST(industrialcde AS REAL)
            END
        """)
        op.execute("""
            UPDATE products 
            SET distributorcde_new = CASE 
                WHEN distributorcde IS NULL OR distributorcde = '' THEN NULL
                ELSE CAST(distributorcde AS REAL)
            END
        """)
        
        # Drop old columns
        op.drop_column('products', 'wholesalecde')
        op.drop_column('products', 'retailcde')
        op.drop_column('products', 'countercde')
        op.drop_column('products', 'tradecde')
        op.drop_column('products', 'contractcde')
        op.drop_column('products', 'industrialcde')
        op.drop_column('products', 'distributorcde')
        
        # Rename new columns
        op.alter_column('products', 'wholesalecde_new', new_column_name='wholesalecde')
        op.alter_column('products', 'retailcde_new', new_column_name='retailcde')
        op.alter_column('products', 'countercde_new', new_column_name='countercde')
        op.alter_column('products', 'tradecde_new', new_column_name='tradecde')
        op.alter_column('products', 'contractcde_new', new_column_name='contractcde')
        op.alter_column('products', 'industrialcde_new', new_column_name='industrialcde')
        op.alter_column('products', 'distributorcde_new', new_column_name='distributorcde')
    else:
        # PostgreSQL and other databases can use ALTER COLUMN
        op.alter_column('products', 'wholesalecde',
                       type_=sa.Numeric(10, 2),
                       existing_type=sa.String(1),
                       postgresql_using='CAST(wholesalecde AS NUMERIC(10,2))')
        op.alter_column('products', 'retailcde',
                       type_=sa.Numeric(10, 2),
                       existing_type=sa.String(1),
                       postgresql_using='CAST(retailcde AS NUMERIC(10,2))')
        op.alter_column('products', 'countercde',
                       type_=sa.Numeric(10, 2),
                       existing_type=sa.String(1),
                       postgresql_using='CAST(countercde AS NUMERIC(10,2))')
        op.alter_column('products', 'tradecde',
                       type_=sa.Numeric(10, 2),
                       existing_type=sa.String(1),
                       postgresql_using='CAST(tradecde AS NUMERIC(10,2))')
        op.alter_column('products', 'contractcde',
                       type_=sa.Numeric(10, 2),
                       existing_type=sa.String(1),
                       postgresql_using='CAST(contractcde AS NUMERIC(10,2))')
        op.alter_column('products', 'industrialcde',
                       type_=sa.Numeric(10, 2),
                       existing_type=sa.String(1),
                       postgresql_using='CAST(industrialcde AS NUMERIC(10,2))')
        op.alter_column('products', 'distributorcde',
                       type_=sa.Numeric(10, 2),
                       existing_type=sa.String(1),
                       postgresql_using='CAST(distributorcde AS NUMERIC(10,2))')


def downgrade() -> None:
    # Revert price columns back to String(1)
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == 'sqlite'
    
    if is_sqlite:
        # SQLite workaround
        op.add_column('products', sa.Column('wholesalecde_old', sa.String(1), nullable=True))
        op.add_column('products', sa.Column('retailcde_old', sa.String(1), nullable=True))
        op.add_column('products', sa.Column('countercde_old', sa.String(1), nullable=True))
        op.add_column('products', sa.Column('tradecde_old', sa.String(1), nullable=True))
        op.add_column('products', sa.Column('contractcde_old', sa.String(1), nullable=True))
        op.add_column('products', sa.Column('industrialcde_old', sa.String(1), nullable=True))
        op.add_column('products', sa.Column('distributorcde_old', sa.String(1), nullable=True))
        
        # Copy data back (truncate to 1 character)
        op.execute("""
            UPDATE products 
            SET wholesalecde_old = SUBSTR(CAST(wholesalecde AS TEXT), 1, 1)
        """)
        op.execute("""
            UPDATE products 
            SET retailcde_old = SUBSTR(CAST(retailcde AS TEXT), 1, 1)
        """)
        op.execute("""
            UPDATE products 
            SET countercde_old = SUBSTR(CAST(countercde AS TEXT), 1, 1)
        """)
        op.execute("""
            UPDATE products 
            SET tradecde_old = SUBSTR(CAST(tradecde AS TEXT), 1, 1)
        """)
        op.execute("""
            UPDATE products 
            SET contractcde_old = SUBSTR(CAST(contractcde AS TEXT), 1, 1)
        """)
        op.execute("""
            UPDATE products 
            SET industrialcde_old = SUBSTR(CAST(industrialcde AS TEXT), 1, 1)
        """)
        op.execute("""
            UPDATE products 
            SET distributorcde_old = SUBSTR(CAST(distributorcde AS TEXT), 1, 1)
        """)
        
        op.drop_column('products', 'wholesalecde')
        op.drop_column('products', 'retailcde')
        op.drop_column('products', 'countercde')
        op.drop_column('products', 'tradecde')
        op.drop_column('products', 'contractcde')
        op.drop_column('products', 'industrialcde')
        op.drop_column('products', 'distributorcde')
        
        op.alter_column('products', 'wholesalecde_old', new_column_name='wholesalecde')
        op.alter_column('products', 'retailcde_old', new_column_name='retailcde')
        op.alter_column('products', 'countercde_old', new_column_name='countercde')
        op.alter_column('products', 'tradecde_old', new_column_name='tradecde')
        op.alter_column('products', 'contractcde_old', new_column_name='contractcde')
        op.alter_column('products', 'industrialcde_old', new_column_name='industrialcde')
        op.alter_column('products', 'distributorcde_old', new_column_name='distributorcde')
    else:
        # PostgreSQL
        op.alter_column('products', 'wholesalecde',
                       type_=sa.String(1),
                       existing_type=sa.Numeric(10, 2))
        op.alter_column('products', 'retailcde',
                       type_=sa.String(1),
                       existing_type=sa.Numeric(10, 2))
        op.alter_column('products', 'countercde',
                       type_=sa.String(1),
                       existing_type=sa.Numeric(10, 2))
        op.alter_column('products', 'tradecde',
                       type_=sa.String(1),
                       existing_type=sa.Numeric(10, 2))
        op.alter_column('products', 'contractcde',
                       type_=sa.String(1),
                       existing_type=sa.Numeric(10, 2))
        op.alter_column('products', 'industrialcde',
                       type_=sa.String(1),
                       existing_type=sa.Numeric(10, 2))
        op.alter_column('products', 'distributorcde',
                       type_=sa.String(1),
                       existing_type=sa.Numeric(10, 2))
