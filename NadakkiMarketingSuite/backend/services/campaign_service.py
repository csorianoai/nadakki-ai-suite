"""Campaign Service - Lógica de negocio para campañas."""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from ..models.campaign import Campaign, CampaignStatus
from ..schemas.campaign_schemas import CampaignCreate, CampaignUpdate

logger = logging.getLogger(__name__)


class CampaignService:
    """Servicio para gestión de campañas."""
    
    def __init__(self):
        self._campaigns: Dict[str, Campaign] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_campaign(self, tenant_id: str, data: CampaignCreate, created_by: Optional[str] = None) -> Campaign:
        campaign = Campaign(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=data.name,
            objective=data.objective.value,
            content_type=data.content_type.value,
            content_text=data.content_text,
            content_media_urls=data.content_media_urls,
            hashtags=data.hashtags,
            link_url=data.link_url,
            call_to_action=data.call_to_action,
            scheduled_at=data.scheduled_at,
            frequency=data.frequency.value,
            timezone=data.timezone,
            target_pages=[tp.model_dump() for tp in data.target_pages],
            status=CampaignStatus.SCHEDULED if data.scheduled_at else CampaignStatus.DRAFT,
            created_by=created_by,
            ai_generated=data.ai_generated
        )
        self._campaigns[campaign.id] = campaign
        self.logger.info(f"Campaign created: {campaign.id}")
        return campaign

    async def get_campaign(self, campaign_id: str, tenant_id: str) -> Optional[Campaign]:
        campaign = self._campaigns.get(campaign_id)
        if campaign and campaign.tenant_id == tenant_id:
            return campaign
        return None

    async def list_campaigns(self, tenant_id: str, status: Optional[str] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        campaigns = [c for c in self._campaigns.values() if c.tenant_id == tenant_id]
        if status:
            campaigns = [c for c in campaigns if c.status.value == status]
        campaigns.sort(key=lambda x: x.created_at, reverse=True)
        total = len(campaigns)
        start = (page - 1) * page_size
        end = start + page_size
        return {"campaigns": campaigns[start:end], "total": total, "page": page, "page_size": page_size, "has_more": end < total}

    async def update_campaign(self, campaign_id: str, tenant_id: str, data: CampaignUpdate) -> Optional[Campaign]:
        campaign = await self.get_campaign(campaign_id, tenant_id)
        if not campaign:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(campaign, field):
                if field == "target_pages" and value:
                    value = [tp if isinstance(tp, dict) else tp.model_dump() for tp in value]
                setattr(campaign, field, value)
        campaign.updated_at = datetime.utcnow()
        return campaign

    async def delete_campaign(self, campaign_id: str, tenant_id: str) -> bool:
        campaign = await self.get_campaign(campaign_id, tenant_id)
        if not campaign or campaign.status in [CampaignStatus.PUBLISHED, CampaignStatus.PUBLISHING]:
            return False
        del self._campaigns[campaign_id]
        return True

    async def publish_campaign(self, campaign_id: str, tenant_id: str) -> Optional[Campaign]:
        campaign = await self.get_campaign(campaign_id, tenant_id)
        if not campaign or not campaign.is_ready_to_publish():
            return None
        campaign.status = CampaignStatus.PUBLISHING
        campaign.updated_at = datetime.utcnow()
        campaign.status = CampaignStatus.PUBLISHED
        campaign.published_at = datetime.utcnow()
        return campaign

    async def cancel_campaign(self, campaign_id: str, tenant_id: str) -> Optional[Campaign]:
        campaign = await self.get_campaign(campaign_id, tenant_id)
        if not campaign or campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            return None
        campaign.status = CampaignStatus.CANCELLED
        campaign.updated_at = datetime.utcnow()
        return campaign

    def count_by_status(self, tenant_id: str) -> Dict[str, int]:
        counts = {}
        for campaign in self._campaigns.values():
            if campaign.tenant_id == tenant_id:
                status = campaign.status.value
                counts[status] = counts.get(status, 0) + 1
        return counts
