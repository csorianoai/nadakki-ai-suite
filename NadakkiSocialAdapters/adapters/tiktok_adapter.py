"""TikTok Adapter."""
import os
from datetime import datetime
from urllib.parse import urlencode
from .social_network_adapter import (
    SocialNetworkAdapter, SocialNetworkRegistry,
    Platform, PostContent, PublishResult, ConnectionResult
)


class TikTokAdapter(SocialNetworkAdapter):
    """Adaptador para TikTok."""
    platforms = [Platform.TIKTOK]

    def __init__(self, access_token=None):
        super().__init__(access_token)
        self.client_key = os.environ.get("TIKTOK_CLIENT_KEY", "")

    def get_auth_url(self, tenant_id: str, redirect_uri: str) -> str:
        params = {
            "client_key": self.client_key,
            "redirect_uri": redirect_uri,
            "state": tenant_id,
            "scope": "video.upload"
        }
        return f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token="tiktok_token")

    async def refresh_token(self, refresh_token: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token=refresh_token)

    async def publish_post(self, content: PostContent) -> PublishResult:
        if not content.video_url:
            return PublishResult(success=False, error="TikTok requires video")
        return PublishResult(success=True, post_id="tt_12345", platform=Platform.TIKTOK)


SocialNetworkRegistry.register(Platform.TIKTOK, TikTokAdapter)
