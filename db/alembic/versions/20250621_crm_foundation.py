"""CRM foundation: sales reps, buying groups, activities, staff.

Revision ID: 20250621_crm
Revises: 20250621_pb_items_audit
Create Date: 2025-06-21

"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250621_crm"
down_revision: Union[str, None] = "20250621_pb_items_audit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_AUDIT_COLS = (
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
    sa.Column("deleted_by", sa.String(100), nullable=True),
    sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    sa.Column("versioned_at", sa.DateTime(), nullable=True),
    sa.Column("versioned_by", sa.String(100), nullable=True),
    sa.Column("previous_version_id", sa.String(36), nullable=True),
    sa.Column("archived_at", sa.DateTime(), nullable=True),
    sa.Column("archived_by", sa.String(100), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
)


def _has_table(insp, name: str) -> bool:
    return name in insp.get_table_names()


def _has_column(insp, table: str, column: str) -> bool:
    if not _has_table(insp, table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def _has_index(insp, table: str, name: str) -> bool:
    if not _has_table(insp, table):
        return False
    return any(ix["name"] == name for ix in insp.get_indexes(table))


def _audit_table_args():
    return _AUDIT_COLS


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # --- buying_groups -----------------------------------------------------
    if not _has_table(insp, "buying_groups"):
        op.create_table(
            "buying_groups",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("code", sa.String(20), nullable=False),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            *_audit_table_args(),
            sa.PrimaryKeyConstraint("id", name="pk_buying_groups"),
            sa.UniqueConstraint("code", name="uq_buying_groups_code"),
        )
        op.create_index("ix_buying_groups_name", "buying_groups", ["name"])
        insp = sa.inspect(bind)

    if _has_table(insp, "buying_groups"):
        seeds = [
            ("CELLAR", "Cellarbrations"),
            ("THIRSTY", "Thirsty Camel"),
            ("BOTTLEO", "Bottle-O"),
            ("BWS", "BWS"),
            ("IGA", "IGA Liquor"),
            ("INDEP", "Independent"),
            ("OTHER", "Other"),
        ]
        existing = bind.execute(sa.text("SELECT COUNT(*) FROM buying_groups")).scalar()
        if not existing:
            for code, name in seeds:
                bind.execute(
                    sa.text(
                        "INSERT INTO buying_groups "
                        "(id, code, name, is_active, version, created_at, updated_at) "
                        "VALUES (:id, :code, :name, 1, 1, :now, :now)"
                    ),
                    {"id": str(uuid.uuid4()), "code": code, "name": name, "now": now},
                )

    # --- sales_reps --------------------------------------------------------
    if not _has_table(insp, "sales_reps"):
        op.create_table(
            "sales_reps",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("code", sa.String(20), nullable=False),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("email", sa.String(200), nullable=True),
            sa.Column("phone", sa.String(50), nullable=True),
            sa.Column("user_id", sa.String(36), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            *_audit_table_args(),
            sa.PrimaryKeyConstraint("id", name="pk_sales_reps"),
            sa.UniqueConstraint("code", name="uq_sales_reps_code"),
        )
        op.create_index("ix_sales_reps_name", "sales_reps", ["name"])
        insp = sa.inspect(bind)

    # --- customers CRM columns ---------------------------------------------
    if _has_table(insp, "customers"):
        pending = []
        if not _has_column(insp, "customers", "buying_group_id"):
            pending.append(sa.Column("buying_group_id", sa.String(36), nullable=True))
        if not _has_column(insp, "customers", "visit_frequency_target_days"):
            pending.append(
                sa.Column("visit_frequency_target_days", sa.Integer(), nullable=True)
            )
        if not _has_column(insp, "customers", "preferred_contact_method"):
            pending.append(
                sa.Column("preferred_contact_method", sa.String(20), nullable=True)
            )
        if pending:
            with op.batch_alter_table("customers") as batch_op:
                for col in pending:
                    batch_op.add_column(col)
            insp = sa.inspect(bind)
            if not _has_index(insp, "customers", "ix_customers_buying_group_id"):
                try:
                    op.create_index(
                        "ix_customers_buying_group_id",
                        "customers",
                        ["buying_group_id"],
                    )
                except Exception:
                    pass

    # --- customer_rep_assignments ------------------------------------------
    if not _has_table(insp, "customer_rep_assignments"):
        op.create_table(
            "customer_rep_assignments",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("customer_id", sa.String(36), nullable=False),
            sa.Column("sales_rep_id", sa.String(36), nullable=False),
            sa.Column("role", sa.String(20), nullable=False, server_default="primary"),
            sa.Column("assigned_at", sa.DateTime(), nullable=False),
            *_audit_table_args(),
            sa.ForeignKeyConstraint(
                ["customer_id"],
                ["customers.id"],
                name="fk_customer_rep_assignments__customer_id__customers",
            ),
            sa.ForeignKeyConstraint(
                ["sales_rep_id"],
                ["sales_reps.id"],
                name="fk_customer_rep_assignments__sales_rep_id__sales_reps",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_customer_rep_assignments"),
            sa.UniqueConstraint(
                "customer_id",
                "sales_rep_id",
                name="uq_customer_rep_assignments_customer_rep",
            ),
            sa.CheckConstraint(
                "role IN ('primary','secondary','support')",
                name="ck_customer_rep_assignments_role",
            ),
        )
        op.create_index(
            "ix_customer_rep_assignments_customer",
            "customer_rep_assignments",
            ["customer_id"],
        )
        op.create_index(
            "ix_customer_rep_assignments_rep",
            "customer_rep_assignments",
            ["sales_rep_id"],
        )
        insp = sa.inspect(bind)

    # --- crm_activities ----------------------------------------------------
    if not _has_table(insp, "crm_activities"):
        op.create_table(
            "crm_activities",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("customer_id", sa.String(36), nullable=False),
            sa.Column("contact_id", sa.String(36), nullable=True),
            sa.Column("customer_site_id", sa.String(36), nullable=True),
            sa.Column("sales_rep_id", sa.String(36), nullable=True),
            sa.Column(
                "activity_type", sa.String(20), nullable=False, server_default="note"
            ),
            sa.Column("subject", sa.String(200), nullable=True),
            sa.Column("body", sa.Text(), nullable=True),
            sa.Column("activity_at", sa.DateTime(), nullable=False),
            sa.Column("note_category", sa.String(30), nullable=True),
            sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("linked_sales_order_id", sa.String(36), nullable=True),
            *_audit_table_args(),
            sa.ForeignKeyConstraint(
                ["customer_id"],
                ["customers.id"],
                name="fk_crm_activities__customer_id__customers",
            ),
            sa.ForeignKeyConstraint(
                ["contact_id"],
                ["contacts.id"],
                name="fk_crm_activities__contact_id__contacts",
            ),
            sa.ForeignKeyConstraint(
                ["customer_site_id"],
                ["customer_sites.id"],
                name="fk_crm_activities__customer_site_id__customer_sites",
            ),
            sa.ForeignKeyConstraint(
                ["sales_rep_id"],
                ["sales_reps.id"],
                name="fk_crm_activities__sales_rep_id__sales_reps",
            ),
            sa.ForeignKeyConstraint(
                ["linked_sales_order_id"],
                ["sales_orders.id"],
                name="fk_crm_activities__linked_sales_order_id__sales_orders",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_crm_activities"),
            sa.CheckConstraint(
                "activity_type IN ('visit','phone','email','note','photo','file','reminder_done')",
                name="ck_crm_activities_type",
            ),
        )
        op.create_index("ix_crm_activities_customer", "crm_activities", ["customer_id"])
        op.create_index(
            "ix_crm_activities_activity_at", "crm_activities", ["activity_at"]
        )
        insp = sa.inspect(bind)

    # --- crm_customer_staff ------------------------------------------------
    if not _has_table(insp, "crm_customer_staff"):
        op.create_table(
            "crm_customer_staff",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("customer_id", sa.String(36), nullable=False),
            sa.Column("customer_site_id", sa.String(36), nullable=True),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("role", sa.String(50), nullable=True),
            sa.Column("phone", sa.String(50), nullable=True),
            sa.Column("email", sa.String(200), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            *_audit_table_args(),
            sa.ForeignKeyConstraint(
                ["customer_id"],
                ["customers.id"],
                name="fk_crm_customer_staff__customer_id__customers",
            ),
            sa.ForeignKeyConstraint(
                ["customer_site_id"],
                ["customer_sites.id"],
                name="fk_crm_customer_staff__customer_site_id__customer_sites",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_crm_customer_staff"),
        )
        op.create_index(
            "ix_crm_customer_staff_customer", "crm_customer_staff", ["customer_id"]
        )
        op.create_index(
            "ix_crm_customer_staff_site", "crm_customer_staff", ["customer_site_id"]
        )
        insp = sa.inspect(bind)

    # --- crm_attachments ---------------------------------------------------
    if not _has_table(insp, "crm_attachments"):
        op.create_table(
            "crm_attachments",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("customer_id", sa.String(36), nullable=False),
            sa.Column("activity_id", sa.String(36), nullable=True),
            sa.Column("uploaded_by_rep_id", sa.String(36), nullable=True),
            sa.Column(
                "storage_backend", sa.String(20), nullable=False, server_default="local"
            ),
            sa.Column("storage_key", sa.String(500), nullable=False),
            sa.Column("external_url", sa.String(500), nullable=True),
            sa.Column("file_name", sa.String(255), nullable=False),
            sa.Column("mime_type", sa.String(100), nullable=True),
            sa.Column("file_size", sa.Integer(), nullable=True),
            sa.Column("caption", sa.Text(), nullable=True),
            sa.Column("taken_at", sa.DateTime(), nullable=True),
            *_audit_table_args(),
            sa.ForeignKeyConstraint(
                ["customer_id"],
                ["customers.id"],
                name="fk_crm_attachments__customer_id__customers",
            ),
            sa.ForeignKeyConstraint(
                ["activity_id"],
                ["crm_activities.id"],
                name="fk_crm_attachments__activity_id__crm_activities",
            ),
            sa.ForeignKeyConstraint(
                ["uploaded_by_rep_id"],
                ["sales_reps.id"],
                name="fk_crm_attachments__uploaded_by_rep_id__sales_reps",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_crm_attachments"),
        )
        op.create_index(
            "ix_crm_attachments_customer", "crm_attachments", ["customer_id"]
        )
        insp = sa.inspect(bind)

    # --- crm_scheduled_activities ------------------------------------------
    if not _has_table(insp, "crm_scheduled_activities"):
        op.create_table(
            "crm_scheduled_activities",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("customer_id", sa.String(36), nullable=False),
            sa.Column("customer_site_id", sa.String(36), nullable=True),
            sa.Column("sales_rep_id", sa.String(36), nullable=False),
            sa.Column(
                "activity_type", sa.String(20), nullable=False, server_default="visit"
            ),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("scheduled_at", sa.DateTime(), nullable=False),
            sa.Column("duration_minutes", sa.Integer(), nullable=True),
            sa.Column(
                "status", sa.String(20), nullable=False, server_default="scheduled"
            ),
            sa.Column("completed_activity_id", sa.String(36), nullable=True),
            sa.Column("reminder_minutes_before", sa.Integer(), nullable=True),
            *_audit_table_args(),
            sa.ForeignKeyConstraint(
                ["customer_id"],
                ["customers.id"],
                name="fk_crm_scheduled__customer_id__customers",
            ),
            sa.ForeignKeyConstraint(
                ["customer_site_id"],
                ["customer_sites.id"],
                name="fk_crm_scheduled__customer_site_id__customer_sites",
            ),
            sa.ForeignKeyConstraint(
                ["sales_rep_id"],
                ["sales_reps.id"],
                name="fk_crm_scheduled__sales_rep_id__sales_reps",
            ),
            sa.ForeignKeyConstraint(
                ["completed_activity_id"],
                ["crm_activities.id"],
                name="fk_crm_scheduled__completed_activity_id__crm_activities",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_crm_scheduled_activities"),
            sa.CheckConstraint(
                "activity_type IN ('visit','phone','email','task')",
                name="ck_crm_scheduled_type",
            ),
            sa.CheckConstraint(
                "status IN ('scheduled','completed','cancelled','overdue')",
                name="ck_crm_scheduled_status",
            ),
        )
        op.create_index(
            "ix_crm_scheduled_customer", "crm_scheduled_activities", ["customer_id"]
        )
        op.create_index(
            "ix_crm_scheduled_rep", "crm_scheduled_activities", ["sales_rep_id"]
        )
        op.create_index(
            "ix_crm_scheduled_at", "crm_scheduled_activities", ["scheduled_at"]
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    for table, indexes in (
        (
            "crm_scheduled_activities",
            (
                "ix_crm_scheduled_at",
                "ix_crm_scheduled_rep",
                "ix_crm_scheduled_customer",
            ),
        ),
        ("crm_attachments", ("ix_crm_attachments_customer",)),
        (
            "crm_customer_staff",
            ("ix_crm_customer_staff_site", "ix_crm_customer_staff_customer"),
        ),
        (
            "crm_activities",
            ("ix_crm_activities_activity_at", "ix_crm_activities_customer"),
        ),
        (
            "customer_rep_assignments",
            (
                "ix_customer_rep_assignments_rep",
                "ix_customer_rep_assignments_customer",
            ),
        ),
    ):
        if _has_table(insp, table):
            for ix in indexes:
                try:
                    op.drop_index(ix, table_name=table)
                except Exception:
                    pass
            op.drop_table(table)
    insp = sa.inspect(bind)

    if _has_table(insp, "customers"):
        cols_to_drop = [
            c
            for c in (
                "preferred_contact_method",
                "visit_frequency_target_days",
                "buying_group_id",
            )
            if _has_column(insp, "customers", c)
        ]
        if cols_to_drop:
            with op.batch_alter_table("customers") as batch_op:
                for col in cols_to_drop:
                    batch_op.drop_column(col)
        insp = sa.inspect(bind)

    for table, indexes in (
        ("sales_reps", ("ix_sales_reps_name",)),
        ("buying_groups", ("ix_buying_groups_name",)),
    ):
        if _has_table(insp, table):
            for ix in indexes:
                try:
                    op.drop_index(ix, table_name=table)
                except Exception:
                    pass
            op.drop_table(table)
