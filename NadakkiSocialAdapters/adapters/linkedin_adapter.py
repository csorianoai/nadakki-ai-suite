"""LinkedIn Adapter."""
import os
from urllib.parse import urlencode
from .social_network_adapter import (
    SocialNetworkAdapter, SocialNetworkRegistry,
    Platform, PostContent, PublishResult, ConnectionResult
)


class LinkedInAdapter(SocialNetworkAdapter):
    """Adaptador para LinkedIn."""
    platforms = [Platform.LINKEDIN]

    def __init__(self, access_token=None):
        super().__init__(access_token)
        self.client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")

    def get_auth_url(self, tenant_id: str, redirect_uri: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": tenant_id,
            "scope": "w_member_social"
        }
        return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token="linkedin_token")

    async def refresh_token(self, refresh_token: str) -> ConnectionResult:
        return ConnectionResult(success=False, error="LinkedIn requires re-auth")

    async def publish_post(self, content: PostContent) -> PublishResult:
        return PublishResult(success=True, post_id="li_12345", platform=Platform.LINKEDIN)


SocialNetworkRegistry.register(Platform.LINKEDIN, LinkedInAdapter)
