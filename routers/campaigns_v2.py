"""
Campaign Persistence Router v2 - Real Database Persistence
NADAKKI AI Suite v2.0
"""
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import json

from database import get_db

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
    version: int = 1
    content: Dict[str, Any]
    auto_save: bool = True
    tenant_id: str = "default"

class Campaign(BaseModel):
    id: str
    name: str
    type: str
    status: str
    description: str
    subject: Optional[str]
    content: Dict[str, Any]
    audience_id: Optional[str]
    audience_size: int
    schedule: Optional[Dict[str, Any]]
    settings: Dict[str, Any]
    version: int
    tenant_id: str
    created_at: str
    updated_at: str
    created_by: str
    metrics: Dict[str, Any]

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def row_to_campaign(row) -> Campaign:
    """Convert database row to Campaign model"""
    return Campaign(
        id=row["id"],
        name=row["name"],
        type=row["type"],
        status=row["status"],
        description=row["description"] or "",
        subject=row["subject"],
        content=json.loads(row["content"]) if row["content"] else {},
        audience_id=row["audience_id"],
        audience_size=row["audience_size"] or 0,
        schedule=json.loads(row["schedule"]) if row["schedule"] else None,
        settings=json.loads(row["settings"]) if row["settings"] else {},
        version=row["version"] or 1,
        tenant_id=row["tenant_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        created_by=row["created_by"] or "user",
        metrics=json.loads(row["metrics"]) if row["metrics"] else {"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0}
    )

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
    """List all campaigns from DATABASE"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM campaigns WHERE tenant_id = ?"
        params = [tenant_id]
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        if type:
            query += " AND type = ?"
            params.append(type.value)
        
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [row_to_campaign(row) for row in rows]

@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Get single campaign by ID from DATABASE"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return row_to_campaign(row)

@router.post("", response_model=Campaign)
async def create_campaign(campaign: CampaignCreate):
    """Create new campaign in DATABASE"""
    campaign_id = f"cmp_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaigns (id, tenant_id, name, type, status, description, subject, content, audience_id, audience_size, schedule, settings, version, created_at, updated_at, created_by, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 1, ?, ?, 'user', ?)
        ''', (
            campaign_id,
            campaign.tenant_id,
            campaign.name,
            campaign.type.value,
            CampaignStatus.DRAFT.value,
            campaign.description,
            campaign.subject,
            json.dumps(campaign.content),
            campaign.audience_id,
            json.dumps(campaign.schedule) if campaign.schedule else None,
            json.dumps(campaign.settings),
            now,
            now,
            json.dumps({"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0})
        ))
        
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        
        return row_to_campaign(row)

@router.put("/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, update: CampaignUpdate):
    """Update existing campaign in DATABASE"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check exists
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Build update query
        updates = []
        params = []
        
        if update.name is not None:
            updates.append("name = ?")
            params.append(update.name)
        if update.description is not None:
            updates.append("description = ?")
            params.append(update.description)
        if update.subject is not None:
            updates.append("subject = ?")
            params.append(update.subject)
        if update.content is not None:
            updates.append("content = ?")
            params.append(json.dumps(update.content))
        if update.audience_id is not None:
            updates.append("audience_id = ?")
            params.append(update.audience_id)
        if update.schedule is not None:
            updates.append("schedule = ?")
            params.append(json.dumps(update.schedule))
        if update.settings is not None:
            updates.append("settings = ?")
            params.append(json.dumps(update.settings))
        if update.status is not None:
            updates.append("status = ?")
            params.append(update.status.value)
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        updates.append("version = version + 1")
        
        params.append(campaign_id)
        
        cursor.execute(f"UPDATE campaigns SET {', '.join(updates)} WHERE id = ?", params)
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        
        return row_to_campaign(row)

@router.post("/{campaign_id}/save-draft")
async def save_campaign_draft(campaign_id: str, draft: CampaignDraft):
    """Save campaign draft to DATABASE (auto-save support)"""
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get current version
        cursor.execute("SELECT version FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        version = (row["version"] + 1) if row else 1
        
        # Save draft
        cursor.execute('''
            INSERT INTO campaign_drafts (campaign_id, version, content, created_at, tenant_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (campaign_id, version, json.dumps(draft.content), now, draft.tenant_id))
        
        # Update main campaign
        if row:
            cursor.execute('''
                UPDATE campaigns 
                SET content = ?, updated_at = ?, version = ?
                WHERE id = ?
            ''', (json.dumps(draft.content), now, version, campaign_id))
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "version": version,
        "saved_at": now,
        "persisted": True
    }

@router.get("/{campaign_id}/drafts")
async def get_campaign_drafts(campaign_id: str):
    """Get all drafts/versions of a campaign from DATABASE"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM campaign_drafts 
            WHERE campaign_id = ? 
            ORDER BY version DESC
        ''', (campaign_id,))
        
        return [
            {
                "version": row["version"],
                "content": json.loads(row["content"]) if row["content"] else {},
                "created_at": row["created_at"]
            }
            for row in cursor.fetchall()
        ]

@router.post("/{campaign_id}/duplicate", response_model=Campaign)
async def duplicate_campaign(campaign_id: str):
    """Duplicate an existing campaign in DATABASE"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        new_id = f"cmp_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO campaigns (id, tenant_id, name, type, status, description, subject, content, audience_id, audience_size, schedule, settings, version, created_at, updated_at, created_by, metrics)
            VALUES (?, ?, ?, ?, 'draft', ?, ?, ?, ?, ?, NULL, ?, 1, ?, ?, 'user', ?)
        ''', (
            new_id,
            row["tenant_id"],
            f"{row['name']} (Copy)",
            row["type"],
            row["description"],
            row["subject"],
            row["content"],
            row["audience_id"],
            row["audience_size"],
            row["settings"],
            now,
            now,
            json.dumps({"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0})
        ))
        
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (new_id,))
        new_row = cursor.fetchone()
        
        return row_to_campaign(new_row)

@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Archive campaign in DATABASE (soft delete)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM campaigns WHERE id = ?", (campaign_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        cursor.execute('''
            UPDATE campaigns SET status = 'archived', updated_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), campaign_id))
    
    return {"success": True, "message": "Campaign archived", "persisted": True}

@router.post("/{campaign_id}/activate")
async def activate_campaign(campaign_id: str):
    """Activate a campaign in DATABASE"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if row["status"] not in ["draft", "paused", "scheduled"]:
            raise HTTPException(status_code=400, detail="Campaign cannot be activated from current status")
        
        cursor.execute('''
            UPDATE campaigns SET status = 'active', updated_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), campaign_id))
    
    return {"success": True, "status": "active", "persisted": True}

@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Pause an active campaign in DATABASE"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if row["status"] != "active":
            raise HTTPException(status_code=400, detail="Only active campaigns can be paused")
        
        cursor.execute('''
            UPDATE campaigns SET status = 'paused', updated_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), campaign_id))
    
    return {"success": True, "status": "paused", "persisted": True}
