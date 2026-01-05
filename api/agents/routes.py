from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/agents", tags=["agents"])

# ═══════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════

class Agent(BaseModel):
    id: Optional[str] = None
    tenant_id: str = "credicefi"
    name: str
    description: str = ""
    type: str = "chatbot"  # chatbot, email, voice, support, sales
    status: str = "draft"  # active, paused, draft
    model: str = "GPT-4"
    conversations: int = 0
    success_rate: float = 0.0
    avg_response_time: str = "-"
    last_active: str = "Never"
    config: dict = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class AgentCreate(BaseModel):
    name: str
    description: str = ""
    type: str = "chatbot"
    model: str = "GPT-4"
    config: dict = {}

# ═══════════════════════════════════════════════════════════════
# IN-MEMORY DATABASE
# ═══════════════════════════════════════════════════════════════

agents_db: dict[str, List[Agent]] = {
    "credicefi": [
        Agent(
            id="agent-1", tenant_id="credicefi", name="Customer Support Bot",
            description="Handles customer inquiries 24/7", type="support",
            status="active", model="GPT-4", conversations=12450,
            success_rate=94.2, avg_response_time="1.2s", last_active="2 min ago",
            created_at="2024-01-01T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Agent(
            id="agent-2", tenant_id="credicefi", name="Sales Assistant",
            description="Qualifies leads and schedules demos", type="sales",
            status="active", model="Claude 3", conversations=3420,
            success_rate=87.5, avg_response_time="2.1s", last_active="5 min ago",
            created_at="2024-01-05T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Agent(
            id="agent-3", tenant_id="credicefi", name="Email Responder",
            description="Auto-responds to common email queries", type="email",
            status="active", model="GPT-4", conversations=8900,
            success_rate=91.8, avg_response_time="45s", last_active="1 min ago",
            created_at="2024-01-10T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Agent(
            id="agent-4", tenant_id="credicefi", name="Onboarding Guide",
            description="Guides new users through setup", type="chatbot",
            status="paused", model="Claude 3", conversations=2100,
            success_rate=96.3, avg_response_time="0.8s", last_active="2 hours ago",
            created_at="2024-01-15T00:00:00Z", updated_at="2024-01-20T00:00:00Z"
        ),
        Agent(
            id="agent-5", tenant_id="credicefi", name="Voice Support",
            description="Handles phone support calls", type="voice",
            status="draft", model="Whisper + GPT-4", conversations=0,
            success_rate=0, avg_response_time="-", last_active="Never",
            created_at="2024-02-01T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
    ]
}

# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

@router.get("")
async def get_agents(
    tenant_id: str = Query("credicefi"),
    status: Optional[str] = None,
    type: Optional[str] = None
):
    """Get all agents for a tenant"""
    agents = agents_db.get(tenant_id, [])
    
    if status:
        agents = [a for a in agents if a.status == status]
    if type:
        agents = [a for a in agents if a.type == type]
    
    return {
        "agents": [a.dict() for a in agents],
        "total": len(agents)
    }

@router.get("/stats/summary")
async def get_agents_stats(tenant_id: str = Query("credicefi")):
    """Get agents statistics summary"""
    agents = agents_db.get(tenant_id, [])
    active_agents = [a for a in agents if a.status == "active"]
    
    return {
        "summary": {
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "total_conversations": sum(a.conversations for a in agents),
            "avg_success_rate": round(
                sum(a.success_rate for a in active_agents) / len(active_agents), 1
            ) if active_agents else 0,
            "by_type": {
                "chatbot": len([a for a in agents if a.type == "chatbot"]),
                "email": len([a for a in agents if a.type == "email"]),
                "voice": len([a for a in agents if a.type == "voice"]),
                "support": len([a for a in agents if a.type == "support"]),
                "sales": len([a for a in agents if a.type == "sales"]),
            }
        }
    }

@router.get("/{agent_id}")
async def get_agent(agent_id: str, tenant_id: str = Query("credicefi")):
    """Get a single agent by ID"""
    agents = agents_db.get(tenant_id, [])
    agent = next((a for a in agents if a.id == agent_id), None)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent.dict()

@router.post("")
async def create_agent(agent: AgentCreate, tenant_id: str = Query("credicefi")):
    """Create a new agent"""
    if tenant_id not in agents_db:
        agents_db[tenant_id] = []
    
    new_agent = Agent(
        id=f"agent-{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        name=agent.name,
        description=agent.description,
        type=agent.type,
        status="draft",
        model=agent.model,
        config=agent.config,
        created_at=datetime.utcnow().isoformat() + "Z",
        updated_at=datetime.utcnow().isoformat() + "Z"
    )
    
    agents_db[tenant_id].append(new_agent)
    
    return {"message": "Agent created", "agent": new_agent.dict()}

@router.put("/{agent_id}")
async def update_agent(
    agent_id: str,
    updates: dict,
    tenant_id: str = Query("credicefi")
):
    """Update an agent"""
    agents = agents_db.get(tenant_id, [])
    agent_idx = next((i for i, a in enumerate(agents) if a.id == agent_id), None)
    
    if agent_idx is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_idx]
    agent_dict = agent.dict()
    
    for key, value in updates.items():
        if key in agent_dict and key not in ["id", "tenant_id", "created_at"]:
            agent_dict[key] = value
    
    agent_dict["updated_at"] = datetime.utcnow().isoformat() + "Z"
    agents[agent_idx] = Agent(**agent_dict)
    
    return {"message": "Agent updated", "agent": agents[agent_idx].dict()}

