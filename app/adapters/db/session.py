# app/adapters/db/session.py
"""Database engine & session management."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.adapters.db.base import Base
from app.settings import settings


def get_engine(echo: bool | None = None):
    url = settings.database.database_url
    kw = {
        "echo": False if echo is None else echo,
        "pool_pre_ping": True,
        "future": True,
    }
    if url.startswith("sqlite"):
        kw.update(
            {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
        )
    else:
        kw.update(
            {
                "pool_size": settings.database.pool_size,
                "max_overflow": settings.database.max_overflow,
            }
        )
    return create_engine(url, **kw)


_engine = None
_SessionLocal = None


def _lazy_init():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = get_engine()
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=_engine, autoflush=False, autocommit=False, future=True
        )


def get_session():
    _lazy_init()
    return _SessionLocal()


def get_db():
    _lazy_init()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    _lazy_init()
    Base.metadata.create_all(bind=_engine)


def drop_tables():
    _lazy_init()
    Base.metadata.drop_all(bind=_engine)
