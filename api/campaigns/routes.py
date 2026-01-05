from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

# ═══════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════

class CampaignVariant(BaseModel):
    id: str
    name: str
    content: str = ""

class Campaign(BaseModel):
    id: Optional[str] = None
    tenant_id: str = "credicefi"
    name: str
    description: str = ""
    type: str = "email"  # email, sms, push, in-app, banner, multichannel, whatsapp
    status: str = "draft"  # draft, active, paused, completed
    schedule_type: str = "immediate"  # immediate, scheduled, action-based, recurring
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    target_segments: List[str] = []
    conversion_events: List[str] = []
    conversion_window: int = 7
    variants: List[CampaignVariant] = []
    tags: List[str] = []
    sent: int = 0
    opened: int = 0
    clicked: int = 0
    converted: int = 0
    revenue: float = 0.0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    type: str = "email"
    schedule_type: str = "immediate"
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    target_segments: List[str] = []
    conversion_events: List[str] = []
    conversion_window: int = 7
    variants: List[dict] = []
    tags: List[str] = []

# ═══════════════════════════════════════════════════════════════
# IN-MEMORY DATABASE
# ═══════════════════════════════════════════════════════════════

campaigns_db: dict[str, List[Campaign]] = {
    "credicefi": [
        Campaign(
            id="camp-1", tenant_id="credicefi", name="Welcome Series",
            description="Onboarding email sequence for new users",
            type="email", status="active", schedule_type="action-based",
            target_segments=["new-users"], tags=["onboarding", "email"],
            sent=45000, opened=18900, clicked=5670, converted=1350, revenue=12500,
            created_at="2024-01-01T00:00:00Z", updated_at="2024-01-15T00:00:00Z"
        ),
        Campaign(
            id="camp-2", tenant_id="credicefi", name="Black Friday Promo",
            description="Annual Black Friday promotion campaign",
            type="multichannel", status="completed", schedule_type="scheduled",
            scheduled_date="2024-11-29", target_segments=["all-users", "vip"],
            tags=["promo", "sale"], sent=125000, opened=47500, clicked=18750,
            converted=6000, revenue=85000,
            created_at="2024-11-01T00:00:00Z", updated_at="2024-11-30T00:00:00Z"
        ),
        Campaign(
            id="camp-3", tenant_id="credicefi", name="Cart Abandonment",
            description="Automated emails for abandoned carts",
            type="email", status="active", schedule_type="action-based",
            target_segments=["cart-abandoners"], tags=["retention", "automated"],
            sent=23000, opened=11960, clicked=5129, converted=1955, revenue=32000,
            created_at="2024-02-01T00:00:00Z", updated_at="2024-02-15T00:00:00Z"
        ),
        Campaign(
            id="camp-4", tenant_id="credicefi", name="Weekly Newsletter",
            description="Weekly content digest",
            type="email", status="active", schedule_type="recurring",
            target_segments=["subscribers"], tags=["newsletter", "content"],
            sent=89000, opened=25460, clicked=7298, converted=1335, revenue=4200,
            created_at="2024-01-01T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Campaign(
            id="camp-5", tenant_id="credicefi", name="Push Notification Test",
            description="Testing push notification engagement",
            type="push", status="draft", schedule_type="immediate",
            target_segments=["mobile-users"], tags=["test", "push"],
            sent=0, opened=0, clicked=0, converted=0, revenue=0,
            created_at="2024-02-10T00:00:00Z", updated_at="2024-02-10T00:00:00Z"
        ),
    ]
}

# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

@router.get("")
async def get_campaigns(
    tenant_id: str = Query("credicefi"),
    status: Optional[str] = None,
    type: Optional[str] = None
):
    """Get all campaigns for a tenant"""
    campaigns = campaigns_db.get(tenant_id, [])
    
    if status:
        campaigns = [c for c in campaigns if c.status == status]
    if type:
        campaigns = [c for c in campaigns if c.type == type]
    
    return {
        "campaigns": [c.dict() for c in campaigns],
        "total": len(campaigns)
    }

@router.get("/stats/summary")
async def get_campaigns_stats(tenant_id: str = Query("credicefi")):
    """Get campaign statistics summary"""
    campaigns = campaigns_db.get(tenant_id, [])
    
    total_sent = sum(c.sent for c in campaigns)
    total_opened = sum(c.opened for c in campaigns)
    total_clicked = sum(c.clicked for c in campaigns)
    total_converted = sum(c.converted for c in campaigns)
    total_revenue = sum(c.revenue for c in campaigns)
    
    return {
        "summary": {
            "total_campaigns": len(campaigns),
            "active_campaigns": len([c for c in campaigns if c.status == "active"]),
            "total_sent": total_sent,
            "total_opened": total_opened,
            "total_clicked": total_clicked,
            "total_converted": total_converted,
            "total_revenue": total_revenue,
            "open_rate": round((total_opened / total_sent * 100) if total_sent > 0 else 0, 1),
            "click_rate": round((total_clicked / total_sent * 100) if total_sent > 0 else 0, 1),
            "conversion_rate": round((total_converted / total_sent * 100) if total_sent > 0 else 0, 2),
        }
    }

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, tenant_id: str = Query("credicefi")):
    """Get a single campaign by ID"""
    campaigns = campaigns_db.get(tenant_id, [])
    campaign = next((c for c in campaigns if c.id == campaign_id), None)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign.dict()

