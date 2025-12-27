"""
NADAKKI AI SUITE v4.0.0 - Enterprise AI Platform
185+ Agents across 20 AI Cores
"""

from fastapi import FastAPI, Header, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import hashlib
import json
import importlib
from uuid import uuid4

# ============================================================================
# SETUP
# ============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("NadakkiAISuite")
workflow_logger = logging.getLogger("WorkflowEngine")

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


# ============================================================================
# ============================================================================
# WORKFLOW ENGINE - Campaign Optimization v1.0.0
# Enterprise-grade workflow orchestration
# ============================================================================
# ============================================================================

# Crear router específico para workflows
workflow_router = APIRouter(prefix="/workflows", tags=["workflows"])

# Workflow Configuration
WORKFLOW_CAMPAIGN_OPTIMIZATION = {
    "id": "campaign-optimization",
    "name": "Campaign Optimization Workflow",
    "version": "1.0.0",
    "description": "Optimiza campañas de marketing usando 5 agentes especializados en secuencia",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "audiencesegmenteria", "name": "Audience Analysis", "required": True},
        {"order": 2, "core": "marketing", "agent": "leadscoria", "name": "Lead Scoring", "required": True},
        {"order": 3, "core": "marketing", "agent": "abtestingimpactia", "name": "A/B Test Strategy", "required": False},
        {"order": 4, "core": "marketing", "agent": "campaignoptimizeria", "name": "Campaign Design", "required": True},
        {"order": 5, "core": "marketing", "agent": "budgetforecastia", "name": "Budget Allocation", "required": True}
    ]
}

# Workflow Request Models
class CampaignBrief(BaseModel):
    name: str = Field(default="Unnamed Campaign", description="Nombre de la campaña")
    objective: str = Field(default="lead_generation", description="Objetivo")
    channel: str = Field(default="email", description="Canal principal")
    target_audience: str = Field(default="", description="Audiencia objetivo")

class WorkflowRequest(BaseModel):
    campaign_brief: CampaignBrief = Field(default_factory=CampaignBrief)
    leads: List[Dict] = Field(default=[], description="Lista de leads")
    leads_count: int = Field(default=0, description="Cantidad de leads")
    budget: float = Field(default=0, description="Presupuesto total")
    ab_test_data: Dict = Field(default={}, description="Datos de A/B testing")
    include_ab_strategy: bool = Field(default=True, description="Incluir A/B testing")
    target_criteria: Dict = Field(default={}, description="Criterios de segmentación")
    scoring_criteria: Dict = Field(default={}, description="Criterios de scoring")

# Utility Functions
def generate_hash(data: Any) -> str:
    """Genera hash SHA256 para auditoría"""
    try:
        return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()[:16]
    except:
        return "hash_error"

def safe_get(data: Dict, *keys, default=None):
    """Obtiene valor anidado de forma segura"""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result is not None else default

# Agent Execution (using same pattern as main endpoint)
async def execute_agent_internal(core: str, agent_id: str, input_data: Dict, tenant_id: str = "workflow") -> Dict:
    """Ejecuta un agente usando el mismo patrón que el endpoint principal"""
    try:
        module = importlib.import_module(f'agents.{core}.{agent_id}')
        
        if not hasattr(module, 'execute') or not callable(module.execute):
            return {"status": "error", "error": f"Agent {core}.{agent_id} has no execute function"}
        
        prepared_input = input_data.copy() if isinstance(input_data, dict) else {}
        if 'tenant_id' not in prepared_input:
            prepared_input['tenant_id'] = tenant_id
        
        context = {'tenant_id': tenant_id}
        result = module.execute({'input_data': prepared_input}, context)
        
        return result
        
    except ImportError as e:
        workflow_logger.error(f"Failed to import agent {core}.{agent_id}: {e}")
        return {"status": "error", "error": f"Agent module not found: {core}.{agent_id}"}
    except Exception as e:
        workflow_logger.error(f"Agent execution failed {core}.{agent_id}: {e}")
        return {"status": "error", "error": str(e)}

