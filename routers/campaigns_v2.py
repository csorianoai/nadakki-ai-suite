"""
Campaign Persistence Router - Full CRUD with drafts and versioning
NADAKKI AI Suite v2.0
"""
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import json

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

# ═══════════════════════════════════════════════════════════════
# ENUMS Y MODELOS
# ═══════════════════════════════════════════════════════════════

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CampaignType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in-app"
    WHATSAPP = "whatsapp"
    MULTI_CHANNEL = "multi-channel"

class CampaignCreate(BaseModel):
    name: str
    type: CampaignType
    description: Optional[str] = ""
    subject: Optional[str] = ""
    content: Dict[str, Any] = {}
    audience_id: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    settings: Dict[str, Any] = {}
    tenant_id: str = "default"

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    audience_id: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    status: Optional[CampaignStatus] = None

class CampaignDraft(BaseModel):
    campaign_id: str
    version: int
    content: Dict[str, Any]
    auto_save: bool = True
    tenant_id: str = "default"

class Campaign(BaseModel):
    id: str
    name: str
    type: CampaignType
    status: CampaignStatus
    description: str
    subject: Optional[str]
    content: Dict[str, Any]
    audience_id: Optional[str]
    audience_size: int
    schedule: Optional[Dict[str, Any]]
    settings: Dict[str, Any]
    version: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    metrics: Dict[str, Any]

# ═══════════════════════════════════════════════════════════════
# BASE DE DATOS EN MEMORIA
# ═══════════════════════════════════════════════════════════════

