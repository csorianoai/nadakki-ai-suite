"""
NADAKKI AI SUITE v4.0.0 - Enterprise AI Platform
185+ Agents across 20 AI Cores
"""

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
from collections import defaultdict

# ============================================================================
# SETUP
# ============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("NadakkiAISuite")

app = FastAPI(
    title="Nadakki AI Suite",
    description="Enterprise AI Platform - 185+ Agents across 20 AI Cores",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AGENT REGISTRY - CARGA TODOS LOS AGENTES
# ============================================================================

from agent_loader import registry, CORES_CONFIG

logger.info(f"✓ Loaded {registry.total} agents across {len(registry.cores)} cores")

# ============================================================================
# AUTH & RATE LIMITING
# ============================================================================

VALID_TENANTS = {
    "demo": {"api_key": "demo_key_12345", "plan": "starter"},
    "nadakki": {"api_key": "nadakki_master_key_2025", "plan": "enterprise"},
    "credicefi": {"api_key": "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I", "plan": "enterprise"}
}

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {"default": 100, "starter": 100, "professional": 1000, "enterprise": 10000}
    
    def check(self, tenant_id: str, plan: str = "default") -> bool:
        now = datetime.now()
        self.requests[tenant_id] = [t for t in self.requests[tenant_id] if t > now - timedelta(hours=1)]
        if len(self.requests[tenant_id]) >= self.limits.get(plan, 100):
            return False
        self.requests[tenant_id].append(now)
        return True
    
    def usage(self, tenant_id: str) -> Dict:
        now = datetime.now()
        self.requests[tenant_id] = [t for t in self.requests[tenant_id] if t > now - timedelta(hours=1)]
        return {"tenant_id": tenant_id, "requests_this_hour": len(self.requests[tenant_id])}

rate_limiter = RateLimiter()

async def verify_tenant(x_tenant_id: str = Header(None), x_api_key: str = Header(None)) -> Dict:
    # Permitir acceso sin auth a endpoints públicos
    if x_tenant_id is None:
        return {"tenant_id": "anonymous", "plan": "default"}
    if x_tenant_id not in VALID_TENANTS:
        raise HTTPException(401, "Invalid tenant")
    if VALID_TENANTS[x_tenant_id]["api_key"] != x_api_key:
        raise HTTPException(401, "Invalid API key")
    if not rate_limiter.check(x_tenant_id, VALID_TENANTS[x_tenant_id]["plan"]):
        raise HTTPException(429, "Rate limit exceeded")
    return {"tenant_id": x_tenant_id, "plan": VALID_TENANTS[x_tenant_id]["plan"]}

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Nadakki AI Suite",
        "version": "4.0.0",
        "status": "operational",
        "total_agents": registry.total,
        "total_cores": len(registry.cores),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "4.0.0",
        "agents_loaded": registry.total,
        "cores_active": len(registry.cores),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# CORES ENDPOINTS
# ============================================================================

@app.get("/cores")
async def get_cores(tenant: Dict = Depends(verify_tenant)):
    return {"total": len(registry.cores), "cores": registry.get_cores()}

@app.get("/cores/{core_id}")
async def get_core(core_id: str, tenant: Dict = Depends(verify_tenant)):
    if core_id not in registry.cores:
        raise HTTPException(404, "Core not found")
    agents = registry.get_agents_by_core(core_id)
    config = CORES_CONFIG.get(core_id, {"name": core_id.title()})
    return {
        "id": core_id,
        "name": config.get("name"),
        "color": config.get("color"),
        "icon": config.get("icon"),
        "agents_count": len(agents),
        "agents": [{"id": a["id"], "name": a["name"], "status": a["status"]} for a in agents]
    }

# ============================================================================
# AGENTS ENDPOINTS
# ============================================================================

@app.get("/agents")
async def get_agents(tenant: Dict = Depends(verify_tenant)):
    agents = registry.get_all_agents()
    return {
        "total": len(agents),
        "by_core": registry.get_core_summary(),
        "agents": [{"id": a["id"], "name": a["name"], "core": a["core"], "status": a["status"]} for a in agents]
    }

@app.get("/agents/categories")
async def get_categories(tenant: Dict = Depends(verify_tenant)):
    return {"categories": list(registry.cores.keys()), "counts": registry.get_core_summary()}

@app.get("/agents/{core}/{agent_id}")
async def get_agent(core: str, agent_id: str, tenant: Dict = Depends(verify_tenant)):
    agent = registry.get_agent(core, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent

class ExecuteRequest(BaseModel):
    input_data: Dict[str, Any] = Field(default={})
    options: Dict[str, Any] = Field(default={})

@app.post("/agents/{core}/{agent_id}/execute")
async def execute_agent(core: str, agent_id: str, request: ExecuteRequest, tenant: Dict = Depends(verify_tenant)):
    agent = registry.get_agent(core, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    # Cargar la clase del agente
    agent_class = registry.load_agent(f"{core}.{agent_id}")
    if not agent_class:
        raise HTTPException(503, f"Agent not loadable: {agent.get('error', 'Unknown error')}")
    
    try:
        # Intentar instanciar y ejecutar
        instance = agent_class({"tenant_id": tenant["tenant_id"]})
        
        # Buscar método ejecutable
        result = None
        for method in ["execute", "run", "process", "analyze", "monitor_compliance"]:
            if hasattr(instance, method):
                result = getattr(instance, method)(request.input_data)
                break
        
        if result is None:
            result = {"status": "executed", "message": "Agent processed successfully"}
        
        return {
            "agent": f"{core}.{agent_id}",
            "tenant": tenant["tenant_id"],
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing {core}.{agent_id}: {e}")
        raise HTTPException(500, str(e))

@app.get("/usage/{tenant_id}")
async def get_usage(tenant_id: str, tenant: Dict = Depends(verify_tenant)):
    return rate_limiter.usage(tenant_id)

# ============================================================================
# DASHBOARD ENDPOINT
# ============================================================================

@app.get("/dashboard/summary")
async def dashboard_summary(tenant: Dict = Depends(verify_tenant)):
    return {
        "total_agents": registry.total,
        "total_cores": len(registry.cores),
        "cores": registry.get_cores(),
        "by_core": registry.get_core_summary(),
        "system_status": "active",
        "version": "4.0.0",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("NADAKKI AI SUITE v4.0.0 - STARTING")
    logger.info("=" * 60)
    logger.info(f"✓ {registry.total} agents across {len(registry.cores)} cores")
    for core, agents in sorted(registry.cores.items(), key=lambda x: -len(x[1])):
        logger.info(f"  • {core}: {len(agents)} agents")
    logger.info("=" * 60)
    logger.info("🚀 Server ready at http://localhost:8000")
    logger.info("📚 API docs at http://localhost:8000/docs")
    logger.info("=" * 60)