# Workflow Step Execution
async def execute_workflow_step(workflow_id: str, step_config: Dict, input_data: Dict, tenant_id: str = "workflow") -> Dict:
    """Ejecuta un paso del workflow con auditoría completa"""
    step_id = f"{workflow_id}-step{step_config['order']}"
    started_at = datetime.utcnow()
    
    core = step_config["core"]
    agent_id = step_config["agent"]
    
    workflow_logger.info(f"Executing step {step_id}: {core}.{agent_id}")
    
    try:
        result = await execute_agent_internal(core, agent_id, input_data, tenant_id)
        
        if result.get("status") == "success":
            status = "success"
        elif result.get("status") == "error":
            status = "error"
        elif result.get("_decision_layer_applied") or result.get("decision"):
            status = "success"
        else:
            status = "warning"
            
    except Exception as e:
        result = {"status": "error", "error": str(e)}
        status = "error"
    
    completed_at = datetime.utcnow()
    duration_ms = (completed_at - started_at).total_seconds() * 1000
    
    return {
        "step_id": step_id,
        "step_order": step_config["order"],
        "step_name": step_config["name"],
        "agent": f"{core}.{agent_id}",
        "required": step_config.get("required", True),
        "status": status,
        "started_at": started_at.isoformat() + "Z",
        "completed_at": completed_at.isoformat() + "Z",
        "duration_ms": round(duration_ms, 2),
        "input_hash": generate_hash(input_data),
        "output_hash": generate_hash(result),
        "result": result
    }

# Summary & Recommendations
def generate_workflow_summary(steps: List[Dict]) -> Dict:
    """Genera resumen ejecutivo del workflow"""
    successful = sum(1 for s in steps if s["status"] in ["success", "skipped"])
    failed = sum(1 for s in steps if s["status"] == "error")
    total_duration = sum(s.get("duration_ms", 0) for s in steps)
    
    roi_estimate = 0
    confidence_values = []
    
    for step in steps:
        result = step.get("result", {})
        business_impact = result.get("business_impact", {})
        if business_impact.get("roi_estimate"):
            roi_estimate = business_impact["roi_estimate"]
        decision = result.get("decision", {})
        if decision.get("confidence"):
            confidence_values.append(decision["confidence"])
    
    return {
        "steps_completed": f"{successful}/{len(steps)}",
        "steps_failed": failed,
        "total_duration_ms": round(total_duration, 2),
        "estimated_roi": roi_estimate,
        "average_confidence": round(sum(confidence_values)/len(confidence_values), 3) if confidence_values else 0,
        "workflow_status": "success" if failed == 0 else ("partial" if successful > 0 else "failed")
    }

def extract_recommendations(steps: List[Dict]) -> List[Dict]:
    """Extrae recomendaciones accionables"""
    recommendations = []
    
    for step in steps:
        if step["status"] == "skipped":
            continue
        result = step.get("result", {})
        decision = result.get("decision", {})
        if decision:
            recommendations.append({
                "source": step["step_name"],
                "source_agent": step["agent"],
                "action": decision.get("action", "REVIEW"),
                "priority": decision.get("priority", "MEDIUM"),
                "confidence": decision.get("confidence", 0),
                "explanation": decision.get("explanation", ""),
                "next_steps": decision.get("next_steps", []),
                "expected_impact": decision.get("expected_impact", {})
            })
    
    priority_order = {"HIGH": 0, "CRITICAL": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "LOW"), 2))
    
    return recommendations

