"""
Billing stub router — plans, tenant billing, plan change (no real Stripe).
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from admin_auth import verify_admin_key

logger = logging.getLogger("nadakki.billing")

router = APIRouter(prefix="/api/v1", tags=["billing"])

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


@router.get("/billing/plans")
async def list_plans():
    """Return available billing plans."""
    return {"plans": PLANS}


@router.get("/tenants/{tenant_slug}/billing")
async def get_tenant_billing(
    tenant_slug: str,
    admin_info: dict = Depends(verify_admin_key),
):
    """Return billing info for a tenant."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await session.execute(
            text("SELECT id, plan, created_at FROM tenants WHERE slug = :slug"),
            {"slug": tenant_slug},
        )
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Tenant '{tenant_slug}' not found"})

        tenant_id = str(row[0])
        plan = row[1] or "starter"
        created_at = row[2]

        # Calculate next billing date (1st of next month)
        now = datetime.now(timezone.utc)
        if now.month == 12:
            next_billing = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            next_billing = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)

        # Current month usage
        result = await session.execute(
            text(
                "SELECT COALESCE(SUM(executions_count), 0) "
                "FROM usage_tracking "
                "WHERE tenant_id = :tid AND date >= date_trunc('month', CURRENT_DATE)"
            ),
            {"tid": tenant_id},
        )
        usage_row = result.first()
        usage_this_month = int(usage_row[0]) if usage_row else 0

        plan_info = next((p for p in PLANS if p["name"] == plan), PLANS[0])

        return {
            "tenant_slug": tenant_slug,
            "plan": plan,
            "price_cents": plan_info["price"],
            "max_executions": plan_info["executions"],
            "next_billing_date": next_billing.isoformat(),
            "usage_this_month": usage_this_month,
            "member_since": created_at.isoformat() if created_at else None,
        }


@router.patch("/tenants/{tenant_slug}/billing")
async def change_plan(
    tenant_slug: str,
    body: PlanChangeRequest,
    admin_info: dict = Depends(verify_admin_key),
):
    """Change tenant plan (stub — no real payment processing)."""
    if body.plan not in VALID_PLANS:
        raise HTTPException(400, {"error": f"Invalid plan '{body.plan}'", "valid": list(VALID_PLANS)})

    get_sess = _get_session()

    async with get_sess() as session:
        result = await session.execute(
            text("SELECT id, plan FROM tenants WHERE slug = :slug"),
            {"slug": tenant_slug},
        )
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Tenant '{tenant_slug}' not found"})

        old_plan = row[1]

        await session.execute(
            text("UPDATE tenants SET plan = :plan WHERE slug = :slug"),
            {"plan": body.plan, "slug": tenant_slug},
        )
        await session.commit()

        return {
            "tenant_slug": tenant_slug,
            "old_plan": old_plan,
            "new_plan": body.plan,
            "message": "Plan updated (stub — no payment processed)",
            "changed_by": admin_info.get("name", "unknown"),
        }
