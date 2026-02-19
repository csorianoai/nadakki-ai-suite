"""
Tenant management router — config, gates, onboarding.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from admin_auth import verify_admin_key

logger = logging.getLogger("nadakki.tenant_router")

router = APIRouter(prefix="/api/v1", tags=["tenants"])


# ── Pydantic models ─────────────────────────────────────────────────────────


class TenantConfigUpdate(BaseModel):
    meta_live_enabled: Optional[bool] = None
    sendgrid_live_enabled: Optional[bool] = None


class OnboardRequest(BaseModel):
    name: str
    slug: str
    plan: str = "starter"
    admin_email: str


class GateAction(BaseModel):
    approved_by: Optional[str] = None
    notes: Optional[str] = None


# ── Helpers ──────────────────────────────────────────────────────────────────


def _get_session():
    from services.db import db_available, get_session
    if not db_available():
        raise HTTPException(503, {"error": "Database unavailable"})
    return get_session


# ── TAREA 1: PATCH tenant config (admin only) ───────────────────────────────


@router.patch("/tenants/{tenant_slug}/config")
async def update_tenant_config(
    tenant_slug: str,
    body: TenantConfigUpdate,
    admin_info: dict = Depends(verify_admin_key),
):
    """Update per-tenant live flags. Admin only."""
    get_sess = _get_session()

    async with get_sess() as session:
        # Resolve slug -> UUID
        result = await session.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"),
            {"slug": tenant_slug},
        )
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Tenant '{tenant_slug}' not found"})
        tenant_id = str(row[0])

        # Build SET clause dynamically
        updates = {}
        if body.meta_live_enabled is not None:
            updates["meta_live_enabled"] = body.meta_live_enabled
        if body.sendgrid_live_enabled is not None:
            updates["sendgrid_live_enabled"] = body.sendgrid_live_enabled

        if not updates:
            raise HTTPException(400, {"error": "No fields to update"})

        set_parts = []
        params = {"tenant_id": tenant_id}
        for key, val in updates.items():
            set_parts.append(f"{key} = :{key}")
            params[key] = val
        set_parts.append("updated_at = now()")

        await session.execute(
            text(
                f"UPDATE tenant_config SET {', '.join(set_parts)} "
                f"WHERE tenant_id = :tenant_id"
            ),
            params,
        )
        await session.commit()

        # Return updated config
        result = await session.execute(
            text(
                "SELECT meta_live_enabled, sendgrid_live_enabled, updated_at "
                "FROM tenant_config WHERE tenant_id = :tenant_id"
            ),
            {"tenant_id": tenant_id},
        )
        row = result.first()
        return {
            "tenant_slug": tenant_slug,
            "tenant_id": tenant_id,
            "meta_live_enabled": row[0] if row else None,
            "sendgrid_live_enabled": row[1] if row else None,
            "updated_at": row[2].isoformat() if row and row[2] else None,
            "updated_by": admin_info.get("name", "unknown"),
        }


# ── TAREA 2: Gate engine ────────────────────────────────────────────────────


@router.get("/gates")
async def list_gates():
    """List all gates with status."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await session.execute(
            text(
                "SELECT gate_id, name, status, approved_by, notes, updated_at "
                "FROM gates ORDER BY gate_id"
            )
        )
        gates = [
            {
                "gate_id": r[0],
                "name": r[1],
                "status": r[2],
                "approved_by": r[3],
                "notes": r[4],
                "updated_at": r[5].isoformat() if r[5] else None,
            }
            for r in result.fetchall()
        ]
        return {"gates": gates, "total": len(gates)}


@router.post("/gates/{gate_id}/approve")
async def approve_gate(
    gate_id: str,
    body: GateAction = GateAction(),
    admin_info: dict = Depends(verify_admin_key),
):
    """Approve a gate. Admin only."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await session.execute(
            text("SELECT status FROM gates WHERE gate_id = :gid"),
            {"gid": gate_id},
        )
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Gate '{gate_id}' not found"})

        approved_by = body.approved_by or admin_info.get("name", "admin")
        await session.execute(
            text(
                "UPDATE gates SET status = 'approved', approved_by = :by, "
                "notes = :notes, updated_at = now() WHERE gate_id = :gid"
            ),
            {"by": approved_by, "notes": body.notes, "gid": gate_id},
        )
        await session.commit()

        return {"gate_id": gate_id, "status": "approved", "approved_by": approved_by}


@router.post("/gates/{gate_id}/reject")
async def reject_gate(
    gate_id: str,
    body: GateAction = GateAction(),
    admin_info: dict = Depends(verify_admin_key),
):
    """Reject a gate. Admin only."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await session.execute(
            text("SELECT status FROM gates WHERE gate_id = :gid"),
            {"gid": gate_id},
        )
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Gate '{gate_id}' not found"})

        rejected_by = body.approved_by or admin_info.get("name", "admin")
        await session.execute(
            text(
                "UPDATE gates SET status = 'rejected', approved_by = :by, "
                "notes = :notes, updated_at = now() WHERE gate_id = :gid"
            ),
            {"by": rejected_by, "notes": body.notes, "gid": gate_id},
        )
        await session.commit()

        return {"gate_id": gate_id, "status": "rejected", "rejected_by": rejected_by}


# ── TAREA 3: Onboarding ─────────────────────────────────────────────────────


@router.post("/tenants/onboard")
async def onboard_tenant(
    body: OnboardRequest,
    admin_info: dict = Depends(verify_admin_key),
):
    """Create a new tenant + admin user + tenant_config. Admin only."""
    get_sess = _get_session()

    async with get_sess() as session:
        # Check slug uniqueness
        result = await session.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"),
            {"slug": body.slug},
        )
        if result.first():
            raise HTTPException(409, {"error": f"Slug '{body.slug}' already exists"})

        # Create tenant
        result = await session.execute(
            text(
                "INSERT INTO tenants (name, slug, plan) "
                "VALUES (:name, :slug, :plan) RETURNING id"
            ),
            {"name": body.name, "slug": body.slug, "plan": body.plan},
        )
        tenant_id = str(result.scalar())

        # Create admin user
        result = await session.execute(
            text(
                "INSERT INTO users (tenant_id, email, role) "
                "VALUES (:tid, :email, 'admin') RETURNING id"
            ),
            {"tid": tenant_id, "email": body.admin_email},
        )
        user_id = str(result.scalar())

        # Create tenant_config (defaults: all live flags false)
        await session.execute(
            text(
                "INSERT INTO tenant_config (tenant_id, meta_live_enabled, sendgrid_live_enabled) "
                "VALUES (:tid, false, false)"
            ),
            {"tid": tenant_id},
        )

        await session.commit()

        return {
            "tenant_id": tenant_id,
            "slug": body.slug,
            "name": body.name,
            "plan": body.plan,
            "admin_user_id": user_id,
            "admin_email": body.admin_email,
            "onboarded_by": admin_info.get("name", "unknown"),
        }
