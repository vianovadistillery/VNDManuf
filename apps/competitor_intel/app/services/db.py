from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import scoped_session, sessionmaker

from ..config import CONFIG


def _create_engine() -> Engine:
    engine = create_engine(
        CONFIG.database_url,
        connect_args={"check_same_thread": False}
        if CONFIG.database_url.startswith("sqlite")
        else {},
        future=True,
    )

    if CONFIG.database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[unused-variable]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


ENGINE = _create_engine()
SessionFactory = sessionmaker(
    bind=ENGINE, autoflush=False, autocommit=False, expire_on_commit=False, future=True
)
Session = scoped_session(SessionFactory)


@contextmanager
def session_scope() -> Iterator[SASession]:
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - rethrow after cleanup
        session.rollback()
        raise
    finally:
        session.close()
