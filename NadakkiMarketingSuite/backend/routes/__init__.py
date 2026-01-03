"""API Routes - Day 4 Updated."""
from .campaigns import router as campaigns_router
from .connections import router as connections_router
from .scheduler import router as scheduler_router
from .metrics import router as metrics_router
from .tenants import router as tenants_router
from .ai_content import router as ai_content_router
from .analytics import router as analytics_router
from .export import router as export_router
from .notifications import router as notifications_router

__all__ = ["campaigns_router", "connections_router", "scheduler_router", "metrics_router", "tenants_router", "ai_content_router", "analytics_router", "export_router", "notifications_router"]