@router.post("")
async def create_campaign(campaign: CampaignCreate, tenant_id: str = Query("credicefi")):
    """Create a new campaign"""
    if tenant_id not in campaigns_db:
        campaigns_db[tenant_id] = []
    
    new_campaign = Campaign(
        id=f"camp-{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        name=campaign.name,
        description=campaign.description,
        type=campaign.type,
        status="draft",
        schedule_type=campaign.schedule_type,
        scheduled_date=campaign.scheduled_date,
        scheduled_time=campaign.scheduled_time,
        target_segments=campaign.target_segments,
        conversion_events=campaign.conversion_events,
        conversion_window=campaign.conversion_window,
        variants=[CampaignVariant(**v) for v in campaign.variants] if campaign.variants else [],
        tags=campaign.tags,
        created_at=datetime.utcnow().isoformat() + "Z",
        updated_at=datetime.utcnow().isoformat() + "Z"
    )
    
    campaigns_db[tenant_id].append(new_campaign)
    
    return {"message": "Campaign created", "campaign": new_campaign.dict()}

@router.put("/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    updates: dict,
    tenant_id: str = Query("credicefi")
):
    """Update a campaign"""
    campaigns = campaigns_db.get(tenant_id, [])
    campaign_idx = next((i for i, c in enumerate(campaigns) if c.id == campaign_id), None)
    
    if campaign_idx is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns[campaign_idx]
    campaign_dict = campaign.dict()
    
    for key, value in updates.items():
        if key in campaign_dict and key not in ["id", "tenant_id", "created_at"]:
            campaign_dict[key] = value
    
    campaign_dict["updated_at"] = datetime.utcnow().isoformat() + "Z"
    campaigns[campaign_idx] = Campaign(**campaign_dict)
    
    return {"message": "Campaign updated", "campaign": campaigns[campaign_idx].dict()}

@router.post("/{campaign_id}/activate")
async def activate_campaign(campaign_id: str, tenant_id: str = Query("credicefi")):
    """Activate a campaign"""
    campaigns = campaigns_db.get(tenant_id, [])
    campaign_idx = next((i for i, c in enumerate(campaigns) if c.id == campaign_id), None)
    
    if campaign_idx is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaigns[campaign_idx].status = "active"
    campaigns[campaign_idx].updated_at = datetime.utcnow().isoformat() + "Z"
    
    return {"message": "Campaign activated", "campaign": campaigns[campaign_idx].dict()}

@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str, tenant_id: str = Query("credicefi")):
    """Pause a campaign"""
    campaigns = campaigns_db.get(tenant_id, [])
    campaign_idx = next((i for i, c in enumerate(campaigns) if c.id == campaign_id), None)
    
    if campaign_idx is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaigns[campaign_idx].status = "paused"
    campaigns[campaign_idx].updated_at = datetime.utcnow().isoformat() + "Z"
    
    return {"message": "Campaign paused", "campaign": campaigns[campaign_idx].dict()}

@router.post("/{campaign_id}/duplicate")
async def duplicate_campaign(campaign_id: str, tenant_id: str = Query("credicefi")):
    """Duplicate a campaign"""
    campaigns = campaigns_db.get(tenant_id, [])
    campaign = next((c for c in campaigns if c.id == campaign_id), None)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    new_campaign = Campaign(
        id=f"camp-{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        name=f"{campaign.name} (Copy)",
        description=campaign.description,
        type=campaign.type,
        status="draft",
        schedule_type=campaign.schedule_type,
        target_segments=campaign.target_segments,
        conversion_events=campaign.conversion_events,
        conversion_window=campaign.conversion_window,
        variants=campaign.variants,
        tags=campaign.tags,
        created_at=datetime.utcnow().isoformat() + "Z",
        updated_at=datetime.utcnow().isoformat() + "Z"
    )
    
    campaigns_db[tenant_id].append(new_campaign)
    
    return {"message": "Campaign duplicated", "campaign": new_campaign.dict()}

@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str, tenant_id: str = Query("credicefi")):
    """Delete a campaign"""
    campaigns = campaigns_db.get(tenant_id, [])
    campaign_idx = next((i for i, c in enumerate(campaigns) if c.id == campaign_id), None)
    
    if campaign_idx is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    deleted = campaigns.pop(campaign_idx)
    
    return {"message": "Campaign deleted", "campaign_id": deleted.id}
