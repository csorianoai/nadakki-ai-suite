"""
Agent Execution Router - POST /api/v1/agents/{agent_id}/execute
Carga y ejecuta agentes del catalogo de forma segura con dry_run por defecto.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.agent_runner import execute_agent, AgentLoadError

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
async def execute_agent_endpoint(agent_id: str, body: ExecuteRequest):
    """Ejecuta un agente del catalogo por su ID."""

    agents = _get_all_agents()
    agent = agents.get(agent_id)

    # 404: no encontrado
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # 409: archived o template
    file_path = agent.get("file_path", "")
    status = agent.get("status", "")

    if "_archived" in file_path:
        raise HTTPException(
            status_code=409,
            detail=f"Agent '{agent_id}' is archived and cannot be executed",
        )

    if status == "template":
        raise HTTPException(
            status_code=409,
            detail=f"Agent '{agent_id}' is a template and cannot be executed",
        )

    # Ejecutar
    class_name = agent.get("class_name", "")

    try:
        result = execute_agent(
            file_path=file_path,
            class_name=class_name,
            payload=body.payload,
            dry_run=body.dry_run,
            tenant_id=body.tenant_id,
        )
    except AgentLoadError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(f"Error ejecutando {agent_id}")
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

    return {
        "success": True,
        "agent_id": agent_id,
        "dry_run": body.dry_run,
        "auto_publish": body.auto_publish,
        "auto_email": body.auto_email,
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
    }
