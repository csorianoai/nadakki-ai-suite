"""
NADAKKI Campaigns API
Endpoints para crear, gestionar y ejecutar campañas de marketing
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import uuid

logger = logging.getLogger("CampaignsAPI")
router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])

# Base de datos en memoria (en producción usar DB real)
CAMPAIGNS_DB: Dict[str, Dict[str, Any]] = {}

class CampaignCreate(BaseModel):
    name: str = Field(..., description="Nombre de la campaña")
    channel: str = Field(default="email", description="Canal: email, sms, push, in-app")
    subject: Optional[str] = Field(None, description="Asunto del email")
    content: str = Field(..., description="Contenido del mensaje")
    schedule: str = Field(default="now", description="now o scheduled")
    schedule_date: Optional[str] = Field(None, description="Fecha programada ISO")
    segment: str = Field(default="all", description="Segmento de audiencia")
    
class CampaignResponse(BaseModel):
    id: str
    name: str
    channel: str
    status: str
    created_at: str
    scheduled_at: Optional[str]
    segment: str
    stats: Dict[str, int]

@router.post("")
async def create_campaign(
    campaign: CampaignCreate,
    tenant_id: str = Query("credicefi")
):
    """Crear una nueva campaña"""
    campaign_id = f"cmp-{uuid.uuid4().hex[:8]}"
    
    now = datetime.utcnow().isoformat() + "Z"
    
    campaign_data = {
        "id": campaign_id,
        "tenant_id": tenant_id,
        "name": campaign.name,
        "channel": campaign.channel,
        "subject": campaign.subject,
        "content": campaign.content,
        "schedule": campaign.schedule,
        "scheduled_at": campaign.schedule_date if campaign.schedule == "scheduled" else None,
        "segment": campaign.segment,
        "status": "scheduled" if campaign.schedule == "scheduled" else "sending",
        "created_at": now,
        "updated_at": now,
        "stats": {
            "total": 0,
            "sent": 0,
            "delivered": 0,
            "opened": 0,
            "clicked": 0,
            "bounced": 0
        }
    }
    
    # Simular audiencia basada en segmento
    audience_sizes = {
        "all": 12450,
        "active": 8230,
        "leads": 1850,
        "inactive": 2340,
        "custom": 500
    }
    campaign_data["stats"]["total"] = audience_sizes.get(campaign.segment, 1000)
    
    # Guardar en memoria
    CAMPAIGNS_DB[campaign_id] = campaign_data
    
    logger.info(f"Campaign created: {campaign_id} for tenant {tenant_id}")
    
    # Si es envío inmediato, simular envío
    if campaign.schedule == "now":
        campaign_data["status"] = "sent"
        campaign_data["stats"]["sent"] = campaign_data["stats"]["total"]
        campaign_data["stats"]["delivered"] = int(campaign_data["stats"]["total"] * 0.95)
        campaign_data["stats"]["opened"] = int(campaign_data["stats"]["delivered"] * 0.35)
        campaign_data["stats"]["clicked"] = int(campaign_data["stats"]["opened"] * 0.12)
    
    return {
        "success": True,
        "campaign": campaign_data,
        "message": f"Campaña '{campaign.name}' creada exitosamente"
    }

@router.get("")
async def list_campaigns(
    tenant_id: str = Query("credicefi"),
    status: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    limit: int = Query(20)
):
    """Listar campañas del tenant"""
    # Filtrar por tenant
    campaigns = [c for c in CAMPAIGNS_DB.values() if c.get("tenant_id") == tenant_id]
    
    # Filtrar por status
    if status:
        campaigns = [c for c in campaigns if c.get("status") == status]
    
    # Filtrar por canal
    if channel:
        campaigns = [c for c in campaigns if c.get("channel") == channel]
    
    # Si no hay campañas, devolver datos de ejemplo
    if not campaigns:
        campaigns = [
            {
                "id": "cmp-demo1",
                "name": "Bienvenida Nuevos Usuarios",
                "channel": "email",
                "status": "sent",
                "created_at": "2026-01-03T10:00:00Z",
                "segment": "all",
                "stats": {"total": 5200, "sent": 5200, "delivered": 4940, "opened": 1729, "clicked": 207}
            },
            {
                "id": "cmp-demo2",
                "name": "Promocion Q1 2026",
                "channel": "email",
                "status": "scheduled",
                "scheduled_at": "2026-01-10T09:00:00Z",
                "created_at": "2026-01-04T14:30:00Z",
                "segment": "active",
                "stats": {"total": 8230, "sent": 0, "delivered": 0, "opened": 0, "clicked": 0}
            },
            {
                "id": "cmp-demo3",
                "name": "Reactivacion Usuarios",
                "channel": "sms",
                "status": "draft",
                "created_at": "2026-01-05T08:00:00Z",
                "segment": "inactive",
                "stats": {"total": 2340, "sent": 0, "delivered": 0, "opened": 0, "clicked": 0}
            }
        ]
    
    return {
        "campaigns": campaigns[:limit],
        "total": len(campaigns),
        "tenant_id": tenant_id
    }

@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    tenant_id: str = Query("credicefi")
):
    """Obtener detalles de una campaña"""
    campaign = CAMPAIGNS_DB.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    
    if campaign.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    return {"campaign": campaign}

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    tenant_id: str = Query("credicefi")
):
    """Eliminar una campaña"""
    if campaign_id in CAMPAIGNS_DB:
        if CAMPAIGNS_DB[campaign_id].get("tenant_id") == tenant_id:
            del CAMPAIGNS_DB[campaign_id]
            return {"success": True, "message": "Campaña eliminada"}
    
    raise HTTPException(status_code=404, detail="Campaña no encontrada")

@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: str,
    tenant_id: str = Query("credicefi")
):
    """Enviar una campaña programada o en borrador"""
    campaign = CAMPAIGNS_DB.get(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    
    if campaign.get("status") == "sent":
        raise HTTPException(status_code=400, detail="La campaña ya fue enviada")
    
    # Simular envío
    campaign["status"] = "sent"
    campaign["stats"]["sent"] = campaign["stats"]["total"]
    campaign["stats"]["delivered"] = int(campaign["stats"]["total"] * 0.95)
    campaign["stats"]["opened"] = int(campaign["stats"]["delivered"] * 0.35)
    campaign["stats"]["clicked"] = int(campaign["stats"]["opened"] * 0.12)
    campaign["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return {
        "success": True,
        "campaign": campaign,
        "message": "Campaña enviada exitosamente"
    }

@router.get("/stats/summary")
async def get_campaigns_summary(
    tenant_id: str = Query("credicefi")
):
    """Obtener resumen de estadísticas de campañas"""
    campaigns = [c for c in CAMPAIGNS_DB.values() if c.get("tenant_id") == tenant_id]
    
    total_sent = sum(c["stats"]["sent"] for c in campaigns)
    total_delivered = sum(c["stats"]["delivered"] for c in campaigns)
    total_opened = sum(c["stats"]["opened"] for c in campaigns)
    total_clicked = sum(c["stats"]["clicked"] for c in campaigns)
    
    # Datos de ejemplo si no hay campañas
    if not campaigns:
        total_sent = 15670
        total_delivered = 14886
        total_opened = 5210
        total_clicked = 625
    
    return {
        "summary": {
            "total_campaigns": len(campaigns) or 12,
            "active": len([c for c in campaigns if c.get("status") == "sent"]) or 5,
            "scheduled": len([c for c in campaigns if c.get("status") == "scheduled"]) or 4,
            "draft": len([c for c in campaigns if c.get("status") == "draft"]) or 3,
            "total_sent": total_sent,
            "total_delivered": total_delivered,
            "total_opened": total_opened,
            "total_clicked": total_clicked,
            "delivery_rate": round((total_delivered / total_sent * 100) if total_sent > 0 else 95, 1),
            "open_rate": round((total_opened / total_delivered * 100) if total_delivered > 0 else 35, 1),
            "click_rate": round((total_clicked / total_opened * 100) if total_opened > 0 else 12, 1)
        },
        "tenant_id": tenant_id
    }

def get_router():
    return router
