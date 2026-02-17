"""
Nadakki AI Suite - Token Manager
Handles token retrieval, validation, and automatic refresh.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

logger = logging.getLogger("TokenManager")


class TokenExpiredError(Exception):
    """Raised when a token has expired and cannot be auto-refreshed."""
    pass


class TokenManager:
    """Manages OAuth tokens with automatic refresh for supported platforms."""

    def __init__(self, token_store):
        self.store = token_store

    async def get_valid_token(self, tenant_id: str, platform: str) -> str:
        """Get a valid access token, refreshing if needed.

        For Google: auto-refresh when token expires in <5 min.
        For Meta: raise TokenExpiredError (user must reconnect).
        """
        integration = await self.store.get_integration(tenant_id, platform)
        if not integration:
            raise TokenExpiredError(
                f"No integration found for {tenant_id}/{platform}"
            )

        access_token = integration.get("access_token")
        if not access_token:
            raise TokenExpiredError(f"No access token for {tenant_id}/{platform}")

        expires_at_str = integration.get("expires_at")
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                now = datetime.utcnow()

                if now > expires_at:
                    # Token already expired
                    return await self._handle_expired(
                        tenant_id, platform, integration
                    )

                if expires_at - now < timedelta(minutes=5):
                    # About to expire
                    if platform == "google":
                        return await self._refresh_google(
                            tenant_id, integration
                        )
                    # Meta tokens can't be auto-refreshed with refresh_token
                    # They need user re-auth once the long-lived token expires

            except (ValueError, TypeError):
                pass

        return access_token

    async def _handle_expired(
        self, tenant_id: str, platform: str, integration: dict
    ) -> str:
        """Handle an expired token."""
        if platform == "google" and integration.get("refresh_token"):
            return await self._refresh_google(tenant_id, integration)
        raise TokenExpiredError(
            f"Token expired for {tenant_id}/{platform}. User must reconnect."
        )

    async def _refresh_google(self, tenant_id: str, integration: dict) -> str:
        """Refresh a Google OAuth token using the refresh_token."""
        refresh_token = integration.get("refresh_token")
        if not refresh_token:
            raise TokenExpiredError(
                "No refresh token available for Google. User must reconnect."
            )

        client_id = os.getenv("NADAKKI_GOOGLE_CLIENT_ID")
        client_secret = os.getenv("NADAKKI_GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise TokenExpiredError("Google OAuth credentials not configured")

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                    },
                )

                if resp.status_code != 200:
                    raise TokenExpiredError(
                        f"Google token refresh failed: {resp.status_code}"
                    )

                data = resp.json()
                new_access_token = data["access_token"]
                expires_in = data.get("expires_in", 3600)
                new_expires_at = (
                    datetime.utcnow() + timedelta(seconds=expires_in)
                ).isoformat()

                # Save updated token (preserve refresh_token)
                await self.store.save_integration(
                    tenant_id,
                    "google",
                    {
                        "access_token": new_access_token,
                        "refresh_token": refresh_token,
                        "expires_at": new_expires_at,
                        "user_id": integration.get("user_id"),
                        "user_name": integration.get("user_name"),
                        "user_email": integration.get("user_email"),
                        "ads_customer_ids": integration.get("ads_customer_ids"),
                        "analytics_property_id": integration.get("analytics_property_id"),
                        "youtube_channel_id": integration.get("youtube_channel_id"),
                        "scopes": integration.get("scopes"),
                    },
                )

                await self.store.log_activity(
                    tenant_id, "google", "token_refreshed", "Auto-refresh successful"
                )

                logger.info(f"Google token refreshed for {tenant_id}")
                return new_access_token

        except httpx.TimeoutException:
            raise TokenExpiredError("Google token refresh timed out")
        except KeyError as e:
            raise TokenExpiredError(f"Invalid refresh response: missing {e}")