# Main Workflow Endpoint
@workflow_router.post("/campaign-optimization")
async def workflow_campaign_optimization(request: WorkflowRequest):
    """
    🚀 Workflow de Optimización de Campañas
    
    Orquesta 5 agentes especializados:
    1. audiencesegmenteria - Análisis de audiencias
    2. leadscoria - Scoring de leads
    3. abtestingimpactia - Estrategia A/B (opcional)
    4. campaignoptimizeria - Diseño de campaña
    5. budgetforecastia - Presupuesto y ROI
    """
    workflow_id = f"WF-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_logger.info(f"Starting workflow {workflow_id}")
    
    workflow_result = {
        "workflow_id": workflow_id,
        "workflow_name": WORKFLOW_CAMPAIGN_OPTIMIZATION["name"],
        "workflow_version": WORKFLOW_CAMPAIGN_OPTIMIZATION["version"],
        "tenant_id": tenant_id,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "input_summary": {
            "campaign_name": request.campaign_brief.name,
            "objective": request.campaign_brief.objective,
            "channel": request.campaign_brief.channel,
            "budget": request.budget,
            "leads_count": request.leads_count or len(request.leads),
            "include_ab_strategy": request.include_ab_strategy
        },
        "steps": [],
        "status": "running"
    }
    
    try:
        # PASO 1: AUDIENCE SEGMENTATION
        step1_input = {
            "campaign_brief": request.campaign_brief.dict(),
            "leads": request.leads,
            "leads_count": request.leads_count or len(request.leads),
            "target_criteria": request.target_criteria,
            "channel": request.campaign_brief.channel
        }
        step1 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][0], step1_input, tenant_id)
        workflow_result["steps"].append(step1)
        if step1["required"] and step1["status"] == "error":
            raise Exception(f"Required step failed: {step1['step_name']}")
        
        # PASO 2: LEAD SCORING
        step2_input = {
            "segments": safe_get(step1, "result", "segments", default=[]),
            "segment_distribution": safe_get(step1, "result", "segment_distribution", default={}),
            "leads": request.leads,
            "scoring_criteria": request.scoring_criteria,
            "channel": request.campaign_brief.channel
        }
        step2 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][1], step2_input, tenant_id)
        workflow_result["steps"].append(step2)
        if step2["required"] and step2["status"] == "error":
            raise Exception(f"Required step failed: {step2['step_name']}")
        
        # PASO 3: A/B TEST STRATEGY (Opcional)
        if request.include_ab_strategy or request.ab_test_data:
            step3_input = {
                "segments": safe_get(step1, "result", "segments", default=[]),
                "lead_scores": safe_get(step2, "result", "scores", default={}),
                "ab_test_data": request.ab_test_data if request.ab_test_data else {
                    "variant_a": {"clicks": 100, "conversions": 10, "impressions": 1000},
                    "variant_b": {"clicks": 120, "conversions": 12, "impressions": 1000}
                },
                "channel": request.campaign_brief.channel,
                "test_name": f"{request.campaign_brief.name}_ab_test"
            }
            step3 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][2], step3_input, tenant_id)
            workflow_result["steps"].append(step3)
        else:
            workflow_result["steps"].append({
                "step_id": f"{workflow_id}-step3",
                "step_order": 3,
                "step_name": "A/B Test Strategy",
                "agent": "marketing.abtestingimpactia",
                "required": False,
                "status": "skipped",
                "reason": "A/B testing not requested",
                "result": {}
            })
        
        # PASO 4: CAMPAIGN DESIGN
        step4_input = {
            "segments": safe_get(step1, "result", "segments", default=[]),
            "lead_scores": safe_get(step2, "result", "scores", default={}),
            "lead_category": safe_get(step2, "result", "category", default=""),
            "ab_recommendations": safe_get(workflow_result["steps"][2], "result", "test_results", default={}),
            "campaign_brief": request.campaign_brief.dict(),
            "budget": request.budget,
            "channel": request.campaign_brief.channel
        }
        step4 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][3], step4_input, tenant_id)
        workflow_result["steps"].append(step4)
        if step4["required"] and step4["status"] == "error":
            raise Exception(f"Required step failed: {step4['step_name']}")
        
        # PASO 5: BUDGET ALLOCATION
        step5_input = {
            "optimized_campaign": safe_get(step4, "result", default={}),
            "segments": safe_get(step1, "result", "segments", default=[]),
            "total_budget": request.budget,
            "channel": request.campaign_brief.channel,
            "campaign_name": request.campaign_brief.name
        }
        step5 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][4], step5_input, tenant_id)
        workflow_result["steps"].append(step5)
        if step5["required"] and step5["status"] == "error":
            raise Exception(f"Required step failed: {step5['step_name']}")
        
        # CONSOLIDACIÓN
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        workflow_result["recommendations"] = extract_recommendations(workflow_result["steps"])
        workflow_result["audit_trail"] = {
            "workflow_input_hash": generate_hash(request.dict()),
            "workflow_output_hash": generate_hash(workflow_result["steps"]),
            "steps_executed": len([s for s in workflow_result["steps"] if s["status"] != "skipped"]),
            "total_duration_ms": workflow_result["summary"]["total_duration_ms"]
        }
        
        workflow_logger.info(f"Workflow {workflow_id} completed successfully")
        return workflow_result
        
    except Exception as e:
        workflow_logger.error(f"Workflow {workflow_id} failed: {e}")
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result


