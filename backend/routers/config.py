import os
import logging

from fastapi import APIRouter
from sqlalchemy import text

logger = logging.getLogger("nadakki.config")

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


@router.get("/db/status")
async def db_status():
    """Check PostgreSQL connection, list tables, show default tenant and RLS."""
    try:
        from services.db import db_available, get_session

        if not db_available():
            return {"db": "disconnected", "error": "DATABASE_URL not set or engine not initialized"}

        async with get_session() as session:
            # List tables
            result = await session.execute(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = 'public' ORDER BY tablename"
                )
            )
            tables = [row[0] for row in result.fetchall()]

            # Tenant info
            tenant_count = 0
            default_tenant = None
            if "tenants" in tables:
                result = await session.execute(text("SELECT count(*) FROM tenants"))
                tenant_count = result.scalar()

                result = await session.execute(
                    text("SELECT id, name, slug, plan FROM tenants WHERE slug = 'credicefi'")
                )
                row = result.first()
                if row:
                    default_tenant = {"id": str(row[0]), "name": row[1], "slug": row[2], "plan": row[3]}

            # RLS policies (lightweight query)
            rls_policies = []
            try:
                result = await session.execute(
                    text("SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public'")
                )
                rls_policies = [{"table": row[0], "policy": row[1]} for row in result.fetchall()]
            except Exception:
                rls_policies = []

            return {
                "db": "connected",
                "provider": "supabase",
                "tenants": tenant_count,
                "default_tenant": default_tenant,
                "tables": tables,
                "rls_policies": rls_policies,
            }
    except Exception as e:
        logger.warning("DB status check failed: %s", e)
        return {"db": "disconnected", "error": str(e)}
