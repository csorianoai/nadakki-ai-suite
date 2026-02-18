"""
Database layer — wraps services/db.py and adds FastAPI dependency.
Supports PostgreSQL (async via asyncpg) with SQLite fallback for local dev.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

logger = logging.getLogger("nadakki.db")

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


def _build_url() -> Optional[str]:
    """Build async database URL from DATABASE_URL env var."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        return None

    # PostgreSQL: Render/Heroku use postgres:// but asyncpg needs postgresql+asyncpg://
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql+asyncpg://"):
        return url

    # SQLite fallback for local dev
    if url.startswith("sqlite"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return url


def init_database() -> bool:
    """Initialize the async engine. Returns True if DB is available."""
    global _engine, _session_factory
    url = _build_url()
    if not url:
        logger.info("DATABASE_URL not set — running without persistent DB")
        return False
    _engine = create_async_engine(url, pool_size=5, max_overflow=10, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    logger.info("Database engine initialized (%s)", "postgresql" if "postgresql" in url else "sqlite")
    return True


def db_available() -> bool:
    return _engine is not None


def get_engine() -> Optional[AsyncEngine]:
    return _engine


@asynccontextmanager
async def get_session(tenant_id: Optional[str] = None) -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession. Sets RLS tenant context if tenant_id provided."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized — call init_database() first")
    async with _session_factory() as session:
        if tenant_id:
            await session.execute(
                text("SET LOCAL app.current_tenant_id = :tid"),
                {"tid": tenant_id},
            )
        yield session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized")
    async with _session_factory() as session:
        yield session