# ============================================================================
# ============================================================================
# WORKFLOW #2: CUSTOMER ACQUISITION INTELLIGENCE v1.1.0
# ============================================================================
# ============================================================================

WORKFLOW_CUSTOMER_ACQUISITION = {
    "id": "customer-acquisition-intelligence",
    "name": "Customer Acquisition Intelligence",
    "version": "1.1.0",
    "description": "Pipeline inteligente de adquisición: segmenta, predice, califica, prioriza y activa leads de alto valor",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "audiencesegmenteria", "name": "Audience Segmentation", "phase": "TARGETING", "required": True},
        {"order": 2, "core": "marketing", "agent": "geosegmentationia", "name": "Geo Segmentation", "phase": "TARGETING", "required": False},
        {"order": 3, "core": "marketing", "agent": "predictiveleadia", "name": "Predictive Lead Analysis", "phase": "INTENT", "required": True},
        {"order": 4, "core": "marketing", "agent": "contactqualityia", "name": "Contact Quality Validation", "phase": "QUALITY", "required": True},
        {"order": 5, "core": "marketing", "agent": "leadscoria", "name": "Lead Scoring Primary", "phase": "SCORING", "required": True},
        {"order": 6, "core": "marketing", "agent": "leadscoringia", "name": "Lead Scoring Validation", "phase": "SCORING", "required": True},
        {"order": 7, "core": "marketing", "agent": "conversioncohortia", "name": "Conversion Cohort Analysis", "phase": "ACTIVATION", "required": True}
    ],
    "user_phases": [
        {"id": "TARGETING", "name": "🎯 Targeting", "description": "¿A quién atacamos?", "agents": ["audiencesegmenteria", "geosegmentationia"]},
        {"id": "INTENT", "name": "🔮 Intent Analysis", "description": "¿Quién tiene alta propensión?", "agents": ["predictiveleadia"]},
        {"id": "QUALITY", "name": "✅ Quality Gate", "description": "¿La data es confiable?", "agents": ["contactqualityia"]},
        {"id": "SCORING", "name": "📊 Scoring", "description": "¿Cuál es la prioridad?", "agents": ["leadscoria", "leadscoringia"]},
        {"id": "ACTIVATION", "name": "🚀 Activation", "description": "¿Cómo los activamos?", "agents": ["conversioncohortia"]}
    ],
    "scoring_resolution": {
        "strategy": "PRIMARY_WITH_VALIDATION",
        "conflict_threshold": 15,
        "confidence_penalty_on_conflict": 0.2,
        "rules": {
            "no_conflict": "difference <= 15% → use average, full confidence",
            "mild_conflict": "15% < difference <= 25% → use primary, -10% confidence",
            "severe_conflict": "difference > 25% → flag for review, -20% confidence"
        }
    }
}

