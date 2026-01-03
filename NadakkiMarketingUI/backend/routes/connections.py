"""Social Connections API Routes."""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict

router = APIRouter(prefix="/api/v1/connections", tags=["connections"])
_connections: Dict[str, Dict] = {}


def get_tenant_id(x_tenant_id: str = Header(...)) -> str:
    return x_tenant_id


@router.get("")
async def list_connections(tenant_id: str = Depends(get_tenant_id)):
    conns = [c for c in _connections.values() if c.get("tenant_id") == tenant_id]
    return {"connections": conns, "total": len(conns)}


@router.get("/{platform}/auth-url")
async def get_auth_url(platform: str, redirect_uri: str, tenant_id: str = Depends(get_tenant_id)):
    urls = {
        "facebook": f"https://facebook.com/oauth?redirect={redirect_uri}&state={tenant_id}",
        "instagram": f"https://facebook.com/oauth?redirect={redirect_uri}&state={tenant_id}",
        "tiktok": f"https://tiktok.com/oauth?redirect={redirect_uri}&state={tenant_id}",
        "x": f"https://twitter.com/oauth2?redirect={redirect_uri}&state={tenant_id}",
        "linkedin": f"https://linkedin.com/oauth?redirect={redirect_uri}&state={tenant_id}",
    }
    if platform not in urls:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")
    return {"auth_url": urls[platform], "platform": platform}


@router.post("/callback")
async def oauth_callback(code: str, state: str, platform: str):
    connection = {"id": f"conn_{platform}_{state[:8]}", "tenant_id": state, "platform": platform, "page_name": f"Demo {platform.title()} Page", "status": "active"}
    _connections[connection["id"]] = connection
    return connection


@router.delete("/{connection_id}")
async def disconnect(connection_id: str, tenant_id: str = Depends(get_tenant_id)):
    if connection_id in _connections:
        del _connections[connection_id]
        return {"message": "Disconnected"}
    raise HTTPException(status_code=404, detail="Connection not found")
