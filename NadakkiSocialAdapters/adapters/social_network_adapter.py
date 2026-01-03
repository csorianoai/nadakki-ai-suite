"""Base Social Network Adapter."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Type
from enum import Enum
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Platform(str, Enum):
    """Plataformas soportadas."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    X = "x"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    YOUTUBE = "youtube"


@dataclass
class PostContent:
    """Contenido a publicar."""
    text: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)


@dataclass
class PublishResult:
    """Resultado de publicacion."""
    success: bool
    post_id: Optional[str] = None
    platform: Optional[Platform] = None
    error: Optional[str] = None


@dataclass
class ConnectionResult:
    """Resultado de conexion OAuth."""
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    error: Optional[str] = None


class SocialNetworkAdapter(ABC):
    """Adaptador base para redes sociales."""
    platforms: List[Platform] = []

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_auth_url(self, tenant_id: str, redirect_uri: str) -> str:
        """Genera URL de autorizacion."""
        pass

    @abstractmethod
    async def publish_post(self, content: PostContent) -> PublishResult:
        """Publica contenido."""
        pass

    def publish_post_sync(self, content: PostContent) -> PublishResult:
        """Version sincrona de publish_post."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.publish_post(content))
            loop.close()
            return result
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> ConnectionResult:
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> ConnectionResult:
        pass


class SocialNetworkRegistry:
    """Registro de adaptadores."""
    _adapters: Dict[Platform, Type[SocialNetworkAdapter]] = {}

    @classmethod
    def register(cls, platform: Platform, adapter: Type[SocialNetworkAdapter]):
        cls._adapters[platform] = adapter

    @classmethod
    def get_adapter(cls, platform: Platform, token: str = None) -> SocialNetworkAdapter:
        if platform not in cls._adapters:
            raise ValueError(f"No adapter for: {platform}")
        return cls._adapters[platform](token)

    @classmethod
    def list_platforms(cls) -> List[Platform]:
        return list(cls._adapters.keys())

    @classmethod
    def is_registered(cls, platform: Platform) -> bool:
        return platform in cls._adapters

    @classmethod
    def count(cls) -> int:
        return len(cls._adapters)
