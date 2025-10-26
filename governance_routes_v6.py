# ============================================================
# NADAKKI GOVERNANCE ROUTES v6.0
# ============================================================
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import random

router = APIRouter(prefix="/governance")

# Simulación de consumo
def simulate_usage():
    return {
        "cpu": round(random.uniform(10, 85), 2),
        "memory": round(random.uniform(20, 90), 2),
        "requests_per_min": random.randint(50, 600),
        "uptime": f"{round(random.uniform(99.1, 99.99), 2)}%"
    }

# Simulación de agentes
AGENTS = [
    {"id": "lead_scoring", "category": "marketing", "status": "active"},
    {"id": "customer_segmentation", "category": "marketing", "status": "paused"},
    {"id": "risk_evaluator", "category": "financial", "status": "active"},
    {"id": "contract_auditor", "category": "legal", "status": "active"},
    {"id": "credit_predictor", "category": "financial", "status": "active"},
]

@router.get("/summary", response_class=JSONResponse)
async def governance_summary():
    usage = simulate_usage()
    active = sum(1 for a in AGENTS if a["status"] == "active")
    paused = len(AGENTS) - active
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_agents": len(AGENTS),
        "active_agents": active,
        "paused_agents": paused,
        "usage": usage,
        "agents": AGENTS
    }
    return JSONResponse(data)

@router.post("/toggle/{agent_id}")
async def toggle_agent(agent_id: str):
    for a in AGENTS:
        if a["id"] == agent_id:
            a["status"] = "paused" if a["status"] == "active" else "active"
            return {"status": "ok", "agent": a}
    return {"error": "Agent not found"}
