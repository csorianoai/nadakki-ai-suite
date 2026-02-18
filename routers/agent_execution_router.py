"""
Agent Execution Router - POST /api/v1/agents/{agent_id}/execute
Carga y ejecuta agentes del catalogo de forma segura con dry_run por defecto.
Includes audit logging with trace_id.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, Field

from services.agent_runner import execute_agent, AgentLoadError
from services.audit_logger import generate_trace_id, write_log

logger = logging.getLogger("AgentExecution")

router = APIRouter(prefix="/api/v1/agents", tags=["Agent Execution"])


class ExecuteRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = Field(True, description="Modo seguro, no ejecuta acciones reales")
    auto_publish: bool = Field(False, description="Publicar resultado automaticamente")
    auto_email: bool = Field(False, description="Enviar resultado por email")
    tenant_id: str = Field("default", description="ID del tenant")


def _get_all_agents() -> Dict[str, dict]:
    """Importa ALL_AGENTS desde main (lazy para evitar circular)."""
    from main import ALL_AGENTS
    return ALL_AGENTS


@router.post("/{agent_id}/execute")
async def execute_agent_endpoint(
    agent_id: str,
    body: ExecuteRequest,
    x_tenant_id: Optional[str] = Header(None),
    x_trace_id: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
):
    """Ejecuta un agente del catalogo por su ID."""

    # Resolve tenant: header > body > default
    tenant_id = x_tenant_id or body.tenant_id or "default"
    trace_id = x_trace_id or generate_trace_id()
    mode = "dry" if body.dry_run else "live"
    start_time = time.time()

    agents = _get_all_agents()
    agent = agents.get(agent_id)

    # 404: no encontrado
    if agent is None:
        _audit(trace_id, agent_id, tenant_id, mode, "not_found", 0, x_user_id, 404)
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # 409: archived o template
    file_path = agent.get("file_path", "")
    status = agent.get("status", "")

    if "_archived" in file_path:
        _audit(trace_id, agent_id, tenant_id, mode, "archived", 0, x_user_id, 409)
        raise HTTPException(
            status_code=409,
            detail=f"Agent '{agent_id}' is archived and cannot be executed",
        )

    if status == "template":
        _audit(trace_id, agent_id, tenant_id, mode, "template", 0, x_user_id, 409)
        raise HTTPException(
            status_code=409,
            detail=f"Agent '{agent_id}' is a template and cannot be executed",
        )

    # Ejecutar
    class_name = agent.get("class_name", "")

    try:
        result = await execute_agent(
            file_path=file_path,
            class_name=class_name,
            payload=body.payload,
            dry_run=body.dry_run,
            tenant_id=tenant_id,
        )
        latency_ms = round((time.time() - start_time) * 1000)
        _audit(trace_id, agent_id, tenant_id, mode, "ok", latency_ms, x_user_id, 200)
    except AgentLoadError as e:
        latency_ms = round((time.time() - start_time) * 1000)
        _audit(trace_id, agent_id, tenant_id, mode, "load_error", latency_ms, x_user_id, 500, str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000)
        _audit(trace_id, agent_id, tenant_id, mode, "error", latency_ms, x_user_id, 500, str(e))
        logger.exception(f"Error ejecutando {agent_id}")
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

    return {
        "success": True,
        "agent_id": agent_id,
        "trace_id": trace_id,
        "dry_run": body.dry_run,
        "auto_publish": body.auto_publish,
        "auto_email": body.auto_email,
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
    }


def _audit(
    trace_id: str,
    agent_id: str,
    tenant_id: str,
    mode: str,
    status: str,
    latency_ms: int,
    user_id: Optional[str],
    http_status: int,
    error: Optional[str] = None,
):
    entry = {
        "trace_id": trace_id,
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "mode": mode,
        "status": status,
        "http_status": http_status,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if user_id:
        entry["user_id"] = user_id
    if error:
        entry["error"] = error
    try:
        write_log(entry)
    except Exception as exc:
        logger.warning(f"Audit write failed: {exc}")
