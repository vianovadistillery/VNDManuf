"""Add NU training hub tables (categories + articles).

Revision ID: 20250622_nu_training
Revises: 20250621_crm
Create Date: 2025-06-22

Migrations: nu training hub tables (SQLite batch-safe)
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250622_nu_training"
down_revision: Union[str, None] = "20250621_crm"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(insp: sa.engine.reflection.Inspector, table: str) -> bool:
    return table in insp.get_table_names()


def _has_index(insp: sa.engine.reflection.Inspector, table: str, name: str) -> bool:
    if not _has_table(insp, table):
        return False
    return any(ix["name"] == name for ix in insp.get_indexes(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if not _has_table(insp, "training_categories"):
        op.create_table(
            "training_categories",
            sa.Column("id", sa.String(36), primary_key=True, nullable=False),
            sa.Column("slug", sa.String(100), nullable=False),
            sa.Column("code", sa.String(20), nullable=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("parent_id", sa.String(36), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
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
            sa.ForeignKeyConstraint(
                ["parent_id"],
                ["training_categories.id"],
                name="fk_training_categories__parent_id__training_categories",
            ),
        )
        if not _has_index(insp, "training_categories", "ix_training_categories_slug"):
            op.create_index(
                "ix_training_categories_slug",
                "training_categories",
                ["slug"],
                unique=True,
            )
        if not _has_index(insp, "training_categories", "ix_training_categories_parent"):
            op.create_index(
                "ix_training_categories_parent", "training_categories", ["parent_id"]
            )
        if not _has_index(insp, "training_categories", "ix_training_categories_sort"):
            op.create_index(
                "ix_training_categories_sort", "training_categories", ["sort_order"]
            )

    insp = sa.inspect(bind)
    if not _has_table(insp, "training_articles"):
        op.create_table(
            "training_articles",
            sa.Column("id", sa.String(36), primary_key=True, nullable=False),
            sa.Column("slug", sa.String(150), nullable=False),
            sa.Column("title", sa.String(300), nullable=False),
            sa.Column("category_id", sa.String(36), nullable=True),
            sa.Column(
                "content_type", sa.String(30), nullable=False, server_default="sop"
            ),
            sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("purpose", sa.Text(), nullable=True),
            sa.Column("prerequisites", sa.Text(), nullable=True),
            sa.Column("safety_notes", sa.Text(), nullable=True),
            sa.Column("steps_json", sa.Text(), nullable=True),
            sa.Column("risks_json", sa.Text(), nullable=True),
            sa.Column("troubleshooting", sa.Text(), nullable=True),
            sa.Column("related_links_json", sa.Text(), nullable=True),
            sa.Column("body_markdown", sa.Text(), nullable=True),
            sa.Column("tags", sa.String(500), nullable=True),
            sa.Column("systems", sa.String(200), nullable=True),
            sa.Column("loom_url", sa.String(500), nullable=True),
            sa.Column("sharepoint_url", sa.String(500), nullable=True),
            sa.Column("search_blob", sa.Text(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
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
            sa.ForeignKeyConstraint(
                ["category_id"],
                ["training_categories.id"],
                name="fk_training_articles__category_id__training_categories",
            ),
            sa.CheckConstraint(
                "content_type IN ('sop','guide','checklist','reference')",
                name="ck_training_articles_content_type",
            ),
            sa.CheckConstraint(
                "status IN ('draft','published','archived')",
                name="ck_training_articles_status",
            ),
        )
        insp = sa.inspect(bind)
        for idx_name, cols, unique in (
            ("ix_training_articles_slug", ["slug"], True),
            ("ix_training_articles_category", ["category_id"], False),
            ("ix_training_articles_status", ["status"], False),
            ("ix_training_articles_content_type", ["content_type"], False),
        ):
            if not _has_index(insp, "training_articles", idx_name):
                op.create_index(idx_name, "training_articles", cols, unique=unique)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if _has_table(insp, "training_articles"):
        for idx in (
            "ix_training_articles_content_type",
            "ix_training_articles_status",
            "ix_training_articles_category",
            "ix_training_articles_slug",
        ):
            try:
                op.drop_index(idx, table_name="training_articles")
            except Exception:
                pass
        op.drop_table("training_articles")

    insp = sa.inspect(bind)
    if _has_table(insp, "training_categories"):
        for idx in (
            "ix_training_categories_sort",
            "ix_training_categories_parent",
            "ix_training_categories_slug",
        ):
            try:
                op.drop_index(idx, table_name="training_categories")
            except Exception:
                pass
        op.drop_table("training_categories")
