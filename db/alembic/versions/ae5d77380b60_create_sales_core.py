"""create sales core

Revision ID: ae5d77380b60
Revises: f6d2c4a4c6e1
Create Date: 2025-11-08 22:35:50.164027
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ae5d77380b60"
down_revision: str | None = "f6d2c4a4c6e1"
branch_labels: tuple[str, ...] | None = ("vndmanuf_sales",)
depends_on: tuple[str, ...] | None = None


def _has_table(insp: sa.engine.reflection.Inspector, name: str) -> bool:
    return name in insp.get_table_names()


def _has_column(insp: sa.engine.reflection.Inspector, table: str, column: str) -> bool:
    return any(col["name"] == column for col in insp.get_columns(table))


def _has_index(insp: sa.engine.reflection.Inspector, table: str, name: str) -> bool:
    return any(ix["name"] == name for ix in insp.get_indexes(table))


def _has_constraint(collection: list[dict[str, str]], name: str) -> bool:
    return any(item.get("name") == name for item in collection)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    # Clean up any leftover temp tables from interrupted batch operations
    for tmp_name in (
        "_alembic_tmp_customers",
        "_alembic_tmp_sales_order_lines",
        "sales_order_lines__tmp",
    ):
        if _has_table(insp, tmp_name):
            op.drop_table(tmp_name)
            insp = sa.inspect(bind)

    # --- Sales Channels ---------------------------------------------------
    if not _has_table(insp, "sales_channels"):
        op.create_table(
            "sales_channels",
            sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
            sa.Column("code", sa.String(length=50), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("code", name="uq_sales_channels_code"),
        )
        insp = sa.inspect(bind)
        if not _has_index(insp, "sales_channels", "ix_sales_channels_name"):
            op.create_index(
                "ix_sales_channels_name",
                "sales_channels",
                ["name"],
                unique=False,
            )

    # --- Pricebooks -------------------------------------------------------
    if not _has_table(insp, "pricebooks"):
        op.create_table(
            "pricebooks",
            sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column(
                "currency", sa.String(length=8), nullable=False, server_default="AUD"
            ),
            sa.Column("active_from", sa.Date(), nullable=False),
            sa.Column("active_to", sa.Date(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("name", name="uq_pricebooks_name"),
        )
        insp = sa.inspect(bind)
        if not _has_index(insp, "pricebooks", "ix_pricebooks_active_from"):
            op.create_index(
                "ix_pricebooks_active_from",
                "pricebooks",
                ["active_from"],
                unique=False,
            )

    # --- Sales Tags -------------------------------------------------------
    if not _has_table(insp, "sales_tags"):
        op.create_table(
            "sales_tags",
            sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
            sa.Column("slug", sa.String(length=100), nullable=False),
            sa.Column("label", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("slug", name="uq_sales_tags_slug"),
        )
        insp = sa.inspect(bind)
        if not _has_index(insp, "sales_tags", "ix_sales_tags_label"):
            op.create_index(
                "ix_sales_tags_label",
                "sales_tags",
                ["label"],
                unique=False,
            )

    # --- Customers extensions --------------------------------------------
    if _has_table(insp, "customers"):
        customer_cols = {col["name"] for col in insp.get_columns("customers")}
        customer_checks = insp.get_check_constraints("customers")
        pending_customer_columns: list[sa.Column] = []

        if "customer_type" not in customer_cols:
            pending_customer_columns.append(
                sa.Column(
                    "customer_type",
                    sa.String(length=32),
                    nullable=False,
                    server_default=sa.text("'other'"),
                )
            )
        if "abn" not in customer_cols:
            pending_customer_columns.append(
                sa.Column("abn", sa.String(length=20), nullable=True)
            )
        if "notes" not in customer_cols:
            pending_customer_columns.append(
                sa.Column("notes", sa.Text(), nullable=True)
            )

        if pending_customer_columns or not _has_constraint(
            customer_checks, "ck_customers_type"
        ):
            with op.batch_alter_table("customers", recreate="always") as batch:
                for column in pending_customer_columns:
                    name = column.name
                    batch.add_column(column)
                    if column.server_default is not None:
                        batch.alter_column(
                            name,
                            server_default=None,
                        )
                if not _has_constraint(customer_checks, "ck_customers_type"):
                    batch.create_check_constraint(
                        "ck_customers_type",
                        "customer_type IN "
                        "('bottle_shop','bar','restaurant','venue','retailer','distributor','direct_customer','other')",
                    )

        if not _has_index(insp, "customers", "ix_customers_name"):
            op.create_index(
                "ix_customers_name",
                "customers",
                ["name"],
                unique=False,
            )

    # --- Customer Sites ---------------------------------------------------
    if not _has_table(insp, "customer_sites"):
        op.create_table(
            "customer_sites",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("customer_id", sa.String(length=36), nullable=False),
            sa.Column("site_name", sa.String(length=120), nullable=False),
            sa.Column("state", sa.String(length=8), nullable=False),
            sa.Column("suburb", sa.String(length=120), nullable=True),
            sa.Column("postcode", sa.String(length=10), nullable=True),
            sa.Column("latitude", sa.Numeric(10, 6), nullable=True),
            sa.Column("longitude", sa.Numeric(10, 6), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["customer_id"],
                ["customers.id"],
                name="fk_customer_sites__customer_id__customers",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_customer_sites"),
            sa.UniqueConstraint(
                "customer_id",
                "site_name",
                "state",
                "suburb",
                name="uq_customer_sites_customer_site_state_suburb",
            ),
        )
        insp = sa.inspect(bind)
        if not _has_index(insp, "customer_sites", "ix_customer_sites_customer"):
            op.create_index(
                "ix_customer_sites_customer",
                "customer_sites",
                ["customer_id"],
                unique=False,
            )

    # --- Sales Orders extensions -----------------------------------------
    if _has_table(insp, "sales_orders"):
        sales_order_cols = {col["name"] for col in insp.get_columns("sales_orders")}
        sales_order_checks = insp.get_check_constraints("sales_orders")
        sales_order_fks = insp.get_foreign_keys("sales_orders")

        existing_indexes = {ix["name"] for ix in insp.get_indexes("sales_orders")}
        if "ix_sales_orders_so_number" in existing_indexes:
            op.drop_index("ix_sales_orders_so_number", table_name="sales_orders")

        if "status" in sales_order_cols:
            status_map = {
                "DRAFT": "draft",
                "CONFIRMED": "confirmed",
                "FULFILLED": "fulfilled",
                "SHIPPED": "fulfilled",
                "INVOICED": "fulfilled",
                "CANCELLED": "cancelled",
            }
            for legacy_value, new_value in status_map.items():
                op.execute(
                    sa.text(
                        "UPDATE sales_orders SET status = :new WHERE upper(status) = :legacy"
                    ).bindparams(new=new_value, legacy=legacy_value)
                )
            op.execute(
                sa.text(
                    "UPDATE sales_orders "
                    "SET status = 'draft' "
                    "WHERE status IS NULL "
                    "   OR status NOT IN ('draft','confirmed','fulfilled','cancelled')"
                )
            )

        to_add: list[sa.Column] = []
        if "channel_id" not in sales_order_cols:
            to_add.append(sa.Column("channel_id", sa.String(length=36), nullable=True))
        if "customer_site_id" not in sales_order_cols:
            to_add.append(
                sa.Column("customer_site_id", sa.String(length=36), nullable=True)
            )
        if "pricebook_id" not in sales_order_cols:
            to_add.append(
                sa.Column("pricebook_id", sa.String(length=36), nullable=True)
            )
        if "source" not in sales_order_cols:
            to_add.append(
                sa.Column(
                    "source",
                    sa.String(length=20),
                    nullable=False,
                    server_default=sa.text("'manual'"),
                )
            )
        if "entered_by" not in sales_order_cols:
            to_add.append(sa.Column("entered_by", sa.String(length=100), nullable=True))
        if "total_ex_gst" not in sales_order_cols:
            to_add.append(
                sa.Column(
                    "total_ex_gst",
                    sa.Numeric(12, 2),
                    nullable=False,
                    server_default="0",
                )
            )
        if "total_inc_gst" not in sales_order_cols:
            to_add.append(
                sa.Column(
                    "total_inc_gst",
                    sa.Numeric(12, 2),
                    nullable=False,
                    server_default="0",
                )
            )
        if "order_ref" not in sales_order_cols and "so_number" in sales_order_cols:
            # Rename so_number to order_ref for compatibility
            with op.batch_alter_table("sales_orders", recreate="always") as batch:
                batch.alter_column("so_number", new_column_name="order_ref")
            insp = sa.inspect(bind)
            sales_order_cols = {col["name"] for col in insp.get_columns("sales_orders")}

        if "status" in sales_order_cols:
            # Ensure status column is not nullable and matches new enum
            with op.batch_alter_table("sales_orders", recreate="always") as batch:
                batch.alter_column(
                    "status",
                    existing_type=sa.String(length=20),
                    nullable=False,
                    existing_server_default=None,
                )

        if (
            to_add
            or not _has_constraint(sales_order_checks, "ck_sales_orders_status")
            or not _has_constraint(sales_order_checks, "ck_sales_orders_source")
        ):
            with op.batch_alter_table("sales_orders", recreate="always") as batch:
                for column in to_add:
                    name = column.name
                    batch.add_column(column)
                    if column.server_default is not None:
                        batch.alter_column(name, server_default=None)

                fk_names = {fk["name"] for fk in sales_order_fks}
                if (
                    "fk_sales_orders__channel_id__sales_channels" not in fk_names
                    and _has_table(insp, "sales_channels")
                ):
                    batch.create_foreign_key(
                        "fk_sales_orders__channel_id__sales_channels",
                        "sales_channels",
                        ["channel_id"],
                        ["id"],
                        ondelete="RESTRICT",
                    )
                if (
                    "fk_sales_orders__customer_site_id__customer_sites" not in fk_names
                    and _has_table(insp, "customer_sites")
                ):
                    batch.create_foreign_key(
                        "fk_sales_orders__customer_site_id__customer_sites",
                        "customer_sites",
                        ["customer_site_id"],
                        ["id"],
                        ondelete="SET NULL",
                    )
                if (
                    "fk_sales_orders__pricebook_id__pricebooks" not in fk_names
                    and _has_table(insp, "pricebooks")
                ):
                    batch.create_foreign_key(
                        "fk_sales_orders__pricebook_id__pricebooks",
                        "pricebooks",
                        ["pricebook_id"],
                        ["id"],
                        ondelete="SET NULL",
                    )
                if not _has_constraint(sales_order_checks, "ck_sales_orders_status"):
                    batch.create_check_constraint(
                        "ck_sales_orders_status",
                        "status IN ('draft','confirmed','fulfilled','cancelled')",
                    )
                if not _has_constraint(sales_order_checks, "ck_sales_orders_source"):
                    batch.create_check_constraint(
                        "ck_sales_orders_source",
                        "source IN ('manual','imported','api')",
                    )

        if not _has_index(insp, "sales_orders", "ix_sales_orders_order_date"):
            op.create_index(
                "ix_sales_orders_order_date",
                "sales_orders",
                ["order_date"],
                unique=False,
            )
        if not _has_index(insp, "sales_orders", "ix_sales_orders_channel"):
            op.create_index(
                "ix_sales_orders_channel",
                "sales_orders",
                ["channel_id"],
                unique=False,
            )
        if not _has_index(insp, "sales_orders", "ix_sales_orders_customer"):
            op.create_index(
                "ix_sales_orders_customer",
                "sales_orders",
                ["customer_id"],
                unique=False,
            )
        if not _has_index(insp, "sales_orders", "ix_sales_orders_pricebook"):
            op.create_index(
                "ix_sales_orders_pricebook",
                "sales_orders",
                ["pricebook_id"],
                unique=False,
            )

    # --- Sales Order Lines (so_lines -> sales_order_lines) ----------------
    if _has_table(insp, "so_lines") and not _has_table(insp, "sales_order_lines"):
        op.rename_table("so_lines", "sales_order_lines")
        insp = sa.inspect(bind)

    if _has_table(insp, "sales_order_lines"):
        sol_cols = {col["name"] for col in insp.get_columns("sales_order_lines")}
        rebuild_required = any(
            required not in sol_cols
            for required in (
                "order_id",
                "qty",
                "uom",
                "unit_price_ex_gst",
                "line_total_ex_gst",
            )
        )

        if rebuild_required:
            products_pk = (
                insp.get_pk_constraint("products")
                if _has_table(insp, "products")
                else {}
            )
            products_pk_cols = set(products_pk.get("constrained_columns", []) or [])
            products_fk_supported = "id" in products_pk_cols

            tmp_table_name = "sales_order_lines__tmp"
            if _has_table(insp, tmp_table_name):
                op.drop_table(tmp_table_name)

            tmp_columns: list[sa.schema.SchemaItem] = [
                sa.Column("id", sa.String(length=36), nullable=False),
                sa.Column("order_id", sa.String(length=36), nullable=False),
                sa.Column("product_id", sa.String(length=36), nullable=False),
                sa.Column("qty", sa.Numeric(12, 3), nullable=False),
                sa.Column("uom", sa.String(length=20), nullable=False),
                sa.Column("unit_price_ex_gst", sa.Numeric(12, 2), nullable=False),
                sa.Column("unit_price_inc_gst", sa.Numeric(12, 2), nullable=True),
                sa.Column("discount_ex_gst", sa.Numeric(12, 2), nullable=True),
                sa.Column("tax_rate", sa.Numeric(5, 2), nullable=True),
                sa.Column("line_total_ex_gst", sa.Numeric(12, 2), nullable=False),
                sa.Column("line_total_inc_gst", sa.Numeric(12, 2), nullable=False),
                sa.Column("sequence", sa.Integer(), nullable=False),
                sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
                sa.Column("deleted_by", sa.String(length=100), nullable=True),
                sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
                sa.Column("versioned_at", sa.DateTime(timezone=True), nullable=True),
                sa.Column("versioned_by", sa.String(length=100), nullable=True),
                sa.Column("previous_version_id", sa.String(length=36), nullable=True),
                sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
                sa.Column("archived_by", sa.String(length=100), nullable=True),
                sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
                sa.ForeignKeyConstraint(
                    ["order_id"],
                    ["sales_orders.id"],
                    name="fk_sales_order_lines__order_id__sales_orders",
                    ondelete="CASCADE",
                ),
                sa.PrimaryKeyConstraint("id", name="pk_sales_order_lines"),
            ]
            if products_fk_supported:
                tmp_columns.append(
                    sa.ForeignKeyConstraint(
                        ["product_id"],
                        ["products.id"],
                        name="fk_sales_order_lines__product_id__products",
                        ondelete="RESTRICT",
                    )
                )

            op.create_table(tmp_table_name, *tmp_columns)

            source_to_target: list[tuple[str, str]] = []

            def map_column(target: str, source: str | None) -> None:
                expr = source if source is not None else "NULL"
                source_to_target.append((target, expr))

            map_column("id", "id")
            map_column(
                "order_id",
                "sales_order_id" if "sales_order_id" in sol_cols else "order_id",
            )
            map_column("product_id", "product_id")
            map_column("qty", "quantity_kg" if "quantity_kg" in sol_cols else "qty")
            map_column("uom", "uom" if "uom" in sol_cols else "'unit'")
            map_column(
                "unit_price_ex_gst",
                "unit_price_ex_tax"
                if "unit_price_ex_tax" in sol_cols
                else "unit_price_ex_gst",
            )
            map_column(
                "unit_price_inc_gst",
                "unit_price_inc_gst"
                if "unit_price_inc_gst" in sol_cols
                else "unit_price_inc_tax"
                if "unit_price_inc_tax" in sol_cols
                else "NULL",
            )
            map_column(
                "discount_ex_gst",
                "discount_ex_gst"
                if "discount_ex_gst" in sol_cols
                else "discount_ex_tax"
                if "discount_ex_tax" in sol_cols
                else "NULL",
            )
            map_column("tax_rate", "tax_rate" if "tax_rate" in sol_cols else "NULL")
            map_column(
                "line_total_ex_gst",
                "line_total_ex_gst"
                if "line_total_ex_gst" in sol_cols
                else "line_total_ex_tax",
            )
            map_column(
                "line_total_inc_gst",
                "line_total_inc_gst"
                if "line_total_inc_gst" in sol_cols
                else "line_total_inc_tax",
            )
            map_column("sequence", "sequence")

            for audit_col in (
                "deleted_at",
                "deleted_by",
                "version",
                "versioned_at",
                "versioned_by",
                "previous_version_id",
                "archived_at",
                "archived_by",
                "created_at",
                "updated_at",
            ):
                default_expr = "1" if audit_col == "version" else "NULL"
                map_column(
                    audit_col, audit_col if audit_col in sol_cols else default_expr
                )

            insert_columns = ", ".join(col for col, _ in source_to_target)
            select_exprs = ", ".join(expr for _, expr in source_to_target)
            op.execute(
                sa.text(
                    f"INSERT INTO {tmp_table_name} ({insert_columns}) "
                    f"SELECT {select_exprs} FROM sales_order_lines"
                )
            )

            # Drop any existing indexes on the legacy table before dropping it
            for index in insp.get_indexes("sales_order_lines"):
                op.drop_index(index["name"], table_name="sales_order_lines")

            op.drop_table("sales_order_lines")
            op.rename_table(tmp_table_name, "sales_order_lines")
            insp = sa.inspect(bind)

        if not _has_index(insp, "sales_order_lines", "ix_sales_order_lines_order"):
            op.create_index(
                "ix_sales_order_lines_order",
                "sales_order_lines",
                ["order_id"],
                unique=False,
            )
        if not _has_index(insp, "sales_order_lines", "ix_sales_order_lines_product"):
            op.create_index(
                "ix_sales_order_lines_product",
                "sales_order_lines",
                ["product_id"],
                unique=False,
            )

    # --- Pricebook Items --------------------------------------------------
    if not _has_table(insp, "pricebook_items"):
        op.create_table(
            "pricebook_items",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("pricebook_id", sa.String(length=36), nullable=False),
            sa.Column("product_id", sa.String(length=36), nullable=False),
            sa.Column("sku_code", sa.String(length=50), nullable=True),
            sa.Column("unit_price_ex_gst", sa.Numeric(12, 2), nullable=False),
            sa.Column("unit_price_inc_gst", sa.Numeric(12, 2), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["pricebook_id"],
                ["pricebooks.id"],
                name="fk_pricebook_items__pricebook_id__pricebooks",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["product_id"],
                ["products.id"],
                name="fk_pricebook_items__product_id__products",
                ondelete="RESTRICT",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_pricebook_items"),
            sa.UniqueConstraint(
                "pricebook_id",
                "product_id",
                name="uq_pricebook_items_pricebook_product",
            ),
        )
        insp = sa.inspect(bind)

    # --- Sales Order Tags -------------------------------------------------
    if not _has_table(insp, "sales_order_tags"):
        op.create_table(
            "sales_order_tags",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("order_id", sa.String(length=36), nullable=False),
            sa.Column("tag_id", sa.String(length=36), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["order_id"],
                ["sales_orders.id"],
                name="fk_sales_order_tags__order_id__sales_orders",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["tag_id"],
                ["sales_tags.id"],
                name="fk_sales_order_tags__tag_id__sales_tags",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_sales_order_tags"),
            sa.UniqueConstraint(
                "order_id",
                "tag_id",
                name="uq_sales_order_tags_order_tag",
            ),
        )
        insp = sa.inspect(bind)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if _has_table(insp, "sales_order_tags"):
        op.drop_table("sales_order_tags")

    if _has_table(insp, "pricebook_items"):
        op.drop_table("pricebook_items")

    if _has_table(insp, "sales_order_lines"):
        if _has_index(insp, "sales_order_lines", "ix_sales_order_lines_product"):
            op.drop_index(
                "ix_sales_order_lines_product", table_name="sales_order_lines"
            )
        if _has_index(insp, "sales_order_lines", "ix_sales_order_lines_order"):
            op.drop_index("ix_sales_order_lines_order", table_name="sales_order_lines")

        with op.batch_alter_table("sales_order_lines", recreate="always") as batch:
            batch.drop_constraint(
                "fk_sales_order_lines__product_id__products", type_="foreignkey"
            )
            batch.drop_constraint(
                "fk_sales_order_lines__order_id__sales_orders", type_="foreignkey"
            )
            if _has_column(insp, "sales_order_lines", "discount_ex_gst"):
                batch.drop_column("discount_ex_gst")
            if _has_column(insp, "sales_order_lines", "unit_price_inc_gst"):
                batch.drop_column("unit_price_inc_gst")
            if _has_column(insp, "sales_order_lines", "uom"):
                batch.drop_column("uom")
            if _has_column(insp, "sales_order_lines", "line_total_inc_gst"):
                batch.alter_column(
                    "line_total_inc_gst",
                    new_column_name="line_total_inc_tax",
                    existing_type=sa.Numeric(12, 2),
                )
            if _has_column(insp, "sales_order_lines", "line_total_ex_gst"):
                batch.alter_column(
                    "line_total_ex_gst",
                    new_column_name="line_total_ex_tax",
                    existing_type=sa.Numeric(12, 2),
                )
            if _has_column(insp, "sales_order_lines", "unit_price_ex_gst"):
                batch.alter_column(
                    "unit_price_ex_gst",
                    new_column_name="unit_price_ex_tax",
                    existing_type=sa.Numeric(10, 2),
                )
            if _has_column(insp, "sales_order_lines", "qty"):
                batch.alter_column(
                    "qty",
                    new_column_name="quantity_kg",
                    existing_type=sa.Numeric(12, 3),
                )
            if _has_column(insp, "sales_order_lines", "order_id"):
                batch.alter_column("order_id", new_column_name="sales_order_id")

            batch.create_foreign_key(
                "so_lines_product_id_fkey",
                "products",
                ["product_id"],
                ["id"],
            )
            batch.create_foreign_key(
                "so_lines_sales_order_id_fkey",
                "sales_orders",
                ["sales_order_id"],
                ["id"],
            )

        if _has_table(sa.inspect(bind), "sales_order_lines"):
            op.rename_table("sales_order_lines", "so_lines")

    insp = sa.inspect(bind)

    if _has_table(insp, "sales_orders"):
        if _has_index(insp, "sales_orders", "ix_sales_orders_customer"):
            op.drop_index("ix_sales_orders_customer", table_name="sales_orders")
        if _has_index(insp, "sales_orders", "ix_sales_orders_channel"):
            op.drop_index("ix_sales_orders_channel", table_name="sales_orders")
        if _has_index(insp, "sales_orders", "ix_sales_orders_order_date"):
            op.drop_index("ix_sales_orders_order_date", table_name="sales_orders")
        if _has_index(insp, "sales_orders", "ix_sales_orders_pricebook"):
            op.drop_index("ix_sales_orders_pricebook", table_name="sales_orders")

        with op.batch_alter_table("sales_orders", recreate="always") as batch:
            if _has_constraint(
                insp.get_check_constraints("sales_orders"), "ck_sales_orders_source"
            ):
                batch.drop_constraint("ck_sales_orders_source", type_="check")
            if _has_constraint(
                insp.get_check_constraints("sales_orders"), "ck_sales_orders_status"
            ):
                batch.drop_constraint("ck_sales_orders_status", type_="check")
            if _has_column(insp, "sales_orders", "total_inc_gst"):
                batch.drop_column("total_inc_gst")
            if _has_column(insp, "sales_orders", "total_ex_gst"):
                batch.drop_column("total_ex_gst")
            if _has_column(insp, "sales_orders", "entered_by"):
                batch.drop_column("entered_by")
            if _has_column(insp, "sales_orders", "source"):
                batch.drop_column("source")
            if _has_column(insp, "sales_orders", "customer_site_id"):
                batch.drop_constraint(
                    "fk_sales_orders__customer_site_id__customer_sites",
                    type_="foreignkey",
                )
                batch.drop_column("customer_site_id")
            if _has_column(insp, "sales_orders", "pricebook_id"):
                batch.drop_constraint(
                    "fk_sales_orders__pricebook_id__pricebooks",
                    type_="foreignkey",
                )
                batch.drop_column("pricebook_id")
            if _has_column(insp, "sales_orders", "channel_id"):
                batch.drop_constraint(
                    "fk_sales_orders__channel_id__sales_channels", type_="foreignkey"
                )
                batch.drop_column("channel_id")
            if _has_column(insp, "sales_orders", "order_ref"):
                batch.alter_column(
                    "order_ref",
                    new_column_name="so_number",
                    existing_type=sa.String(length=50),
                )
            batch.alter_column(
                "status",
                existing_type=sa.String(length=20),
                nullable=True,
                existing_server_default=None,
            )

        op.create_index(
            "ix_sales_orders_so_number",
            "sales_orders",
            ["so_number"],
            unique=True,
        )

    if _has_table(insp, "customer_sites"):
        op.drop_table("customer_sites")

    if _has_table(insp, "customers"):
        if _has_index(insp, "customers", "ix_customers_name"):
            op.drop_index("ix_customers_name", table_name="customers")
        with op.batch_alter_table("customers", recreate="always") as batch:
            if _has_constraint(
                insp.get_check_constraints("customers"), "ck_customers_type"
            ):
                batch.drop_constraint("ck_customers_type", type_="check")
            if _has_column(insp, "customers", "notes"):
                batch.drop_column("notes")
            if _has_column(insp, "customers", "abn"):
                batch.drop_column("abn")
            if _has_column(insp, "customers", "customer_type"):
                batch.drop_column("customer_type")

    if _has_table(insp, "sales_tags"):
        if _has_index(insp, "sales_tags", "ix_sales_tags_label"):
            op.drop_index("ix_sales_tags_label", table_name="sales_tags")
        op.drop_table("sales_tags")

    if _has_table(insp, "pricebooks"):
        if _has_index(insp, "pricebooks", "ix_pricebooks_active_from"):
            op.drop_index("ix_pricebooks_active_from", table_name="pricebooks")
        op.drop_table("pricebooks")

    if _has_table(insp, "sales_channels"):
        if _has_index(insp, "sales_channels", "ix_sales_channels_name"):
            op.drop_index("ix_sales_channels_name", table_name="sales_channels")
        op.drop_table("sales_channels")
