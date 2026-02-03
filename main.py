# ===============================================================================
# NADAKKI AI Suite - Main Application
# ===============================================================================
"""
NADAKKI Advertising Manager - Multi-tenant Platform with AI Agents
"""

from fastapi import FastAPI, Header, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import Optional, Dict, Any

# ============================================================
# IMPORTAR LOS 5 AGENTES DE GOOGLE ADS
# ============================================================

try:
    from agents.marketing.advertising.agents.marketing.google_ads_strategist_agent import GoogleAdsStrategistIA
    from agents.marketing.advertising.agents.marketing.google_ads_budget_pacing_agent import GoogleAdsBudgetPacingIA
    from agents.marketing.advertising.agents.marketing.rsa_ad_copy_generator_agent import RSAAdCopyGeneratorIA
    from agents.marketing.advertising.agents.marketing.search_terms_cleaner_agent import SearchTermsCleanerIA
    from agents.marketing.advertising.agents.marketing.orchestrator_agent import OrchestratorIA
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import agents: {e}")
    AGENTS_AVAILABLE = False

# ============================================================
# CREAR APP FASTAPI
# ============================================================

app = FastAPI(
    title="NADAKKI Advertising Manager",
    description="Multi-tenant advertising platform with AI agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# VARIABLES GLOBALES
# ============================================================

AGENTS_MAP = {
    "strategist": {"name": "Google Ads Strategist", "class": GoogleAdsStrategistIA if AGENTS_AVAILABLE else None},
    "budget-pacing": {"name": "Budget Pacing", "class": GoogleAdsBudgetPacingIA if AGENTS_AVAILABLE else None},
    "rsa-copy": {"name": "RSA Copy Generator", "class": RSAAdCopyGeneratorIA if AGENTS_AVAILABLE else None},
    "search-cleaner": {"name": "Search Terms Cleaner", "class": SearchTermsCleanerIA if AGENTS_AVAILABLE else None},
    "orchestrator": {"name": "Orchestrator", "class": OrchestratorIA if AGENTS_AVAILABLE else None}
}

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/health")
async def health():
    return {"status": "healthy", "agents_available": AGENTS_AVAILABLE}

@app.get("/api/v1/agents")
async def list_agents():
    return {"agents": [{"id": k, "name": v["name"]} for k, v in AGENTS_MAP.items()]}

@app.post("/api/v1/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, x_tenant_id: Optional[str] = Header(None), payload: Dict = Body(...)):
    if agent_id not in AGENTS_MAP:
        return {"error": f"Agent {agent_id} not found"}
    
    agent_class = AGENTS_MAP[agent_id]["class"]
    if not agent_class:
        return {"error": f"Agent {agent_id} not available"}
    
    try:
        agent = agent_class()
        result = agent.execute(tenant_id=x_tenant_id or "demo", **payload)
        return {"agent": agent_id, "status": "success", "result": result}
    except Exception as e:
        return {"agent": agent_id, "status": "error", "error": str(e)}

@app.get("/")
async def root():
    return {"name": "NADAKKI Advertising Manager", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
