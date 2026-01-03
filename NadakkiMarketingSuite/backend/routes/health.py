"""Health Check Routes - Kubernetes ready."""
from fastapi import APIRouter
from datetime import datetime
import sys
import platform

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    from ..services.scheduler_service import scheduler_service
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "scheduler": scheduler_service.is_running, "version": "5.1.0"}


@router.get("/health/detailed")
async def detailed_health():
    from ..services.scheduler_service import scheduler_service
    return {
        "status": "healthy",
        "components": {"api": "up", "scheduler": "up" if scheduler_service.is_running else "down"},
        "system": {"python": sys.version, "platform": platform.platform()},
        "version": "5.1.0"
    }


@router.get("/ready")
async def ready():
    return {"status": "ready"}


@router.get("/live")
async def live():
    return {"status": "alive"}
