"""Campaign API Routes."""
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import Optional
from ..schemas.campaign_schemas import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse
from ..services.campaign_service import CampaignService

router = APIRouter(prefix="/api/v1/campaigns", tags=["campaigns"])
campaign_service = CampaignService()

def get_tenant_id(x_tenant_id: str = Header(...)) -> str:
    return x_tenant_id

@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(data: CampaignCreate, tenant_id: str = Depends(get_tenant_id)):
    campaign = await campaign_service.create_campaign(tenant_id=tenant_id, data=data)
    return CampaignResponse(**campaign.to_dict())

@router.get("", response_model=CampaignListResponse)
async def list_campaigns(tenant_id: str = Depends(get_tenant_id), status: Optional[str] = Query(None), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    result = await campaign_service.list_campaigns(tenant_id=tenant_id, status=status, page=page, page_size=page_size)
    return CampaignListResponse(campaigns=[CampaignResponse(**c.to_dict()) for c in result["campaigns"]], **{k: v for k, v in result.items() if k != "campaigns"})

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, tenant_id: str = Depends(get_tenant_id)):
    campaign = await campaign_service.get_campaign(campaign_id, tenant_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse(**campaign.to_dict())

@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: str, data: CampaignUpdate, tenant_id: str = Depends(get_tenant_id)):
    campaign = await campaign_service.update_campaign(campaign_id, tenant_id, data)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse(**campaign.to_dict())

@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: str, tenant_id: str = Depends(get_tenant_id)):
    if not await campaign_service.delete_campaign(campaign_id, tenant_id):
        raise HTTPException(status_code=400, detail="Cannot delete")

@router.post("/{campaign_id}/publish", response_model=CampaignResponse)
async def publish_campaign(campaign_id: str, tenant_id: str = Depends(get_tenant_id)):
    campaign = await campaign_service.publish_campaign(campaign_id, tenant_id)
    if not campaign:
        raise HTTPException(status_code=400, detail="Cannot publish")
    return CampaignResponse(**campaign.to_dict())
