"""
Audit Middleware — logs every HTTP request to audit_events table.
Falls back silently if DB is unavailable.
"""

import asyncio
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import text

logger = logging.getLogger("nadakki.audit_middleware")

# Endpoints to exclude from audit logging
_SKIP_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/favicon.ico", "/health")


class AuditMiddleware(BaseHTTPMiddleware):
    """Logs tenant_id, endpoint, method, status_code, latency to audit_events."""

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip noisy endpoints
        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        tenant_slug = request.headers.get("x-tenant-id", "credicefi")
        user_id = request.headers.get("x-user-id")
        method = request.method
        start = time.time()

        response = await call_next(request)

        latency_ms = round((time.time() - start) * 1000)
        status_code = response.status_code

        # Fire-and-forget DB write
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                _write_audit_event(
                    tenant_slug=tenant_slug,
                    user_id=user_id,
                    action=f"{method} {path}",
                    endpoint=path,
                    method=method,
                    status_code=status_code,
                    latency_ms=latency_ms,
                )
            )
        except Exception:
            pass  # silently skip if no loop or other issue

        return response


async def _write_audit_event(
    tenant_slug: str,
    user_id: str | None,
    action: str,
    endpoint: str,
    method: str,
    status_code: int,
    latency_ms: int,
) -> None:
    """Insert audit event into PostgreSQL. Resolves tenant slug to UUID. Fails silently."""
    try:
        from services.db import db_available, get_session

        if not db_available():
            return

        async with get_session() as session:
            # Resolve tenant slug to UUID
            result = await session.execute(
                text("SELECT id FROM tenants WHERE slug = :slug LIMIT 1"),
                {"slug": tenant_slug},
            )
            row = result.first()
            tenant_uuid = str(row[0]) if row else None

            await session.execute(
                text(
                    "INSERT INTO audit_events "
                    "(tenant_id, user_id, action, endpoint, method, status_code) "
                    "VALUES (:tenant_id, :user_id, :action, :endpoint, :method, :status_code)"
                ),
                {
                    "tenant_id": tenant_uuid,
                    "user_id": user_id,
                    "action": action,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                },
            )
            await session.commit()
    except Exception as exc:
        logger.debug("Audit event write failed: %s", exc)