class AcquisitionRequest(BaseModel):
    target_market: str = Field(default="B2B", description="B2B, B2C, or Both")
    industry_focus: List[str] = Field(default=[], description="Industries to target")
    company_size: List[str] = Field(default=["SMB", "MidMarket"], description="Company sizes")
    regions: List[str] = Field(default=[], description="Target regions")
    leads: List[Dict] = Field(default=[], description="Existing leads to analyze")
    leads_count: int = Field(default=0, description="Number of leads")
    min_quality_score: float = Field(default=0.5, description="Minimum quality threshold")
    auto_activate: bool = Field(default=False, description="Auto-trigger downstream workflows")
    confidence_threshold: float = Field(default=0.7, description="Min confidence for activation")

def resolve_scoring_conflict(primary_result: Dict, secondary_result: Dict) -> Dict:
    """Árbitro de conflictos entre leadscoria y leadscoringia"""
    config = WORKFLOW_CUSTOMER_ACQUISITION["scoring_resolution"]
    threshold = config["conflict_threshold"] / 100
    penalty = config["confidence_penalty_on_conflict"]
    
    primary_score = safe_get(primary_result, "result", "scores", "final_score", default=0)
    if primary_score == 0:
        primary_score = safe_get(primary_result, "result", "conversion_probability", default=0.5)
    
    secondary_score = safe_get(secondary_result, "result", "scores", "final_score", default=0)
    if secondary_score == 0:
        secondary_score = safe_get(secondary_result, "result", "conversion_probability", default=0.5)
    
    primary_conf = safe_get(primary_result, "result", "decision", "confidence", default=0.7)
    secondary_conf = safe_get(secondary_result, "result", "decision", "confidence", default=0.7)
    
    difference = abs(primary_score - secondary_score)
    difference_pct = difference * 100
    
    if difference <= threshold:
        resolution = "CONSENSUS"
        final_score = (primary_score + secondary_score) / 2
        confidence = (primary_conf + secondary_conf) / 2
        conflict_level = "NONE"
    elif difference <= threshold * 1.67:
        resolution = "PRIMARY_WINS"
        final_score = primary_score
        confidence = primary_conf - (penalty * 0.5)
        conflict_level = "MILD"
    else:
        resolution = "REVIEW_REQUIRED"
        final_score = primary_score
        confidence = max(primary_conf, secondary_conf) - penalty
        conflict_level = "SEVERE"
    
    confidence = max(0.3, min(1.0, confidence))
    
    explanations = {
        "CONSENSUS": f"Scores within {difference_pct:.1f}% - high agreement between models",
        "PRIMARY_WINS": f"Mild conflict ({difference_pct:.1f}%) - using primary scorer with slight confidence reduction",
        "REVIEW_REQUIRED": f"Significant conflict ({difference_pct:.1f}%) - manual review recommended before activation"
    }
    
    return {
        "primary_score": round(primary_score, 3),
        "secondary_score": round(secondary_score, 3),
        "difference_pct": round(difference_pct, 1),
        "conflict_level": conflict_level,
        "resolution": resolution,
        "final_score": round(final_score, 3),
        "confidence": round(confidence, 3),
        "strategy_applied": config["strategy"],
        "explanation": explanations.get(resolution, "Unknown resolution")
    }

