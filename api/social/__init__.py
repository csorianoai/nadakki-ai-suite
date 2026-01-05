"""
NADAKKI Social Connections API
Endpoints para conectar y gestionar redes sociales via OAuth
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional, Dict, Any
from datetime import datetime
import os
import json
import logging

logger = logging.getLogger("SocialAPI")
router = APIRouter(prefix="/api/social", tags=["Social Connections"])

# Almacenamiento en memoria (en produccion usar base de datos)
SOCIAL_CONNECTIONS: Dict[str, Dict[str, Any]] = {}

# Configuracion de OAuth por plataforma
OAUTH_CONFIG = {
    "facebook": {
        "client_id": os.getenv("FACEBOOK_CLIENT_ID", ""),
        "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET", ""),
        "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "scope": "pages_show_list,pages_read_engagement,pages_manage_posts,instagram_basic,instagram_content_publish"
    },
    "instagram": {
        "client_id": os.getenv("INSTAGRAM_CLIENT_ID", ""),
        "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET", ""),
        "auth_url": "https://api.instagram.com/oauth/authorize",
        "token_url": "https://api.instagram.com/oauth/access_token",
        "scope": "user_profile,user_media"
    },
    "twitter": {
        "client_id": os.getenv("TWITTER_CLIENT_ID", ""),
        "client_secret": os.getenv("TWITTER_CLIENT_SECRET", ""),
        "auth_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "scope": "tweet.read tweet.write users.read offline.access"
    },
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", ""),
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scope": "r_liteprofile r_emailaddress w_member_social"
    },
    "tiktok": {
        "client_id": os.getenv("TIKTOK_CLIENT_ID", ""),
        "client_secret": os.getenv("TIKTOK_CLIENT_SECRET", ""),
        "auth_url": "https://www.tiktok.com/auth/authorize",
        "token_url": "https://open-api.tiktok.com/oauth/access_token",
        "scope": "user.info.basic,video.list,video.upload"
    },
    "youtube": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": "https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.upload"
    }
}


@router.get("/connections")
async def get_connections(tenant_id: str = Query("default")):
    """Obtiene las conexiones sociales de un tenant"""
    tenant_connections = SOCIAL_CONNECTIONS.get(tenant_id, {})
    
    connections = []
    for platform, config in OAUTH_CONFIG.items():
        conn_data = tenant_connections.get(platform, {})
        connections.append({
            "platform": platform,
            "connected": conn_data.get("connected", False),
            "account": conn_data.get("account"),
            "accountId": conn_data.get("account_id"),
            "followers": conn_data.get("followers"),
            "lastSync": conn_data.get("last_sync")
        })
    
    return {"connections": connections, "tenant_id": tenant_id}


@router.get("/{platform}/auth-url")
async def get_auth_url(
    platform: str,
    tenant_id: str = Query("default"),
    redirect_uri: str = Query("")
):
    """Genera la URL de autorizacion OAuth para una plataforma"""
    if platform not in OAUTH_CONFIG:
        raise HTTPException(status_code=400, detail=f"Plataforma no soportada: {platform}")
    
    config = OAUTH_CONFIG[platform]
    
    if not config["client_id"]:
        return JSONResponse(
            status_code=400,
            content={
                "error": "not_configured",
                "message": f"OAuth para {platform} no esta configurado. Configura {platform.upper()}_CLIENT_ID en las variables de entorno.",
                "docs": get_docs_url(platform)
            }
        )
    
    # Construir URL de OAuth
    state = f"{tenant_id}|{platform}|{redirect_uri}"
    
    params = {
        "client_id": config["client_id"],
        "redirect_uri": redirect_uri or f"https://nadakki-ai-suite.onrender.com/api/social/{platform}/callback",
        "scope": config["scope"],
        "response_type": "code",
        "state": state
    }
    
    # Twitter usa PKCE
    if platform == "twitter":
        params["code_challenge"] = "challenge"
        params["code_challenge_method"] = "plain"
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"{config['auth_url']}?{query_string}"
    
    return {"auth_url": auth_url, "platform": platform}


@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str = Query(None),
    state: str = Query(""),
    error: str = Query(None)
):
    """Callback de OAuth - recibe el codigo de autorizacion"""
    if error:
        return RedirectResponse(url=f"/social/connections?error={error}")
    
    if not code:
        return RedirectResponse(url="/social/connections?error=no_code")
    
    # Parsear state
    parts = state.split("|")
    tenant_id = parts[0] if len(parts) > 0 else "default"
    redirect_uri = parts[2] if len(parts) > 2 else "/social/connections"
    
    # En produccion: intercambiar code por access_token
    # Por ahora, simulamos una conexion exitosa
    if tenant_id not in SOCIAL_CONNECTIONS:
        SOCIAL_CONNECTIONS[tenant_id] = {}
    
    SOCIAL_CONNECTIONS[tenant_id][platform] = {
        "connected": True,
        "account": f"@{tenant_id}_{platform}",
        "account_id": f"{platform}_123456",
        "followers": "1.2K",
        "last_sync": datetime.now().isoformat(),
        "access_token": "simulated_token"
    }
    
    logger.info(f"Connected {platform} for tenant {tenant_id}")
    
    # Redirigir de vuelta al dashboard
    return RedirectResponse(url=redirect_uri + "?connected=" + platform)


@router.post("/{platform}/disconnect")
async def disconnect_platform(
    platform: str,
    tenant_id: str = Query("default")
):
    """Desconecta una plataforma social"""
    if tenant_id in SOCIAL_CONNECTIONS and platform in SOCIAL_CONNECTIONS[tenant_id]:
        del SOCIAL_CONNECTIONS[tenant_id][platform]
        logger.info(f"Disconnected {platform} for tenant {tenant_id}")
    
    return {"success": True, "platform": platform, "tenant_id": tenant_id}


@router.post("/{platform}/sync")
async def sync_platform(
    platform: str,
    tenant_id: str = Query("default")
):
    """Sincroniza datos de una plataforma (seguidores, metricas, etc)"""
    if tenant_id not in SOCIAL_CONNECTIONS or platform not in SOCIAL_CONNECTIONS[tenant_id]:
        raise HTTPException(status_code=404, detail=f"{platform} no esta conectado")
    
    # Actualizar last_sync
    SOCIAL_CONNECTIONS[tenant_id][platform]["last_sync"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "platform": platform,
        "synced_at": SOCIAL_CONNECTIONS[tenant_id][platform]["last_sync"]
    }


def get_docs_url(platform: str) -> str:
    """Retorna URL de documentacion para configurar OAuth"""
    docs = {
        "facebook": "https://developers.facebook.com/docs/facebook-login/",
        "instagram": "https://developers.facebook.com/docs/instagram-basic-display-api/",
        "twitter": "https://developer.twitter.com/en/docs/authentication/oauth-2-0",
        "linkedin": "https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow",
        "tiktok": "https://developers.tiktok.com/doc/login-kit-web/",
        "youtube": "https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps"
    }
    return docs.get(platform, "")


# Crear archivo __init__.py
def get_router():
    return router
