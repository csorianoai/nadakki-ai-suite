"""YouTube Adapter."""
import os
from urllib.parse import urlencode
from .social_network_adapter import (
    SocialNetworkAdapter, SocialNetworkRegistry,
    Platform, PostContent, PublishResult, ConnectionResult
)


class YouTubeAdapter(SocialNetworkAdapter):
    """Adaptador para YouTube."""
    platforms = [Platform.YOUTUBE]

    def __init__(self, access_token=None):
        super().__init__(access_token)
        self.client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")

    def get_auth_url(self, tenant_id: str, redirect_uri: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": tenant_id,
            "scope": "https://www.googleapis.com/auth/youtube.upload"
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token="youtube_token")

    async def refresh_token(self, refresh_token: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token=refresh_token)

    async def publish_post(self, content: PostContent) -> PublishResult:
        if not content.video_url:
            return PublishResult(success=False, error="YouTube requires video")
        return PublishResult(success=True, post_id="yt_12345", platform=Platform.YOUTUBE)


SocialNetworkRegistry.register(Platform.YOUTUBE, YouTubeAdapter)
