"""add_qc_test_types

Revision ID: 2f0c52f5af1d
Revises: f6d2c4a4c6e1
Create Date: 2025-11-08 20:00:00.000000
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2f0c52f5af1d"
down_revision = "f6d2c4a4c6e1"
branch_labels = ("core",)
depends_on = None


def has_table(insp: sa.engine.reflection.Inspector, table_name: str) -> bool:
    return table_name in insp.get_table_names()


def has_column(
    insp: sa.engine.reflection.Inspector, table_name: str, column_name: str
) -> bool:
    return any(col["name"] == column_name for col in insp.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)

    if not has_table(insp, "qc_test_types"):
        op.create_table(
            "qc_test_types",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("code", sa.String(length=50), nullable=False, index=True),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("unit", sa.String(length=20), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1"),
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(length=100), nullable=True),
            sa.Column(
                "version",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("1"),
            ),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(length=100), nullable=True),
            sa.Column("previous_version_id", sa.String(length=36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(length=100), nullable=True),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_qc_test_types")),
            sa.UniqueConstraint("code", name=op.f("uq_qc_test_types_code")),
        )
        op.create_index(
            "ix_qc_test_types_active", "qc_test_types", ["is_active"], unique=False
        )

        now = datetime.now(timezone.utc)
        abv_id = str(uuid.uuid4())
        ph_id = str(uuid.uuid4())

        qc_test_types_table = sa.table(
            "qc_test_types",
            sa.column("id", sa.String(length=36)),
            sa.column("code", sa.String(length=50)),
            sa.column("name", sa.String(length=100)),
            sa.column("unit", sa.String(length=20)),
            sa.column("description", sa.Text()),
            sa.column("is_active", sa.Boolean()),
            sa.column("created_at", sa.DateTime()),
            sa.column("updated_at", sa.DateTime()),
            sa.column("deleted_at", sa.DateTime()),
            sa.column("deleted_by", sa.String(length=100)),
            sa.column("version", sa.Integer()),
            sa.column("versioned_at", sa.DateTime()),
            sa.column("versioned_by", sa.String(length=100)),
            sa.column("previous_version_id", sa.String(length=36)),
            sa.column("archived_at", sa.DateTime()),
            sa.column("archived_by", sa.String(length=100)),
        )

        op.bulk_insert(
            qc_test_types_table,
            [
                {
                    "id": abv_id,
                    "code": "ABV",
                    "name": "Alcohol By Volume",
                    "unit": "vol/vol",
                    "description": "Alcohol by volume",
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                    "deleted_at": None,
                    "deleted_by": None,
                    "version": 1,
                    "versioned_at": None,
                    "versioned_by": None,
                    "previous_version_id": None,
                    "archived_at": None,
                    "archived_by": None,
                },
                {
                    "id": ph_id,
                    "code": "PH",
                    "name": "pH",
                    "unit": None,
                    "description": "Acidity / alkalinity",
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                    "deleted_at": None,
                    "deleted_by": None,
                    "version": 1,
                    "versioned_at": None,
                    "versioned_by": None,
                    "previous_version_id": None,
                    "archived_at": None,
                    "archived_by": None,
                },
            ],
        )
    else:
        # Retrieve seeded IDs if table already existed
        rows = bind.execute(
            sa.text("SELECT id, code FROM qc_test_types WHERE code IN ('ABV', 'PH')")
        ).fetchall()
        abv_id = next((row.id for row in rows if row.code.upper() == "ABV"), None)
        ph_id = next((row.id for row in rows if row.code.upper() == "PH"), None)

    # Ensure wo_qc_tests has test_type_id column
    if not has_column(insp, "wo_qc_tests", "test_type_id"):
        with op.batch_alter_table("wo_qc_tests", recreate="always") as batch_op:
            batch_op.add_column(
                sa.Column("test_type_id", sa.String(length=36), nullable=True)
            )
            batch_op.create_index(
                "ix_wo_qc_tests_test_type_id", ["test_type_id"], unique=False
            )
            batch_op.create_foreign_key(
                op.f("fk_wo_qc_tests__test_type_id__qc_test_types"),
                "qc_test_types",
                ["test_type_id"],
                ["id"],
                ondelete="SET NULL",
            )

    # Backfill existing QC tests where possible
    if has_column(insp, "wo_qc_tests", "test_type_id"):
        updates: list[tuple[str, str]] = []
        if "abv_id" in locals() and abv_id:
            updates.append((abv_id, "abv"))
        if "ph_id" in locals() and ph_id:
            updates.append((ph_id, "ph"))

        for type_id, code in updates:
            op.execute(
                sa.text(
                    "UPDATE wo_qc_tests SET test_type_id = :type_id "
                    "WHERE test_type_id IS NULL AND LOWER(test_type) = :code"
                ),
                {"type_id": type_id, "code": code.lower()},
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)

    if has_column(insp, "wo_qc_tests", "test_type_id"):
        with op.batch_alter_table("wo_qc_tests", recreate="always") as batch_op:
            try:
                batch_op.drop_constraint(
                    op.f("fk_wo_qc_tests__test_type_id__qc_test_types"),
                    type_="foreignkey",
                )
            except Exception:
                pass
            try:
                batch_op.drop_index("ix_wo_qc_tests_test_type_id")
            except Exception:
                pass
            batch_op.drop_column("test_type_id")

    if has_table(insp, "qc_test_types"):
        try:
            op.drop_index("ix_qc_test_types_active", table_name="qc_test_types")
        except Exception:
            pass
        op.drop_table("qc_test_types")
