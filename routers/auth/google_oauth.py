"""
Nadakki AI Suite - Google OAuth Router
Handles Google OAuth2 flow for Ads, Analytics, YouTube.
CSRF protection + encrypted token storage.
"""
import os
import json
import base64
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse

logger = logging.getLogger("GoogleOAuth")

router = APIRouter(prefix="/auth/google", tags=["OAuth - Google"])

_token_store = None


def _get_store():
    global _token_store
    if _token_store is None:
        from database.token_store import TokenStore
        _token_store = TokenStore()
    return _token_store


def _get_env():
    return {
        "client_id": os.getenv("NADAKKI_GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("NADAKKI_GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv(
            "GOOGLE_REDIRECT_URI",
            "https://nadakki-ai-suite.onrender.com/auth/google/callback",
        ),
        "frontend_url": os.getenv("FRONTEND_URL", "https://dashboard.nadakki.com"),
    }


GOOGLE_SCOPES = " ".join([
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
])


@router.get("/connect/{tenant_id}")
async def connect_google(tenant_id: str):
    """Initiate Google OAuth flow."""
    env = _get_env()
    if not env["client_id"] or not env["client_secret"]:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    store = _get_store()

    nonce = secrets.token_urlsafe(32)
    state_payload = json.dumps({"tenant_id": tenant_id, "nonce": nonce})
    state_key = base64.urlsafe_b64encode(state_payload.encode()).decode()

    await store.save_oauth_state(state_key, tenant_id, nonce, ttl_minutes=10)

    params = {
        "client_id": env["client_id"],
        "redirect_uri": env["redirect_uri"],
        "response_type": "code",
        "scope": GOOGLE_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": state_key,
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=auth_url, status_code=307)


@router.get("/callback")
async def google_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
):
    """Handle Google OAuth callback."""
    env = _get_env()
    store = _get_store()

    if error:
        logger.warning(f"Google OAuth error: {error}")
        return RedirectResponse(
            url=f"{env['frontend_url']}/marketing/social-connections?error=google&reason={error}",
            status_code=307,
        )

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    state_data = await store.validate_and_consume_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    tenant_id = state_data["tenant_id"]

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Exchange code for tokens
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": env["client_id"],
                    "client_secret": env["client_secret"],
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": env["redirect_uri"],
                },
            )

            if token_resp.status_code != 200:
                logger.error(f"Google token exchange failed: {token_resp.text}")
                return RedirectResponse(
                    url=f"{env['frontend_url']}/marketing/social-connections?error=google&reason=token_exchange",
                    status_code=307,
                )

            token_data = token_resp.json()
            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            expires_at = (
                datetime.utcnow() + timedelta(seconds=expires_in)
            ).isoformat()

            # Get user info
            user_resp = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_info = user_resp.json() if user_resp.status_code == 200 else {}

            # Try Google Ads accounts (graceful fail)
            ads_customer_ids = None
            try:
                ads_resp = await client.get(
                    "https://googleads.googleapis.com/v14/customers:listAccessibleCustomers",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if ads_resp.status_code == 200:
                    ads_data = ads_resp.json()
                    ads_customer_ids = ads_data.get("resourceNames", [])
            except Exception as e:
                logger.info(f"Google Ads discovery skipped: {e}")

            # Try Analytics properties (graceful fail)
            analytics_property_id = None
            try:
                analytics_resp = await client.get(
                    "https://analyticsadmin.googleapis.com/v1beta/accountSummaries",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if analytics_resp.status_code == 200:
                    summaries = analytics_resp.json().get("accountSummaries", [])
                    if summaries:
                        props = summaries[0].get("propertySummaries", [])
                        if props:
                            analytics_property_id = props[0].get("property")
            except Exception as e:
                logger.info(f"Analytics discovery skipped: {e}")

            # Try YouTube channel (graceful fail)
            youtube_channel_id = None
            try:
                yt_resp = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={"part": "id", "mine": "true"},
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if yt_resp.status_code == 200:
                    items = yt_resp.json().get("items", [])
                    if items:
                        youtube_channel_id = items[0]["id"]
            except Exception as e:
                logger.info(f"YouTube discovery skipped: {e}")

            # Save integration
            integration_data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user_info.get("id"),
                "user_name": user_info.get("name"),
                "user_email": user_info.get("email"),
                "ads_customer_ids": ads_customer_ids,
                "analytics_property_id": analytics_property_id,
                "youtube_channel_id": youtube_channel_id,
                "scopes": GOOGLE_SCOPES,
                "expires_at": expires_at,
            }

            await store.save_integration(tenant_id, "google", integration_data)

            await store.log_activity(
                tenant_id, "google", "connected",
                f"Email: {user_info.get('email')}, Ads: {bool(ads_customer_ids)}, "
                f"Analytics: {bool(analytics_property_id)}, YouTube: {bool(youtube_channel_id)}",
            )

            logger.info(f"Google connected for {tenant_id}: {user_info.get('email')}")

    except httpx.TimeoutException:
        logger.error("Google OAuth timeout")
        return RedirectResponse(
            url=f"{env['frontend_url']}/marketing/social-connections?error=google&reason=timeout",
            status_code=307,
        )
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        return RedirectResponse(
            url=f"{env['frontend_url']}/marketing/social-connections?error=google&reason=internal",
            status_code=307,
        )

    return RedirectResponse(
        url=f"{env['frontend_url']}/marketing/social-connections?success=google",
        status_code=307,
    )


@router.get("/status/{tenant_id}")
async def google_status(tenant_id: str):
    """Get Google connection status."""
    store = _get_store()
    integration = await store.get_integration(tenant_id, "google")

    if not integration:
        return {
            "connected": False,
            "user_email": None,
            "services": {
                "ads": {"connected": False},
                "analytics": {"connected": False},
                "youtube": {"connected": False},
            },
            "token_valid": False,
            "needs_refresh": False,
        }

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
        "user_email": integration.get("user_email"),
        "services": {
            "ads": {"connected": bool(integration.get("ads_customer_ids"))},
            "analytics": {"connected": bool(integration.get("analytics_property_id"))},
            "youtube": {"connected": bool(integration.get("youtube_channel_id"))},
        },
        "token_valid": token_valid,
        "needs_refresh": needs_refresh,
    }


@router.delete("/disconnect/{tenant_id}")
async def disconnect_google(tenant_id: str):
    """Disconnect Google integration."""
    store = _get_store()
    deleted = await store.delete_integration(tenant_id, "google")
    if deleted:
        await store.log_activity(tenant_id, "google", "disconnected", "")
    return {"disconnected": deleted, "tenant_id": tenant_id, "platform": "google"}


@router.post("/refresh/{tenant_id}")
async def refresh_google_token(tenant_id: str):
    """Manually refresh Google access token."""
    store = _get_store()
    from integrations.token_manager import TokenManager, TokenExpiredError

    manager = TokenManager(store)
    try:
        new_token = await manager._refresh_google(
            tenant_id, await store.get_integration(tenant_id, "google") or {}
        )
        return {"success": True, "token_refreshed": True}
    except TokenExpiredError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}
