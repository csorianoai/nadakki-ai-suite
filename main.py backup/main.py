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
    """
    Ejecutar un agente con manejo robusto de input.
    Los agentes pueden esperar dict o objetos tipados - manejamos ambos casos.
    """
    agent = registry.get_agent(core, agent_id)
    if not agent:
        raise HTTPException(404, f"Agent not found: {core}/{agent_id}")
    
    agent_key = f"{core}.{agent_id}"

    # SUPER AGENT v3.2.0 SUPPORT - Try module-level execute first
    try:
        import importlib as _imp
        _mod = _imp.import_module(f'agents.{core}.{agent_id}')
        if hasattr(_mod, 'execute') and callable(_mod.execute):
            _in = request.input_data or {}
            if isinstance(_in, dict) and 'tenant_id' not in _in:
                _in['tenant_id'] = tenant['tenant_id']
            _ctx = {'tenant_id': tenant['tenant_id']}
            _res = _mod.execute({'input_data': _in}, _ctx)
            from datetime import datetime as _dt
            return {'agent': agent_key, 'agent_name': agent_id.title(), 'tenant': tenant['tenant_id'], 'timestamp': str(_dt.utcnow()), 'result': _res}
    except Exception as _e:
        pass  # Fall through to class-based execution

    
    try:
        # Crear instancia del agente
        instance = registry.create_instance(agent_key, tenant["tenant_id"])
        
        if not instance:
            raise HTTPException(503, f"Agent not instantiable: {agent.get('error', 'Unknown error')}")
        
        # Preparar input data
        input_data = request.input_data or {}
        
        # Inyectar tenant_id en el input si no está presente
        if isinstance(input_data, dict) and "tenant_id" not in input_data:
            input_data["tenant_id"] = tenant["tenant_id"]
        
        # Buscar y ejecutar método
        result = None
        methods_to_try = ["execute", "run", "process", "analyze", "score", "personalize", "optimize", "generate", "predict"]
        
        for method_name in methods_to_try:
            if hasattr(instance, method_name):
                method = getattr(instance, method_name)
                if callable(method):
                    try:
                        # Intentar llamar con input_data
                        method_result = method(input_data)
                        
                        # Manejar métodos async
                        import asyncio
                        if asyncio.iscoroutine(method_result):
                            result = await method_result
                        else:
                            result = method_result
                        break
                    except TypeError as te:
                        # Si falla por tipo de argumento, intentar sin argumentos
                        if "argument" in str(te).lower() or "positional" in str(te).lower():
                            try:
                                method_result = method()
                                import asyncio
                                if asyncio.iscoroutine(method_result):
                                    result = await method_result
                                else:
                                    result = method_result
                                break
                            except:
                                continue
                        else:
                            # Re-raise si es otro tipo de TypeError
                            raise
                    except AttributeError as ae:
                        # Error común: 'dict' object has no attribute 'x'
                        # El agente espera un objeto tipado, devolver error informativo
                        return {
                            "agent": agent_key,
                            "agent_name": agent.get("name"),
                            "tenant": tenant["tenant_id"],
                            "timestamp": datetime.now().isoformat(),
                            "status": "input_schema_error",
                            "error": str(ae),
                            "message": "Agent requires typed input. Check agent documentation for required schema.",
                            "input_received": list(input_data.keys()) if isinstance(input_data, dict) else type(input_data).__name__
                        }
        
        if result is None:
            result = {"status": "executed", "message": "Agent processed but returned no result"}
        
        # Serializar resultado
        if hasattr(result, 'dict'):
            result = result.dict()
        elif hasattr(result, 'model_dump'):
            result = result.model_dump()
        elif hasattr(result, '__dict__') and not isinstance(result, dict):
            result = vars(result)
        
        return {
            "agent": agent_key,
            "agent_name": agent.get("name"),
            "tenant": tenant["tenant_id"],
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error executing {agent_key}: {error_msg}")
        
        # Devolver error estructurado en lugar de 500
        return {
            "agent": agent_key,
            "agent_name": agent.get("name"),
            "tenant": tenant["tenant_id"],
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error_type": type(e).__name__,
            "error": error_msg,
            "suggestion": "Check agent input schema requirements"
        }

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

# ============================================================================
# CATALOG ENDPOINTS - Marketing Module v3.2.0
# ============================================================================

@app.get("/api/catalog/marketing")
async def get_marketing_catalog():
    """Retorna el catalogo completo de agentes de Marketing"""
    import json as _json
    import os
    
    catalog_path = os.path.join(os.path.dirname(__file__), "agents", "marketing", "agent_catalog_es.json")
    
    try:
        if os.path.exists(catalog_path):
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog = _json.load(f)
        else:
            catalog = {"agents": {}, "categories": {}, "_metadata": {}}
        
        enriched_agents = {}
        for agent_id, agent_info in catalog.get('agents', {}).items():
            try:
                import importlib
                module = importlib.import_module(f'agents.marketing.{agent_id}')
                status = "active" if hasattr(module, 'execute') else "inactive"
                version = getattr(module, 'VERSION', '3.2.0')
            except:
                status = "error"
                version = "unknown"
            
            enriched_agents[agent_id] = {
                **agent_info,
                "status": status,
                "version": version,
                "endpoint": f"/agents/marketing/{agent_id}/execute"
            }
        
        return {
            "module": "marketing",
            "display_name": "Marketing Core",
            "total_agents": len(enriched_agents),
            "active_agents": sum(1 for a in enriched_agents.values() if a.get('status') == 'active'),
            "version": "3.2.0",
            "agents": enriched_agents,
            "categories": catalog.get('categories', {})
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/catalog/marketing/summary")
async def get_marketing_summary():
    """Resumen del modulo Marketing para dashboard"""
    return {
        "module": "marketing",
        "display_name": "Marketing Core",
        "total_agents": 35,
        "active_agents": 35,
        "version": "3.2.0",
        "categories": [
            {"name": "Gestion de Leads", "count": 3, "color": "#3B82F6"},
            {"name": "Experimentacion", "count": 2, "color": "#8B5CF6"},
            {"name": "Campanas", "count": 1, "color": "#F59E0B"},
            {"name": "Contenido", "count": 2, "color": "#10B981"},
            {"name": "Redes Sociales", "count": 2, "color": "#EC4899"},
            {"name": "Analitica", "count": 2, "color": "#6366F1"},
            {"name": "Inteligencia Competitiva", "count": 2, "color": "#EF4444"},
            {"name": "Atribucion", "count": 2, "color": "#14B8A6"},
            {"name": "Pronosticos", "count": 2, "color": "#F97316"},
            {"name": "Segmentacion", "count": 3, "color": "#84CC16"},
            {"name": "Personalizacion", "count": 1, "color": "#A855F7"},
            {"name": "Retencion", "count": 2, "color": "#22C55E"},
            {"name": "Email Marketing", "count": 1, "color": "#0EA5E9"},
            {"name": "Customer Journey", "count": 1, "color": "#F43F5E"},
            {"name": "Precios", "count": 1, "color": "#FBBF24"},
            {"name": "Influencers", "count": 2, "color": "#FB7185"},
            {"name": "Creatividad", "count": 1, "color": "#C084FC"},
            {"name": "Calidad de Datos", "count": 1, "color": "#2DD4BF"},
            {"name": "Conversion", "count": 1, "color": "#4ADE80"},
            {"name": "Producto", "count": 1, "color": "#60A5FA"},
            {"name": "Ofertas", "count": 1, "color": "#FACC15"},
            {"name": "Orquestacion", "count": 1, "color": "#818CF8"}
        ],
        "metrics": {"avg_latency_ms": 45, "success_rate": 98.5}
    }


@app.get("/api/catalog/marketing/agents")
async def get_marketing_agents_list():
    """Lista de agentes para UI"""
    return {
        "total": 35,
        "agents": [
            {"id": "leadscoria", "name": "Puntuador de Leads", "category": "Lead Management"},
            {"id": "leadscoringia", "name": "Calificador de Leads", "category": "Lead Management"},
            {"id": "predictiveleadia", "name": "Predictor de Leads", "category": "Lead Management"},
            {"id": "abtestingia", "name": "Analizador de Pruebas A/B", "category": "Experimentation"},
            {"id": "abtestingimpactia", "name": "Medidor de Impacto A/B", "category": "Experimentation"},
            {"id": "campaignoptimizeria", "name": "Optimizador de Campanas", "category": "Campaign Management"},
            {"id": "contentgeneratoria", "name": "Generador de Contenido", "category": "Content"},
            {"id": "contentperformanceia", "name": "Analizador de Contenido", "category": "Content"},
            {"id": "socialpostgeneratoria", "name": "Generador de Posts Sociales", "category": "Social Media"},
            {"id": "sentimentanalyzeria", "name": "Analizador de Sentimiento", "category": "Analytics"},
            {"id": "sociallisteningia", "name": "Monitor de Redes Sociales", "category": "Social Media"},
            {"id": "competitoranalyzeria", "name": "Analizador de Competencia", "category": "Competitive Intelligence"},
            {"id": "competitorintelligenceia", "name": "Inteligencia Competitiva", "category": "Competitive Intelligence"},
            {"id": "channelattributia", "name": "Atribuidor de Canales", "category": "Attribution"},
            {"id": "attributionmodelia", "name": "Modelador de Atribucion", "category": "Attribution"},
            {"id": "budgetforecastia", "name": "Pronosticador de Presupuesto", "category": "Forecasting"},
            {"id": "marketingmixmodelia", "name": "Modelador de Mix Marketing", "category": "Forecasting"},
            {"id": "audiencesegmenteria", "name": "Segmentador de Audiencias", "category": "Segmentation"},
            {"id": "customersegmentatonia", "name": "Segmentador de Clientes", "category": "Segmentation"},
            {"id": "geosegmentationia", "name": "Segmentador Geografico", "category": "Segmentation"},
            {"id": "personalizationengineia", "name": "Motor de Personalizacion", "category": "Personalization"},
            {"id": "retentionpredictoria", "name": "Predictor de Retencion", "category": "Retention"},
            {"id": "retentionpredictorea", "name": "Analizador de Retencion", "category": "Retention"},
            {"id": "emailautomationia", "name": "Automatizador de Email", "category": "Email Marketing"},
            {"id": "journeyoptimizeria", "name": "Optimizador de Journey", "category": "Customer Journey"},
            {"id": "pricingoptimizeria", "name": "Optimizador de Precios", "category": "Pricing"},
            {"id": "influencermatcheria", "name": "Buscador de Influencers", "category": "Influencer Marketing"},
            {"id": "influencermatchingia", "name": "Emparejador de Influencers", "category": "Influencer Marketing"},
            {"id": "creativeanalyzeria", "name": "Analizador de Creatividades", "category": "Creative"},
            {"id": "contactqualityia", "name": "Evaluador de Contactos", "category": "Data Quality"},
            {"id": "minimalformia", "name": "Optimizador de Formularios", "category": "Conversion"},
            {"id": "conversioncohortia", "name": "Analizador de Cohortes", "category": "Analytics"},
            {"id": "productaffinityia", "name": "Analizador de Afinidad", "category": "Product"},
            {"id": "cashofferfilteria", "name": "Filtrador de Ofertas", "category": "Offers"},
            {"id": "marketingorchestratorea", "name": "Orquestador de Marketing", "category": "Orchestration"}
        ]
    }

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






# ============================================================================
# CATALOG ENDPOINTS - ALL CORES (Auto-generated)
# ============================================================================

# --- LEGAL CORE (32 agentes) ---
@app.get("/api/catalog/legal/agents")
async def get_legal_agents():
    return {
        "total": 32,
        "core": "legal",
        "display_name": "Legal AI System",
        "agents": [
            {"id": "derechoadministrativo", "name": "Derecho Administrativo", "category": "Administrativo"},
            {"id": "derechoadministrativophd", "name": "Derecho Administrativo PhD", "category": "Administrativo"},
            {"id": "derechoambiental", "name": "Derecho Ambiental", "category": "Ambiental"},
            {"id": "derechobancario", "name": "Derecho Bancario", "category": "Bancario"},
            {"id": "derechocivilphd", "name": "Derecho Civil PhD", "category": "Civil"},
            {"id": "derechocomercial", "name": "Derecho Comercial", "category": "Comercial"},
            {"id": "derechocomercialephd", "name": "Derecho Comercial PhD", "category": "Comercial"},
            {"id": "derechoconstitucional", "name": "Derecho Constitucional", "category": "Constitucional"},
            {"id": "derechoconstitucionalphd", "name": "Derecho Constitucional PhD", "category": "Constitucional"},
            {"id": "derechocontratacion", "name": "Derecho Contratacion", "category": "Contratos"},
            {"id": "derechofamiliaphd", "name": "Derecho Familia PhD", "category": "Familia"},
            {"id": "derechofamiliar", "name": "Derecho Familiar", "category": "Familia"},
            {"id": "derechofinanciero", "name": "Derecho Financiero", "category": "Financiero"},
            {"id": "derechoinmobiliario", "name": "Derecho Inmobiliario", "category": "Inmobiliario"},
            {"id": "derechoinmobiliariophd", "name": "Derecho Inmobiliario PhD", "category": "Inmobiliario"},
            {"id": "derechointelectual", "name": "Derecho Intelectual", "category": "Propiedad Intelectual"},
            {"id": "derechointernacional", "name": "Derecho Internacional", "category": "Internacional"},
            {"id": "derecholaboral", "name": "Derecho Laboral", "category": "Laboral"},
            {"id": "derecholaboralphd", "name": "Derecho Laboral PhD", "category": "Laboral"},
            {"id": "derechomarcario", "name": "Derecho Marcario", "category": "Marcas"},
            {"id": "derechomaritimo", "name": "Derecho Maritimo", "category": "Maritimo"},
            {"id": "derechomigratorio", "name": "Derecho Migratorio", "category": "Migratorio"},
            {"id": "derechominero", "name": "Derecho Minero", "category": "Minero"},
            {"id": "derechonotarial", "name": "Derecho Notarial", "category": "Notarial"},
            {"id": "derechopenal", "name": "Derecho Penal", "category": "Penal"},
            {"id": "derechopenalphd", "name": "Derecho Penal PhD", "category": "Penal"},
            {"id": "derechoprocesalpenal", "name": "Derecho Procesal Penal", "category": "Procesal"},
            {"id": "derechoprocesalpenalphd", "name": "Derecho Procesal Penal PhD", "category": "Procesal"},
            {"id": "derechoseguros", "name": "Derecho Seguros", "category": "Seguros"},
            {"id": "derechotributario", "name": "Derecho Tributario", "category": "Tributario"},
            {"id": "derechotributariophd", "name": "Derecho Tributario PhD", "category": "Tributario"},
            {"id": "legal_coordinator", "name": "Coordinador Legal", "category": "Coordinacion"}
        ]
    }

# --- LOGISTICA CORE (23 agentes) ---
@app.get("/api/catalog/logistica/agents")
async def get_logistica_agents():
    return {
        "total": 23,
        "core": "logistica",
        "display_name": "Logistica Inteligente",
        "agents": [
            {"id": "alertasinventario", "name": "Alertas de Inventario", "category": "Inventario"},
            {"id": "almaceninteligente", "name": "Almacen Inteligente", "category": "Almacen"},
            {"id": "analisisrendimiento", "name": "Analisis de Rendimiento", "category": "Analytics"},
            {"id": "controlcalidad", "name": "Control de Calidad", "category": "Calidad"},
            {"id": "controlcalidadia", "name": "Control Calidad IA", "category": "Calidad"},
            {"id": "controlpedidosia", "name": "Control de Pedidos IA", "category": "Pedidos"},
            {"id": "costoslogisticos", "name": "Costos Logisticos", "category": "Costos"},
            {"id": "evaluadorproveedoresia", "name": "Evaluador de Proveedores", "category": "Proveedores"},
            {"id": "gestionriesgos", "name": "Gestion de Riesgos", "category": "Riesgos"},
            {"id": "logisticareversa", "name": "Logistica Reversa", "category": "Reversa"},
            {"id": "logistica_coordinator", "name": "Coordinador Logistica", "category": "Coordinacion"},
            {"id": "optimizacionalmacen", "name": "Optimizacion Almacen", "category": "Almacen"},
            {"id": "optimizacioncostos", "name": "Optimizacion de Costos", "category": "Costos"},
            {"id": "optimizadorrutasia", "name": "Optimizador de Rutas", "category": "Rutas"},
            {"id": "planificaciondemanda", "name": "Planificacion Demanda", "category": "Demanda"},
            {"id": "predicciondemanda", "name": "Prediccion de Demanda", "category": "Demanda"},
            {"id": "previsioninventarioia", "name": "Prevision de Inventario", "category": "Inventario"},
            {"id": "seguridadcarga", "name": "Seguridad de Carga", "category": "Seguridad"},
            {"id": "sostenibilidadia", "name": "Sostenibilidad IA", "category": "Sostenibilidad"},
            {"id": "transporteoptimizado", "name": "Transporte Optimizado", "category": "Transporte"},
            {"id": "transportepredictivo", "name": "Transporte Predictivo", "category": "Transporte"},
            {"id": "trazabilidadia", "name": "Trazabilidad IA", "category": "Trazabilidad"},
            {"id": "trazabilidadtotal", "name": "Trazabilidad Total", "category": "Trazabilidad"}
        ]
    }

# --- CONTABILIDAD CORE (22 agentes) ---
@app.get("/api/catalog/contabilidad/agents")
async def get_contabilidad_agents():
    return {
        "total": 22,
        "core": "contabilidad",
        "display_name": "Contabilidad Cuantica",
        "agents": [
            {"id": "activosfijos", "name": "Activos Fijos", "category": "Activos"},
            {"id": "analisis_financiero", "name": "Analisis Financiero", "category": "Analisis"},
            {"id": "analisis_financiero_super_agent", "name": "Analisis Financiero Super", "category": "Analisis"},
            {"id": "auditoriainterna", "name": "Auditoria Interna", "category": "Auditoria"},
            {"id": "cierrecontable", "name": "Cierre Contable", "category": "Cierres"},
            {"id": "compliance_contable", "name": "Compliance Contable", "category": "Compliance"},
            {"id": "conciliacionbancaria", "name": "Conciliacion Bancaria", "category": "Conciliacion"},
            {"id": "contabilidadinteligente", "name": "Contabilidad Inteligente", "category": "General"},
            {"id": "contabilidad_coordinator", "name": "Coordinador Contabilidad", "category": "Coordinacion"},
            {"id": "controlgastos", "name": "Control de Gastos", "category": "Gastos"},
            {"id": "dgiiautoreporter", "name": "DGII Auto Reporter", "category": "Fiscal"},
            {"id": "facturacionelectronica", "name": "Facturacion Electronica", "category": "Facturacion"},
            {"id": "facturacionia", "name": "Facturacion IA", "category": "Facturacion"},
            {"id": "flujocajaia", "name": "Flujo de Caja IA", "category": "Flujo"},
            {"id": "flujocajaprediccion", "name": "Prediccion Flujo Caja", "category": "Flujo"},
            {"id": "inventariovaloracion", "name": "Valoracion Inventario", "category": "Inventario"},
            {"id": "previsionfiscal", "name": "Prevision Fiscal", "category": "Fiscal"},
            {"id": "reconcilia_auto", "name": "Reconciliacion Auto", "category": "Conciliacion"},
            {"id": "reportesejecutivos", "name": "Reportes Ejecutivos", "category": "Reportes"},
            {"id": "reportes_fiscales", "name": "Reportes Fiscales", "category": "Fiscal"},
            {"id": "reportingfinanciero", "name": "Reporting Financiero", "category": "Reportes"},
            {"id": "tributarioia", "name": "Tributario IA", "category": "Fiscal"}
        ]
    }

# --- PRESUPUESTO CORE (13 agentes) ---
@app.get("/api/catalog/presupuesto/agents")
async def get_presupuesto_agents():
    return {
        "total": 13,
        "core": "presupuesto",
        "display_name": "Presupuesto Inteligente",
        "agents": [
            {"id": "analisisvarianza", "name": "Analisis de Varianza", "category": "Varianza"},
            {"id": "budgetoptimizer", "name": "Optimizador de Budget", "category": "Optimizacion"},
            {"id": "controlpresupuestario", "name": "Control Presupuestario", "category": "Control"},
            {"id": "costocentros", "name": "Centros de Costo", "category": "Costos"},
            {"id": "forecastingavanzado", "name": "Forecasting Avanzado", "category": "Forecasting"},
            {"id": "forecastingia", "name": "Forecasting IA", "category": "Forecasting"},
            {"id": "optimizacionrecursos", "name": "Optimizacion Recursos", "category": "Optimizacion"},
            {"id": "planificacionestrategica", "name": "Planificacion Estrategica", "category": "Planificacion"},
            {"id": "presupuestomaestro", "name": "Presupuesto Maestro", "category": "General"},
            {"id": "presupuestopredictivoia", "name": "Presupuesto Predictivo", "category": "Prediccion"},
            {"id": "presupuesto_coordinator", "name": "Coordinador Presupuesto", "category": "Coordinacion"},
            {"id": "roipredictor", "name": "Predictor de ROI", "category": "ROI"},
            {"id": "varianzaanalisis", "name": "Analisis Varianza", "category": "Varianza"}
        ]
    }

# --- ORIGINACION CORE (10 agentes) ---
@app.get("/api/catalog/originacion/agents")
async def get_originacion_agents():
    return {
        "total": 10,
        "core": "originacion",
        "display_name": "Originacion Neural",
        "agents": [
            {"id": "base_components_v2", "name": "Componentes Base v2", "category": "Base"},
            {"id": "behaviorminer", "name": "Behavior Miner", "category": "Behavioral"},
            {"id": "behavior_miner_v2", "name": "Behavior Miner v2", "category": "Behavioral"},
            {"id": "dnaprofiler", "name": "DNA Profiler", "category": "Profiling"},
            {"id": "dna_profiler_v2", "name": "DNA Profiler v2", "category": "Profiling"},
            {"id": "incomeoracle", "name": "Income Oracle", "category": "Income"},
            {"id": "income_oracle_v2", "name": "Income Oracle v2", "category": "Income"},
            {"id": "originacion_coordinator", "name": "Coordinador Originacion", "category": "Coordinacion"},
            {"id": "sentinelbot", "name": "Sentinel Bot", "category": "Monitoring"},
            {"id": "sentinel_bot_v2", "name": "Sentinel Bot v2", "category": "Monitoring"}
        ]
    }

# --- RRHH CORE (10 agentes) ---
@app.get("/api/catalog/rrhh/agents")
async def get_rrhh_agents():
    return {
        "total": 10,
        "core": "rrhh",
        "display_name": "Recursos Humanos IA",
        "agents": [
            {"id": "capacitacionia", "name": "Capacitacion IA", "category": "Capacitacion"},
            {"id": "cvanalyzeria", "name": "Analizador de CV", "category": "Reclutamiento"},
            {"id": "nominaautomatica", "name": "Nomina Automatica", "category": "Nomina"},
            {"id": "nominainteligente", "name": "Nomina Inteligente", "category": "Nomina"},
            {"id": "performanceanalyzer", "name": "Analizador Performance", "category": "Performance"},
            {"id": "performancetracker", "name": "Tracker de Performance", "category": "Performance"},
            {"id": "rrhh_coordinator", "name": "Coordinador RRHH", "category": "Coordinacion"},
            {"id": "selectioncvia", "name": "Seleccion CV IA", "category": "Reclutamiento"},
            {"id": "talentoprediccion", "name": "Prediccion de Talento", "category": "Talento"},
            {"id": "talentopredictor", "name": "Predictor de Talento", "category": "Talento"}
        ]
    }

# --- EDUCACION CORE (9 agentes) ---
@app.get("/api/catalog/educacion/agents")
async def get_educacion_agents():
    return {
        "total": 9,
        "core": "educacion",
        "display_name": "Educacion Adaptativa",
        "agents": [
            {"id": "competenciasia", "name": "Competencias IA", "category": "Competencias"},
            {"id": "contenidopersonalizado", "name": "Contenido Personalizado", "category": "Contenido"},
            {"id": "curriculumadaptativo", "name": "Curriculum Adaptativo", "category": "Curriculum"},
            {"id": "cursosautomaticos", "name": "Cursos Automaticos", "category": "Cursos"},
            {"id": "educacion_coordinator", "name": "Coordinador Educacion", "category": "Coordinacion"},
            {"id": "evaluacionadaptativa", "name": "Evaluacion Adaptativa", "category": "Evaluacion"},
            {"id": "evaluacionia", "name": "Evaluacion IA", "category": "Evaluacion"},
            {"id": "progresionestudiante", "name": "Progresion Estudiante", "category": "Progreso"},
            {"id": "tutorvirtualia", "name": "Tutor Virtual IA", "category": "Tutoria"}
        ]
    }

# --- INVESTIGACION CORE (9 agentes) ---
@app.get("/api/catalog/investigacion/agents")
async def get_investigacion_agents():
    return {
        "total": 9,
        "core": "investigacion",
        "display_name": "Investigacion I+D",
        "agents": [
            {"id": "analisistendencias", "name": "Analisis de Tendencias", "category": "Tendencias"},
            {"id": "innovacionia", "name": "Innovacion IA", "category": "Innovacion"},
            {"id": "innovaciontracker", "name": "Tracker de Innovacion", "category": "Innovacion"},
            {"id": "investigacion_coordinator", "name": "Coordinador Investigacion", "category": "Coordinacion"},
            {"id": "patentesanalyzer", "name": "Analizador de Patentes", "category": "Patentes"},
            {"id": "patentesautomaticos", "name": "Patentes Automaticas", "category": "Patentes"},
            {"id": "prototipogenerator", "name": "Generador Prototipos", "category": "Prototipos"},
            {"id": "prototiposgenerativos", "name": "Prototipos Generativos", "category": "Prototipos"},
            {"id": "tendenciasia", "name": "Tendencias IA", "category": "Tendencias"}
        ]
    }

# --- VENTASCRM CORE (9 agentes) ---
@app.get("/api/catalog/ventascrm/agents")
async def get_ventascrm_agents():
    return {
        "total": 9,
        "core": "ventascrm",
        "display_name": "Ventas CRM Cuantico",
        "agents": [
            {"id": "churnpredictor", "name": "Predictor de Churn", "category": "Churn"},
            {"id": "cierrepredictivoia", "name": "Cierre Predictivo IA", "category": "Cierre"},
            {"id": "clientelifecycleia", "name": "Lifecycle Cliente IA", "category": "Lifecycle"},
            {"id": "communicationbot", "name": "Bot de Comunicacion", "category": "Comunicacion"},
            {"id": "leadscoringia", "name": "Lead Scoring IA", "category": "Leads"},
            {"id": "pipelineoptimizer", "name": "Optimizador Pipeline", "category": "Pipeline"},
            {"id": "pipelinepredictivoia", "name": "Pipeline Predictivo IA", "category": "Pipeline"},
            {"id": "upsellengine", "name": "Motor de Upsell", "category": "Upsell"},
            {"id": "ventascrm_coordinator", "name": "Coordinador Ventas", "category": "Coordinacion"}
        ]
    }

# --- REGTECH CORE (8 agentes) ---
@app.get("/api/catalog/regtech/agents")
async def get_regtech_agents():
    return {
        "total": 8,
        "core": "regtech",
        "display_name": "RegTech Compliance",
        "agents": [
            {"id": "amldetector", "name": "Detector AML", "category": "AML"},
            {"id": "amltiemporeal", "name": "AML Tiempo Real", "category": "AML"},
            {"id": "kycautomatico", "name": "KYC Automatico", "category": "KYC"},
            {"id": "monitoreotransacciones", "name": "Monitoreo Transacciones", "category": "Monitoreo"},
            {"id": "regtech_coordinator", "name": "Coordinador RegTech", "category": "Coordinacion"},
            {"id": "reportesregulatorios", "name": "Reportes Regulatorios", "category": "Reportes"},
            {"id": "reportingregulatorio", "name": "Reporting Regulatorio", "category": "Reportes"},
            {"id": "sancioneschecker", "name": "Checker de Sanciones", "category": "Sanciones"}
        ]
    }

# --- COMPLIANCE CORE (5 agentes) ---
@app.get("/api/catalog/compliance/agents")
async def get_compliance_agents():
    return {
        "total": 5,
        "core": "compliance",
        "display_name": "Compliance Core",
        "agents": [
            {"id": "auditmaster", "name": "Audit Master", "category": "Auditoria"},
            {"id": "compliancewatchdog", "name": "Compliance Watchdog", "category": "Monitoreo"},
            {"id": "compliance_coordinator", "name": "Coordinador Compliance", "category": "Coordinacion"},
            {"id": "docguardian", "name": "Doc Guardian", "category": "Documentos"},
            {"id": "regulatory_radar", "name": "Regulatory Radar", "category": "Regulatorio"}
        ]
    }

# --- DECISION CORE (5 agentes) ---
@app.get("/api/catalog/decision/agents")
async def get_decision_agents():
    return {
        "total": 5,
        "core": "decision",
        "display_name": "Motor de Decisiones",
        "agents": [
            {"id": "decision_coordinator", "name": "Coordinador Decision", "category": "Coordinacion"},
            {"id": "policyguardian", "name": "Policy Guardian", "category": "Politicas"},
            {"id": "quantumdecision", "name": "Quantum Decision", "category": "Decisiones"},
            {"id": "riskoracle", "name": "Risk Oracle", "category": "Riesgo"},
            {"id": "turboapprover", "name": "Turbo Approver", "category": "Aprobaciones"}
        ]
    }

# --- EXPERIENCIA CORE (5 agentes) ---
@app.get("/api/catalog/experiencia/agents")
async def get_experiencia_agents():
    return {
        "total": 5,
        "core": "experiencia",
        "display_name": "Experiencia Cliente",
        "agents": [
            {"id": "chatbotsupreme", "name": "Chatbot Supreme", "category": "Chatbot"},
            {"id": "customergenius", "name": "Customer Genius", "category": "Cliente"},
            {"id": "experiencia_coordinator", "name": "Coordinador Experiencia", "category": "Coordinacion"},
            {"id": "onboardingwizard", "name": "Onboarding Wizard", "category": "Onboarding"},
            {"id": "personalizationengine", "name": "Engine Personalizacion", "category": "Personalizacion"}
        ]
    }

# --- FORTALEZA CORE (5 agentes) ---
@app.get("/api/catalog/fortaleza/agents")
async def get_fortaleza_agents():
    return {
        "total": 5,
        "core": "fortaleza",
        "display_name": "Fortaleza Security",
        "agents": [
            {"id": "backupguardian", "name": "Backup Guardian", "category": "Backup"},
            {"id": "cybersentinel", "name": "Cyber Sentinel", "category": "Ciberseguridad"},
            {"id": "datavault", "name": "Data Vault", "category": "Datos"},
            {"id": "fortaleza_coordinator", "name": "Coordinador Fortaleza", "category": "Coordinacion"},
            {"id": "systemhealthmonitor", "name": "System Health Monitor", "category": "Monitoreo"}
        ]
    }

# --- INTELIGENCIA CORE (5 agentes) ---
@app.get("/api/catalog/inteligencia/agents")
async def get_inteligencia_agents():
    return {
        "total": 5,
        "core": "inteligencia",
        "display_name": "Inteligencia Neural",
        "agents": [
            {"id": "cashfloworacle", "name": "Cashflow Oracle", "category": "Cashflow"},
            {"id": "inteligencia_coordinator", "name": "Coordinador Inteligencia", "category": "Coordinacion"},
            {"id": "pricinggenius", "name": "Pricing Genius", "category": "Pricing"},
            {"id": "profitmaximizer", "name": "Profit Maximizer", "category": "Profit"},
            {"id": "roimaster", "name": "ROI Master", "category": "ROI"}
        ]
    }

# --- OPERACIONAL CORE (5 agentes) ---
@app.get("/api/catalog/operacional/agents")
async def get_operacional_agents():
    return {
        "total": 5,
        "core": "operacional",
        "display_name": "Operaciones Automaticas",
        "agents": [
            {"id": "costoptimizer", "name": "Cost Optimizer", "category": "Costos"},
            {"id": "operacional_coordinator", "name": "Coordinador Operacional", "category": "Coordinacion"},
            {"id": "processgenius", "name": "Process Genius", "category": "Procesos"},
            {"id": "qualitycontroller", "name": "Quality Controller", "category": "Calidad"},
            {"id": "workflowmaster", "name": "Workflow Master", "category": "Workflows"}
        ]
    }

# --- ORCHESTRATION CORE (5 agentes) ---
@app.get("/api/catalog/orchestration/agents")
async def get_orchestration_agents():
    return {
        "total": 5,
        "core": "orchestration",
        "display_name": "Orchestration Center",
        "agents": [
            {"id": "coordinator", "name": "Coordinator", "category": "Coordinacion"},
            {"id": "healthchecker", "name": "Health Checker", "category": "Health"},
            {"id": "loadbalancer", "name": "Load Balancer", "category": "Balance"},
            {"id": "orchestrationmaster", "name": "Orchestration Master", "category": "Orquestacion"},
            {"id": "resourcemanager", "name": "Resource Manager", "category": "Recursos"}
        ]
    }

# --- RECUPERACION CORE (5 agentes) ---
@app.get("/api/catalog/recuperacion/agents")
async def get_recuperacion_agents():
    return {
        "total": 5,
        "core": "recuperacion",
        "display_name": "Recuperacion IA",
        "agents": [
            {"id": "collectionmaster", "name": "Collection Master", "category": "Cobranza"},
            {"id": "legalpathway", "name": "Legal Pathway", "category": "Legal"},
            {"id": "negotiationbot", "name": "Negotiation Bot", "category": "Negociacion"},
            {"id": "recoveryoptimizer", "name": "Recovery Optimizer", "category": "Optimizacion"},
            {"id": "recuperacion_coordinator", "name": "Coordinador Recuperacion", "category": "Coordinacion"}
        ]
    }

# --- VIGILANCIA CORE (4 agentes) ---
@app.get("/api/catalog/vigilancia/agents")
async def get_vigilancia_agents():
    return {
        "total": 4,
        "core": "vigilancia",
        "display_name": "Vigilancia Continua",
        "agents": [
            {"id": "earlywarning", "name": "Early Warning", "category": "Alertas"},
            {"id": "marketradar", "name": "Market Radar", "category": "Mercado"},
            {"id": "portfoliosentinel", "name": "Portfolio Sentinel", "category": "Portfolio"},
            {"id": "vigilancia_coordinator", "name": "Coordinador Vigilancia", "category": "Coordinacion"}
        ]
    }

# ============================================================================
# GENERIC CATALOG ENDPOINT (fallback for any core)
# ============================================================================

@app.get("/api/catalog/{core_id}/agents")
async def get_core_agents_generic(core_id: str):
    """Endpoint generico para obtener agentes de cualquier core"""
    if core_id not in registry.cores:
        raise HTTPException(404, f"Core '{core_id}' not found")
    
    agents = registry.get_agents_by_core(core_id)
    return {
        "total": len(agents),
        "core": core_id,
        "agents": [{"id": a["id"], "name": a["name"], "category": "General"} for a in agents]
    }