@router.post("/{agent_id}/activate")
async def activate_agent(agent_id: str, tenant_id: str = Query("credicefi")):
    """Activate an agent"""
    agents = agents_db.get(tenant_id, [])
    agent_idx = next((i for i, a in enumerate(agents) if a.id == agent_id), None)
    
    if agent_idx is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agents[agent_idx].status = "active"
    agents[agent_idx].last_active = "Just now"
    agents[agent_idx].updated_at = datetime.utcnow().isoformat() + "Z"
    
    return {"message": "Agent activated", "agent": agents[agent_idx].dict()}

@router.post("/{agent_id}/pause")
async def pause_agent(agent_id: str, tenant_id: str = Query("credicefi")):
    """Pause an agent"""
    agents = agents_db.get(tenant_id, [])
    agent_idx = next((i for i, a in enumerate(agents) if a.id == agent_id), None)
    
    if agent_idx is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agents[agent_idx].status = "paused"
    agents[agent_idx].updated_at = datetime.utcnow().isoformat() + "Z"
    
    return {"message": "Agent paused", "agent": agents[agent_idx].dict()}

@router.post("/{agent_id}/duplicate")
async def duplicate_agent(agent_id: str, tenant_id: str = Query("credicefi")):
    """Duplicate an agent"""
    agents = agents_db.get(tenant_id, [])
    agent = next((a for a in agents if a.id == agent_id), None)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    new_agent = Agent(
        id=f"agent-{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        name=f"{agent.name} (Copy)",
        description=agent.description,
        type=agent.type,
        status="draft",
        model=agent.model,
        config=agent.config,
        created_at=datetime.utcnow().isoformat() + "Z",
        updated_at=datetime.utcnow().isoformat() + "Z"
    )
    
    agents_db[tenant_id].append(new_agent)
    
    return {"message": "Agent duplicated", "agent": new_agent.dict()}

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, tenant_id: str = Query("credicefi")):
    """Delete an agent"""
    agents = agents_db.get(tenant_id, [])
    agent_idx = next((i for i, a in enumerate(agents) if a.id == agent_id), None)
    
    if agent_idx is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    deleted = agents.pop(agent_idx)
    
    return {"message": "Agent deleted", "agent_id": deleted.id}
