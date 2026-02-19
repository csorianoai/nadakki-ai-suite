"""
Usage tracking router.
GET /api/v1/tenants/{tenant_id}/usage        — current month summary
GET /api/v1/tenants/{tenant_id}/usage/recent — last 10 agent executions

{tenant_id} accepts both slug and UUID.
"""

import logging
import re

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

logger = logging.getLogger("nadakki.usage")

router = APIRouter(prefix="/api/v1", tags=["usage"])

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)

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


async def _resolve_tenant(session, tenant_id: str):
    """Returns (uuid_str, plan)."""
    if _UUID_RE.match(tenant_id):
        result = await session.execute(
            text("SELECT id, plan FROM tenants WHERE id = :tid"), {"tid": tenant_id}
        )
    else:
        result = await session.execute(
            text("SELECT id, plan FROM tenants WHERE slug = :slug"), {"slug": tenant_id}
        )
    row = result.first()
    if not row:
        raise HTTPException(404, {"error": f"Tenant '{tenant_id}' not found"})
    return str(row[0]), row[1] or "starter"


@router.get("/tenants/{tenant_id}/usage")
async def get_tenant_usage(tenant_id: str):
    """Return current month usage for a tenant."""
    get_sess = _get_session()

    async with get_sess() as session:
        tid, plan = await _resolve_tenant(session, tenant_id)

        # Count agent_executions this month
        result = await session.execute(
            text(
                "SELECT count(*) FROM agent_executions "
                "WHERE tenant_id = :tid "
                "AND created_at >= date_trunc('month', CURRENT_TIMESTAMP)"
            ),
            {"tid": tid},
        )
        executions = result.scalar() or 0

        # Also check usage_tracking table if it has data
        try:
            result = await session.execute(
                text(
                    "SELECT COALESCE(SUM(executions_count), 0), COALESCE(SUM(tokens_used), 0) "
                    "FROM usage_tracking "
                    "WHERE tenant_id = :tid AND date >= date_trunc('month', CURRENT_DATE)"
                ),
                {"tid": tid},
            )
            row = result.first()
            tracked_exec = int(row[0]) if row else 0
            tokens = int(row[1]) if row else 0
            # Use the higher of the two counts
            executions = max(executions, tracked_exec)
        except Exception:
            tokens = 0

        max_exec = PLAN_LIMITS.get(plan)

        return {
            "tenant_id": tid,
            "plan": plan,
            "executions_this_month": executions,
            "tokens_used": tokens,
            "limit": max_exec if max_exec is not None else "unlimited",
            "usage_pct": round(executions / max_exec * 100, 1) if max_exec else 0,
        }


@router.get("/tenants/{tenant_id}/usage/recent")
async def get_recent_executions(tenant_id: str):
    """Return last 10 agent executions for a tenant."""
    get_sess = _get_session()

    async with get_sess() as session:
        tid, plan = await _resolve_tenant(session, tenant_id)

        result = await session.execute(
            text(
                "SELECT id, agent_id, dry_run, created_at "
                "FROM agent_executions "
                "WHERE tenant_id = :tid "
                "ORDER BY created_at DESC LIMIT 10"
            ),
            {"tid": tid},
        )
        rows = [
            {
                "id": str(r[0]),
                "agent_id": r[1],
                "dry_run": r[2],
                "created_at": r[3].isoformat() if r[3] else None,
            }
            for r in result.fetchall()
        ]
        return {"tenant_id": tid, "recent_executions": rows, "total": len(rows)}
