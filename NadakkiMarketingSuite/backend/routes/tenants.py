"""Tenant Management API Routes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from core.tenant_manager import tenant_manager

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


@router.post("", status_code=201)
async def create_tenant(name: str, industry: str = "finance") -> Dict[str, Any]:
    tenant = tenant_manager.create_tenant(name=name, industry=industry)
    return tenant.to_dict()


@router.get("")
async def list_tenants() -> Dict[str, Any]:
    tenants = tenant_manager.list_tenants()
    return {"tenants": [t.to_dict() for t in tenants], "total": len(tenants)}


@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str) -> Dict[str, Any]:
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant.to_dict()


@router.delete("/{tenant_id}")
async def delete_tenant(tenant_id: str) -> Dict[str, Any]:
    if tenant_manager.delete_tenant(tenant_id):
        return {"message": "Tenant deleted"}
    raise HTTPException(status_code=404, detail="Tenant not found")
