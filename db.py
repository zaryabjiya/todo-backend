"""
Database module - re-exports from db.session for backwards compatibility
"""
from db.session import (
    async_engine,
    sync_engine,
    AsyncSessionLocal,
    SessionLocal,
    get_async_db,
    get_sync_db,
    create_tables,
)

__all__ = [
    "async_engine",
    "sync_engine",
    "AsyncSessionLocal",
    "SessionLocal",
    "get_async_db",
    "get_sync_db",
    "create_tables",
]
