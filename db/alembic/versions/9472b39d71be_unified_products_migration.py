"""unified_products_migration

Revision ID: 9472b39d71be
Revises: 262c7cd34fdd
Create Date: 2025-10-31 11:00:15.079313

"""

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "9472b39d71be"
down_revision: Union[str, None] = "262c7cd34fdd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate raw_materials and finished_goods to unified products table."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Step 1: Add product_type column to products (nullable initially)
    # Check existing columns to avoid duplicates
    products_columns = [col["name"] for col in inspector.get_columns("products")]

    with op.batch_alter_table("products", schema=None) as batch_op:
        if "product_type" not in products_columns:
            batch_op.add_column(
                sa.Column("product_type", sa.String(length=20), nullable=True)
            )
        if "raw_material_group_id" not in products_columns:
            batch_op.add_column(
                sa.Column("raw_material_group_id", sa.String(length=36), nullable=True)
            )

        # Raw Material specific fields
        if "raw_material_code" not in products_columns:
            batch_op.add_column(
                sa.Column("raw_material_code", sa.Integer(), nullable=True)
            )
        if "raw_material_search_key" not in products_columns:
            batch_op.add_column(
                sa.Column("raw_material_search_key", sa.String(length=5), nullable=True)
            )
        if "raw_material_search_ext" not in products_columns:
            batch_op.add_column(
                sa.Column("raw_material_search_ext", sa.String(length=8), nullable=True)
            )
        if "specific_gravity" not in products_columns:
            batch_op.add_column(
                sa.Column(
                    "specific_gravity", sa.Numeric(precision=10, scale=6), nullable=True
                )
            )
        if "vol_solid" not in products_columns:
            batch_op.add_column(
                sa.Column("vol_solid", sa.Numeric(precision=10, scale=6), nullable=True)
            )
        if "solid_sg" not in products_columns:
            batch_op.add_column(
                sa.Column("solid_sg", sa.Numeric(precision=10, scale=6), nullable=True)
            )
        if "wt_solid" not in products_columns:
            batch_op.add_column(
                sa.Column("wt_solid", sa.Numeric(precision=10, scale=6), nullable=True)
            )
        if "usage_unit" not in products_columns:
            batch_op.add_column(
                sa.Column("usage_unit", sa.String(length=2), nullable=True)
            )
        if "usage_cost" not in products_columns:
            batch_op.add_column(
                sa.Column(
                    "usage_cost", sa.Numeric(precision=10, scale=2), nullable=True
                )
            )
        if "restock_level" not in products_columns:
            batch_op.add_column(
                sa.Column(
                    "restock_level", sa.Numeric(precision=12, scale=3), nullable=True
                )
            )
        if "used_ytd" not in products_columns:
            batch_op.add_column(
                sa.Column("used_ytd", sa.Numeric(precision=12, scale=3), nullable=True)
            )
        if "hazard" not in products_columns:
            batch_op.add_column(sa.Column("hazard", sa.String(length=1), nullable=True))
        if "condition" not in products_columns:
            batch_op.add_column(
                sa.Column("condition", sa.String(length=1), nullable=True)
            )
        if "msds_flag" not in products_columns:
            batch_op.add_column(
                sa.Column("msds_flag", sa.String(length=1), nullable=True)
            )
        if "altno1" not in products_columns:
            batch_op.add_column(sa.Column("altno1", sa.Integer(), nullable=True))
        if "altno2" not in products_columns:
            batch_op.add_column(sa.Column("altno2", sa.Integer(), nullable=True))
        if "altno3" not in products_columns:
            batch_op.add_column(sa.Column("altno3", sa.Integer(), nullable=True))
        if "altno4" not in products_columns:
            batch_op.add_column(sa.Column("altno4", sa.Integer(), nullable=True))
        if "altno5" not in products_columns:
            batch_op.add_column(sa.Column("altno5", sa.Integer(), nullable=True))
        if "last_movement_date" not in products_columns:
            batch_op.add_column(
                sa.Column("last_movement_date", sa.String(length=8), nullable=True)
            )
        if "last_purchase_date" not in products_columns:
            batch_op.add_column(
                sa.Column("last_purchase_date", sa.String(length=8), nullable=True)
            )
        if "ean13_raw" not in products_columns:
            batch_op.add_column(
                sa.Column("ean13_raw", sa.Numeric(precision=18, scale=4), nullable=True)
            )
        if "xero_account" not in products_columns:
            batch_op.add_column(
                sa.Column("xero_account", sa.String(length=50), nullable=True)
            )

        # Finished Good specific fields
        if "formula_id" not in products_columns:
            batch_op.add_column(
                sa.Column("formula_id", sa.String(length=36), nullable=True)
            )
        if "formula_revision" not in products_columns:
            batch_op.add_column(
                sa.Column("formula_revision", sa.Integer(), nullable=True)
            )

    # Step 2: Create migration mapping table for tracking
    tables = inspector.get_table_names()

    if "product_migration_map" not in tables:
        op.create_table(
            "product_migration_map",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("legacy_table", sa.String(length=50), nullable=False),
            sa.Column("legacy_id", sa.String(length=36), nullable=False),
            sa.Column("product_id", sa.String(length=36), nullable=False),
            sa.Column("migrated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_migration_map_legacy",
            "product_migration_map",
            ["legacy_table", "legacy_id"],
        )

    # Step 3: Migrate raw_materials to products
    # Check if raw_materials table exists

    if "raw_materials" in tables:
        raw_materials_query = text(
            """
            SELECT
                id, code, desc1, desc2, search_key, search_ext,
                sg, vol_solid, solid_sg, wt_solid,
                purqty, purchase_cost, purchase_unit, deal_cost, sup_unit, sup_qty,
                usage_cost, usage_unit,
                group_id,
                active_flag,
                soh, opening_soh, soh_value, so_on_order, so_in_process, restock_level, used_ytd,
                hazard, condition, msds_flag,
                altno1, altno2, altno3, altno4, altno5,
                last_movement_date, last_purchase_date,
                notes,
                ean13,
                xero_account,
                created_at, updated_at
            FROM raw_materials
        """
        )

        raw_materials = connection.execute(raw_materials_query).fetchall()

        for rm in raw_materials:
            # Generate SKU from code if not exists
            sku = f"RM-{rm.code}" if rm.code else None
            name = rm.desc1 or f"Raw Material {rm.code}" if rm.code else "Raw Material"
            description = (
                (rm.desc1 or "") + " " + (rm.desc2 or "") if rm.desc2 else rm.desc1
            )

            # Check if product already exists (by SKU or legacy code)
            existing_query = text(
                """
                SELECT id FROM products
                WHERE sku = :sku OR raw_material_code = :code
            """
            )
            existing = connection.execute(
                existing_query, {"sku": sku, "code": rm.code}
            ).fetchone()

            if existing:
                product_id = existing[0]
                # Update existing product
                update_query = text(
                    """
                    UPDATE products SET
                        product_type = 'RAW',
                        raw_material_group_id = :group_id,
                        raw_material_code = :code,
                        raw_material_search_key = :search_key,
                        raw_material_search_ext = :search_ext,
                        specific_gravity = :sg,
                        vol_solid = :vol_solid,
                        solid_sg = :solid_sg,
                        wt_solid = :wt_solid,
                        usage_unit = :usage_unit,
                        usage_cost = :usage_cost,
                        restock_level = :restock_level,
                        used_ytd = :used_ytd,
                        hazard = :hazard,
                        condition = :condition,
                        msds_flag = :msds_flag,
                        altno1 = :altno1,
                        altno2 = :altno2,
                        altno3 = :altno3,
                        altno4 = :altno4,
                        altno5 = :altno5,
                        last_movement_date = :last_movement_date,
                        last_purchase_date = :last_purchase_date,
                        ean13_raw = :ean13,
                        xero_account = :xero_account
                    WHERE id = :product_id
                """
                )
                connection.execute(
                    update_query,
                    {
                        "group_id": rm.group_id,
                        "code": rm.code,
                        "search_key": rm.search_key,
                        "search_ext": rm.search_ext,
                        "sg": rm.sg,
                        "vol_solid": rm.vol_solid,
                        "solid_sg": rm.solid_sg,
                        "wt_solid": rm.wt_solid,
                        "usage_unit": rm.usage_unit,
                        "usage_cost": rm.usage_cost,
                        "restock_level": rm.restock_level,
                        "used_ytd": rm.used_ytd,
                        "hazard": rm.hazard,
                        "condition": rm.condition,
                        "msds_flag": rm.msds_flag,
                        "altno1": rm.altno1,
                        "altno2": rm.altno2,
                        "altno3": rm.altno3,
                        "altno4": rm.altno4,
                        "altno5": rm.altno5,
                        "last_movement_date": rm.last_movement_date,
                        "last_purchase_date": rm.last_purchase_date,
                        "ean13": rm.ean13,
                        "xero_account": rm.xero_account,
                        "product_id": product_id,
                    },
                )
            else:
                # Create new product
                import uuid

                product_id = str(uuid.uuid4())
                insert_query = text(
                    """
                    INSERT INTO products (
                        id, sku, name, description, product_type,
                        raw_material_group_id, raw_material_code,
                        raw_material_search_key, raw_material_search_ext,
                        specific_gravity, vol_solid, solid_sg, wt_solid,
                        usage_unit, usage_cost, restock_level, used_ytd,
                        hazard, condition, msds_flag,
                        altno1, altno2, altno3, altno4, altno5,
                        last_movement_date, last_purchase_date,
                        ean13_raw, xero_account,
                        base_unit, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :sku, :name, :description, 'RAW',
                        :group_id, :code,
                        :search_key, :search_ext,
                        :sg, :vol_solid, :solid_sg, :wt_solid,
                        :usage_unit, :usage_cost, :restock_level, :used_ytd,
                        :hazard, :condition, :msds_flag,
                        :altno1, :altno2, :altno3, :altno4, :altno5,
                        :last_movement_date, :last_purchase_date,
                        :ean13, :xero_account,
                        'KG', :is_active, :created_at, :updated_at
                    )
                """
                )
                connection.execute(
                    insert_query,
                    {
                        "id": product_id,
                        "sku": sku,
                        "name": name,
                        "description": description,
                        "group_id": rm.group_id,
                        "code": rm.code,
                        "search_key": rm.search_key,
                        "search_ext": rm.search_ext,
                        "sg": rm.sg,
                        "vol_solid": rm.vol_solid,
                        "solid_sg": rm.solid_sg,
                        "wt_solid": rm.wt_solid,
                        "usage_unit": rm.usage_unit,
                        "usage_cost": rm.usage_cost,
                        "restock_level": rm.restock_level,
                        "used_ytd": rm.used_ytd,
                        "hazard": rm.hazard,
                        "condition": rm.condition,
                        "msds_flag": rm.msds_flag,
                        "altno1": rm.altno1,
                        "altno2": rm.altno2,
                        "altno3": rm.altno3,
                        "altno4": rm.altno4,
                        "altno5": rm.altno5,
                        "last_movement_date": rm.last_movement_date,
                        "last_purchase_date": rm.last_purchase_date,
                        "ean13": rm.ean13,
                        "xero_account": rm.xero_account,
                        "is_active": rm.active_flag == "A" if rm.active_flag else True,
                        "created_at": rm.created_at or datetime.utcnow(),
                        "updated_at": rm.updated_at or datetime.utcnow(),
                    },
                )

            # Record migration mapping
            map_id = str(uuid.uuid4())
            map_query = text(
                """
                INSERT INTO product_migration_map (id, legacy_table, legacy_id, product_id, migrated_at)
                VALUES (:id, 'raw_materials', :legacy_id, :product_id, :migrated_at)
            """
            )
            connection.execute(
                map_query,
                {
                    "id": map_id,
                    "legacy_id": rm.id,
                    "product_id": product_id,
                    "migrated_at": datetime.utcnow(),
                },
            )

            # Migrate raw_materials.soh to inventory_lots if exists
            if rm.soh and rm.soh > 0:
                lot_query = text(
                    """
                    INSERT INTO inventory_lots (
                        id, product_id, lot_code, quantity_kg, unit_cost, received_at, is_active, created_at
                    )
                    SELECT
                        :lot_id, :product_id, :lot_code, :qty, :cost, :received_at, 1, :created_at
                    WHERE NOT EXISTS (
                        SELECT 1 FROM inventory_lots WHERE product_id = :product_id AND lot_code = :lot_code
                    )
                """
                )
                lot_id = str(uuid.uuid4())
                lot_code = f"LEGACY-RM-{rm.code}" if rm.code else f"LEGACY-{rm.id[:8]}"
                unit_cost = (
                    float(rm.soh_value) / float(rm.soh)
                    if rm.soh_value and rm.soh
                    else None
                )
                connection.execute(
                    lot_query,
                    {
                        "lot_id": lot_id,
                        "product_id": product_id,
                        "lot_code": lot_code,
                        "qty": rm.soh,
                        "cost": unit_cost,
                        "received_at": rm.created_at or datetime.utcnow(),
                        "created_at": datetime.utcnow(),
                    },
                )

    # Step 4: Migrate finished_goods to products
    if "finished_goods" in tables:
        finished_goods_query = text(
            """
            SELECT id, code, description, base_unit, formula_id, formula_revision,
                   is_active, created_at, updated_at
            FROM finished_goods
        """
        )

        finished_goods = connection.execute(finished_goods_query).fetchall()

        for fg in finished_goods:
            sku = fg.code
            name = fg.description or fg.code

            # Check if product already exists
            existing_query = text(
                """
                SELECT id FROM products WHERE sku = :sku
            """
            )
            existing = connection.execute(existing_query, {"sku": sku}).fetchone()

            if existing:
                product_id = existing[0]
                # Update existing product
                update_query = text(
                    """
                    UPDATE products SET
                        product_type = 'FINISHED',
                        formula_id = :formula_id,
                        formula_revision = :formula_revision,
                        base_unit = :base_unit
                    WHERE id = :product_id
                """
                )
                connection.execute(
                    update_query,
                    {
                        "formula_id": fg.formula_id,
                        "formula_revision": fg.formula_revision,
                        "base_unit": fg.base_unit,
                        "product_id": product_id,
                    },
                )
            else:
                # Create new product
                product_id = str(uuid.uuid4())
                insert_query = text(
                    """
                    INSERT INTO products (
                        id, sku, name, description, product_type,
                        formula_id, formula_revision,
                        base_unit, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :sku, :name, :description, 'FINISHED',
                        :formula_id, :formula_revision,
                        :base_unit, :is_active, :created_at, :updated_at
                    )
                """
                )
                connection.execute(
                    insert_query,
                    {
                        "id": product_id,
                        "sku": sku,
                        "name": name,
                        "description": fg.description,
                        "formula_id": fg.formula_id,
                        "formula_revision": fg.formula_revision,
                        "base_unit": fg.base_unit or "LT",
                        "is_active": fg.is_active if fg.is_active is not None else True,
                        "created_at": fg.created_at or datetime.utcnow(),
                        "updated_at": fg.updated_at or datetime.utcnow(),
                    },
                )

            # Record migration mapping
            map_id = str(uuid.uuid4())
            map_query = text(
                """
                INSERT INTO product_migration_map (id, legacy_table, legacy_id, product_id, migrated_at)
                VALUES (:id, 'finished_goods', :legacy_id, :product_id, :migrated_at)
            """
            )
            connection.execute(
                map_query,
                {
                    "id": map_id,
                    "legacy_id": fg.id,
                    "product_id": product_id,
                    "migrated_at": datetime.utcnow(),
                },
            )

            # Migrate finished_goods_inventory.soh to inventory_lots
            inventory_query = text(
                """
                SELECT soh FROM finished_goods_inventory WHERE fg_id = :fg_id
            """
            )
            inventory = connection.execute(inventory_query, {"fg_id": fg.id}).fetchone()

            if inventory and inventory[0] and inventory[0] > 0:
                lot_query = text(
                    """
                    INSERT INTO inventory_lots (
                        id, product_id, lot_code, quantity_kg, received_at, is_active, created_at
                    )
                    SELECT
                        :lot_id, :product_id, :lot_code, :qty, :received_at, 1, :created_at
                    WHERE NOT EXISTS (
                        SELECT 1 FROM inventory_lots WHERE product_id = :product_id AND lot_code = :lot_code
                    )
                """
                )
                lot_id = str(uuid.uuid4())
                lot_code = f"LEGACY-FG-{fg.code}"
                connection.execute(
                    lot_query,
                    {
                        "lot_id": lot_id,
                        "product_id": product_id,
                        "lot_code": lot_code,
                        "qty": inventory[0],
                        "received_at": fg.created_at or datetime.utcnow(),
                        "created_at": datetime.utcnow(),
                    },
                )

    # Step 5: Update formula_lines to use product_id instead of raw_material_id
    if "formula_lines" in tables:
        # Check if raw_material_id column exists
        formula_columns = [
            col["name"] for col in inspector.get_columns("formula_lines")
        ]

        if "raw_material_id" in formula_columns:
            # Add product_id column if it doesn't exist
            if "product_id" not in formula_columns:
                with op.batch_alter_table("formula_lines", schema=None) as batch_op:
                    batch_op.add_column(
                        sa.Column("product_id", sa.String(length=36), nullable=True)
                    )

            # Update formula_lines: map raw_material_id to product_id via migration map
            update_formula_query = text(
                """
                UPDATE formula_lines
                SET product_id = (
                    SELECT product_id FROM product_migration_map
                    WHERE legacy_table = 'raw_materials'
                    AND legacy_id = formula_lines.raw_material_id
                    LIMIT 1
                )
                WHERE raw_material_id IS NOT NULL
                AND product_id IS NULL
            """
            )
            connection.execute(update_formula_query)

            # For any remaining NULL product_ids, try direct match by id
            direct_update_query = text(
                """
                UPDATE formula_lines
                SET product_id = raw_material_id
                WHERE product_id IS NULL
                AND EXISTS (SELECT 1 FROM products WHERE id = formula_lines.raw_material_id)
            """
            )
            connection.execute(direct_update_query)

            # Remove raw_material_id column after migration
            # Note: Keep it for backward compatibility during transition
            # We'll remove it in a later migration after all code is updated

    # Step 6: Update inventory_movements to use product_id instead of item_type/item_id
    if "inventory_movements" in tables:
        movement_columns = [
            col["name"] for col in inspector.get_columns("inventory_movements")
        ]

        if "item_type" in movement_columns and "item_id" in movement_columns:
            # Add product_id column if it doesn't exist
            if "product_id" not in movement_columns:
                with op.batch_alter_table(
                    "inventory_movements", schema=None
                ) as batch_op:
                    batch_op.add_column(
                        sa.Column("product_id", sa.String(length=36), nullable=True)
                    )

            # Update inventory_movements for RAW items
            update_raw_query = text(
                """
                UPDATE inventory_movements
                SET product_id = (
                    SELECT product_id FROM product_migration_map
                    WHERE legacy_table = 'raw_materials'
                    AND legacy_id = inventory_movements.item_id
                    LIMIT 1
                )
                WHERE item_type = 'RAW'
                AND product_id IS NULL
            """
            )
            connection.execute(update_raw_query)

            # Update inventory_movements for FG items
            update_fg_query = text(
                """
                UPDATE inventory_movements
                SET product_id = (
                    SELECT product_id FROM product_migration_map
                    WHERE legacy_table = 'finished_goods'
                    AND legacy_id = inventory_movements.item_id
                    LIMIT 1
                )
                WHERE item_type = 'FG'
                AND product_id IS NULL
            """
            )
            connection.execute(update_fg_query)

            # For any remaining, try direct match
            direct_update_query = text(
                """
                UPDATE inventory_movements
                SET product_id = item_id
                WHERE product_id IS NULL
                AND EXISTS (SELECT 1 FROM products WHERE id = inventory_movements.item_id)
            """
            )
            connection.execute(direct_update_query)

            # Remove old columns after migration (keep for backward compatibility)
            # We'll remove them in a later migration

    # Step 7: Set default product_type for existing products that don't have it set
    set_default_query = text(
        """
        UPDATE products SET product_type = 'RAW'
        WHERE product_type IS NULL
    """
    )
    connection.execute(set_default_query)

    # Step 8: Make product_type NOT NULL
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.alter_column("product_type", nullable=False)

    # Step 9: Create indexes
    try:
        op.create_index("ix_product_type", "products", ["product_type"])
    except Exception:
        pass  # Index may already exist

    try:
        op.create_index("ix_raw_material_code", "products", ["raw_material_code"])
    except Exception:
        pass  # Index may already exist

    # Step 10: Add foreign key constraints
    try:
        op.create_foreign_key(
            "fk_products_raw_material_group",
            "products",
            "raw_material_groups",
            ["raw_material_group_id"],
            ["id"],
        )
    except Exception:
        # Foreign key may already exist or table may not exist
        pass

    try:
        op.create_foreign_key(
            "fk_products_formula", "products", "formulas", ["formula_id"], ["id"]
        )
    except Exception:
        # Foreign key may already exist
        pass


def downgrade() -> None:
    """Rollback migration - restore separate tables structure."""
    # Note: This is a complex rollback. In practice, restore from backup.
    # For now, we'll just remove the new columns.

    with op.batch_alter_table("products", schema=None) as batch_op:
        # Remove added columns (will lose data!)
        batch_op.drop_column("product_type")
        batch_op.drop_column("raw_material_group_id")
        batch_op.drop_column("raw_material_code")
        batch_op.drop_column("raw_material_search_key")
        batch_op.drop_column("raw_material_search_ext")
        batch_op.drop_column("specific_gravity")
        batch_op.drop_column("vol_solid")
        batch_op.drop_column("solid_sg")
        batch_op.drop_column("wt_solid")
        batch_op.drop_column("usage_unit")
        batch_op.drop_column("usage_cost")
        batch_op.drop_column("restock_level")
        batch_op.drop_column("used_ytd")
        batch_op.drop_column("hazard")
        batch_op.drop_column("condition")
        batch_op.drop_column("msds_flag")
        batch_op.drop_column("altno1")
        batch_op.drop_column("altno2")
        batch_op.drop_column("altno3")
        batch_op.drop_column("altno4")
        batch_op.drop_column("altno5")
        batch_op.drop_column("last_movement_date")
        batch_op.drop_column("last_purchase_date")
        batch_op.drop_column("ean13_raw")
        batch_op.drop_column("xero_account")
        # Note: formula_id and formula_revision may exist from before

    # Drop migration mapping table
    op.drop_table("product_migration_map")

    # Note: We don't restore raw_materials and finished_goods data here
    # as that would require complex data migration back
