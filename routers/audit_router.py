"""
Audit Router — GET /api/v1/audit/logs
Query execution audit logs by tenant, agent, limit.
"""

from fastapi import APIRouter, Query
from services.audit_logger import read_logs_async

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


@router.get("/logs")
async def get_audit_logs(
    tenant_id: str = Query(None, description="Filter by tenant"),
    agent_id: str = Query(None, description="Filter by agent"),
    limit: int = Query(50, ge=1, le=500, description="Max entries to return"),
):
    entries = await read_logs_async(tenant_id=tenant_id, agent_id=agent_id, limit=limit)
    return {
        "success": True,
        "count": len(entries),
        "logs": entries,
    }
