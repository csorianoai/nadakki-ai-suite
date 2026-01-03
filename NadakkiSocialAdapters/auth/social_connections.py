"""Social Connections Manager."""
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any


@dataclass
class SocialConnection:
    """Conexion a red social."""
    id: str
    tenant_id: str
    platform: str
    platform_user_id: str
    platform_username: str
    access_token: str
    refresh_token: Optional[str] = None
    is_active: bool = True
    connected_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["connected_at"] = data["connected_at"].isoformat()
        return data


class SocialAuthManager:
    """Gestor de autenticacion."""

    def __init__(self):
        self._connections: Dict[str, SocialConnection] = {}
        self._states: Dict[str, Dict] = {}

    def generate_state(self, tenant_id: str, platform: str) -> str:
        state = str(uuid.uuid4())
        self._states[state] = {
            "tenant_id": tenant_id,
            "platform": platform,
            "created": datetime.utcnow().isoformat()
        }
        return state

    def validate_state(self, state: str) -> Optional[Dict]:
        return self._states.pop(state, None)

    async def save_connection(self, conn: SocialConnection) -> bool:
        self._connections[conn.id] = conn
        return True

    async def get_connection(self, conn_id: str) -> Optional[SocialConnection]:
        return self._connections.get(conn_id)

    async def delete_connection(self, conn_id: str) -> bool:
        if conn_id in self._connections:
            del self._connections[conn_id]
            return True
        return False
