"""Pydantic Schemas para Campañas."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class CampaignObjectiveEnum(str, Enum):
    AWARENESS = "awareness"
    ENGAGEMENT = "engagement"
    LEADS = "leads"
    SALES = "sales"
    TRAFFIC = "traffic"


class ContentTypeEnum(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class FrequencyEnum(str, Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class CampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    PARTIALLY_PUBLISHED = "partially_published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TargetPageSchema(BaseModel):
    platform: str
    page_id: str
    page_name: str
    connection_id: str


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    objective: CampaignObjectiveEnum = CampaignObjectiveEnum.AWARENESS
    content_type: ContentTypeEnum = ContentTypeEnum.TEXT
    content_text: str = Field(default="", max_length=5000)
    content_media_urls: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    link_url: Optional[str] = None
    call_to_action: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    frequency: FrequencyEnum = FrequencyEnum.ONCE
    timezone: str = "America/New_York"
    target_pages: List[TargetPageSchema] = Field(default_factory=list)
    ai_generated: bool = False

    @field_validator("hashtags")
    @classmethod
    def clean_hashtags(cls, v):
        return [h.lstrip("#").strip() for h in v if h.strip()]


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    objective: Optional[CampaignObjectiveEnum] = None
    content_type: Optional[ContentTypeEnum] = None
    content_text: Optional[str] = Field(None, max_length=5000)
    content_media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    link_url: Optional[str] = None
    call_to_action: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    frequency: Optional[FrequencyEnum] = None
    timezone: Optional[str] = None
    target_pages: Optional[List[TargetPageSchema]] = None
    status: Optional[CampaignStatusEnum] = None


class CampaignResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    objective: str
    content_type: str
    content_text: str
    content_media_urls: List[str]
    hashtags: List[str]
    link_url: Optional[str]
    call_to_action: Optional[str]
    scheduled_at: Optional[datetime]
    frequency: str
    timezone: str
    target_pages: List[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    published_at: Optional[datetime]
    publish_results: List[Dict[str, Any]]
    total_reach: int
    total_engagement: int
    ai_generated: bool
    ai_suggestions: Dict[str, Any]

    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    campaigns: List[CampaignResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