def generate_unified_decision(workflow_id: str, steps: List[Dict], scoring_resolution: Dict, request_data: Dict) -> Dict:
    """Genera UNA SOLA DECISIÓN unificada"""
    final_score = scoring_resolution["final_score"]
    confidence = scoring_resolution["confidence"]
    conflict_level = scoring_resolution["conflict_level"]
    
    if conflict_level == "SEVERE":
        decision = "REVIEW_BEFORE_ACTIVATION"
        priority = "MEDIUM"
    elif final_score >= 0.7 and confidence >= 0.7:
        decision = "ACTIVATE_ACQUISITION"
        priority = "HIGH"
    elif final_score >= 0.5 and confidence >= 0.6:
        decision = "NURTURE_PIPELINE"
        priority = "MEDIUM"
    elif final_score >= 0.3:
        decision = "ENRICH_AND_REANALYZE"
        priority = "LOW"
    else:
        decision = "DISQUALIFY"
        priority = "LOW"
    
    raw_segments = safe_get(steps[0], "result", "segments", default=[])
    segments = []
    for seg in raw_segments[:5]:
        segment_score = final_score + (0.1 if seg.get("segment") == "high_value" else 0)
        channels = ["EMAIL", "PAID_SEARCH", "LINKEDIN"] if segment_score > 0.7 else (["EMAIL", "CONTENT"] if segment_score > 0.5 else ["CONTENT", "ORGANIC"])
        segments.append({
            "segment": seg.get("segment", "unknown"),
            "size": seg.get("count", 0),
            "priority": "HIGH" if segment_score > 0.7 else ("MEDIUM" if segment_score > 0.5 else "LOW"),
            "expected_cvr": round(segment_score * 0.22, 3),
            "expected_ltv": round(segment_score * 5500, 0),
            "recommended_channels": channels
        })
    
    total_leads = sum(s.get("size", 0) for s in segments) or request_data.get("leads_count", 100)
    qualified = int(total_leads * final_score)
    pipeline_value = qualified * 5000
    
    actions_map = {
        "ACTIVATE_ACQUISITION": ["emailautomationia", "campaignoptimizeria", "sync_to_crm", "alert_sales_team"],
        "NURTURE_PIPELINE": ["content-performance-engine", "emailautomationia", "schedule_reanalysis_14d"],
        "ENRICH_AND_REANALYZE": ["enrich_from_clearbit", "enrich_from_zoominfo", "schedule_reanalysis_7d"],
        "REVIEW_BEFORE_ACTIVATION": ["create_review_task", "notify_marketing_ops", "hold_automation"],
        "DISQUALIFY": ["archive_leads", "update_exclusion_list"]
    }
    
    valid_days = 7 if decision == "ACTIVATE_ACQUISITION" else 14
    valid_until = (datetime.utcnow() + timedelta(days=valid_days)).isoformat() + "Z"
    
    return {
        "decision": decision,
        "confidence": confidence,
        "valid_until": valid_until,
        "segments": segments,
        "lead_summary": {
            "total_analyzed": total_leads,
            "qualified": qualified,
            "disqualified": total_leads - qualified,
            "qualification_rate": round(final_score, 3)
        },
        "next_actions": actions_map.get(decision, ["manual_review"]),
        "business_impact": {
            "pipeline_value": pipeline_value,
            "expected_roi": round(2.5 + (confidence * 2), 1),
            "payback_days": 35 - int(confidence * 15)
        },
        "scoring_metadata": {
            "resolution": scoring_resolution["resolution"],
            "conflict_level": conflict_level,
            "explanation": scoring_resolution["explanation"]
        }
    }

