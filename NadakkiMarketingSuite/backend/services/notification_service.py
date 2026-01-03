"""Notification Service - Alertas y Webhooks."""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"


@dataclass
class Notification:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    user_id: Optional[str] = None
    type: NotificationType = NotificationType.INFO
    title: str = ""
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    channels: List[NotificationChannel] = field(default_factory=list)
    read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "tenant_id": self.tenant_id, "type": self.type.value,
            "title": self.title, "message": self.message, "read": self.read,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class WebhookConfig:
    id: str
    tenant_id: str
    url: str
    events: List[str]
    active: bool = True


class NotificationService:
    def __init__(self):
        self._notifications: Dict[str, Notification] = {}
        self._webhooks: Dict[str, WebhookConfig] = {}
    
    def create_notification(self, tenant_id: str, title: str, message: str, type: NotificationType = NotificationType.INFO, user_id: Optional[str] = None, data: Optional[Dict] = None, channels: Optional[List[NotificationChannel]] = None) -> Notification:
        notification = Notification(tenant_id=tenant_id, user_id=user_id, type=type, title=title, message=message, data=data or {}, channels=channels or [NotificationChannel.IN_APP])
        self._notifications[notification.id] = notification
        self._trigger_webhooks(tenant_id, "notification.created", notification.to_dict())
        return notification
    
    def get_notifications(self, tenant_id: str, user_id: Optional[str] = None, unread_only: bool = False) -> List[Notification]:
        notifications = [n for n in self._notifications.values() if n.tenant_id == tenant_id]
        if user_id: notifications = [n for n in notifications if n.user_id == user_id or n.user_id is None]
        if unread_only: notifications = [n for n in notifications if not n.read]
        return sorted(notifications, key=lambda x: x.created_at, reverse=True)
    
    def mark_as_read(self, notification_id: str) -> bool:
        if notification_id in self._notifications:
            self._notifications[notification_id].read = True
            return True
        return False
    
    def mark_all_as_read(self, tenant_id: str, user_id: Optional[str] = None) -> int:
        count = 0
        for n in self._notifications.values():
            if n.tenant_id == tenant_id and not n.read:
                if user_id is None or n.user_id == user_id:
                    n.read = True
                    count += 1
        return count
    
    def register_webhook(self, tenant_id: str, url: str, events: List[str], secret: Optional[str] = None) -> WebhookConfig:
        webhook = WebhookConfig(id=str(uuid.uuid4()), tenant_id=tenant_id, url=url, events=events)
        self._webhooks[webhook.id] = webhook
        return webhook
    
    def _trigger_webhooks(self, tenant_id: str, event: str, data: Dict):
        webhooks = [w for w in self._webhooks.values() if w.tenant_id == tenant_id and w.active and event in w.events]
        for w in webhooks:
            logger.info(f"Would trigger webhook {w.id} for event {event}")
    
    def get_webhooks(self, tenant_id: str) -> List[WebhookConfig]:
        return [w for w in self._webhooks.values() if w.tenant_id == tenant_id]


notification_service = NotificationService()
