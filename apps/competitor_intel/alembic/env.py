# ruff: noqa: E402
from __future__ import annotations

import logging
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool, text

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from apps.competitor_intel.app import models  # noqa: F401,E402
from apps.competitor_intel.app.config import CONFIG  # noqa: E402

config = context.config
config.set_main_option("sqlalchemy.url", CONFIG.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

target_metadata = models.Base.metadata


def _enable_sqlite_pragmas(connection) -> None:
    if connection.dialect.name == "sqlite":
        logger.debug("Enabling SQLite pragmas for foreign keys and performance")
        connection.execute(text("PRAGMA foreign_keys=ON"))
        connection.execute(text("PRAGMA journal_mode=WAL"))


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _enable_sqlite_pragmas(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
