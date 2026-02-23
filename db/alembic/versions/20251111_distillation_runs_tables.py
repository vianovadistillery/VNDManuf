"""distillation tables (SQLite batch-safe)

Revision ID: distillation_runs_20251111
Revises: eaf2f04d3b5d
Create Date: 2025-11-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "distillation_runs_20251111"
down_revision: Union[str, None] = "fde4c825d571"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_table(insp: sa.Inspector, table_name: str) -> bool:
    return table_name in insp.get_table_names()


def has_index(insp: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(ix["name"] == index_name for ix in insp.get_indexes(table_name))


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if not has_table(insp, "distillation_runs"):
        op.create_table(
            "distillation_runs",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("code", sa.String(40), nullable=False, unique=True),
            sa.Column("external_run_code", sa.String(64), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, index=True),
            sa.Column("still_code", sa.String(64), nullable=True),
            sa.Column(
                "product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=True
            ),
            sa.Column("open_at", sa.DateTime(), nullable=True),
            sa.Column("close_at", sa.DateTime(), nullable=True),
            sa.Column("actual_cost", sa.Numeric(12, 4), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(100), nullable=True),
            sa.Column("previous_version_id", sa.String(36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(100), nullable=True),
        )

    if has_table(insp, "distillation_runs") and not has_index(
        insp, "distillation_runs", "ix_distillation_runs_status"
    ):
        op.create_index(
            "ix_distillation_runs_status",
            "distillation_runs",
            ["status", "still_code"],
        )

    if not has_table(insp, "distillation_periods"):
        op.create_table(
            "distillation_periods",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "run_id",
                sa.String(36),
                sa.ForeignKey("distillation_runs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "botanical_product_id",
                sa.String(36),
                sa.ForeignKey("products.id"),
                nullable=True,
            ),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("ended_at", sa.DateTime(), nullable=True),
            sa.Column("duration_seconds", sa.Integer(), nullable=True),
            sa.Column("avg_feed_rate_lph", sa.Numeric(12, 4), nullable=True),
            sa.Column("avg_product_rate_lph", sa.Numeric(12, 4), nullable=True),
            sa.Column("feed_mass_kg", sa.Numeric(12, 4), nullable=True),
            sa.Column("product_mass_kg", sa.Numeric(12, 4), nullable=True),
            sa.Column(
                "record_source", sa.String(20), nullable=False, server_default="manual"
            ),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(100), nullable=True),
            sa.Column("previous_version_id", sa.String(36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(100), nullable=True),
        )

    if has_table(insp, "distillation_periods") and not has_index(
        insp, "distillation_periods", "ix_distillation_periods_run"
    ):
        op.create_index(
            "ix_distillation_periods_run",
            "distillation_periods",
            ["run_id", "started_at"],
        )

    if not has_table(insp, "distillation_events"):
        op.create_table(
            "distillation_events",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "run_id",
                sa.String(36),
                sa.ForeignKey("distillation_runs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "period_id",
                sa.String(36),
                sa.ForeignKey("distillation_periods.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("event_type", sa.String(32), nullable=False),
            sa.Column("occurred_at", sa.DateTime(), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=True),
            sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
            sa.Column("external_id", sa.String(64), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(100), nullable=True),
            sa.Column("previous_version_id", sa.String(36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(100), nullable=True),
        )

    if has_table(insp, "distillation_events"):
        if not has_index(insp, "distillation_events", "ix_distillation_events_run_ts"):
            op.create_index(
                "ix_distillation_events_run_ts",
                "distillation_events",
                ["run_id", "occurred_at"],
            )
        if not has_index(
            insp, "distillation_events", "ix_distillation_events_external"
        ):
            op.create_index(
                "ix_distillation_events_external",
                "distillation_events",
                ["external_id"],
            )

    if not has_table(insp, "distillation_materials"):
        op.create_table(
            "distillation_materials",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "run_id",
                sa.String(36),
                sa.ForeignKey("distillation_runs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "period_id",
                sa.String(36),
                sa.ForeignKey("distillation_periods.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "product_id",
                sa.String(36),
                sa.ForeignKey("products.id"),
                nullable=False,
            ),
            sa.Column("direction", sa.String(10), nullable=False),
            sa.Column(
                "inventory_movement_id",
                sa.String(36),
                sa.ForeignKey("inventory_movements.id"),
                nullable=True,
            ),
            sa.Column("qty_kg", sa.Numeric(12, 4), nullable=False),
            sa.Column("uom", sa.String(10), nullable=False, server_default="KG"),
            sa.Column("unit_cost", sa.Numeric(12, 4), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(100), nullable=True),
            sa.Column("previous_version_id", sa.String(36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(100), nullable=True),
        )

    if has_table(insp, "distillation_materials"):
        if not has_index(
            insp, "distillation_materials", "ix_distillation_materials_run"
        ):
            op.create_index(
                "ix_distillation_materials_run",
                "distillation_materials",
                ["run_id", "direction"],
            )
        if not has_index(
            insp, "distillation_materials", "ix_distillation_materials_movement"
        ):
            op.create_index(
                "ix_distillation_materials_movement",
                "distillation_materials",
                ["inventory_movement_id"],
            )

    if not has_table(insp, "distillation_parameters"):
        op.create_table(
            "distillation_parameters",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "run_id",
                sa.String(36),
                sa.ForeignKey("distillation_runs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "period_id",
                sa.String(36),
                sa.ForeignKey("distillation_periods.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("parameter_name", sa.String(64), nullable=False),
            sa.Column("unit", sa.String(16), nullable=True),
            sa.Column("recorded_at", sa.DateTime(), nullable=False),
            sa.Column("value_numeric", sa.Numeric(18, 6), nullable=True),
            sa.Column("value_text", sa.String(128), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("deleted_by", sa.String(100), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("versioned_at", sa.DateTime(), nullable=True),
            sa.Column("versioned_by", sa.String(100), nullable=True),
            sa.Column("previous_version_id", sa.String(36), nullable=True),
            sa.Column("archived_at", sa.DateTime(), nullable=True),
            sa.Column("archived_by", sa.String(100), nullable=True),
        )

    if has_table(insp, "distillation_parameters") and not has_index(
        insp, "distillation_parameters", "ix_distillation_parameters_run_param"
    ):
        op.create_index(
            "ix_distillation_parameters_run_param",
            "distillation_parameters",
            ["run_id", "parameter_name"],
        )


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if has_table(insp, "distillation_parameters"):
        if has_index(
            insp, "distillation_parameters", "ix_distillation_parameters_run_param"
        ):
            op.drop_index(
                "ix_distillation_parameters_run_param",
                table_name="distillation_parameters",
            )
        op.drop_table("distillation_parameters")

    if has_table(insp, "distillation_materials"):
        if has_index(
            insp, "distillation_materials", "ix_distillation_materials_movement"
        ):
            op.drop_index(
                "ix_distillation_materials_movement",
                table_name="distillation_materials",
            )
        if has_index(insp, "distillation_materials", "ix_distillation_materials_run"):
            op.drop_index(
                "ix_distillation_materials_run",
                table_name="distillation_materials",
            )
        op.drop_table("distillation_materials")

    if has_table(insp, "distillation_events"):
        if has_index(insp, "distillation_events", "ix_distillation_events_external"):
            op.drop_index(
                "ix_distillation_events_external",
                table_name="distillation_events",
            )
        if has_index(insp, "distillation_events", "ix_distillation_events_run_ts"):
            op.drop_index(
                "ix_distillation_events_run_ts",
                table_name="distillation_events",
            )
        op.drop_table("distillation_events")

    if has_table(insp, "distillation_periods"):
        if has_index(insp, "distillation_periods", "ix_distillation_periods_run"):
            op.drop_index(
                "ix_distillation_periods_run",
                table_name="distillation_periods",
            )
        op.drop_table("distillation_periods")

    if has_table(insp, "distillation_runs"):
        if has_index(insp, "distillation_runs", "ix_distillation_runs_status"):
            op.drop_index(
                "ix_distillation_runs_status",
                table_name="distillation_runs",
            )
        op.drop_table("distillation_runs")
