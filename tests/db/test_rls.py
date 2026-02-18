"""
Tests for Row-Level Security (RLS) tenant isolation.
Requires a PostgreSQL database with migrations applied.

Run: DATABASE_URL=postgresql://... pytest tests/db/test_rls.py -v
"""

import os
import pytest
import asyncio
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Skip entire module if no DATABASE_URL
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set — skipping PostgreSQL RLS tests",
)


def _get_async_url() -> str:
    url = os.environ["DATABASE_URL"]
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def engine():
    eng = create_async_engine(_get_async_url(), echo=False)
    yield eng
    await eng.dispose()


@pytest.fixture(scope="module")
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_test_tenants(session_factory):
    """Ensure test tenants exist, clean up test data after."""
    async with session_factory() as session:
        await session.execute(
            text("INSERT INTO tenants (id, name) VALUES ('test_a', 'Tenant A') ON CONFLICT DO NOTHING")
        )
        await session.execute(
            text("INSERT INTO tenants (id, name) VALUES ('test_b', 'Tenant B') ON CONFLICT DO NOTHING")
        )
        await session.commit()

    yield

    # Cleanup
    async with session_factory() as session:
        await session.execute(text("DELETE FROM audit_events WHERE tenant_id IN ('test_a', 'test_b')"))
        await session.execute(text("DELETE FROM agent_executions WHERE tenant_id IN ('test_a', 'test_b')"))
        await session.commit()


class TestRLSTenantIsolation:
    """Test that RLS policies enforce tenant isolation."""

    @pytest.mark.asyncio
    async def test_tenant_a_cannot_see_tenant_b_data(self, session_factory):
        """Insert data for tenant A, query from tenant B context — should return 0 rows."""
        # Insert data as superuser (no RLS context)
        async with session_factory() as session:
            await session.execute(
                text(
                    "INSERT INTO audit_events (tenant_id, action, endpoint, method, status_code, latency_ms) "
                    "VALUES ('test_a', 'GET /test', '/test', 'GET', 200, 10)"
                )
            )
            await session.commit()

        # Query from tenant B context
        async with session_factory() as session:
            await session.execute(text("SET LOCAL app.tenant_id = 'test_b'"))
            result = await session.execute(
                text("SELECT * FROM audit_events WHERE tenant_id = 'test_a'")
            )
            rows = result.fetchall()
            assert len(rows) == 0, "Tenant B should not see Tenant A data through RLS"

    @pytest.mark.asyncio
    async def test_tenant_a_sees_own_data(self, session_factory):
        """Insert data for tenant A, query from tenant A context — should see it."""
        async with session_factory() as session:
            await session.execute(
                text(
                    "INSERT INTO audit_events (tenant_id, action, endpoint, method, status_code, latency_ms) "
                    "VALUES ('test_a', 'GET /own', '/own', 'GET', 200, 5)"
                )
            )
            await session.commit()

        # Query from tenant A context
        async with session_factory() as session:
            await session.execute(text("SET LOCAL app.tenant_id = 'test_a'"))
            result = await session.execute(
                text("SELECT * FROM audit_events WHERE tenant_id = 'test_a' AND endpoint = '/own'")
            )
            rows = result.fetchall()
            assert len(rows) >= 1, "Tenant A should see its own data"

    @pytest.mark.asyncio
    async def test_agent_execution_isolation(self, session_factory):
        """Agent executions for tenant A invisible to tenant B."""
        async with session_factory() as session:
            await session.execute(
                text(
                    "INSERT INTO agent_executions (tenant_id, agent_id, dry_run, result) "
                    "VALUES ('test_a', 'test_agent', true, '{}')"
                )
            )
            await session.commit()

        # Query from tenant B
        async with session_factory() as session:
            await session.execute(text("SET LOCAL app.tenant_id = 'test_b'"))
            result = await session.execute(
                text("SELECT * FROM agent_executions WHERE tenant_id = 'test_a'")
            )
            rows = result.fetchall()
            assert len(rows) == 0, "Tenant B should not see Tenant A agent executions"


class TestAuditEventGeneration:
    """Test that audit events are created."""

    @pytest.mark.asyncio
    async def test_audit_event_insert(self, session_factory):
        """Verify we can insert and read audit events."""
        async with session_factory() as session:
            await session.execute(
                text(
                    "INSERT INTO audit_events (tenant_id, action, endpoint, method, status_code, latency_ms) "
                    "VALUES ('test_a', 'POST /agents/execute', '/agents/execute', 'POST', 200, 42)"
                )
            )
            await session.commit()

        async with session_factory() as session:
            await session.execute(text("SET LOCAL app.tenant_id = 'test_a'"))
            result = await session.execute(
                text("SELECT * FROM audit_events WHERE tenant_id = 'test_a' AND endpoint = '/agents/execute'")
            )
            rows = result.fetchall()
            assert len(rows) >= 1
            row = rows[0]
            assert row.status_code == 200
            assert row.latency_ms == 42
