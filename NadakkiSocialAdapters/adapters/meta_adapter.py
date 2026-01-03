"""Meta (Facebook + Instagram) Adapter."""
import os
from datetime import datetime
from urllib.parse import urlencode
from .social_network_adapter import (
    SocialNetworkAdapter, SocialNetworkRegistry,
    Platform, PostContent, PublishResult, ConnectionResult
)


class MetaAdapter(SocialNetworkAdapter):
    """Adaptador para Facebook e Instagram."""
    platforms = [Platform.FACEBOOK, Platform.INSTAGRAM]

    def __init__(self, access_token=None):
        super().__init__(access_token)
        self.app_id = os.environ.get("META_APP_ID", "")

    def get_auth_url(self, tenant_id: str, redirect_uri: str) -> str:
        params = {
            "client_id": self.app_id,
            "redirect_uri": redirect_uri,
            "state": tenant_id,
            "scope": "pages_manage_posts,instagram_content_publish"
        }
        return f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token="meta_token")

    async def refresh_token(self, refresh_token: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token=refresh_token)

    async def publish_post(self, content: PostContent, page_id: str = None) -> PublishResult:
        return PublishResult(
            success=True,
            post_id="fb_12345",
            platform=Platform.FACEBOOK
        )

    def _format_text(self, content: PostContent) -> str:
        text = content.text
        if content.hashtags:
            text += " " + " ".join(f"#{t}" for t in content.hashtags)
        return text


SocialNetworkRegistry.register(Platform.FACEBOOK, MetaAdapter)
SocialNetworkRegistry.register(Platform.INSTAGRAM, MetaAdapter)
