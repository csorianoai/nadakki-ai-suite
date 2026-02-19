"""
Tenant management router — config, gates, onboarding.
Path param {tenant_id} accepts both slug (e.g. 'credicefi') and UUID.
"""

import logging
import re
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

logger = logging.getLogger("nadakki.tenant_router")

router = APIRouter(prefix="/api/v1", tags=["tenants"])

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)


# ── Pydantic models ─────────────────────────────────────────────────────────


class TenantConfigUpdate(BaseModel):
    meta_live_enabled: Optional[bool] = None
    sendgrid_live_enabled: Optional[bool] = None


class OnboardRequest(BaseModel):
    name: str
    admin_email: str
    plan: str = "starter"


class GateAction(BaseModel):
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    notes: Optional[str] = None


# ── Helpers ──────────────────────────────────────────────────────────────────


def _get_session():
    from services.db import db_available, get_session
    if not db_available():
        raise HTTPException(503, {"error": "Database unavailable"})
    return get_session


async def _resolve_tenant(session, tenant_id: str):
    """Resolve tenant_id (slug or UUID) to (uuid_str, slug, plan). Raises 404."""
    if _UUID_RE.match(tenant_id):
        result = await session.execute(
            text("SELECT id, slug, plan FROM tenants WHERE id = :tid"),
            {"tid": tenant_id},
        )
    else:
        result = await session.execute(
            text("SELECT id, slug, plan FROM tenants WHERE slug = :slug"),
            {"slug": tenant_id},
        )
    row = result.first()
    if not row:
        raise HTTPException(404, {"error": f"Tenant '{tenant_id}' not found"})
    return str(row[0]), row[1], row[2]


def _slugify(name: str) -> str:
    """Generate URL-safe slug from name."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


# ── PATCH tenant config ─────────────────────────────────────────────────────


@router.patch("/tenants/{tenant_id}/config")
async def update_tenant_config(tenant_id: str, body: TenantConfigUpdate):
    """Update per-tenant live flags."""
    get_sess = _get_session()

    async with get_sess() as session:
        tid, slug, _ = await _resolve_tenant(session, tenant_id)

        updates = {}
        if body.meta_live_enabled is not None:
            updates["meta_live_enabled"] = body.meta_live_enabled
        if body.sendgrid_live_enabled is not None:
            updates["sendgrid_live_enabled"] = body.sendgrid_live_enabled

        if not updates:
            raise HTTPException(400, {"error": "No fields to update"})

        set_parts = []
        params = {"tenant_id": tid}
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

        result = await session.execute(
            text(
                "SELECT meta_live_enabled, sendgrid_live_enabled, updated_at "
                "FROM tenant_config WHERE tenant_id = :tenant_id"
            ),
            {"tenant_id": tid},
        )
        row = result.first()
        return {
            "tenant_id": tid,
            "tenant_slug": slug,
            "meta_live_enabled": row[0] if row else None,
            "sendgrid_live_enabled": row[1] if row else None,
            "updated_at": row[2].isoformat() if row and row[2] else None,
        }


# ── Gate engine ──────────────────────────────────────────────────────────────


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
async def approve_gate(gate_id: str, body: GateAction = GateAction()):
    """Approve a gate."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await session.execute(
            text("SELECT status FROM gates WHERE gate_id = :gid"),
            {"gid": gate_id},
        )
        if not result.first():
            raise HTTPException(404, {"error": f"Gate '{gate_id}' not found"})

        approved_by = body.approved_by or "admin"
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
async def reject_gate(gate_id: str, body: GateAction = GateAction()):
    """Reject a gate."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await session.execute(
            text("SELECT status FROM gates WHERE gate_id = :gid"),
            {"gid": gate_id},
        )
        if not result.first():
            raise HTTPException(404, {"error": f"Gate '{gate_id}' not found"})

        rejected_by = body.rejected_by or body.approved_by or "admin"
        await session.execute(
            text(
                "UPDATE gates SET status = 'rejected', approved_by = :by, "
                "notes = :notes, updated_at = now() WHERE gate_id = :gid"
            ),
            {"by": rejected_by, "notes": body.notes, "gid": gate_id},
        )
        await session.commit()

        return {"gate_id": gate_id, "status": "rejected", "rejected_by": rejected_by}


# ── Onboarding ───────────────────────────────────────────────────────────────


@router.post("/tenants/onboard")
async def onboard_tenant(body: OnboardRequest):
    """Create a new tenant + admin user + tenant_config."""
    get_sess = _get_session()
    slug = _slugify(body.name)

    async with get_sess() as session:
        # Check slug uniqueness
        result = await session.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"),
            {"slug": slug},
        )
        if result.first():
            raise HTTPException(409, {"error": f"Slug '{slug}' already exists"})

        # Create tenant
        result = await session.execute(
            text(
                "INSERT INTO tenants (name, slug, plan) "
                "VALUES (:name, :slug, :plan) RETURNING id"
            ),
            {"name": body.name, "slug": slug, "plan": body.plan},
        )
        tenant_id = str(result.scalar())

        # Create admin user
        await session.execute(
            text(
                "INSERT INTO users (tenant_id, email, role) "
                "VALUES (:tid, :email, 'admin')"
            ),
            {"tid": tenant_id, "email": body.admin_email},
        )

        # Create tenant_config
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
            "slug": slug,
            "name": body.name,
            "plan": body.plan,
            "admin_email": body.admin_email,
        }
