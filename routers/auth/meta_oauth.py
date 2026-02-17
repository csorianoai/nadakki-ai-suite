"""
Nadakki AI Suite - Meta OAuth Router
Handles Facebook/Instagram OAuth2 flow with CSRF protection.
Tokens encrypted with Fernet before storage.
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

logger = logging.getLogger("MetaOAuth")

router = APIRouter(prefix="/auth/meta", tags=["OAuth - Meta"])

# Lazy-initialized token store
_token_store = None


def _get_store():
    global _token_store
    if _token_store is None:
        from database.token_store import TokenStore
        _token_store = TokenStore()
    return _token_store


def _get_env():
    return {
        "app_id": os.getenv("NADAKKI_META_APP_ID", ""),
        "app_secret": os.getenv("NADAKKI_META_APP_SECRET", ""),
        "redirect_uri": os.getenv(
            "META_REDIRECT_URI",
            "https://nadakki-ai-suite.onrender.com/auth/meta/callback",
        ),
        "frontend_url": os.getenv("FRONTEND_URL", "https://dashboard.nadakki.com"),
        "preferred_page_id": os.getenv("FACEBOOK_PAGE_ID", "59633914943"),
    }


META_SCOPES = (
    "pages_manage_posts,pages_read_engagement,pages_read_user_content,"
    "instagram_basic,instagram_content_publish,"
    "ads_management,ads_read,business_management"
)


@router.get("/connect/{tenant_id}")
async def connect_meta(tenant_id: str):
    """Initiate Meta OAuth flow."""
    env = _get_env()
    if not env["app_id"] or not env["app_secret"]:
        raise HTTPException(status_code=500, detail="Meta OAuth not configured")

    store = _get_store()

    # Generate CSRF state
    nonce = secrets.token_urlsafe(32)
    state_payload = json.dumps({"tenant_id": tenant_id, "nonce": nonce})
    state_key = base64.urlsafe_b64encode(state_payload.encode()).decode()

    await store.save_oauth_state(state_key, tenant_id, nonce, ttl_minutes=10)

    params = {
        "client_id": env["app_id"],
        "redirect_uri": env["redirect_uri"],
        "scope": META_SCOPES,
        "state": state_key,
        "response_type": "code",
    }

    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
    return RedirectResponse(url=auth_url, status_code=307)


@router.get("/callback")
async def meta_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """Handle Meta OAuth callback."""
    env = _get_env()
    store = _get_store()

    if error:
        logger.warning(f"Meta OAuth error: {error} - {error_description}")
        return RedirectResponse(
            url=f"{env['frontend_url']}/marketing/social-connections?error=meta&reason={error}",
            status_code=307,
        )

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    # Validate CSRF state
    state_data = await store.validate_and_consume_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    tenant_id = state_data["tenant_id"]

    try:
        # Exchange code for short-lived token
        async with httpx.AsyncClient(timeout=15) as client:
            token_resp = await client.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": env["app_id"],
                    "client_secret": env["app_secret"],
                    "redirect_uri": env["redirect_uri"],
                    "code": code,
                },
            )

            if token_resp.status_code != 200:
                logger.error(f"Token exchange failed: {token_resp.text}")
                return RedirectResponse(
                    url=f"{env['frontend_url']}/marketing/social-connections?error=meta&reason=token_exchange",
                    status_code=307,
                )

            token_data = token_resp.json()
            short_token = token_data["access_token"]

            # Convert to long-lived token (60 days)
            ll_resp = await client.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": env["app_id"],
                    "client_secret": env["app_secret"],
                    "fb_exchange_token": short_token,
                },
            )

            if ll_resp.status_code == 200:
                ll_data = ll_resp.json()
                access_token = ll_data["access_token"]
                expires_in = ll_data.get("expires_in", 5184000)  # 60 days default
            else:
                access_token = short_token
                expires_in = token_data.get("expires_in", 3600)

            expires_at = (
                datetime.utcnow() + timedelta(seconds=expires_in)
            ).isoformat()

            # Get user info
            me_resp = await client.get(
                "https://graph.facebook.com/v18.0/me",
                params={"access_token": access_token, "fields": "id,name,email"},
            )
            user_info = me_resp.json() if me_resp.status_code == 200 else {}

            # Get pages
            pages_resp = await client.get(
                "https://graph.facebook.com/v18.0/me/accounts",
                params={"access_token": access_token},
            )

            page_token = access_token
            page_id = None
            page_name = None
            ig_account_id = None

            if pages_resp.status_code == 200:
                pages = pages_resp.json().get("data", [])
                preferred = env["preferred_page_id"]

                # Prefer the configured page
                selected = None
                for p in pages:
                    if p.get("id") == preferred:
                        selected = p
                        break
                if not selected and pages:
                    selected = pages[0]

                if selected:
                    page_token = selected.get("access_token", access_token)
                    page_id = selected["id"]
                    page_name = selected.get("name")

                    # Try to get IG business account
                    ig_resp = await client.get(
                        f"https://graph.facebook.com/v18.0/{page_id}",
                        params={
                            "fields": "instagram_business_account",
                            "access_token": page_token,
                        },
                    )
                    if ig_resp.status_code == 200:
                        ig_data = ig_resp.json()
                        ig_biz = ig_data.get("instagram_business_account")
                        if ig_biz:
                            ig_account_id = ig_biz.get("id")

            # Save encrypted integration
            await store.save_integration(
                tenant_id,
                "meta",
                {
                    "access_token": page_token,
                    "user_id": user_info.get("id"),
                    "user_name": user_info.get("name"),
                    "user_email": user_info.get("email"),
                    "page_id": page_id,
                    "page_name": page_name,
                    "ig_account_id": ig_account_id,
                    "scopes": META_SCOPES,
                    "expires_at": expires_at,
                },
            )

            await store.log_activity(
                tenant_id, "meta", "connected",
                f"Page: {page_name} ({page_id}), IG: {ig_account_id or 'none'}",
            )

            logger.info(
                f"Meta connected for {tenant_id}: page={page_id}, ig={ig_account_id}"
            )

    except httpx.TimeoutException:
        logger.error("Meta OAuth timeout")
        return RedirectResponse(
            url=f"{env['frontend_url']}/marketing/social-connections?error=meta&reason=timeout",
            status_code=307,
        )
    except Exception as e:
        logger.error(f"Meta OAuth error: {e}")
        return RedirectResponse(
            url=f"{env['frontend_url']}/marketing/social-connections?error=meta&reason=internal",
            status_code=307,
        )

    return RedirectResponse(
        url=f"{env['frontend_url']}/marketing/social-connections?success=meta",
        status_code=307,
    )


@router.get("/status/{tenant_id}")
async def meta_status(tenant_id: str):
    """Get Meta connection status for a tenant."""
    store = _get_store()
    integration = await store.get_integration(tenant_id, "meta")

    if not integration:
        return {
            "connected": False,
            "page_name": None,
            "page_id": None,
            "ig_connected": False,
            "expires_at": None,
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
            needs_refresh = (exp - now) < timedelta(days=7)
        except (ValueError, TypeError):
            pass

    return {
        "connected": True,
        "page_name": integration.get("page_name"),
        "page_id": integration.get("page_id"),
        "ig_connected": bool(integration.get("ig_account_id")),
        "expires_at": expires_at,
        "token_valid": token_valid,
        "needs_refresh": needs_refresh,
    }


@router.delete("/disconnect/{tenant_id}")
async def disconnect_meta(tenant_id: str):
    """Disconnect Meta integration."""
    store = _get_store()
    deleted = await store.delete_integration(tenant_id, "meta")
    if deleted:
        await store.log_activity(tenant_id, "meta", "disconnected", "")
    return {"disconnected": deleted, "tenant_id": tenant_id, "platform": "meta"}
