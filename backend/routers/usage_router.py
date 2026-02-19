"""
Usage tracking router — GET /api/v1/tenants/{tenant_slug}/usage
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from admin_auth import verify_admin_key

logger = logging.getLogger("nadakki.usage")

router = APIRouter(prefix="/api/v1", tags=["usage"])

PLAN_LIMITS = {
    "starter": 100,
    "pro": 1000,
    "enterprise": None,
}


def _get_session():
    from services.db import db_available, get_session
    if not db_available():
        raise HTTPException(503, {"error": "Database unavailable"})
    return get_session


@router.get("/tenants/{tenant_slug}/usage")
async def get_tenant_usage(
    tenant_slug: str,
    admin_info: dict = Depends(verify_admin_key),
):
    """Return current month usage for a tenant."""
    get_sess = _get_session()

    async with get_sess() as session:
        # Get tenant info
        result = await session.execute(
            text("SELECT id, plan FROM tenants WHERE slug = :slug"),
            {"slug": tenant_slug},
        )
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Tenant '{tenant_slug}' not found"})
        tenant_id = str(row[0])
        plan = row[1] or "starter"

        # Current month usage
        result = await session.execute(
            text(
                "SELECT COALESCE(SUM(executions_count), 0), COALESCE(SUM(tokens_used), 0) "
                "FROM usage_tracking "
                "WHERE tenant_id = :tid AND date >= date_trunc('month', CURRENT_DATE)"
            ),
            {"tid": tenant_id},
        )
        row = result.first()
        executions = int(row[0]) if row else 0
        tokens = int(row[1]) if row else 0

        max_exec = PLAN_LIMITS.get(plan)

        return {
            "tenant_slug": tenant_slug,
            "tenant_id": tenant_id,
            "plan": plan,
            "current_month": {
                "executions": executions,
                "tokens": tokens,
            },
            "limits": {
                "max_executions": max_exec if max_exec is not None else "unlimited",
            },
            "usage_pct": round(executions / max_exec * 100, 1) if max_exec else 0,
        }
