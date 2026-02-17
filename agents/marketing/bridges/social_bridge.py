"""
Nadakki AI Suite - Social Bridge
Publishes content to social platforms with DRY_RUN by default.
Uses TokenManager when available, falls back to env vars.
"""
import os
import logging
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger("SocialBridge")


class SocialBridge:
    """Bridge between marketing agents and social platforms."""

    def __init__(self, tenant_id: str, token_manager=None):
        self.tenant_id = tenant_id
        self.token_manager = token_manager
        self.page_id = os.getenv("FACEBOOK_PAGE_ID", "59633914943")

    async def _get_token(self, platform: str) -> Optional[str]:
        """Get token: TokenManager first, env fallback."""
        if self.token_manager:
            try:
                return await self.token_manager.get_valid_token(self.tenant_id, platform)
            except Exception as e:
                logger.warning(f"TokenManager failed for {platform}: {e}")
        return os.getenv("FACEBOOK_ACCESS_TOKEN")

    async def publish(
        self,
        platform: str,
        content: str,
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Publish content to a social platform.

        DRY_RUN by default unless META_POST_LIVE=true.
        """
        if os.getenv("META_POST_LIVE", "false").lower() != "true":
            return {
                "dry_run": True,
                "platform": platform,
                "would_publish": content[:100],
                "tenant_id": self.tenant_id,
            }

        if platform in ("meta", "facebook"):
            return await self._publish_meta(content, media_url)

        return {
            "success": False,
            "platform": platform,
            "error": f"Platform {platform} not yet supported for live publishing",
        }

    async def _publish_meta(
        self, content: str, media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Publish to Meta (Facebook page)."""
        token = await self._get_token("meta")
        if not token:
            return {"success": False, "error": "No Meta access token available"}

        url = f"https://graph.facebook.com/v18.0/{self.page_id}/feed"
        payload: Dict[str, Any] = {
            "message": content,
            "access_token": token,
        }
        if media_url:
            payload["link"] = media_url

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, data=payload)
                data = resp.json()
                if resp.status_code == 200 and "id" in data:
                    return {
                        "success": True,
                        "platform": "meta",
                        "post_id": data["id"],
                        "page_id": self.page_id,
                    }
                return {
                    "success": False,
                    "platform": "meta",
                    "error": data.get("error", {}).get("message", str(data)),
                    "status_code": resp.status_code,
                }
        except httpx.TimeoutException:
            return {"success": False, "platform": "meta", "error": "Request timed out"}
        except Exception as e:
            return {"success": False, "platform": "meta", "error": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """Return current bridge status per platform."""
        meta_token = await self._get_token("meta")
        return {
            "tenant_id": self.tenant_id,
            "platforms": {
                "meta": {
                    "configured": bool(meta_token),
                    "page_id": self.page_id,
                    "live_mode": os.getenv("META_POST_LIVE", "false").lower() == "true",
                },
            },
        }
