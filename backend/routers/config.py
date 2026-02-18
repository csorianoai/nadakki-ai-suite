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


@router.get("/social/status")
def social_status():
    """Returns dry_run / live status flags. Always 200."""
    return {
        "status": "dry_run",
        "live_enabled": os.getenv("LIVE_ENABLED", "false").lower() == "true",
        "meta_live": os.getenv("META_POST_LIVE", "false").lower() == "true",
        "sendgrid_live": os.getenv("SENDGRID_LIVE", "false").lower() == "true",
    }
