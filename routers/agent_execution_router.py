"""
Agent Execution Router
- POST /api/v1/agents/{agent_id}/execute  (legacy path-based)
- POST /agents/execute                     (new body-based with flexible ID matching)

Carga y ejecuta agentes del catalogo de forma segura con dry_run por defecto.
Includes audit logging, rate limiting, and live gate.
Backup agents (_backup_ in ID) are excluded from execution.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, Field

from services.agent_runner import execute_agent, AgentLoadError
from services.audit_logger import generate_trace_id, write_log
from services.security import rate_limit_check, live_gate_check

logger = logging.getLogger("AgentExecution")

router = APIRouter(tags=["Agent Execution"])


class ExecuteRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = Field(True, description="Modo seguro, no ejecuta acciones reales")
    auto_publish: bool = Field(False, description="Publicar resultado automaticamente")
    auto_email: bool = Field(False, description="Enviar resultado por email")
    tenant_id: str = Field("default", description="ID del tenant")
    role: Optional[str] = Field(None, description="User role for live gate")


class FlexExecuteRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID (short or long format)")
    payload: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = Field(True, description="Modo seguro, no ejecuta acciones reales")
    auto_publish: bool = Field(False, description="Publicar resultado automaticamente")
    auto_email: bool = Field(False, description="Enviar resultado por email")
    tenant_id: str = Field("default", description="ID del tenant")
    role: Optional[str] = Field(None, description="User role for live gate")


def _get_all_agents() -> Dict[str, dict]:
    """Importa ALL_AGENTS desde main (lazy para evitar circular)."""
    from main import ALL_AGENTS
    return ALL_AGENTS


def _is_backup_agent(agent_id: str) -> bool:
    """Check if an agent ID corresponds to a backup agent."""
    return "_backup_" in agent_id


def _is_executable(agent: dict) -> bool:
    """Check if an agent is executable (has action methods and is not backup/archived/template)."""
    agent_id = agent.get("id", "")
    if _is_backup_agent(agent_id):
        return False
    if "_archived" in agent.get("file_path", ""):
        return False
    if agent.get("status") == "template":
        return False
    action_methods = agent.get("action_methods", [])
    return "execute" in action_methods or "run" in action_methods


def _resolve_agent_id(agent_id: str, agents: Dict[str, dict]) -> Optional[dict]:
    """
    Resolve an agent by ID with flexible matching:
    - If agent_id contains '__': exact match (long ID format)
    - If agent_id is short: find agent whose long ID ends with '__<short_id>'
    Backup agents are excluded from matching.
    """
    # Long ID: exact match
    if "__" in agent_id:
        agent = agents.get(agent_id)
        if agent and not _is_backup_agent(agent_id):
            return agent
        return None

    # Short ID: find match where long ID ends with __<short_id>
    suffix = f"__{agent_id}"
    candidates = []
    for aid, agent in agents.items():
        if _is_backup_agent(aid):
            continue
        if aid.endswith(suffix):
            candidates.append(agent)

    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        # Return first non-backup production agent, or just first
        for c in candidates:
            if c.get("status") == "production":
                return c
        return candidates[0]
    return None


def _get_suggestions(agent_id: str, agents: Dict[str, dict]) -> List[str]:
    """Get similar agent ID suggestions for 404 responses."""
    search = agent_id.lower()
    suggestions = []
    for aid in agents:
        if _is_backup_agent(aid):
            continue
        if search in aid.lower():
            suggestions.append(aid)
        if len(suggestions) >= 5:
            break
    return suggestions


def _validate_and_check(agent: dict, agent_id: str) -> Optional[dict]:
    """
    Validate agent is executable. Returns error dict if not, None if OK.
    """
    real_id = agent.get("id", agent_id)

    if _is_backup_agent(real_id):
        return {"status": 400, "detail": f"Agent '{real_id}' is a backup and not executable"}

    if "_archived" in agent.get("file_path", ""):
        return {"status": 409, "detail": f"Agent '{real_id}' is archived and cannot be executed"}

    if agent.get("status") == "template":
        return {"status": 409, "detail": f"Agent '{real_id}' is a template and cannot be executed"}

    action_methods = agent.get("action_methods", [])
    if "execute" not in action_methods and "run" not in action_methods:
        return {"status": 400, "detail": f"Agent '{real_id}' has no executable methods", "error": "Not executable"}

    return None


# ---------------------------------------------------------------------------
# NEW: POST /agents/execute (body-based, flexible ID matching)
# ---------------------------------------------------------------------------
@router.post("/agents/execute")
async def execute_agent_flex(
    body: FlexExecuteRequest,
    request: Request,
    x_tenant_id: Optional[str] = Header(None),
    x_trace_id: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_role: Optional[str] = Header(None),
):
    """Execute an agent by ID (supports short and long ID formats). Backup agents excluded."""

    agent_id = body.agent_id
    tenant_id = x_tenant_id or body.tenant_id or "default"
    trace_id = x_trace_id or generate_trace_id()
    mode = "dry" if body.dry_run else "live"
    role = x_role or body.role
    start_time = time.time()

    # --- Rate limit ---
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{tenant_id}:{client_ip}"
    if not rate_limit_check(rate_key):
        _audit(trace_id, agent_id, tenant_id, mode, "rate_limited", 0, x_user_id, 429)
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    # --- Live gate ---
    gate_error = live_gate_check(dry_run=body.dry_run, role=role)
    if gate_error:
        _audit(trace_id, agent_id, tenant_id, mode, "live_blocked", 0, x_user_id, 403, gate_error)
        raise HTTPException(status_code=403, detail=gate_error)

    agents = _get_all_agents()
    agent = _resolve_agent_id(agent_id, agents)

    # 404: not found
    if agent is None:
        suggestions = _get_suggestions(agent_id, agents)
        _audit(trace_id, agent_id, tenant_id, mode, "not_found", 0, x_user_id, 404)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Agent not found",
                "agent_id": agent_id,
                "suggestions": suggestions,
            },
        )

    # Validate executable
    validation_error = _validate_and_check(agent, agent_id)
    if validation_error:
        status_code = validation_error["status"]
        _audit(trace_id, agent_id, tenant_id, mode, "not_executable", 0, x_user_id, status_code)
        raise HTTPException(status_code=status_code, detail=validation_error["detail"])

    resolved_id = agent.get("id", agent_id)
    file_path = agent.get("file_path", "")
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
        _audit(trace_id, resolved_id, tenant_id, mode, "ok", latency_ms, x_user_id, 200)
    except AgentLoadError as e:
        latency_ms = round((time.time() - start_time) * 1000)
        _audit(trace_id, resolved_id, tenant_id, mode, "load_error", latency_ms, x_user_id, 500, str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000)
        _audit(trace_id, resolved_id, tenant_id, mode, "error", latency_ms, x_user_id, 500, str(e))
        logger.exception(f"Error ejecutando {resolved_id}")
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

    return {
        "success": True,
        "agent_id": resolved_id,
        "requested_id": agent_id,
        "trace_id": trace_id,
        "dry_run": body.dry_run,
        "auto_publish": body.auto_publish,
        "auto_email": body.auto_email,
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# LEGACY: POST /api/v1/agents/{agent_id}/execute (path-based)
# ---------------------------------------------------------------------------
@router.post("/api/v1/agents/{agent_id}/execute")
async def execute_agent_endpoint(
    agent_id: str,
    body: ExecuteRequest,
    request: Request,
    x_tenant_id: Optional[str] = Header(None),
    x_trace_id: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_role: Optional[str] = Header(None),
):
    """Ejecuta un agente del catalogo por su ID (legacy path-based)."""

    tenant_id = x_tenant_id or body.tenant_id or "default"
    trace_id = x_trace_id or generate_trace_id()
    mode = "dry" if body.dry_run else "live"
    role = x_role or body.role
    start_time = time.time()

    # --- Rate limit (per tenant + IP) ---
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{tenant_id}:{client_ip}"
    if not rate_limit_check(rate_key):
        _audit(trace_id, agent_id, tenant_id, mode, "rate_limited", 0, x_user_id, 429)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
        )

    # --- Live gate ---
    gate_error = live_gate_check(dry_run=body.dry_run, role=role)
    if gate_error:
        _audit(trace_id, agent_id, tenant_id, mode, "live_blocked", 0, x_user_id, 403, gate_error)
        raise HTTPException(status_code=403, detail=gate_error)

    agents = _get_all_agents()
    agent = _resolve_agent_id(agent_id, agents)

    # 404: not found
    if agent is None:
        suggestions = _get_suggestions(agent_id, agents)
        _audit(trace_id, agent_id, tenant_id, mode, "not_found", 0, x_user_id, 404)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Agent not found",
                "agent_id": agent_id,
                "suggestions": suggestions,
            },
        )

    # Validate executable
    validation_error = _validate_and_check(agent, agent_id)
    if validation_error:
        status_code = validation_error["status"]
        _audit(trace_id, agent_id, tenant_id, mode, "not_executable", 0, x_user_id, status_code)
        raise HTTPException(status_code=status_code, detail=validation_error["detail"])

    resolved_id = agent.get("id", agent_id)
    file_path = agent.get("file_path", "")
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
        _audit(trace_id, resolved_id, tenant_id, mode, "ok", latency_ms, x_user_id, 200)
    except AgentLoadError as e:
        latency_ms = round((time.time() - start_time) * 1000)
        _audit(trace_id, resolved_id, tenant_id, mode, "load_error", latency_ms, x_user_id, 500, str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000)
        _audit(trace_id, resolved_id, tenant_id, mode, "error", latency_ms, x_user_id, 500, str(e))
        logger.exception(f"Error ejecutando {resolved_id}")
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

    return {
        "success": True,
        "agent_id": resolved_id,
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
