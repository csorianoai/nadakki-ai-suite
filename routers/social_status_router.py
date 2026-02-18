"""
Nadakki AI Suite - Social Status Router
Returns connection status for all social platforms per tenant.
Checks TokenStore (BD) first, env vars as fallback.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Header

logger = logging.getLogger("SocialStatus")

router = APIRouter(prefix="/api/social", tags=["Social Status"])

_token_store = None


def _get_store():
    global _token_store
    if _token_store is None:
        try:
            from database.token_store import TokenStore
            _token_store = TokenStore()
        except Exception as e:
            logger.warning(f"TokenStore unavailable: {e}")
    return _token_store


@router.get("/status/{tenant_id}")
async def get_social_status(tenant_id: str):
    """Get connection status for all social platforms."""
    store = _get_store()

    meta_status = await _get_meta_status(store, tenant_id)
    google_status = await _get_google_status(store, tenant_id)

    return {
        "tenant_id": tenant_id,
        "platforms": {
            "meta": meta_status,
            "google": google_status,
            "tiktok": {"connected": False, "status": "pending"},
            "linkedin": {"connected": False, "status": "pending"},
            "x": {"connected": False, "status": "pending"},
            "pinterest": {"connected": False, "status": "pending"},
            "youtube": {"connected": False, "status": "pending"},
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


async def _get_meta_status(store, tenant_id: str) -> dict:
    """Check Meta connection: BD first, env fallback."""
    # Try TokenStore first
    if store:
        try:
            integration = await store.get_integration(tenant_id, "meta")
            if integration:
                expires_at = integration.get("expires_at")
                token_valid = True
                needs_refresh = False

                if expires_at:
                    try:
                        exp = datetime.fromisoformat(expires_at)
                        now = datetime.utcnow()
                        token_valid = now < exp
                        needs_refresh = (exp - now) < timedelta(days=7)
                    except (ValueError, TypeError):
                        pass

                return {
                    "connected": True,
                    "method": "oauth",
                    "page_name": integration.get("page_name"),
                    "page_id": integration.get("page_id"),
                    "ig_connected": bool(integration.get("ig_account_id")),
                    "token_valid": token_valid,
                    "token_expires_at": expires_at,
                    "needs_refresh": needs_refresh,
                }
        except Exception as e:
            logger.warning(f"Error checking Meta integration: {e}")

    # Env fallback
    env_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    if env_token:
        return {
            "connected": True,
            "method": "legacy_env",
            "page_name": None,
            "page_id": os.getenv("FACEBOOK_PAGE_ID"),
            "ig_connected": False,
            "token_valid": True,
            "token_expires_at": None,
            "needs_refresh": False,
        }

    return {
        "connected": False,
        "method": None,
        "page_name": None,
        "page_id": None,
        "ig_connected": False,
        "token_valid": False,
        "token_expires_at": None,
        "needs_refresh": False,
    }


async def _get_google_status(store, tenant_id: str) -> dict:
    """Check Google connection: BD first, env fallback."""
    if store:
        try:
            integration = await store.get_integration(tenant_id, "google")
            if integration:
                expires_at = integration.get("expires_at")
                token_valid = True
                needs_refresh = False

                if expires_at:
                    try:
                        exp = datetime.fromisoformat(expires_at)
                        now = datetime.utcnow()
                        token_valid = now < exp
                        needs_refresh = (exp - now) < timedelta(minutes=30)
                    except (ValueError, TypeError):
                        pass

                return {
                    "connected": True,
                    "method": "oauth",
                    "user_email": integration.get("user_email"),
                    "services": {
                        "ads": {"connected": bool(integration.get("ads_customer_ids"))},
                        "analytics": {"connected": bool(integration.get("analytics_property_id"))},
                        "youtube": {"connected": bool(integration.get("youtube_channel_id"))},
                    },
                    "token_valid": token_valid,
                    "needs_refresh": needs_refresh,
                }
        except Exception as e:
            logger.warning(f"Error checking Google integration: {e}")

    return {
        "connected": False,
        "method": None,
        "user_email": None,
        "services": {
            "ads": {"connected": False},
            "analytics": {"connected": False},
            "youtube": {"connected": False},
        },
        "token_valid": False,
        "needs_refresh": False,
    }


# ---------------------------------------------------------------------------
# GET /api/social/connections — simplified connection status via X-Tenant-ID
# ---------------------------------------------------------------------------
@router.get("/connections")
async def get_social_connections(
    x_tenant_id: Optional[str] = Header(None),
):
    """
    Returns social platform connection status for the tenant.
    Reads X-Tenant-ID header. Always returns 200.
    """
    tenant_id = x_tenant_id or "default"
    store = _get_store()

    meta_connected = False
    meta_page_name = None
    meta_expires = None
    google_connected = False
    google_email = None

    if store:
        try:
            meta_int = await store.get_integration(tenant_id, "meta")
            if meta_int:
                meta_connected = True
                meta_page_name = meta_int.get("page_name")
                meta_expires = meta_int.get("expires_at")
        except Exception as e:
            logger.warning(f"Error reading Meta integration: {e}")

        try:
            google_int = await store.get_integration(tenant_id, "google")
            if google_int:
                google_connected = True
                google_email = google_int.get("user_email")
        except Exception as e:
            logger.warning(f"Error reading Google integration: {e}")

    # Env fallback for meta
    if not meta_connected and os.getenv("FACEBOOK_ACCESS_TOKEN"):
        meta_connected = True
        meta_page_name = None

    return {
        "tenant_id": tenant_id,
        "platforms": [
            {
                "name": "meta",
                "connected": meta_connected,
                "page_name": meta_page_name,
                "expires": meta_expires,
            },
            {
                "name": "google",
                "connected": google_connected,
                "email": google_email,
            },
        ],
    }
