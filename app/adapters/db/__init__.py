# app/adapters/db/__init__.py
"""DB subpackage exports."""
from .base import Base, metadata
from .session import get_engine, get_session, get_db, create_tables, drop_tables

# Import QB models to register with Base
from . import qb_models  # noqa

# Import assemblies and shopify models to register with Base
from . import models_assemblies_shopify  # noqa

__all__ = [
    "Base", "metadata",
    "get_engine", "get_session", "get_db",
    "create_tables", "drop_tables",
]