class CampaignDB:
    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.drafts: Dict[str, List[CampaignDraft]] = {}
        self._seed_data()
    
    def _seed_data(self):
        """Seed with sample campaigns"""
        samples = [
            {
                "name": "Welcome Series - Day 1",
                "type": CampaignType.EMAIL,
                "status": CampaignStatus.ACTIVE,
                "description": "First email in welcome sequence",
                "subject": "Welcome to {{company_name}}! 🎉",
                "audience_size": 12450,
                "metrics": {"sent": 12450, "delivered": 12300, "opened": 5535, "clicked": 1230, "converted": 245}
            },
            {
                "name": "Cart Abandonment Reminder",
                "type": CampaignType.MULTI_CHANNEL,
                "status": CampaignStatus.ACTIVE,
                "description": "Multi-channel cart recovery",
                "subject": "You left something behind! 🛒",
                "audience_size": 3420,
                "metrics": {"sent": 3420, "delivered": 3380, "opened": 1860, "clicked": 680, "converted": 170}
            },
            {
                "name": "Monthly Newsletter",
                "type": CampaignType.EMAIL,
                "status": CampaignStatus.SCHEDULED,
                "description": "January 2026 newsletter",
                "subject": "Your January Update 📰",
                "audience_size": 45200,
                "metrics": {"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0}
            },
            {
                "name": "Flash Sale Alert",
                "type": CampaignType.PUSH,
                "status": CampaignStatus.DRAFT,
                "description": "24-hour flash sale notification",
                "subject": "⚡ 50% OFF - 24 Hours Only!",
                "audience_size": 28900,
                "metrics": {"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0}
            },
        ]
        
        for i, sample in enumerate(samples):
            campaign_id = f"cmp_{uuid.uuid4().hex[:8]}"
            self.campaigns[campaign_id] = Campaign(
                id=campaign_id,
                name=sample["name"],
                type=sample["type"],
                status=sample["status"],
                description=sample["description"],
                subject=sample["subject"],
                content={"body": "", "blocks": []},
                audience_id=f"aud_{i+1}",
                audience_size=sample["audience_size"],
                schedule=None,
                settings={"track_opens": True, "track_clicks": True},
                version=1,
                tenant_id="default",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by="system",
                metrics=sample["metrics"]
            )

campaign_db = CampaignDB()

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("", response_model=List[Campaign])
async def list_campaigns(
    tenant_id: str = Query(default="default"),
    status: Optional[CampaignStatus] = None,
    type: Optional[CampaignType] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0)
):
    """List all campaigns with optional filtering"""
    campaigns = list(campaign_db.campaigns.values())
    
    # Filter by tenant
    campaigns = [c for c in campaigns if c.tenant_id == tenant_id]
    
    # Filter by status
    if status:
        campaigns = [c for c in campaigns if c.status == status]
    
    # Filter by type
    if type:
        campaigns = [c for c in campaigns if c.type == type]
    
    # Sort by updated_at desc
    campaigns.sort(key=lambda x: x.updated_at, reverse=True)
    
    return campaigns[offset:offset+limit]

@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Get single campaign by ID"""
    if campaign_id not in campaign_db.campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_db.campaigns[campaign_id]

@router.post("", response_model=Campaign)
async def create_campaign(campaign: CampaignCreate):
    """Create new campaign"""
    campaign_id = f"cmp_{uuid.uuid4().hex[:8]}"
    
    new_campaign = Campaign(
        id=campaign_id,
        name=campaign.name,
        type=campaign.type,
        status=CampaignStatus.DRAFT,
        description=campaign.description,
        subject=campaign.subject,
        content=campaign.content,
        audience_id=campaign.audience_id,
        audience_size=0,
        schedule=campaign.schedule,
        settings=campaign.settings,
        version=1,
        tenant_id=campaign.tenant_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="user",
        metrics={"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0}
    )
    
    campaign_db.campaigns[campaign_id] = new_campaign
    return new_campaign

@router.put("/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, update: CampaignUpdate):
    """Update existing campaign"""
    if campaign_id not in campaign_db.campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaign_db.campaigns[campaign_id]
    update_data = update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            setattr(campaign, field, value)
    
    campaign.updated_at = datetime.now()
    campaign.version += 1
    
    return campaign

@router.post("/{campaign_id}/save-draft")
async def save_campaign_draft(campaign_id: str, draft: CampaignDraft):
    """Save campaign draft (auto-save support)"""
    if campaign_id not in campaign_db.drafts:
        campaign_db.drafts[campaign_id] = []
    
    draft.version = len(campaign_db.drafts[campaign_id]) + 1
    campaign_db.drafts[campaign_id].append(draft)
    
    # Also update main campaign content
    if campaign_id in campaign_db.campaigns:
        campaign_db.campaigns[campaign_id].content = draft.content
        campaign_db.campaigns[campaign_id].updated_at = datetime.now()
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "version": draft.version,
        "saved_at": datetime.now().isoformat()
    }

@router.get("/{campaign_id}/drafts")
async def get_campaign_drafts(campaign_id: str):
    """Get all drafts/versions of a campaign"""
    return campaign_db.drafts.get(campaign_id, [])

@router.post("/{campaign_id}/duplicate", response_model=Campaign)
async def duplicate_campaign(campaign_id: str):
    """Duplicate an existing campaign"""
    if campaign_id not in campaign_db.campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    original = campaign_db.campaigns[campaign_id]
    new_id = f"cmp_{uuid.uuid4().hex[:8]}"
    
    duplicate = Campaign(
        id=new_id,
        name=f"{original.name} (Copy)",
        type=original.type,
        status=CampaignStatus.DRAFT,
        description=original.description,
        subject=original.subject,
        content=original.content.copy(),
        audience_id=original.audience_id,
        audience_size=original.audience_size,
        schedule=None,
        settings=original.settings.copy(),
        version=1,
        tenant_id=original.tenant_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="user",
        metrics={"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0}
    )
    
    campaign_db.campaigns[new_id] = duplicate
    return duplicate

@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete campaign (soft delete - moves to archived)"""
    if campaign_id not in campaign_db.campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign_db.campaigns[campaign_id].status = CampaignStatus.ARCHIVED
    return {"success": True, "message": "Campaign archived"}

@router.post("/{campaign_id}/activate")
async def activate_campaign(campaign_id: str):
    """Activate a campaign"""
    if campaign_id not in campaign_db.campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaign_db.campaigns[campaign_id]
    
    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.PAUSED, CampaignStatus.SCHEDULED]:
        raise HTTPException(status_code=400, detail="Campaign cannot be activated from current status")
    
    campaign.status = CampaignStatus.ACTIVE
    campaign.updated_at = datetime.now()
    
    return {"success": True, "status": "active"}

@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Pause an active campaign"""
    if campaign_id not in campaign_db.campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaign_db.campaigns[campaign_id]
    
    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active campaigns can be paused")
    
    campaign.status = CampaignStatus.PAUSED
    campaign.updated_at = datetime.now()
    
    return {"success": True, "status": "paused"}
