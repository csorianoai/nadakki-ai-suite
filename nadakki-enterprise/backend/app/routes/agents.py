from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import AgentExecution
from datetime import datetime
import json

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.post("/execute")
async def execute_agent(tenant_id: str, agent_name: str, input_data: dict, db: Session = Depends(get_db)):
    execution = AgentExecution(
        tenant_id=tenant_id,
        agent_name=agent_name,
        input_data=json.dumps(input_data),
        status="pending"
    )
    db.add(execution)
    db.commit()
    return {"execution_id": str(execution.id), "status": "pending"}

@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str, db: Session = Depends(get_db)):
    execution = db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return {
        "id": str(execution.id),
        "agent_name": execution.agent_name,
        "status": execution.status,
        "created_at": execution.created_at.isoformat() if execution.created_at else None
    }
