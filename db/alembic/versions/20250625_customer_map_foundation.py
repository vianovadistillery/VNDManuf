"""Customer map: buying group colours, relationship status, customer coordinates.

Revision ID: 20250625_cust_map
Revises: 20250624_so_payment
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250625_cust_map"
down_revision: Union[str, None] = "20250625_cust_price_notes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFAULT_GROUP_COLORS = {
    "CELLAR": "#E91E63",
    "BOTTLEO": "#FF9800",
    "LIQUORLAND": "#9C27B0",
    "IGA": "#F44336",
    "ENDEAVOUR": "#2196F3",
    "BWS": "#1976D2",
    "THIRSTY": "#4CAF50",
    "NONE": "#9E9E9E",
    "INDEP": "#795548",
    "OTHER": "#607D8B",
}


def _has_table(insp, name: str) -> bool:
    return name in insp.get_table_names()


def _has_column(insp, table: str, column: str) -> bool:
    if not _has_table(insp, table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
        bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_buying_groups"))
        bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_customers"))
    insp = sa.inspect(bind)

    if _has_table(insp, "buying_groups") and not _has_column(
        insp, "buying_groups", "map_color"
    ):
        if bind.dialect.name == "sqlite":
            bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
        try:
            with op.batch_alter_table("buying_groups", recreate="always") as batch:
                batch.add_column(sa.Column("map_color", sa.String(7), nullable=True))
        finally:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)
    if _has_table(insp, "customers"):
        pending = []
        if not _has_column(insp, "customers", "relationship_status"):
            pending.append(
                sa.Column(
                    "relationship_status",
                    sa.String(20),
                    nullable=False,
                    server_default="active",
                )
            )
        if not _has_column(insp, "customers", "latitude"):
            pending.append(sa.Column("latitude", sa.Numeric(10, 6), nullable=True))
        if not _has_column(insp, "customers", "longitude"):
            pending.append(sa.Column("longitude", sa.Numeric(10, 6), nullable=True))
        if pending:
            if bind.dialect.name == "sqlite":
                bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
                bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_customers"))
            try:
                with op.batch_alter_table("customers", recreate="always") as batch:
                    for col in pending:
                        batch.add_column(col)
            finally:
                if bind.dialect.name == "sqlite":
                    bind.execute(sa.text("PRAGMA foreign_keys=ON"))

    insp = sa.inspect(bind)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if _has_table(insp, "buying_groups"):
        seeds = [
            ("LIQUORLAND", "LiquorLand", "#9C27B0"),
            ("ENDEAVOUR", "Endeavour", "#2196F3"),
            ("NONE", "None", "#9E9E9E"),
        ]
        for code, name, color in seeds:
            row = bind.execute(
                sa.text(
                    "SELECT id FROM buying_groups WHERE code = :code AND deleted_at IS NULL"
                ),
                {"code": code},
            ).fetchone()
            if not row:
                bind.execute(
                    sa.text(
                        "INSERT INTO buying_groups "
                        "(id, code, name, map_color, is_active, version, created_at, updated_at) "
                        "VALUES (:id, :code, :name, :color, 1, 1, :now, :now)"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "code": code,
                        "name": name,
                        "color": color,
                        "now": now,
                    },
                )

        for code, color in _DEFAULT_GROUP_COLORS.items():
            bind.execute(
                sa.text(
                    "UPDATE buying_groups SET map_color = :color "
                    "WHERE code = :code AND deleted_at IS NULL "
                    "AND (map_color IS NULL OR map_color = '')"
                ),
                {"code": code, "color": color},
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)

    if _has_table(insp, "customers"):
        cols = [
            c
            for c in ("relationship_status", "latitude", "longitude")
            if _has_column(insp, "customers", c)
        ]
        if cols:
            with op.batch_alter_table("customers", recreate="always") as batch:
                for col in cols:
                    batch.drop_column(col)

    insp = sa.inspect(bind)
    if _has_table(insp, "buying_groups") and _has_column(
        insp, "buying_groups", "map_color"
    ):
        with op.batch_alter_table("buying_groups", recreate="always") as batch:
            batch.drop_column("map_color")
