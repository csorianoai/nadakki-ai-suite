import os
import logging
import time as _time_mod

from fastapi import APIRouter
from sqlalchemy import text

logger = logging.getLogger("nadakki.config")

router = APIRouter(prefix="/api/v1", tags=["debug"])

_CONFIG_ROUTER_START = _time_mod.time()


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

            # Gates summary
            gates_summary = []
            if "gates" in tables:
                try:
                    result = await session.execute(
                        text("SELECT gate_id, name, status FROM gates ORDER BY gate_id")
                    )
                    gates_summary = [
                        {"gate_id": r[0], "name": r[1], "status": r[2]}
                        for r in result.fetchall()
                    ]
                except Exception:
                    gates_summary = []

            return {
                "db": "connected",
                "provider": "supabase",
                "tenants": tenant_count,
                "default_tenant": default_tenant,
                "tables": tables,
                "rls_policies": rls_policies,
                "gates": gates_summary,
            }
    except Exception as e:
        logger.warning("DB status check failed: %s", e)
        return {"db": "disconnected", "error": str(e)}


@router.get("/db/audit-events")
async def db_audit_events():
    """Return recent audit_events rows (last 20)."""
    try:
        from services.db import db_available, get_session

        if not db_available():
            return {"error": "DATABASE_URL not set"}

        async with get_session() as session:
            result = await session.execute(text("SELECT count(*) FROM audit_events"))
            total = result.scalar()

            result = await session.execute(
                text(
                    "SELECT id, tenant_id, action, endpoint, method, status_code, timestamp "
                    "FROM audit_events ORDER BY timestamp DESC LIMIT 20"
                )
            )
            rows = [
                {
                    "id": str(r[0]),
                    "tenant_id": str(r[1]) if r[1] else None,
                    "action": r[2],
                    "endpoint": r[3],
                    "method": r[4],
                    "status_code": r[5],
                    "timestamp": r[6].isoformat() if r[6] else None,
                }
                for r in result.fetchall()
            ]
            return {"total": total, "recent": rows}
    except Exception as e:
        return {"error": str(e)}


@router.get("/system/info")
async def system_info():
    """System-wide information: version, uptime, db, tenants, agents, executions."""
    uptime_seconds = round(_time_mod.time() - _CONFIG_ROUTER_START)

    info = {
        "version": "5.4.4",
        "uptime_seconds": uptime_seconds,
        "db_provider": "none",
        "total_tenants": 0,
        "total_agents": 0,
        "total_executions": 0,
    }

    try:
        from services.db import db_available, get_session
        if db_available():
            info["db_provider"] = "supabase"
            async with get_session() as session:
                result = await session.execute(text("SELECT count(*) FROM tenants"))
                info["total_tenants"] = result.scalar()

                result = await session.execute(text("SELECT count(*) FROM agent_executions"))
                info["total_executions"] = result.scalar()
    except Exception:
        pass

    try:
        from main import ALL_AGENTS
        info["total_agents"] = len(ALL_AGENTS)
    except Exception:
        pass

    return info
