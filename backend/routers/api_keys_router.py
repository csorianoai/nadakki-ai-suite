"""
API Key management per tenant.
POST   /api/v1/tenants/{tenant_slug}/api-keys   — generate key
GET    /api/v1/tenants/{tenant_slug}/api-keys   — list keys (prefix only)
DELETE /api/v1/tenants/{tenant_slug}/api-keys/{key_id} — deactivate key
"""

import hashlib
import logging
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from admin_auth import verify_admin_key

logger = logging.getLogger("nadakki.api_keys")

router = APIRouter(prefix="/api/v1", tags=["api-keys"])


class CreateKeyRequest(BaseModel):
    name: str = "default"


def _get_session():
    from services.db import db_available, get_session
    if not db_available():
        raise HTTPException(503, {"error": "Database unavailable"})
    return get_session


def _resolve_tenant(session, tenant_slug: str):
    """Coroutine helper — must be awaited."""
    return session.execute(
        text("SELECT id FROM tenants WHERE slug = :slug"),
        {"slug": tenant_slug},
    )


def _generate_key() -> str:
    """Generate nad_live_<20 hex chars> key."""
    return f"nad_live_{secrets.token_hex(20)}"


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


@router.post("/tenants/{tenant_slug}/api-keys")
async def create_api_key(
    tenant_slug: str,
    body: CreateKeyRequest = CreateKeyRequest(),
    admin_info: dict = Depends(verify_admin_key),
):
    """Generate a new API key for a tenant. Returns the key ONCE."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await _resolve_tenant(session, tenant_slug)
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Tenant '{tenant_slug}' not found"})
        tenant_id = str(row[0])

        raw_key = _generate_key()
        key_hash = _hash_key(raw_key)
        prefix = raw_key[:14]  # "nad_live_XXXXX"

        await session.execute(
            text(
                "INSERT INTO api_keys (tenant_id, key_hash, prefix, name) "
                "VALUES (:tid, :hash, :prefix, :name)"
            ),
            {"tid": tenant_id, "hash": key_hash, "prefix": prefix, "name": body.name},
        )
        await session.commit()

        return {
            "key": raw_key,
            "prefix": prefix,
            "name": body.name,
            "tenant_slug": tenant_slug,
            "warning": "Store this key securely. It will NOT be shown again.",
        }


@router.get("/tenants/{tenant_slug}/api-keys")
async def list_api_keys(
    tenant_slug: str,
    admin_info: dict = Depends(verify_admin_key),
):
    """List API keys for a tenant (prefix only, no full key)."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await _resolve_tenant(session, tenant_slug)
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Tenant '{tenant_slug}' not found"})
        tenant_id = str(row[0])

        result = await session.execute(
            text(
                "SELECT id, prefix, name, active, created_at "
                "FROM api_keys WHERE tenant_id = :tid ORDER BY created_at DESC"
            ),
            {"tid": tenant_id},
        )
        keys = [
            {
                "id": str(r[0]),
                "prefix": r[1],
                "name": r[2],
                "active": r[3],
                "created_at": r[4].isoformat() if r[4] else None,
            }
            for r in result.fetchall()
        ]
        return {"tenant_slug": tenant_slug, "api_keys": keys, "total": len(keys)}


@router.delete("/tenants/{tenant_slug}/api-keys/{key_id}")
async def deactivate_api_key(
    tenant_slug: str,
    key_id: str,
    admin_info: dict = Depends(verify_admin_key),
):
    """Deactivate an API key."""
    get_sess = _get_session()

    async with get_sess() as session:
        result = await _resolve_tenant(session, tenant_slug)
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"Tenant '{tenant_slug}' not found"})
        tenant_id = str(row[0])

        result = await session.execute(
            text(
                "UPDATE api_keys SET active = false "
                "WHERE id = :kid AND tenant_id = :tid RETURNING id"
            ),
            {"kid": key_id, "tid": tenant_id},
        )
        row = result.first()
        if not row:
            raise HTTPException(404, {"error": f"API key '{key_id}' not found"})

        await session.commit()
        return {"id": key_id, "active": False, "message": "Key deactivated"}
