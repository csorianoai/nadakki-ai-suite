"""Notifications API Routes."""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ..services.notification_service import notification_service

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class RegisterWebhookRequest(BaseModel):
    url: str
    events: List[str]


@router.get("")
async def list_notifications(x_tenant_id: str = Header(...), unread_only: bool = Query(False)) -> Dict[str, Any]:
    notifications = notification_service.get_notifications(x_tenant_id, unread_only=unread_only)
    return {"notifications": [n.to_dict() for n in notifications], "total": len(notifications), "unread_count": len([n for n in notifications if not n.read])}


@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: str) -> Dict[str, Any]:
    if notification_service.mark_as_read(notification_id): return {"message": "Marked as read"}
    raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/read-all")
async def mark_all_as_read(x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    count = notification_service.mark_all_as_read(x_tenant_id)
    return {"message": f"Marked {count} notifications as read"}


@router.post("/webhooks")
async def register_webhook(data: RegisterWebhookRequest, x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    webhook = notification_service.register_webhook(tenant_id=x_tenant_id, url=data.url, events=data.events)
    return {"id": webhook.id, "url": webhook.url, "events": webhook.events, "active": webhook.active}


@router.get("/webhooks")
async def list_webhooks(x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    webhooks = notification_service.get_webhooks(x_tenant_id)
    return {"webhooks": [{"id": w.id, "url": w.url, "events": w.events, "active": w.active} for w in webhooks], "total": len(webhooks)}