@workflow_router.post("/customer-acquisition-intelligence")
async def workflow_customer_acquisition(request: AcquisitionRequest):
    """
    🎯 Customer Acquisition Intelligence Workflow v1.1.0
    
    SECUENCIA (ORDEN CORREGIDO):
    1. audiencesegmenteria    → ¿Quiénes son mis mercados?
    2. geosegmentationia      → ¿Dónde están? (opcional)
    3. predictiveleadia       → ¿Quién tiene alta propensión?
    4. contactqualityia       → ¿La data es confiable?
    5. leadscoria             → Scoring primario
    6. leadscoringia          → Validación scoring
    7. conversioncohortia     → Análisis de cohortes
    
    OUTPUT: Una decisión unificada, no 7 outputs.
    """
    workflow_id = f"CAI-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_logger.info(f"Starting Customer Acquisition Intelligence: {workflow_id}")
    
    workflow_result = {
        "workflow_id": workflow_id,
        "workflow_name": WORKFLOW_CUSTOMER_ACQUISITION["name"],
        "workflow_version": WORKFLOW_CUSTOMER_ACQUISITION["version"],
        "tenant_id": tenant_id,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "request_summary": {
            "target_market": request.target_market,
            "industries": request.industry_focus,
            "regions": request.regions,
            "leads_count": len(request.leads) or request.leads_count
        },
        "phases": [],
        "steps": [],
        "status": "running"
    }
    
    try:
        # STEP 1: AUDIENCE SEGMENTATION
        step1_input = {
            "target_market": request.target_market,
            "industries": request.industry_focus,
            "company_sizes": request.company_size,
            "leads": request.leads,
            "leads_count": request.leads_count or len(request.leads)
        }
        step1 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][0], step1_input, tenant_id)
        workflow_result["steps"].append(step1)
        if step1["required"] and step1["status"] == "error":
            raise Exception(f"Required step failed: {step1['step_name']}")
        
        # STEP 2: GEO SEGMENTATION (opcional)
        if request.regions:
            step2_input = {"segments": safe_get(step1, "result", "segments", default=[]), "regions": request.regions}
            step2 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][1], step2_input, tenant_id)
        else:
            step2 = {"step_id": f"{workflow_id}-step2", "step_order": 2, "step_name": "Geo Segmentation", "status": "skipped", "reason": "No regions specified", "result": {}}
        workflow_result["steps"].append(step2)
        
        # STEP 3: PREDICTIVE LEAD ANALYSIS
        step3_input = {"segments": safe_get(step1, "result", "segments", default=[]), "leads": request.leads, "target_market": request.target_market}
        step3 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][2], step3_input, tenant_id)
        workflow_result["steps"].append(step3)
        if step3["required"] and step3["status"] == "error":
            raise Exception(f"Required step failed: {step3['step_name']}")
        
        # STEP 4: CONTACT QUALITY
        step4_input = {"segments": safe_get(step1, "result", "segments", default=[]), "predictions": safe_get(step3, "result", default={}), "leads": request.leads, "min_quality": request.min_quality_score}
        step4 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][3], step4_input, tenant_id)
        workflow_result["steps"].append(step4)
        if step4["required"] and step4["status"] == "error":
            raise Exception(f"Required step failed: {step4['step_name']}")
        
        # STEP 5: LEAD SCORING PRIMARY
        step5_input = {"segments": safe_get(step1, "result", "segments", default=[]), "predictions": safe_get(step3, "result", default={}), "quality_data": safe_get(step4, "result", default={}), "leads": request.leads}
        step5 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][4], step5_input, tenant_id)
        workflow_result["steps"].append(step5)
        if step5["required"] and step5["status"] == "error":
            raise Exception(f"Required step failed: {step5['step_name']}")
        
        # STEP 6: LEAD SCORING VALIDATION
        step6_input = {"segments": safe_get(step1, "result", "segments", default=[]), "primary_scores": safe_get(step5, "result", "scores", default={}), "leads": request.leads, "validation_mode": True}
        step6 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][5], step6_input, tenant_id)
        workflow_result["steps"].append(step6)
        if step6["required"] and step6["status"] == "error":
            raise Exception(f"Required step failed: {step6['step_name']}")
        
        # SCORING RESOLUTION (ÁRBITRO)
        scoring_resolution = resolve_scoring_conflict(step5, step6)
        
        # STEP 7: CONVERSION COHORT ANALYSIS
        step7_input = {"segments": safe_get(step1, "result", "segments", default=[]), "final_score": scoring_resolution["final_score"], "resolution": scoring_resolution["resolution"]}
        step7 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][6], step7_input, tenant_id)
        workflow_result["steps"].append(step7)
        if step7["required"] and step7["status"] == "error":
            raise Exception(f"Required step failed: {step7['step_name']}")
        
        # GENERATE UNIFIED DECISION
        unified_decision = generate_unified_decision(workflow_id, workflow_result["steps"], scoring_resolution, request.dict())
        
        # FINAL OUTPUT
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["decision"] = unified_decision
        
        total_duration = sum(s.get("duration_ms", 0) for s in workflow_result["steps"] if isinstance(s.get("duration_ms"), (int, float)))
        workflow_result["summary"] = {
            "steps_executed": len([s for s in workflow_result["steps"] if s.get("status") != "skipped"]),
            "total_duration_ms": round(total_duration, 2),
            "final_decision": unified_decision["decision"],
            "confidence": unified_decision["confidence"],
            "pipeline_value": unified_decision["business_impact"]["pipeline_value"]
        }
        
        workflow_result["audit_trail"] = {
            "workflow_input_hash": generate_hash(request.dict()),
            "decision_hash": generate_hash(unified_decision),
            "scoring_resolution": scoring_resolution["resolution"],
            "conflict_level": scoring_resolution["conflict_level"]
        }
        
        workflow_logger.info(f"Workflow {workflow_id} completed: {unified_decision['decision']} (confidence: {unified_decision['confidence']})")
        return workflow_result
        
    except Exception as e:
        workflow_logger.error(f"Workflow {workflow_id} failed: {e}")
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result

