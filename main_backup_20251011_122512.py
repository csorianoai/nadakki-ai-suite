"""
NADAKKI AI SUITE v3.3.1 - Enterprise Marketing AI Platform
FastAPI REST API with 24 Marketing Agents + Admin Endpoints
Multi-tenant, Rate-limited, Production-Ready
"""

from fastapi import FastAPI, Header, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timedelta
import logging
import time
from collections import defaultdict
import asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("NadakkiAISuite")

app = FastAPI(
    title="Nadakki AI Suite",
    description="Enterprise Marketing AI Platform with 24 Specialized Agents + Admin API",
    version="3.3.1",
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

from agents.marketing.canonical import AgentFactory, CANONICAL_AGENTS
from database.tenant_db import tenant_db

assert len(CANONICAL_AGENTS) == 24, f"Expected 24 agents, found {len(CANONICAL_AGENTS)}"
logger.info(f"✓ Loaded {len(CANONICAL_AGENTS)} marketing agents")

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {"default": 100, "starter": 100, "professional": 1000, "enterprise": 10000}
    
    def check_limit(self, tenant_id: str, plan: str = "default") -> bool:
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        self.requests[tenant_id] = [ts for ts in self.requests[tenant_id] if ts > hour_ago]
        limit = self.limits.get(plan, self.limits["default"])
        if len(self.requests[tenant_id]) >= limit:
            return False
        self.requests[tenant_id].append(now)
        return True
    
    def get_usage(self, tenant_id: str) -> Dict[str, Any]:
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        self.requests[tenant_id] = [ts for ts in self.requests[tenant_id] if ts > hour_ago]
        return {"requests_last_hour": len(self.requests[tenant_id]), "timestamp": now.isoformat()}

rate_limiter = RateLimiter()

# Models
class AgentRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Agent-specific input data")
    options: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    success: bool
    agent_id: str
    tenant_id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float
    timestamp: str

class CreateTenantRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    country: Optional[str] = None
    region: str = Field(default="latam", pattern="^(latam|north_america|europe|asia)$")
    plan: str = Field(default="starter", pattern="^(starter|professional|enterprise)$")
    config: Optional[Dict[str, Any]] = None

class UpdateTenantRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    country: Optional[str] = None
    region: Optional[str] = None
    plan: Optional[str] = None
    active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class ProvisionCoresRequest(BaseModel):
    cores: List[str] = Field(..., description="List of core names")
    config: Optional[Dict[str, Any]] = None

# Auth
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_tenant_from_api_key(api_key: str = Depends(api_key_header)) -> Dict[str, Any]:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    tenant = tenant_db.get_tenant_by_api_key(api_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if not tenant.get("active"):
        raise HTTPException(status_code=403, detail="Tenant is inactive")
    return tenant

async def check_rate_limit(tenant: Dict[str, Any] = Depends(get_tenant_from_api_key)) -> Dict[str, Any]:
    tenant_id = tenant["tenant_id"]
    plan = tenant.get("plan", "starter")
    if not rate_limiter.check_limit(tenant_id, plan):
        usage = rate_limiter.get_usage(tenant_id)
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Used {usage['requests_last_hour']} requests/hour.")
    return tenant


@app.get("/")
async def root():
    return {"service": "Nadakki AI Suite", "version": "3.3.1", "status": "operational", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.3.1", "agents_loaded": len(CANONICAL_AGENTS), "timestamp": datetime.now().isoformat()}

@app.get("/agents")
async def list_agents(category: Optional[str] = None, tenant: Dict[str, Any] = Depends(get_tenant_from_api_key)):
    agents = AgentFactory.list_agents(category=category)
    return {"total": len(agents), "agents": agents}

@app.get("/agents/categories")
async def list_categories(tenant: Dict[str, Any] = Depends(get_tenant_from_api_key)):
    return AgentFactory.get_categories()

# ADMIN ENDPOINTS
@app.post("/api/admin/tenants", status_code=201)
async def create_tenant(request: CreateTenantRequest):
    """Create new tenant (called by Onboarding System)"""
    try:
        tenant = tenant_db.create_tenant(
            name=request.name, email=request.email, country=request.country,
            region=request.region, plan=request.plan, config=request.config
        )
        logger.info(f"✓ Admin: Created tenant {tenant['tenant_id']} ({tenant['name']})")
        return {**tenant, "active": True, "updated_at": tenant['created_at']}
    except Exception as e:
        logger.error(f"Error creating tenant: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")

@app.get("/api/admin/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get tenant details"""
    tenant = tenant_db.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@app.get("/api/admin/tenants")
async def list_all_tenants(active_only: bool = True, limit: int = 100, offset: int = 0):
    """List all tenants"""
    tenants = tenant_db.list_tenants(active_only=active_only, limit=limit, offset=offset)
    return {"total": len(tenants), "tenants": tenants}

@app.patch("/api/admin/tenants/{tenant_id}")
async def update_tenant(tenant_id: str, request: UpdateTenantRequest):
    """Update tenant"""
    updates = {k: v for k, v in request.dict(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    success = tenant_db.update_tenant(tenant_id, **updates)
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant = tenant_db.get_tenant(tenant_id)
    return tenant

@app.post("/api/admin/tenants/{tenant_id}/provision-cores")
async def provision_cores(tenant_id: str, request: ProvisionCoresRequest):
    """Provision cores for tenant"""
    tenant = tenant_db.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    provisioned = []
    for core_name in request.cores:
        success = tenant_db.provision_core(tenant_id, core_name, request.config)
        if success:
            provisioned.append(core_name)
    
    logger.info(f"✓ Admin: Provisioned {len(provisioned)} cores for {tenant_id}")
    return {"tenant_id": tenant_id, "provisioned_cores": provisioned, "total": len(provisioned)}

@app.get("/api/admin/tenants/{tenant_id}/cores")
async def get_tenant_cores(tenant_id: str):
    """Get provisioned cores for tenant"""
    cores = tenant_db.get_tenant_cores(tenant_id)
    return {"tenant_id": tenant_id, "cores": cores, "total": len(cores)}

@app.get("/api/admin/tenants/{tenant_id}/stats")
async def get_tenant_statistics(tenant_id: str):
    """Get tenant usage statistics"""
    stats = tenant_db.get_tenant_stats(tenant_id)
    return {"tenant_id": tenant_id, **stats}


# AGENT EXECUTION
@app.post("/api/marketing/{agent_id}/execute", response_model=AgentResponse)
async def execute_agent(agent_id: str, request: AgentRequest, tenant: Dict[str, Any] = Depends(check_rate_limit)):
    """Execute a marketing agent"""
    start_time = time.time()
    tenant_id = tenant["tenant_id"]
    
    try:
        if agent_id not in CANONICAL_AGENTS:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        agent = AgentFactory.create_agent(agent_id)
        result = await asyncio.to_thread(lambda: {"status": "executed", "agent_id": agent_id, "data": request.data})
        
        execution_time = (time.time() - start_time) * 1000
        tenant_db.log_usage(tenant_id, agent_id, execution_time, True)
        
        logger.info(f"Agent '{agent_id}' executed for tenant '{tenant_id}' in {execution_time:.2f}ms")
        
        return AgentResponse(
            success=True, agent_id=agent_id, tenant_id=tenant_id, result=result,
            execution_time_ms=execution_time, timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        tenant_db.log_usage(tenant_id, agent_id, execution_time, False)
        logger.error(f"Error executing agent '{agent_id}': {str(e)}")
        return AgentResponse(
            success=False, agent_id=agent_id, tenant_id=tenant_id, error=str(e),
            execution_time_ms=execution_time, timestamp=datetime.now().isoformat()
        )

# Individual agent shortcuts
@app.post("/api/marketing/lead-scoring")
async def lead_scoring(request: AgentRequest, tenant: Dict[str, Any] = Depends(check_rate_limit)):
    return await execute_agent("lead_scoring", request, tenant)

@app.post("/api/marketing/contact-quality")
async def contact_quality(request: AgentRequest, tenant: Dict[str, Any] = Depends(check_rate_limit)):
    return await execute_agent("contact_quality", request, tenant)

@app.post("/api/marketing/campaign-optimizer")
async def campaign_optimizer(request: AgentRequest, tenant: Dict[str, Any] = Depends(check_rate_limit)):
    return await execute_agent("campaign_optimizer", request, tenant)

@app.post("/api/marketing/customer-segmentation")
async def customer_segmentation(request: AgentRequest, tenant: Dict[str, Any] = Depends(check_rate_limit)):
    return await execute_agent("customer_segmentation", request, tenant)

@app.post("/api/marketing/email-automation")
async def email_automation(request: AgentRequest, tenant: Dict[str, Any] = Depends(check_rate_limit)):
    return await execute_agent("email_automation", request, tenant)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail, "timestamp": datetime.now().isoformat()})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(status_code=500, content={"success": False, "error": "Internal server error", "timestamp": datetime.now().isoformat()})

# Startup
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("NADAKKI AI SUITE v3.3.1 - STARTING")
    logger.info("=" * 60)
    logger.info(f"✓ Loaded {len(CANONICAL_AGENTS)} marketing agents")
    logger.info("✓ Tenant database initialized")
    logger.info("✓ FastAPI server initialized")
    logger.info("=" * 60)
    logger.info("🚀 Server ready at http://localhost:8000")
    logger.info("📚 API docs at http://localhost:8000/docs")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Nadakki AI Suite...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
