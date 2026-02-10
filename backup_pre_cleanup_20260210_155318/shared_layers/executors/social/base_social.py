"""
NADAKKI AI SUITE - Base Social Executor
Clase base para publicar en redes sociales
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PostRequest:
    """Solicitud de publicacion"""
    content: str
    media_urls: List[str] = field(default_factory=list)
    scheduled_time: Optional[datetime] = None
    tenant_id: str = "default"

@dataclass
class PostResponse:
    """Respuesta de publicacion"""
    success: bool
    post_id: Optional[str] = None
    platform: str = ""
    url: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseSocialExecutor(ABC):
    """Clase base para todos los social executors"""
    
    def __init__(self, access_token: str, page_id: str = None):
        self.access_token = access_token
        self.page_id = page_id
        self.platform = "unknown"
    
    @abstractmethod
    async def post(self, request: PostRequest) -> PostResponse:
        """Publicar contenido"""
        pass
    
    @abstractmethod
    async def get_insights(self, post_id: str) -> Dict[str, Any]:
        """Obtener metricas de un post"""
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """Eliminar un post"""
        pass