@workflow_router.get("/customer-acquisition-intelligence/schema")
async def acquisition_schema():
    """Schema del workflow Customer Acquisition"""
    return {
        "workflow": {
            "id": WORKFLOW_CUSTOMER_ACQUISITION["id"],
            "name": WORKFLOW_CUSTOMER_ACQUISITION["name"],
            "version": WORKFLOW_CUSTOMER_ACQUISITION["version"],
            "agents_count": 7,
            "phases": WORKFLOW_CUSTOMER_ACQUISITION["user_phases"]
        },
        "scoring_resolution": WORKFLOW_CUSTOMER_ACQUISITION["scoring_resolution"],
        "example_request": {
            "target_market": "B2B",
            "industry_focus": ["technology", "finance"],
            "company_size": ["SMB", "MidMarket"],
            "regions": ["US", "LATAM"],
            "auto_activate": False
        },
        "possible_decisions": ["ACTIVATE_ACQUISITION", "NURTURE_PIPELINE", "ENRICH_AND_REANALYZE", "REVIEW_BEFORE_ACTIVATION", "DISQUALIFY"]
    }

@workflow_router.get("/")
async def list_all_workflows():
    """Lista todos los workflows disponibles"""
    return {
        "workflows": [
            {
                "id": "campaign-optimization",
                "name": "Campaign Optimization",
                "version": "1.0.0",
                "tier": "CORE",
                "agents": 5,
                "status": "active",
                "endpoint": "/workflows/campaign-optimization"
            },
            {
                "id": "customer-acquisition-intelligence",
                "name": "Customer Acquisition Intelligence",
                "version": "1.1.0",
                "tier": "CORE",
                "agents": 7,
                "status": "active",
                "endpoint": "/workflows/customer-acquisition-intelligence"
            }
        ],
        "total": 2,
        "pending_workflows": [
            "customer-lifecycle-revenue",
            "content-performance-engine",
            "social-media-intelligence",
            "email-automation-master",
            "multi-channel-attribution",
            "competitive-intelligence-hub",
            "ab-testing-experimentation",
            "influencer-partnership-engine"
        ]
    }

@workflow_router.get("/campaign-optimization/schema")
async def workflow_schema():
    """Schema del workflow Campaign Optimization"""
    return {
        "workflow": WORKFLOW_CAMPAIGN_OPTIMIZATION,
        "example_request": {
            "campaign_brief": {"name": "Q1 2025 Campaign", "objective": "lead_generation", "channel": "email"},
            "budget": 10000,
            "include_ab_strategy": True
        }
    }

@workflow_router.get("/health")
async def workflow_health():
    """Health check del workflow engine"""
    return {"status": "healthy", "engine_version": "1.1.0", "workflows_available": 2}

# Integrar el workflow router en la app
app.include_router(workflow_router)


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
    logger.info("🔄 Workflows at http://localhost:8000/workflows")
    logger.info("=" * 60)
