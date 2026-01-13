from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from datetime import datetime
import random

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

INTEGRATIONS_DB = {
    "hubspot": {"id": "hubspot", "tenant_id": "credicefi", "name": "HubSpot", "type": "CRM", "status": "connected", "last_sync": "hace 5 min", "stats": {"contacts": "12.5K", "companies": "2.4K", "deals": 560}, "color": "#FF7A59"},
    "salesforce": {"id": "salesforce", "tenant_id": "credicefi", "name": "Salesforce", "type": "CRM", "status": "connected", "last_sync": "hace 15 min", "stats": {"leads": "8.4K", "accounts": "1.2K"}, "color": "#00A1E0"},
    "segment": {"id": "segment", "tenant_id": "credicefi", "name": "Segment", "type": "CDP", "status": "connected", "last_sync": "tiempo real", "stats": {"events": "1.2M/mes", "sources": 8}, "color": "#43AF79"},
    "zapier": {"id": "zapier", "tenant_id": "credicefi", "name": "Zapier", "type": "Automation", "status": "connected", "last_sync": "hace 2 min", "stats": {"zaps": 24, "tasks": "12K/mes"}, "color": "#FF4A00"},
    "intercom": {"id": "intercom", "tenant_id": "credicefi", "name": "Intercom", "type": "Support", "status": "disconnected", "last_sync": "hace 3 dias", "stats": {}, "color": "#1F8BED"},
    "google-analytics": {"id": "google-analytics", "tenant_id": "credicefi", "name": "Google Analytics", "type": "Analytics", "status": "connected", "last_sync": "hace 1 hora", "stats": {"sessions": "45K/mes"}, "color": "#F9AB00"},
    "stripe": {"id": "stripe", "tenant_id": "credicefi", "name": "Stripe", "type": "Payments", "status": "connected", "last_sync": "hace 10 min", "stats": {"revenue": "$125K/mes", "mrr": "$42K"}, "color": "#635BFF"},
    "slack": {"id": "slack", "tenant_id": "credicefi", "name": "Slack", "type": "Comms", "status": "connected", "last_sync": "tiempo real", "stats": {"channels": 8}, "color": "#4A154B"},
}

SYNC_LOGS: List[Dict] = []

@router.get("")
async def list_integrations(tenant_id: str = Query("credicefi", description="Tenant ID")):
    integrations = [i for i in INTEGRATIONS_DB.values() if i["tenant_id"] == tenant_id]
    connected = len([i for i in integrations if i["status"] == "connected"])
    return {"integrations": integrations, "summary": {"total": len(integrations), "connected": connected, "success_rate": 99.8}}

@router.get("/{integration_id}")
async def get_integration(integration_id: str, tenant_id: str = Query("credicefi", description="Tenant ID")):
    integration = INTEGRATIONS_DB.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@router.post("/{integration_id}/connect")
async def connect_integration(integration_id: str, tenant_id: str = Query("credicefi", description="Tenant ID")):
    integration = INTEGRATIONS_DB.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    integration["status"] = "connected"
    integration["last_sync"] = "ahora"
    return {"message": f"{integration['name']} connected", "status": "connected"}

@router.post("/{integration_id}/disconnect")
async def disconnect_integration(integration_id: str, tenant_id: str = Query("credicefi", description="Tenant ID")):
    integration = INTEGRATIONS_DB.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    integration["status"] = "disconnected"
    return {"message": f"{integration['name']} disconnected", "status": "disconnected"}

@router.post("/{integration_id}/sync")
async def sync_integration(integration_id: str, tenant_id: str = Query("credicefi", description="Tenant ID")):
    integration = INTEGRATIONS_DB.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if integration["status"] != "connected":
        raise HTTPException(status_code=400, detail="Must be connected to sync")
    integration["last_sync"] = "ahora"
    records = random.randint(100, 5000)
    SYNC_LOGS.insert(0, {"integration": integration["name"], "records": records, "status": "success", "time": datetime.now().isoformat()})
    return {"message": f"Synced {integration['name']}", "records": records}

@router.post("/sync-all")
async def sync_all(tenant_id: str = Query("credicefi", description="Tenant ID")):
    results = []
    for i in INTEGRATIONS_DB.values():
        if i["tenant_id"] == tenant_id and i["status"] == "connected":
            i["last_sync"] = "ahora"
            results.append({"name": i["name"], "records": random.randint(100, 2000)})
    return {"message": f"Synced {len(results)} integrations", "results": results}

@router.get("/logs/recent")
async def get_logs(tenant_id: str = Query("credicefi", description="Tenant ID"), limit: int = 10):
    return {"logs": SYNC_LOGS[:limit], "total": len(SYNC_LOGS)}

@router.get("/available")
async def list_available():
    return {"available": [
        {"id": "microsoft-dynamics", "name": "Microsoft Dynamics", "category": "CRM"},
        {"id": "marketo", "name": "Marketo", "category": "Marketing"},
        {"id": "braze", "name": "Braze", "category": "CDP"},
        {"id": "mixpanel", "name": "Mixpanel", "category": "Analytics"},
        {"id": "amplitude", "name": "Amplitude", "category": "Analytics"},
    ]}
