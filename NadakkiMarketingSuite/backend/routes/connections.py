"""Social Connections API Routes."""
from fastapi import APIRouter, HTTPException, Header
from typing import Dict

router = APIRouter(prefix="/api/v1/connections", tags=["connections"])
_connections: Dict[str, Dict] = {}

def get_tenant_id(x_tenant_id: str = Header(...)) -> str:
    return x_tenant_id

@router.get("")
async def list_connections(x_tenant_id: str = Header(...)):
    conns = [c for c in _connections.values() if c.get("tenant_id") == x_tenant_id]
    return {"connections": conns, "total": len(conns)}

@router.get("/{platform}/auth-url")
async def get_auth_url(platform: str, redirect_uri: str, x_tenant_id: str = Header(...)):
    urls = {"facebook": f"https://facebook.com/oauth?redirect={redirect_uri}", "instagram": f"https://facebook.com/oauth?redirect={redirect_uri}", "tiktok": f"https://tiktok.com/oauth?redirect={redirect_uri}"}
    if platform not in urls:
        raise HTTPException(status_code=400, detail=f"Unknown: {platform}")
    return {"auth_url": urls[platform]}

@router.delete("/{connection_id}")
async def disconnect(connection_id: str, x_tenant_id: str = Header(...)):
    if connection_id in _connections:
        del _connections[connection_id]
        return {"message": "Disconnected"}
    raise HTTPException(status_code=404)
