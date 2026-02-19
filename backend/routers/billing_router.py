"""
Billing stub router — plans, tenant billing, plan change (no real Stripe).
{tenant_id} accepts both slug and UUID.
"""

import logging
import re
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

logger = logging.getLogger("nadakki.billing")

router = APIRouter(prefix="/api/v1", tags=["billing"])

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)

PLANS = [
    {"name": "starter", "price": 999, "executions": 100, "description": "For small teams getting started"},
    {"name": "pro", "price": 2999, "executions": 1000, "description": "For growing businesses"},
    {"name": "enterprise", "price": 9999, "executions": "unlimited", "description": "For large organizations"},
]

VALID_PLANS = {p["name"] for p in PLANS}


class PlanChangeRequest(BaseModel):
    plan: str


def _get_session():
    from services.db import db_available, get_session
    if not db_available():
        raise HTTPException(503, {"error": "Database unavailable"})
    return get_session


async def _resolve_tenant(session, tenant_id: str):
    """Returns (uuid_str, slug, plan, created_at)."""
    if _UUID_RE.match(tenant_id):
        result = await session.execute(
            text("SELECT id, slug, plan, created_at FROM tenants WHERE id = :tid"),
            {"tid": tenant_id},
        )
    else:
        result = await session.execute(
            text("SELECT id, slug, plan, created_at FROM tenants WHERE slug = :slug"),
            {"slug": tenant_id},
        )
    row = result.first()
    if not row:
        raise HTTPException(404, {"error": f"Tenant '{tenant_id}' not found"})
    return str(row[0]), row[1], row[2] or "starter", row[3]


@router.get("/billing/plans")
async def list_plans():
    """Return available billing plans."""
    return {"plans": PLANS}


@router.get("/tenants/{tenant_id}/billing")
async def get_tenant_billing(tenant_id: str):
    """Return billing info for a tenant."""
    get_sess = _get_session()

    async with get_sess() as session:
        tid, slug, plan, created_at = await _resolve_tenant(session, tenant_id)

        # Next billing date (1st of next month)
        now = datetime.now(timezone.utc)
        if now.month == 12:
            next_billing = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            next_billing = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)

        # Current month usage from agent_executions
        result = await session.execute(
            text(
                "SELECT count(*) FROM agent_executions "
                "WHERE tenant_id = :tid "
                "AND created_at >= date_trunc('month', CURRENT_TIMESTAMP)"
            ),
            {"tid": tid},
        )
        usage_this_month = result.scalar() or 0

        plan_info = next((p for p in PLANS if p["name"] == plan), PLANS[0])

        return {
            "tenant_id": tid,
            "plan": plan,
            "price_cents": plan_info["price"],
            "max_executions": plan_info["executions"],
            "next_billing_date": next_billing.isoformat(),
            "usage_this_month": usage_this_month,
            "member_since": created_at.isoformat() if created_at else None,
        }


@router.patch("/tenants/{tenant_id}/billing")
async def change_plan(tenant_id: str, body: PlanChangeRequest):
    """Change tenant plan (stub — no real payment processing)."""
    if body.plan not in VALID_PLANS:
        raise HTTPException(400, {"error": f"Invalid plan '{body.plan}'", "valid": list(VALID_PLANS)})

    get_sess = _get_session()

    async with get_sess() as session:
        tid, slug, old_plan, _ = await _resolve_tenant(session, tenant_id)

        await session.execute(
            text("UPDATE tenants SET plan = :plan WHERE id = :tid"),
            {"plan": body.plan, "tid": tid},
        )
        await session.commit()

        return {
            "tenant_id": tid,
            "old_plan": old_plan,
            "new_plan": body.plan,
            "message": "Plan updated successfully",
        }
