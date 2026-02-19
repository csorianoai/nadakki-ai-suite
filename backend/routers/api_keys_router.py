"""
API Key management per tenant.
POST   /api/v1/tenants/{tenant_id}/api-keys   — generate key
GET    /api/v1/tenants/{tenant_id}/api-keys   — list keys (prefix only)
DELETE /api/v1/tenants/{tenant_id}/api-keys/{key_id} — deactivate key

{tenant_id} accepts both slug and UUID.
"""

import hashlib
import logging
import re
import secrets
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

logger = logging.getLogger("nadakki.api_keys")

router = APIRouter(prefix="/api/v1", tags=["api-keys"])

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)


class CreateKeyRequest(BaseModel):
    name: str = "default"


async def _resolve_tenant_id(session, tenant_id: str) -> str:
    """Resolve slug or UUID to tenant UUID string. Raises 404."""
    if _UUID_RE.match(tenant_id):
        result = await session.execute(
            text("SELECT id FROM tenants WHERE id = :tid"), {"tid": tenant_id}
        )
    else:
        result = await session.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"), {"slug": tenant_id}
        )
    row = result.first()
    if not row:
        raise HTTPException(404, {"error": f"Tenant '{tenant_id}' not found"})
    return str(row[0])


def _get_session():
    from services.db import db_available, get_session
    if not db_available():
        raise HTTPException(503, {"error": "Database unavailable"})
    return get_session


def _generate_key() -> str:
    return f"nad_live_{secrets.token_hex(20)}"


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


@router.post("/tenants/{tenant_id}/api-keys")
async def create_api_key(tenant_id: str, body: CreateKeyRequest = CreateKeyRequest()):
    """Generate a new API key for a tenant. Returns the key ONCE."""
    get_sess = _get_session()

    async with get_sess() as session:
        tid = await _resolve_tenant_id(session, tenant_id)

        raw_key = _generate_key()
        key_hash = _hash_key(raw_key)
        prefix = raw_key[:14]

        await session.execute(
            text(
                "INSERT INTO api_keys (tenant_id, key_hash, prefix, name) "
                "VALUES (:tid, :hash, :prefix, :name)"
            ),
            {"tid": tid, "hash": key_hash, "prefix": prefix, "name": body.name},
        )
        await session.commit()

        return {
            "key": raw_key,
            "prefix": prefix,
            "name": body.name,
            "tenant_id": tid,
            "warning": "Store this key securely. It will NOT be shown again.",
        }


@router.get("/tenants/{tenant_id}/api-keys")
async def list_api_keys(tenant_id: str):
    """List API keys for a tenant (prefix only, no full key)."""
    get_sess = _get_session()

    async with get_sess() as session:
        tid = await _resolve_tenant_id(session, tenant_id)

        result = await session.execute(
            text(
                "SELECT id, prefix, name, active, created_at "
                "FROM api_keys WHERE tenant_id = :tid ORDER BY created_at DESC"
            ),
            {"tid": tid},
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
        return {"tenant_id": tid, "api_keys": keys, "total": len(keys)}


@router.delete("/tenants/{tenant_id}/api-keys/{key_id}")
async def deactivate_api_key(tenant_id: str, key_id: str):
    """Deactivate an API key."""
    get_sess = _get_session()

    async with get_sess() as session:
        tid = await _resolve_tenant_id(session, tenant_id)

        result = await session.execute(
            text(
                "UPDATE api_keys SET active = false "
                "WHERE id = :kid AND tenant_id = :tid RETURNING id"
            ),
            {"kid": key_id, "tid": tid},
        )
        if not result.first():
            raise HTTPException(404, {"error": f"API key '{key_id}' not found"})

        await session.commit()
        return {"id": key_id, "active": False, "message": "Key deactivated"}
