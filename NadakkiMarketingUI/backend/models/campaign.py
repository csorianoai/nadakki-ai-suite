"""Campaign Model - Gestión de campañas de marketing."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    PARTIALLY_PUBLISHED = "partially_published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CampaignObjective(str, Enum):
    AWARENESS = "awareness"
    ENGAGEMENT = "engagement"
    LEADS = "leads"
    SALES = "sales"
    TRAFFIC = "traffic"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class Frequency(str, Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Campaign:
    """Modelo de Campaña de Marketing."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    name: str = ""
    objective: CampaignObjective = CampaignObjective.AWARENESS
    content_type: ContentType = ContentType.TEXT
    content_text: str = ""
    content_media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    link_url: Optional[str] = None
    call_to_action: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    frequency: Frequency = Frequency.ONCE
    timezone: str = "America/New_York"
    target_pages: List[Dict[str, Any]] = field(default_factory=list)
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    published_at: Optional[datetime] = None
    publish_results: List[Dict[str, Any]] = field(default_factory=list)
    total_reach: int = 0
    total_engagement: int = 0
    ai_generated: bool = False
    ai_suggestions: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.objective, str):
            self.objective = CampaignObjective(self.objective)
        if isinstance(self.content_type, str):
            self.content_type = ContentType(self.content_type)
        if isinstance(self.status, str):
            self.status = CampaignStatus(self.status)
        if isinstance(self.frequency, str):
            self.frequency = Frequency(self.frequency)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["objective"] = self.objective.value
        data["content_type"] = self.content_type.value
        data["status"] = self.status.value
        data["frequency"] = self.frequency.value
        if data["created_at"]:
            data["created_at"] = self.created_at.isoformat()
        if data["updated_at"]:
            data["updated_at"] = self.updated_at.isoformat()
        if data["scheduled_at"]:
            data["scheduled_at"] = self.scheduled_at.isoformat()
        if data["published_at"]:
            data["published_at"] = self.published_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Campaign":
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at") and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("scheduled_at") and isinstance(data["scheduled_at"], str):
            data["scheduled_at"] = datetime.fromisoformat(data["scheduled_at"])
        if data.get("published_at") and isinstance(data["published_at"], str):
            data["published_at"] = datetime.fromisoformat(data["published_at"])
        return cls(**data)

    def is_ready_to_publish(self) -> bool:
        if not self.content_text and not self.content_media_urls:
            return False
        if not self.target_pages:
            return False
        if self.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            return False
        return True

    def get_content_preview(self, max_length: int = 100) -> str:
        text = self.content_text
        if self.hashtags:
            text += " " + " ".join(f"#{h}" for h in self.hashtags[:3])
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text
