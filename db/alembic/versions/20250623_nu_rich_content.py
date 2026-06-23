"""Add rich_content_html and video_embed_url to training_articles.

Revision ID: 20250623_nu_rich
Revises: 20250622_nu_training
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250623_nu_rich"
down_revision: Union[str, None] = "20250622_nu_training"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)
    if not insp.has_table("training_articles"):
        return
    with op.batch_alter_table("training_articles", recreate="always") as batch:
        if not _has_column(insp, "training_articles", "rich_content_html"):
            batch.add_column(sa.Column("rich_content_html", sa.Text(), nullable=True))
        if not _has_column(insp, "training_articles", "video_embed_url"):
            batch.add_column(
                sa.Column("video_embed_url", sa.String(500), nullable=True)
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        bind.execute(sa.text("PRAGMA foreign_keys=ON"))
    insp = sa.inspect(bind)
    if not insp.has_table("training_articles"):
        return
    cols = [c["name"] for c in insp.get_columns("training_articles")]
    with op.batch_alter_table("training_articles", recreate="always") as batch:
        if "video_embed_url" in cols:
            batch.drop_column("video_embed_url")
        if "rich_content_html" in cols:
            batch.drop_column("rich_content_html")
