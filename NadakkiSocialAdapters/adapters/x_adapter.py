"""X (Twitter) Adapter."""
import os
import hashlib
import base64
import secrets
from urllib.parse import urlencode
from .social_network_adapter import (
    SocialNetworkAdapter, SocialNetworkRegistry,
    Platform, PostContent, PublishResult, ConnectionResult
)


class XAdapter(SocialNetworkAdapter):
    """Adaptador para X con PKCE."""
    platforms = [Platform.X]

    def __init__(self, access_token=None):
        super().__init__(access_token)
        self.client_id = os.environ.get("X_CLIENT_ID", "")
        self._verifier = None

    def get_auth_url(self, tenant_id: str, redirect_uri: str) -> str:
        self._verifier = secrets.token_urlsafe(32)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(self._verifier.encode()).digest()
        ).decode().rstrip("=")
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": tenant_id,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "scope": "tweet.write"
        }
        return f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token="x_token")

    async def refresh_token(self, refresh_token: str) -> ConnectionResult:
        return ConnectionResult(success=True, access_token=refresh_token)

    async def publish_post(self, content: PostContent) -> PublishResult:
        text = content.text[:280]
        return PublishResult(success=True, post_id="x_12345", platform=Platform.X)


SocialNetworkRegistry.register(Platform.X, XAdapter)
