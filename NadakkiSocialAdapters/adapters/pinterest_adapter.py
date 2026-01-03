"""Pinterest Adapter."""
import os
from urllib.parse import urlencode
from .social_network_adapter import (
    SocialNetworkAdapter, SocialNetworkRegistry,
    Platform, PostContent, PublishResult, ConnectionResult
)


class PinterestAdapter(SocialNetworkAdapter):
    """Adaptador para Pinterest."""
    platforms = [Platform.PINTEREST]

    def __init__(self, access_token=None):
        super().__init__(access_token)
        self.app_id = os.environ.get("PINTEREST_APP_ID", "")

    def get_auth_url(self, tenant_id: str, redirect_uri: str) -> str:
        params = {
            "client_id": self.app_id,
            "redirect_uri": redirect_uri,
            "state": tenant_id,
            "scope": "pins:write"
        }
        return f"https://www.pinterest.com/oauth/?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token="pinterest_token")

    async def refresh_token(self, refresh_token: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token=refresh_token)

    async def publish_post(self, content: PostContent) -> PublishResult:
        if not content.image_url:
            return PublishResult(success=False, error="Pinterest requires image")
        return PublishResult(success=True, post_id="pin_12345", platform=Platform.PINTEREST)


SocialNetworkRegistry.register(Platform.PINTEREST, PinterestAdapter)
