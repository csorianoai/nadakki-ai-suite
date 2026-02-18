import os
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["debug"])

@router.get("/config")
def config():
    raw = os.getenv("LIVE_ENABLED")
    return {
        "live_enabled_raw": raw,
        "live_enabled_eval": str(raw).lower() in ("1", "true", "yes", "on"),
        "version": os.getenv("APP_VERSION", "unknown"),
    }
