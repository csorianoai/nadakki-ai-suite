"""
NADAKKI AI SUITE - MULTI-TENANT INTEGRATION MODULE v2.0.0
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends
from admin_auth import verify_admin_key
from uuid import uuid4
import hashlib
import json
import logging

logger = logging.getLogger("NadakkiMultiTenant")

PRICING_TIERS = {
    "starter": {
        "name": "Starter", "price_monthly": 999, "decisions_per_month": 100,
        "workflows_allowed": ["campaign-optimization", "customer-acquisition-intelligence", "customer-lifecycle-revenue"],
        "max_requests_per_hour": 100, "features": {"audit_trail": True, "api_access": False}
    },
    "professional": {
        "name": "Professional", "price_monthly": 2499, "decisions_per_month": 500,
        "workflows_allowed": ["campaign-optimization", "customer-acquisition-intelligence", "customer-lifecycle-revenue",
            "content-performance-engine", "social-media-intelligence", "email-automation-master"],
        "max_requests_per_hour": 1000, "features": {"audit_trail": True, "api_access": True, "hash_chain": True}
    },
    "enterprise": {
        "name": "Enterprise", "price_monthly": 7999, "decisions_per_month": -1,
        "workflows_allowed": ["ALL"], "max_requests_per_hour": 10000,
        "features": {"audit_trail": True, "api_access": True, "hash_chain": True, "sso": True}
    }
}

TENANTS_DB: Dict[str, Dict] = {
    "credicefi": {
        "tenant_id": "credicefi", "name": "Credicefi", "email": "admin@credicefi.com",
        "plan": "enterprise", "status": "active",
        "api_key": "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I",
        "region": "latam", "created_at": "2024-01-01T00:00:00Z",
        "billing": {"decisions_this_month": 0, "month_started": datetime.utcnow().replace(day=1).isoformat() + "Z"}
    },
    "demo": {
        "tenant_id": "demo", "name": "Demo Account", "email": "demo@nadakki.com",
        "plan": "starter", "status": "active", "api_key": "demo_key_12345",
        "region": "latam", "created_at": "2025-01-01T00:00:00Z",
        "billing": {"decisions_this_month": 0, "month_started": datetime.utcnow().replace(day=1).isoformat() + "Z"}
    },
    "banco_demo": {
        "tenant_id": "banco_demo", "name": "Banco Demo", "email": "demo@banco.com",
        "plan": "professional", "status": "active", "api_key": "banco_demo_key_2025_secure",
        "region": "latam", "created_at": "2025-12-01T00:00:00Z",
        "billing": {"decisions_this_month": 0, "month_started": datetime.utcnow().replace(day=1).isoformat() + "Z"}
    }
}

DECISIONS_LOG: List[Dict] = []
AUDIT_LOG: List[Dict] = []

class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: str
    plan: str = "starter"
    region: str = "latam"

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None

def generate_tenant_id() -> str:
    return f"tn_{int(datetime.utcnow().timestamp())}_{uuid4().hex[:8]}"

def generate_api_key() -> str:
    return f"pk_live_{uuid4().hex}{uuid4().hex[:8]}"

def get_execution_boundary(tenant_id: str) -> str:
    return f"tenant::{tenant_id}"

def create_audit_entry(tenant_id: str, action: str, resource_type: str, resource_id: str = None, details: Dict = None):
    entry = {
        "audit_id": f"aud_{uuid4().hex[:12]}", "tenant_id": tenant_id,
        "execution_boundary": get_execution_boundary(tenant_id),
        "action": action, "resource_type": resource_type, "resource_id": resource_id,
        "details": details or {}, "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    AUDIT_LOG.append(entry)
    return entry

class TenantContext:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.tenant_data = TENANTS_DB.get(tenant_id)
        self.plan = PRICING_TIERS.get(self.tenant_data["plan"]) if self.tenant_data else None
        self.is_valid = self.tenant_data is not None and self.tenant_data.get("status") == "active"
        self.execution_boundary = get_execution_boundary(tenant_id)
    
    def can_execute_workflow(self, workflow_id: str) -> bool:
        if not self.is_valid or not self.plan: return False
        allowed = self.plan["workflows_allowed"]
        return "ALL" in allowed or workflow_id in allowed

tenant_router = APIRouter(prefix="/tenants", tags=["tenants"])

@tenant_router.get("")
async def list_tenants():
    return {"total": len(TENANTS_DB), "tenants": [
        {"tenant_id": t["tenant_id"], "name": t["name"], "plan": t["plan"], "status": t["status"],
         "decisions_this_month": t["billing"]["decisions_this_month"]}
        for t in TENANTS_DB.values()
    ]}

@tenant_router.get("/{tenant_id}")
async def get_tenant(tenant_id: str):
    if tenant_id not in TENANTS_DB: raise HTTPException(404, "Tenant not found")
    t = TENANTS_DB[tenant_id]
    plan = PRICING_TIERS.get(t["plan"], {})
    return {"tenant_id": t["tenant_id"], "name": t["name"], "email": t.get("email"),
            "plan": {"id": t["plan"], "name": plan.get("name"), "price": plan.get("price_monthly")},
            "billing": {"decisions_used": t["billing"]["decisions_this_month"], "limit": plan.get("decisions_per_month")},
            "status": t["status"]}

@tenant_router.post("")
async def create_tenant(tenant: TenantCreate, admin = Depends(verify_admin_key)):
    if tenant.plan not in PRICING_TIERS: raise HTTPException(400, f"Invalid plan: {tenant.plan}")
    tenant_id = generate_tenant_id()
    api_key = generate_api_key()
    now = datetime.utcnow().isoformat() + "Z"
    TENANTS_DB[tenant_id] = {
        "tenant_id": tenant_id, "name": tenant.name, "email": tenant.email,
        "plan": tenant.plan, "status": "provisioned", "api_key": api_key,
        "region": tenant.region, "created_at": now,
        "billing": {"decisions_this_month": 0, "month_started": datetime.utcnow().replace(day=1).isoformat() + "Z"}
    }
    create_audit_entry(tenant_id, "tenant_created", "tenant", tenant_id, {"name": tenant.name})
    logger.info(f"Tenant created: {tenant_id}")
    return {"success": True, "tenant_id": tenant_id, "api_key": api_key, "message": "Tenant created"}

@tenant_router.patch("/{tenant_id}")
async def update_tenant(tenant_id: str, update: TenantUpdate, admin = Depends(verify_admin_key)):
    if tenant_id not in TENANTS_DB: raise HTTPException(404, "Tenant not found")
    t = TENANTS_DB[tenant_id]
    if update.name: t["name"] = update.name
    if update.email: t["email"] = update.email
    if update.plan and update.plan in PRICING_TIERS: t["plan"] = update.plan
    if update.status: t["status"] = update.status
    return {"success": True, "tenant_id": tenant_id}

@tenant_router.post("/{tenant_id}/activate")
async def activate_tenant(tenant_id: str, admin = Depends(verify_admin_key)):
    if tenant_id not in TENANTS_DB: raise HTTPException(404, "Tenant not found")
    TENANTS_DB[tenant_id]["status"] = "active"
    return {"success": True, "status": "active"}

@tenant_router.post("/{tenant_id}/suspend")
async def suspend_tenant(tenant_id: str, admin = Depends(verify_admin_key)):
    if tenant_id not in TENANTS_DB: raise HTTPException(404, "Tenant not found")
    TENANTS_DB[tenant_id]["status"] = "suspended"
    return {"success": True, "status": "suspended"}

decisions_router = APIRouter(prefix="/decisions", tags=["decisions"])

@decisions_router.get("/{tenant_id}")
async def get_decisions(tenant_id: str, limit: int = 20):
    decisions = [d for d in DECISIONS_LOG if d.get("tenant", {}).get("tenant_id") == tenant_id]
    return {"tenant_id": tenant_id, "total": len(decisions), "decisions": decisions[:limit]}

@decisions_router.get("/{tenant_id}/stats")
async def get_decision_stats(tenant_id: str):
    decisions = [d for d in DECISIONS_LOG if d.get("tenant", {}).get("tenant_id") == tenant_id]
    if not decisions: return {"tenant_id": tenant_id, "total": 0, "stats": {}}
    confidences = [d.get("decision", {}).get("confidence", 0) for d in decisions]
    pipelines = [d.get("business_impact", {}).get("pipeline_value", 0) for d in decisions]
    return {"tenant_id": tenant_id, "total": len(decisions),
            "stats": {"avg_confidence": sum(confidences)/len(confidences) if confidences else 0, "total_pipeline": sum(pipelines)}}

audit_router = APIRouter(prefix="/audit", tags=["audit"])

@audit_router.get("/{tenant_id}")
async def get_audit(tenant_id: str, limit: int = 50):
    entries = [a for a in AUDIT_LOG if a.get("tenant_id") == tenant_id]
    return {"tenant_id": tenant_id, "execution_boundary": get_execution_boundary(tenant_id),
            "total": len(entries), "entries": entries[:limit]}

pricing_router = APIRouter(prefix="/pricing", tags=["pricing"])

@pricing_router.get("")
async def get_pricing():
    return {"plans": [{"id": k, "name": v["name"], "price": v["price_monthly"],
                       "decisions": v["decisions_per_month"], "features": v["features"]}
                      for k, v in PRICING_TIERS.items()]}

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@dashboard_router.get("/{tenant_id}/metrics")
async def get_metrics(tenant_id: str):
    if tenant_id not in TENANTS_DB: raise HTTPException(404, "Tenant not found")
    t = TENANTS_DB[tenant_id]
    plan = PRICING_TIERS.get(t["plan"], {})
    decisions = [d for d in DECISIONS_LOG if d.get("tenant", {}).get("tenant_id") == tenant_id]
    return {
        "tenant_id": tenant_id, "tenant_name": t["name"], "plan": plan.get("name"),
        "execution_boundary": get_execution_boundary(tenant_id),
        "usage": {"used": t["billing"]["decisions_this_month"], "limit": plan.get("decisions_per_month", 0)},
        "metrics": {"total_decisions": len(decisions), "decisions_today": 0}
    }

def register_tenant_routes(app):
    app.include_router(tenant_router)
    app.include_router(decisions_router)
    app.include_router(audit_router)
    app.include_router(pricing_router)
    app.include_router(dashboard_router)
    logger.info("Multi-tenant routes registered: /tenants, /decisions, /audit, /pricing, /dashboard")

__all__ = ["PRICING_TIERS", "TENANTS_DB", "TenantContext", "register_tenant_routes"]
