"""
Usage tracking middleware — increments executions_count on POST /agents/execute.
Also enforces plan execution limits (429 Too Many Requests).
"""

import asyncio
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from sqlalchemy import text

logger = logging.getLogger("nadakki.usage_middleware")

PLAN_LIMITS = {
    "starter": 100,
    "pro": 1000,
    "enterprise": None,  # unlimited
}


class UsageTrackingMiddleware(BaseHTTPMiddleware):
    """Tracks agent executions per tenant per day. Enforces plan limits."""

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        method = request.method

        # Only track POST /agents/execute
        if not (method == "POST" and path in ("/agents/execute", "/api/v1/agents/execute")):
            return await call_next(request)

        # Also match /api/v1/agents/{id}/execute
        if method == "POST" and "/agents/" in path and path.endswith("/execute"):
            pass  # fall through to tracking
        elif method == "POST" and path == "/agents/execute":
            pass  # fall through
        else:
            return await call_next(request)

        tenant_slug = request.headers.get("x-tenant-id", "credicefi")

        # Check limit before execution
        limit_error = await _check_plan_limit(tenant_slug)
        if limit_error:
            return JSONResponse(
                status_code=429,
                content={"error": "Plan execution limit exceeded", "detail": limit_error},
            )

        response = await call_next(request)

        # Increment usage counter (fire-and-forget) only on success
        if response.status_code == 200:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_increment_usage(tenant_slug))
            except Exception:
                pass

        return response


async def _check_plan_limit(tenant_slug: str) -> str | None:
    """Returns error message if tenant exceeds plan limit, None if OK."""
    try:
        from services.db import db_available, get_session
        if not db_available():
            return None

        async with get_session() as session:
            # Get tenant plan and current month usage
            result = await session.execute(
                text(
                    "SELECT t.plan, COALESCE(SUM(u.executions_count), 0) "
                    "FROM tenants t "
                    "LEFT JOIN usage_tracking u ON u.tenant_id = t.id "
                    "  AND u.date >= date_trunc('month', CURRENT_DATE) "
                    "WHERE t.slug = :slug "
                    "GROUP BY t.plan"
                ),
                {"slug": tenant_slug},
            )
            row = result.first()
            if not row:
                return None

            plan = row[0] or "starter"
            current_usage = int(row[1])
            max_exec = PLAN_LIMITS.get(plan)

            if max_exec is not None and current_usage >= max_exec:
                return (
                    f"Plan '{plan}' allows {max_exec} executions/month. "
                    f"Current usage: {current_usage}. Upgrade your plan."
                )
    except Exception as e:
        logger.debug("Plan limit check failed: %s", e)
    return None


async def _increment_usage(tenant_slug: str) -> None:
    """Increment the daily execution counter for a tenant."""
    try:
        from services.db import db_available, get_session
        if not db_available():
            return

        async with get_session() as session:
            # Resolve slug
            result = await session.execute(
                text("SELECT id FROM tenants WHERE slug = :slug"),
                {"slug": tenant_slug},
            )
            row = result.first()
            if not row:
                return
            tenant_id = str(row[0])

            # Upsert daily counter
            await session.execute(
                text(
                    "INSERT INTO usage_tracking (tenant_id, date, executions_count) "
                    "VALUES (:tid, CURRENT_DATE, 1) "
                    "ON CONFLICT (tenant_id, date) "
                    "DO UPDATE SET executions_count = usage_tracking.executions_count + 1"
                ),
                {"tid": tenant_id},
            )
            await session.commit()
    except Exception as e:
        logger.debug("Usage increment failed: %s", e)
