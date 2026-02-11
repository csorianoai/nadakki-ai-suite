from fastapi import APIRouter, Header
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api", tags=["marketing"])

MOCK_CAMPAIGNS = {"credicefi": {"total": 12, "active": 10, "draft": 2, "completed": 45}}
MOCK_JOURNEYS = {"credicefi": {"total": 8, "active": 5, "paused": 2, "draft": 1}}
MOCK_CONTACTS = {"credicefi": {"total": 125000, "active": 95000, "unsubscribed": 20000, "bounced": 10000}}
MOCK_CONVERSIONS = {"credicefi": {"conversion_rate": 3.2, "email_rate": 2.8, "sms_rate": 4.5, "aov": 1250.50, "ltv": 4500.00, "roi": 450.0}}

@router.get("/campaigns/stats/summary")
async def get_campaigns_summary(tenant_id: Optional[str] = None):
    tenant = tenant_id or "credicefi"
    data = MOCK_CAMPAIGNS.get(tenant, MOCK_CAMPAIGNS["credicefi"])
    return {"success": True, "tenant_id": tenant, "data": {"summary": {"total_campaigns": data["total"], "active_campaigns": data["active"], "draft_campaigns": data["draft"], "completed_campaigns": data["completed"]}, "timestamp": datetime.utcnow().isoformat()}}

@router.get("/journeys/stats/summary")
async def get_journeys_summary(tenant_id: Optional[str] = None):
    tenant = tenant_id or "credicefi"
    data = MOCK_JOURNEYS.get(tenant, MOCK_JOURNEYS["credicefi"])
    return {"success": True, "tenant_id": tenant, "data": {"summary": {"total_journeys": data["total"], "active_journeys": data["active"], "paused_journeys": data["paused"], "draft_journeys": data["draft"]}, "timestamp": datetime.utcnow().isoformat()}}

@router.get("/contacts/stats/summary")
async def get_contacts_summary(tenant_id: Optional[str] = None):
    tenant = tenant_id or "credicefi"
    data = MOCK_CONTACTS.get(tenant, MOCK_CONTACTS["credicefi"])
    return {"success": True, "tenant_id": tenant, "data": {"summary": {"total_contacts": data["total"], "active_contacts": data["active"], "unsubscribed": data["unsubscribed"], "bounced": data["bounced"]}, "timestamp": datetime.utcnow().isoformat()}}

@router.get("/conversions/stats/summary")
async def get_conversions_summary(tenant_id: Optional[str] = None):
    tenant = tenant_id or "credicefi"
    data = MOCK_CONVERSIONS.get(tenant, MOCK_CONVERSIONS["credicefi"])
    return {"success": True, "tenant_id": tenant, "data": {"summary": {"conversion_rate": data["conversion_rate"], "email_conversion": data["email_rate"], "sms_conversion": data["sms_rate"], "average_order_value": data["aov"], "lifetime_value": data["ltv"], "roi_percentage": data["roi"]}, "timestamp": datetime.utcnow().isoformat()}}

@router.get("/marketing/dashboard")
async def get_marketing_dashboard(tenant_id: Optional[str] = None):
    tenant = tenant_id or "credicefi"
    campaigns_data = MOCK_CAMPAIGNS.get(tenant, MOCK_CAMPAIGNS["credicefi"])
    journeys_data = MOCK_JOURNEYS.get(tenant, MOCK_JOURNEYS["credicefi"])
    contacts_data = MOCK_CONTACTS.get(tenant, MOCK_CONTACTS["credicefi"])
    conversions_data = MOCK_CONVERSIONS.get(tenant, MOCK_CONVERSIONS["credicefi"])
    return {"success": True, "tenant_id": tenant, "data": {"campaigns": {"total": campaigns_data["total"], "active": campaigns_data["active"]}, "journeys": {"total": journeys_data["active"], "active": journeys_data["active"]}, "contacts": {"total": contacts_data["total"], "active": contacts_data["active"]}, "conversions": {"rate": conversions_data["conversion_rate"], "aov": conversions_data["aov"], "ltv": conversions_data["ltv"], "roi": conversions_data["roi"]}, "timestamp": datetime.utcnow().isoformat()}}
