"""
ADVERTISING MANAGER ROUTER - Multi-tenant endpoints
"""
from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from config_advertising_platforms import PLATFORM_CONFIGS, DOMINICAN_BANKS

router = APIRouter(prefix="/api/v1/advertising", tags=["advertising"])

class PlatformMetrics(BaseModel):
    platform: str
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    revenue: float = 0.0
    roas: float = 0.0
    cpc: float = 0.0

@router.get("/platforms")
async def get_all_platforms(x_tenant_id: str = Header(None)):
    """Get all available advertising platforms"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header required")
    return {
        "tenant_id": x_tenant_id,
        "platforms": PLATFORM_CONFIGS,
        "total_platforms": len(PLATFORM_CONFIGS),
    }

@router.get("/dashboard")
async def get_advertising_dashboard(x_tenant_id: str = Header(None), platform: Optional[str] = Query(None)):
    """Get advertising dashboard"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header required")
    
    platforms_data = []
    for plat_name in PLATFORM_CONFIGS.keys():
        platforms_data.append(PlatformMetrics(platform=plat_name, impressions=50000, clicks=5000, conversions=500))
    
    return {
        "tenant_id": x_tenant_id,
        "platforms": platforms_data,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/tenants")
async def get_dominican_banks():
    """Get list of Dominican banks"""
    return {"tenants": DOMINICAN_BANKS, "total": len(DOMINICAN_BANKS)}

@router.get("/health")
async def health_check(x_tenant_id: str = Header(None)):
    """Health check"""
    return {"status": "ok", "module": "advertising", "tenant_id": x_tenant_id}
