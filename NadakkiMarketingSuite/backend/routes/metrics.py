"""Metrics API Routes."""
from fastapi import APIRouter, Header
from ..services.metrics_service import metrics_service

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

@router.get("")
async def get_metrics(x_tenant_id: str = Header(default="default")):
    return metrics_service.get_tenant_summary(x_tenant_id)

@router.get("/dashboard")
async def get_dashboard(x_tenant_id: str = Header(default="default")):
    return metrics_service.get_dashboard_data(x_tenant_id)
