"""
Database layer — async SQLAlchemy engine + session factory.
Falls back gracefully when DATABASE_URL is not set.
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

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


def _get_async_url() -> Optional[str]:
    """Convert DATABASE_URL to asyncpg format."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        return None
    # Render / Heroku use postgres:// but SQLAlchemy async needs postgresql+asyncpg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def init_db() -> bool:
    """Initialize the async engine. Returns True if DB is available."""
    global _engine, _session_factory
    url = _get_async_url()
    if not url:
        logger.info("DATABASE_URL not set — using JSONL fallback")
        return False
    _engine = create_async_engine(url, pool_size=5, max_overflow=10, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    logger.info("PostgreSQL engine initialized")
    return True


def db_available() -> bool:
    return _engine is not None


@asynccontextmanager
async def get_session(tenant_id: Optional[str] = None):
    """Yield an AsyncSession. Sets RLS tenant context if tenant_id provided."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized")
    async with _session_factory() as session:
        if tenant_id:
            await session.execute(
                text("SET LOCAL app.current_tenant_id = :tid"),
                {"tid": tenant_id},
            )
        yield session


async def db_ping() -> dict:
    """Health check — returns ok/failed + latency_ms."""
    if _engine is None:
        return {"status": "unavailable", "reason": "DATABASE_URL not set"}
    try:
        start = time.time()
        async with _engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency = round((time.time() - start) * 1000)
        return {"status": "ok", "latency_ms": latency}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
