"""Social Connection Model."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict


class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"


@dataclass
class SocialConnection:
    """Conexión a una red social."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    platform: str = ""
    page_id: str = ""
    page_name: str = ""
    page_username: str = ""
    page_picture_url: Optional[str] = None
    followers_count: int = 0
    access_token: str = ""
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    status: ConnectionStatus = ConnectionStatus.ACTIVE
    last_used_at: Optional[datetime] = None
    last_error: Optional[str] = None
    connected_at: datetime = field(default_factory=datetime.utcnow)
    connected_by: Optional[str] = None

    def is_token_expired(self) -> bool:
        if not self.token_expires_at:
            return False
        return datetime.utcnow() >= self.token_expires_at

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["access_token"] = "***" if self.access_token else None
        data["refresh_token"] = "***" if self.refresh_token else None
        for dt_field in ["token_expires_at", "connected_at", "last_used_at"]:
            if data.get(dt_field):
                data[dt_field] = getattr(self, dt_field).isoformat()
        return data
