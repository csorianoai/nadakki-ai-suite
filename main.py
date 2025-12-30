"""
NADAKKI AI SUITE v4.0.0 - Enterprise AI Platform
185+ Agents across 20 AI Cores
10 Marketing Workflows
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
from multitenant_integration import register_tenant_routes
from decision_logger import register_decision_log_routes, log_workflow_decision
from dashboard_metrics import register_enhanced_dashboard_routes

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

# Registrar rutas multi-tenant
register_tenant_routes(app)
register_decision_log_routes(app)
register_enhanced_dashboard_routes(app)

# ============================================================================
# AGENT REGISTRY
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
# BASE ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Nadakki AI Suite",
        "version": "4.0.0",
        "status": "operational",
        "total_agents": registry.total,
        "total_cores": len(registry.cores),
        "workflows_available": 10,
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
        raise HTTPException(404, f"Agent not found: {core}/{agent_id}")
    
    agent_key = f"{core}.{agent_id}"

    try:
        import importlib as _imp
        _mod = _imp.import_module(f'agents.{core}.{agent_id}')
        if hasattr(_mod, 'execute') and callable(_mod.execute):
            _in = request.input_data or {}
            if isinstance(_in, dict) and 'tenant_id' not in _in:
                _in['tenant_id'] = tenant['tenant_id']
            _ctx = {'tenant_id': tenant['tenant_id']}
            _res = _mod.execute({'input_data': _in}, _ctx)
            return {'agent': agent_key, 'agent_name': agent_id.title(), 'tenant': tenant['tenant_id'], 'timestamp': str(datetime.utcnow()), 'result': _res}
    except Exception as _e:
        pass

    try:
        instance = registry.create_instance(agent_key, tenant["tenant_id"])
        if not instance:
            raise HTTPException(503, f"Agent not instantiable: {agent.get('error', 'Unknown error')}")
        
        input_data = request.input_data or {}
        if isinstance(input_data, dict) and "tenant_id" not in input_data:
            input_data["tenant_id"] = tenant["tenant_id"]
        
        result = None
        methods_to_try = ["execute", "run", "process", "analyze", "score", "personalize", "optimize", "generate", "predict"]
        
        for method_name in methods_to_try:
            if hasattr(instance, method_name):
                method = getattr(instance, method_name)
                if callable(method):
                    try:
                        method_result = method(input_data)
                        import asyncio
                        if asyncio.iscoroutine(method_result):
                            result = await method_result
                        else:
                            result = method_result
                        break
                    except TypeError as te:
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
                            raise
                    except AttributeError as ae:
                        return {
                            "agent": agent_key,
                            "agent_name": agent.get("name"),
                            "tenant": tenant["tenant_id"],
                            "timestamp": datetime.now().isoformat(),
                            "status": "input_schema_error",
                            "error": str(ae),
                            "message": "Agent requires typed input."
                        }
        
        if result is None:
            result = {"status": "executed", "message": "Agent processed but returned no result"}
        
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
        logger.error(f"Error executing {agent_key}: {str(e)}")
        return {
            "agent": agent_key,
            "tenant": tenant["tenant_id"],
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }

@app.get("/usage/{tenant_id}")
async def get_usage(tenant_id: str, tenant: Dict = Depends(verify_tenant)):
    return rate_limiter.usage(tenant_id)

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
# CATALOG ENDPOINTS - Marketing Module
# ============================================================================

@app.get("/api/catalog/marketing")
async def get_marketing_catalog():
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
                module = importlib.import_module(f'agents.marketing.{agent_id}')
                status = "active" if hasattr(module, 'execute') else "inactive"
                version = getattr(module, 'VERSION', '3.2.0')
            except:
                status = "error"
                version = "unknown"
            enriched_agents[agent_id] = {**agent_info, "status": status, "version": version, "endpoint": f"/agents/marketing/{agent_id}/execute"}
        
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
    return {
        "module": "marketing",
        "display_name": "Marketing Core",
        "total_agents": 35,
        "active_agents": 35,
        "version": "3.2.0",
        "workflows_available": 10
    }

@app.get("/api/catalog/marketing/agents")
async def get_marketing_agents_list():
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
# CATALOG ENDPOINTS - ALL OTHER CORES
# ============================================================================

@app.get("/api/catalog/legal/agents")
async def get_legal_agents():
    return {"total": 32, "core": "legal", "display_name": "Legal AI System", "agents": [
        {"id": "derechoadministrativo", "name": "Derecho Administrativo"},
        {"id": "derechoadministrativophd", "name": "Derecho Administrativo PhD"},
        {"id": "derechoambiental", "name": "Derecho Ambiental"},
        {"id": "derechobancario", "name": "Derecho Bancario"},
        {"id": "derechocivilphd", "name": "Derecho Civil PhD"},
        {"id": "derechocomercial", "name": "Derecho Comercial"},
        {"id": "derechocomercialephd", "name": "Derecho Comercial PhD"},
        {"id": "derechoconstitucional", "name": "Derecho Constitucional"},
        {"id": "derechoconstitucionalphd", "name": "Derecho Constitucional PhD"},
        {"id": "derechocontratacion", "name": "Derecho Contratacion"},
        {"id": "derechofamiliaphd", "name": "Derecho Familia PhD"},
        {"id": "derechofamiliar", "name": "Derecho Familiar"},
        {"id": "derechofinanciero", "name": "Derecho Financiero"},
        {"id": "derechoinmobiliario", "name": "Derecho Inmobiliario"},
        {"id": "derechoinmobiliariophd", "name": "Derecho Inmobiliario PhD"},
        {"id": "derechointelectual", "name": "Derecho Intelectual"},
        {"id": "derechointernacional", "name": "Derecho Internacional"},
        {"id": "derecholaboral", "name": "Derecho Laboral"},
        {"id": "derecholaboralphd", "name": "Derecho Laboral PhD"},
        {"id": "derechomarcario", "name": "Derecho Marcario"},
        {"id": "derechomaritimo", "name": "Derecho Maritimo"},
        {"id": "derechomigratorio", "name": "Derecho Migratorio"},
        {"id": "derechominero", "name": "Derecho Minero"},
        {"id": "derechonotarial", "name": "Derecho Notarial"},
        {"id": "derechopenal", "name": "Derecho Penal"},
        {"id": "derechopenalphd", "name": "Derecho Penal PhD"},
        {"id": "derechoprocesalpenal", "name": "Derecho Procesal Penal"},
        {"id": "derechoprocesalpenalphd", "name": "Derecho Procesal Penal PhD"},
        {"id": "derechoseguros", "name": "Derecho Seguros"},
        {"id": "derechotributario", "name": "Derecho Tributario"},
        {"id": "derechotributariophd", "name": "Derecho Tributario PhD"},
        {"id": "legal_coordinator", "name": "Coordinador Legal"}
    ]}

@app.get("/api/catalog/logistica/agents")
async def get_logistica_agents():
    return {"total": 23, "core": "logistica", "display_name": "Logistica Inteligente", "agents": [
        {"id": "alertasinventario", "name": "Alertas de Inventario"},
        {"id": "almaceninteligente", "name": "Almacen Inteligente"},
        {"id": "analisisrendimiento", "name": "Analisis de Rendimiento"},
        {"id": "controlcalidad", "name": "Control de Calidad"},
        {"id": "controlcalidadia", "name": "Control Calidad IA"},
        {"id": "controlpedidosia", "name": "Control de Pedidos IA"},
        {"id": "costoslogisticos", "name": "Costos Logisticos"},
        {"id": "evaluadorproveedoresia", "name": "Evaluador de Proveedores"},
        {"id": "gestionriesgos", "name": "Gestion de Riesgos"},
        {"id": "logisticareversa", "name": "Logistica Reversa"},
        {"id": "logistica_coordinator", "name": "Coordinador Logistica"},
        {"id": "optimizacionalmacen", "name": "Optimizacion Almacen"},
        {"id": "optimizacioncostos", "name": "Optimizacion de Costos"},
        {"id": "optimizadorrutasia", "name": "Optimizador de Rutas"},
        {"id": "planificaciondemanda", "name": "Planificacion Demanda"},
        {"id": "predicciondemanda", "name": "Prediccion de Demanda"},
        {"id": "previsioninventarioia", "name": "Prevision de Inventario"},
        {"id": "seguridadcarga", "name": "Seguridad de Carga"},
        {"id": "sostenibilidadia", "name": "Sostenibilidad IA"},
        {"id": "transporteoptimizado", "name": "Transporte Optimizado"},
        {"id": "transportepredictivo", "name": "Transporte Predictivo"},
        {"id": "trazabilidadia", "name": "Trazabilidad IA"},
        {"id": "trazabilidadtotal", "name": "Trazabilidad Total"}
    ]}

@app.get("/api/catalog/contabilidad/agents")
async def get_contabilidad_agents():
    return {"total": 22, "core": "contabilidad", "display_name": "Contabilidad Cuantica", "agents": [
        {"id": "activosfijos", "name": "Activos Fijos"},
        {"id": "analisis_financiero", "name": "Analisis Financiero"},
        {"id": "analisis_financiero_super_agent", "name": "Analisis Financiero Super"},
        {"id": "auditoriainterna", "name": "Auditoria Interna"},
        {"id": "cierrecontable", "name": "Cierre Contable"},
        {"id": "compliance_contable", "name": "Compliance Contable"},
        {"id": "conciliacionbancaria", "name": "Conciliacion Bancaria"},
        {"id": "contabilidadinteligente", "name": "Contabilidad Inteligente"},
        {"id": "contabilidad_coordinator", "name": "Coordinador Contabilidad"},
        {"id": "controlgastos", "name": "Control de Gastos"},
        {"id": "dgiiautoreporter", "name": "DGII Auto Reporter"},
        {"id": "facturacionelectronica", "name": "Facturacion Electronica"},
        {"id": "facturacionia", "name": "Facturacion IA"},
        {"id": "flujocajaia", "name": "Flujo de Caja IA"},
        {"id": "flujocajaprediccion", "name": "Prediccion Flujo Caja"},
        {"id": "inventariovaloracion", "name": "Valoracion Inventario"},
        {"id": "previsionfiscal", "name": "Prevision Fiscal"},
        {"id": "reconcilia_auto", "name": "Reconciliacion Auto"},
        {"id": "reportesejecutivos", "name": "Reportes Ejecutivos"},
        {"id": "reportes_fiscales", "name": "Reportes Fiscales"},
        {"id": "reportingfinanciero", "name": "Reporting Financiero"},
        {"id": "tributarioia", "name": "Tributario IA"}
    ]}

@app.get("/api/catalog/presupuesto/agents")
async def get_presupuesto_agents():
    return {"total": 13, "core": "presupuesto", "display_name": "Presupuesto Inteligente", "agents": [
        {"id": "analisisvarianza", "name": "Analisis de Varianza"},
        {"id": "budgetoptimizer", "name": "Optimizador de Budget"},
        {"id": "controlpresupuestario", "name": "Control Presupuestario"},
        {"id": "costocentros", "name": "Centros de Costo"},
        {"id": "forecastingavanzado", "name": "Forecasting Avanzado"},
        {"id": "forecastingia", "name": "Forecasting IA"},
        {"id": "optimizacionrecursos", "name": "Optimizacion Recursos"},
        {"id": "planificacionestrategica", "name": "Planificacion Estrategica"},
        {"id": "presupuestomaestro", "name": "Presupuesto Maestro"},
        {"id": "presupuestopredictivoia", "name": "Presupuesto Predictivo"},
        {"id": "presupuesto_coordinator", "name": "Coordinador Presupuesto"},
        {"id": "roipredictor", "name": "Predictor de ROI"},
        {"id": "varianzaanalisis", "name": "Analisis Varianza"}
    ]}

@app.get("/api/catalog/originacion/agents")
async def get_originacion_agents():
    return {"total": 10, "core": "originacion", "display_name": "Originacion Neural", "agents": [
        {"id": "base_components_v2", "name": "Componentes Base v2"},
        {"id": "behaviorminer", "name": "Behavior Miner"},
        {"id": "behavior_miner_v2", "name": "Behavior Miner v2"},
        {"id": "dnaprofiler", "name": "DNA Profiler"},
        {"id": "dna_profiler_v2", "name": "DNA Profiler v2"},
        {"id": "incomeoracle", "name": "Income Oracle"},
        {"id": "income_oracle_v2", "name": "Income Oracle v2"},
        {"id": "originacion_coordinator", "name": "Coordinador Originacion"},
        {"id": "sentinelbot", "name": "Sentinel Bot"},
        {"id": "sentinel_bot_v2", "name": "Sentinel Bot v2"}
    ]}

@app.get("/api/catalog/rrhh/agents")
async def get_rrhh_agents():
    return {"total": 10, "core": "rrhh", "display_name": "Recursos Humanos IA", "agents": [
        {"id": "capacitacionia", "name": "Capacitacion IA"},
        {"id": "cvanalyzeria", "name": "Analizador de CV"},
        {"id": "nominaautomatica", "name": "Nomina Automatica"},
        {"id": "nominainteligente", "name": "Nomina Inteligente"},
        {"id": "performanceanalyzer", "name": "Analizador Performance"},
        {"id": "performancetracker", "name": "Tracker de Performance"},
        {"id": "rrhh_coordinator", "name": "Coordinador RRHH"},
        {"id": "selectioncvia", "name": "Seleccion CV IA"},
        {"id": "talentoprediccion", "name": "Prediccion de Talento"},
        {"id": "talentopredictor", "name": "Predictor de Talento"}
    ]}

@app.get("/api/catalog/educacion/agents")
async def get_educacion_agents():
    return {"total": 9, "core": "educacion", "display_name": "Educacion Adaptativa", "agents": [
        {"id": "competenciasia", "name": "Competencias IA"},
        {"id": "contenidopersonalizado", "name": "Contenido Personalizado"},
        {"id": "curriculumadaptativo", "name": "Curriculum Adaptativo"},
        {"id": "cursosautomaticos", "name": "Cursos Automaticos"},
        {"id": "educacion_coordinator", "name": "Coordinador Educacion"},
        {"id": "evaluacionadaptativa", "name": "Evaluacion Adaptativa"},
        {"id": "evaluacionia", "name": "Evaluacion IA"},
        {"id": "progresionestudiante", "name": "Progresion Estudiante"},
        {"id": "tutorvirtualia", "name": "Tutor Virtual IA"}
    ]}

@app.get("/api/catalog/investigacion/agents")
async def get_investigacion_agents():
    return {"total": 9, "core": "investigacion", "display_name": "Investigacion I+D", "agents": [
        {"id": "analisistendencias", "name": "Analisis de Tendencias"},
        {"id": "innovacionia", "name": "Innovacion IA"},
        {"id": "innovaciontracker", "name": "Tracker de Innovacion"},
        {"id": "investigacion_coordinator", "name": "Coordinador Investigacion"},
        {"id": "patentesanalyzer", "name": "Analizador de Patentes"},
        {"id": "patentesautomaticos", "name": "Patentes Automaticas"},
        {"id": "prototipogenerator", "name": "Generador Prototipos"},
        {"id": "prototiposgenerativos", "name": "Prototipos Generativos"},
        {"id": "tendenciasia", "name": "Tendencias IA"}
    ]}

@app.get("/api/catalog/ventascrm/agents")
async def get_ventascrm_agents():
    return {"total": 9, "core": "ventascrm", "display_name": "Ventas CRM Cuantico", "agents": [
        {"id": "churnpredictor", "name": "Predictor de Churn"},
        {"id": "cierrepredictivoia", "name": "Cierre Predictivo IA"},
        {"id": "clientelifecycleia", "name": "Lifecycle Cliente IA"},
        {"id": "communicationbot", "name": "Bot de Comunicacion"},
        {"id": "leadscoringia", "name": "Lead Scoring IA"},
        {"id": "pipelineoptimizer", "name": "Optimizador Pipeline"},
        {"id": "pipelinepredictivoia", "name": "Pipeline Predictivo IA"},
        {"id": "upsellengine", "name": "Motor de Upsell"},
        {"id": "ventascrm_coordinator", "name": "Coordinador Ventas"}
    ]}

@app.get("/api/catalog/regtech/agents")
async def get_regtech_agents():
    return {"total": 8, "core": "regtech", "display_name": "RegTech Compliance", "agents": [
        {"id": "amldetector", "name": "Detector AML"},
        {"id": "amltiemporeal", "name": "AML Tiempo Real"},
        {"id": "kycautomatico", "name": "KYC Automatico"},
        {"id": "monitoreotransacciones", "name": "Monitoreo Transacciones"},
        {"id": "regtech_coordinator", "name": "Coordinador RegTech"},
        {"id": "reportesregulatorios", "name": "Reportes Regulatorios"},
        {"id": "reportingregulatorio", "name": "Reporting Regulatorio"},
        {"id": "sancioneschecker", "name": "Checker de Sanciones"}
    ]}

@app.get("/api/catalog/compliance/agents")
async def get_compliance_agents():
    return {"total": 5, "core": "compliance", "agents": [
        {"id": "auditmaster", "name": "Audit Master"},
        {"id": "compliancewatchdog", "name": "Compliance Watchdog"},
        {"id": "compliance_coordinator", "name": "Coordinador Compliance"},
        {"id": "docguardian", "name": "Doc Guardian"},
        {"id": "regulatory_radar", "name": "Regulatory Radar"}
    ]}

@app.get("/api/catalog/decision/agents")
async def get_decision_agents():
    return {"total": 5, "core": "decision", "agents": [
        {"id": "decision_coordinator", "name": "Coordinador Decision"},
        {"id": "policyguardian", "name": "Policy Guardian"},
        {"id": "quantumdecision", "name": "Quantum Decision"},
        {"id": "riskoracle", "name": "Risk Oracle"},
        {"id": "turboapprover", "name": "Turbo Approver"}
    ]}

@app.get("/api/catalog/experiencia/agents")
async def get_experiencia_agents():
    return {"total": 5, "core": "experiencia", "agents": [
        {"id": "chatbotsupreme", "name": "Chatbot Supreme"},
        {"id": "customergenius", "name": "Customer Genius"},
        {"id": "experiencia_coordinator", "name": "Coordinador Experiencia"},
        {"id": "onboardingwizard", "name": "Onboarding Wizard"},
        {"id": "personalizationengine", "name": "Engine Personalizacion"}
    ]}

@app.get("/api/catalog/fortaleza/agents")
async def get_fortaleza_agents():
    return {"total": 5, "core": "fortaleza", "agents": [
        {"id": "backupguardian", "name": "Backup Guardian"},
        {"id": "cybersentinel", "name": "Cyber Sentinel"},
        {"id": "datavault", "name": "Data Vault"},
        {"id": "fortaleza_coordinator", "name": "Coordinador Fortaleza"},
        {"id": "systemhealthmonitor", "name": "System Health Monitor"}
    ]}

@app.get("/api/catalog/inteligencia/agents")
async def get_inteligencia_agents():
    return {"total": 5, "core": "inteligencia", "agents": [
        {"id": "cashfloworacle", "name": "Cashflow Oracle"},
        {"id": "inteligencia_coordinator", "name": "Coordinador Inteligencia"},
        {"id": "pricinggenius", "name": "Pricing Genius"},
        {"id": "profitmaximizer", "name": "Profit Maximizer"},
        {"id": "roimaster", "name": "ROI Master"}
    ]}

@app.get("/api/catalog/operacional/agents")
async def get_operacional_agents():
    return {"total": 5, "core": "operacional", "agents": [
        {"id": "costoptimizer", "name": "Cost Optimizer"},
        {"id": "operacional_coordinator", "name": "Coordinador Operacional"},
        {"id": "processgenius", "name": "Process Genius"},
        {"id": "qualitycontroller", "name": "Quality Controller"},
        {"id": "workflowmaster", "name": "Workflow Master"}
    ]}

@app.get("/api/catalog/orchestration/agents")
async def get_orchestration_agents():
    return {"total": 5, "core": "orchestration", "agents": [
        {"id": "coordinator", "name": "Coordinator"},
        {"id": "healthchecker", "name": "Health Checker"},
        {"id": "loadbalancer", "name": "Load Balancer"},
        {"id": "orchestrationmaster", "name": "Orchestration Master"},
        {"id": "resourcemanager", "name": "Resource Manager"}
    ]}

@app.get("/api/catalog/recuperacion/agents")
async def get_recuperacion_agents():
    return {"total": 5, "core": "recuperacion", "agents": [
        {"id": "collectionmaster", "name": "Collection Master"},
        {"id": "legalpathway", "name": "Legal Pathway"},
        {"id": "negotiationbot", "name": "Negotiation Bot"},
        {"id": "recoveryoptimizer", "name": "Recovery Optimizer"},
        {"id": "recuperacion_coordinator", "name": "Coordinador Recuperacion"}
    ]}

@app.get("/api/catalog/vigilancia/agents")
async def get_vigilancia_agents():
    return {"total": 4, "core": "vigilancia", "agents": [
        {"id": "earlywarning", "name": "Early Warning"},
        {"id": "marketradar", "name": "Market Radar"},
        {"id": "portfoliosentinel", "name": "Portfolio Sentinel"},
        {"id": "vigilancia_coordinator", "name": "Coordinador Vigilancia"}
    ]}

@app.get("/api/catalog/{core_id}/agents")
async def get_core_agents_generic(core_id: str):
    if core_id not in registry.cores:
        raise HTTPException(404, f"Core '{core_id}' not found")
    agents = registry.get_agents_by_core(core_id)
    return {"total": len(agents), "core": core_id, "agents": [{"id": a["id"], "name": a["name"]} for a in agents]}


# ============================================================================
# ============================================================================
# WORKFLOW ENGINE v2.0.0 - 10 MARKETING WORKFLOWS
# ============================================================================
# ============================================================================

workflow_router = APIRouter(prefix="/workflows", tags=["workflows"])

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_hash(data: Any) -> str:
    try:
        return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()[:16]
    except:
        return "hash_error"

def safe_get(data: Dict, *keys, default=None):
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result is not None else default

async def execute_agent_internal(core: str, agent_id: str, input_data: Dict, tenant_id: str = "workflow") -> Dict:
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
        return {"status": "error", "error": f"Agent module not found: {core}.{agent_id}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def execute_workflow_step(workflow_id: str, step_config: Dict, input_data: Dict, tenant_id: str = "workflow") -> Dict:
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

def generate_workflow_summary(steps: List[Dict]) -> Dict:
    successful = sum(1 for s in steps if s.get("status") in ["success", "skipped"])
    failed = sum(1 for s in steps if s.get("status") == "error")
    total_duration = sum(s.get("duration_ms", 0) for s in steps if isinstance(s.get("duration_ms"), (int, float)))
    
    confidence_values = []
    for step in steps:
        result = step.get("result", {})
        decision = result.get("decision", {})
        if isinstance(decision, dict) and decision.get("confidence"):
            confidence_values.append(decision["confidence"])
    
    return {
        "steps_completed": f"{successful}/{len(steps)}",
        "steps_failed": failed,
        "total_duration_ms": round(total_duration, 2),
        "average_confidence": round(sum(confidence_values)/len(confidence_values), 3) if confidence_values else 0,
        "workflow_status": "success" if failed == 0 else ("partial" if successful > 0 else "failed")
    }

def extract_recommendations(steps: List[Dict]) -> List[Dict]:
    recommendations = []
    for step in steps:
        if step.get("status") == "skipped":
            continue
        result = step.get("result", {})
        decision = result.get("decision", {})
        if isinstance(decision, dict) and decision:
            recommendations.append({
                "source": step.get("step_name"),
                "action": decision.get("action", "REVIEW"),
                "priority": decision.get("priority", "MEDIUM"),
                "confidence": decision.get("confidence", 0)
            })
    return recommendations


# ============================================================================
# WORKFLOW #1: CAMPAIGN OPTIMIZATION
# ============================================================================

WORKFLOW_CAMPAIGN_OPTIMIZATION = {
    "id": "campaign-optimization",
    "name": "Campaign Optimization Workflow",
    "version": "1.0.0",
    "description": "Optimiza campañas de marketing usando 5 agentes especializados",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "audiencesegmenteria", "name": "Audience Analysis", "required": True},
        {"order": 2, "core": "marketing", "agent": "leadscoria", "name": "Lead Scoring", "required": True},
        {"order": 3, "core": "marketing", "agent": "abtestingimpactia", "name": "A/B Test Strategy", "required": False},
        {"order": 4, "core": "marketing", "agent": "campaignoptimizeria", "name": "Campaign Design", "required": True},
        {"order": 5, "core": "marketing", "agent": "budgetforecastia", "name": "Budget Allocation", "required": True}
    ]
}

class CampaignBrief(BaseModel):
    name: str = Field(default="Unnamed Campaign")
    objective: str = Field(default="lead_generation")
    channel: str = Field(default="email")
    target_audience: str = Field(default="")

class WorkflowRequest(BaseModel):
    campaign_brief: CampaignBrief = Field(default_factory=CampaignBrief)
    leads: List[Dict] = Field(default=[])
    leads_count: int = Field(default=0)
    budget: float = Field(default=0)
    ab_test_data: Dict = Field(default={})
    include_ab_strategy: bool = Field(default=True)
    target_criteria: Dict = Field(default={})
    scoring_criteria: Dict = Field(default={})

@workflow_router.post("/campaign-optimization")
async def workflow_campaign_optimization(request: WorkflowRequest):
    workflow_id = f"WF-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    workflow_logger.info(f"Starting workflow {workflow_id}")
    
    workflow_result = {
        "workflow_id": workflow_id,
        "workflow_name": WORKFLOW_CAMPAIGN_OPTIMIZATION["name"],
        "workflow_version": WORKFLOW_CAMPAIGN_OPTIMIZATION["version"],
        "tenant_id": tenant_id,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "steps": [],
        "status": "running"
    }
    
    try:
        step1_input = {"campaign_brief": request.campaign_brief.dict(), "leads": request.leads, "leads_count": request.leads_count or len(request.leads)}
        step1 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][0], step1_input, tenant_id)
        workflow_result["steps"].append(step1)
        
        step2_input = {"segments": safe_get(step1, "result", "segments", default=[]), "leads": request.leads}
        step2 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][1], step2_input, tenant_id)
        workflow_result["steps"].append(step2)
        
        if request.include_ab_strategy:
            step3_input = {"segments": safe_get(step1, "result", "segments", default=[]), "ab_test_data": request.ab_test_data or {"variant_a": {"clicks": 100}, "variant_b": {"clicks": 120}}}
            step3 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][2], step3_input, tenant_id)
            workflow_result["steps"].append(step3)
        else:
            workflow_result["steps"].append({"step_id": f"{workflow_id}-step3", "status": "skipped", "result": {}})
        
        step4_input = {"segments": safe_get(step1, "result", "segments", default=[]), "campaign_brief": request.campaign_brief.dict(), "budget": request.budget}
        step4 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][3], step4_input, tenant_id)
        workflow_result["steps"].append(step4)
        
        step5_input = {"optimized_campaign": safe_get(step4, "result", default={}), "total_budget": request.budget}
        step5 = await execute_workflow_step(workflow_id, WORKFLOW_CAMPAIGN_OPTIMIZATION["steps"][4], step5_input, tenant_id)
        workflow_result["steps"].append(step5)
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        workflow_result["recommendations"] = extract_recommendations(workflow_result["steps"])
        
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #2: CUSTOMER ACQUISITION INTELLIGENCE
# ============================================================================

WORKFLOW_CUSTOMER_ACQUISITION = {
    "id": "customer-acquisition-intelligence",
    "name": "Customer Acquisition Intelligence",
    "version": "1.1.0",
    "description": "Pipeline inteligente de adquisición con 7 agentes",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "audiencesegmenteria", "name": "Audience Segmentation", "required": True},
        {"order": 2, "core": "marketing", "agent": "geosegmentationia", "name": "Geo Segmentation", "required": False},
        {"order": 3, "core": "marketing", "agent": "predictiveleadia", "name": "Predictive Lead Analysis", "required": True},
        {"order": 4, "core": "marketing", "agent": "contactqualityia", "name": "Contact Quality Validation", "required": True},
        {"order": 5, "core": "marketing", "agent": "leadscoria", "name": "Lead Scoring Primary", "required": True},
        {"order": 6, "core": "marketing", "agent": "leadscoringia", "name": "Lead Scoring Validation", "required": True},
        {"order": 7, "core": "marketing", "agent": "conversioncohortia", "name": "Conversion Cohort Analysis", "required": True}
    ],
    "user_phases": [
        {"id": "TARGETING", "name": "🎯 Targeting"},
        {"id": "INTENT", "name": "🔮 Intent Analysis"},
        {"id": "QUALITY", "name": "✅ Quality Gate"},
        {"id": "SCORING", "name": "📊 Scoring"},
        {"id": "ACTIVATION", "name": "🚀 Activation"}
    ],
    "scoring_resolution": {
        "strategy": "PRIMARY_WITH_VALIDATION",
        "conflict_threshold": 15,
        "confidence_penalty_on_conflict": 0.2
    }
}

class AcquisitionRequest(BaseModel):
    target_market: str = Field(default="B2B")
    industry_focus: List[str] = Field(default=[])
    company_size: List[str] = Field(default=["SMB", "MidMarket"])
    regions: List[str] = Field(default=[])
    leads: List[Dict] = Field(default=[])
    leads_count: int = Field(default=0)
    min_quality_score: float = Field(default=0.5)
    auto_activate: bool = Field(default=False)
    confidence_threshold: float = Field(default=0.7)

def resolve_scoring_conflict(primary_result: Dict, secondary_result: Dict) -> Dict:
    config = WORKFLOW_CUSTOMER_ACQUISITION["scoring_resolution"]
    threshold = config["conflict_threshold"] / 100
    penalty = config["confidence_penalty_on_conflict"]
    
    primary_score = safe_get(primary_result, "result", "scores", "final_score", default=0) or safe_get(primary_result, "result", "conversion_probability", default=0.5)
    secondary_score = safe_get(secondary_result, "result", "scores", "final_score", default=0) or safe_get(secondary_result, "result", "conversion_probability", default=0.5)
    primary_conf = safe_get(primary_result, "result", "decision", "confidence", default=0.7)
    secondary_conf = safe_get(secondary_result, "result", "decision", "confidence", default=0.7)
    
    difference = abs(primary_score - secondary_score)
    
    if difference <= threshold:
        return {"resolution": "CONSENSUS", "final_score": round((primary_score + secondary_score) / 2, 3), "confidence": round((primary_conf + secondary_conf) / 2, 3), "conflict_level": "NONE", "explanation": f"Scores within {difference*100:.1f}%"}
    elif difference <= threshold * 1.67:
        return {"resolution": "PRIMARY_WINS", "final_score": round(primary_score, 3), "confidence": round(primary_conf - (penalty * 0.5), 3), "conflict_level": "MILD", "explanation": f"Mild conflict ({difference*100:.1f}%)"}
    else:
        return {"resolution": "REVIEW_REQUIRED", "final_score": round(primary_score, 3), "confidence": round(max(primary_conf, secondary_conf) - penalty, 3), "conflict_level": "SEVERE", "explanation": f"Significant conflict ({difference*100:.1f}%)"}

def generate_unified_decision(workflow_id: str, steps: List[Dict], scoring_resolution: Dict, request_data: Dict) -> Dict:
    final_score = scoring_resolution["final_score"]
    confidence = scoring_resolution["confidence"]
    
    if scoring_resolution["conflict_level"] == "SEVERE":
        decision = "REVIEW_BEFORE_ACTIVATION"
    elif final_score >= 0.7 and confidence >= 0.7:
        decision = "ACTIVATE_ACQUISITION"
    elif final_score >= 0.5:
        decision = "NURTURE_PIPELINE"
    elif final_score >= 0.3:
        decision = "ENRICH_AND_REANALYZE"
    else:
        decision = "DISQUALIFY"
    
    total_leads = request_data.get("leads_count", 100)
    qualified = int(total_leads * final_score)
    
    return {
        "decision": decision,
        "confidence": confidence,
        "valid_until": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
        "lead_summary": {"total_analyzed": total_leads, "qualified": qualified, "qualification_rate": round(final_score, 3)},
        "business_impact": {"pipeline_value": qualified * 5000, "expected_roi": round(2.5 + (confidence * 2), 1)},
        "scoring_metadata": scoring_resolution
    }

@workflow_router.post("/customer-acquisition-intelligence")
async def workflow_customer_acquisition(request: AcquisitionRequest):
    workflow_id = f"CAI-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    workflow_logger.info(f"Starting Customer Acquisition Intelligence: {workflow_id}")
    
    workflow_result = {
        "workflow_id": workflow_id,
        "workflow_name": WORKFLOW_CUSTOMER_ACQUISITION["name"],
        "workflow_version": WORKFLOW_CUSTOMER_ACQUISITION["version"],
        "tenant_id": tenant_id,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "steps": [],
        "status": "running"
    }
    
    try:
        step1 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][0], {"target_market": request.target_market, "industries": request.industry_focus, "leads_count": request.leads_count}, tenant_id)
        workflow_result["steps"].append(step1)
        
        if request.regions:
            step2 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][1], {"segments": safe_get(step1, "result", "segments", default=[]), "regions": request.regions}, tenant_id)
        else:
            step2 = {"step_id": f"{workflow_id}-step2", "status": "skipped", "result": {}}
        workflow_result["steps"].append(step2)
        
        step3 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][2], {"segments": safe_get(step1, "result", "segments", default=[]), "leads": request.leads}, tenant_id)
        workflow_result["steps"].append(step3)
        
        step4 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][3], {"segments": safe_get(step1, "result", "segments", default=[]), "min_quality": request.min_quality_score}, tenant_id)
        workflow_result["steps"].append(step4)
        
        step5 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][4], {"segments": safe_get(step1, "result", "segments", default=[]), "leads": request.leads}, tenant_id)
        workflow_result["steps"].append(step5)
        
        step6 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][5], {"segments": safe_get(step1, "result", "segments", default=[]), "primary_scores": safe_get(step5, "result", "scores", default={})}, tenant_id)
        workflow_result["steps"].append(step6)
        
        scoring_resolution = resolve_scoring_conflict(step5, step6)
        
        step7 = await execute_workflow_step(workflow_id, WORKFLOW_CUSTOMER_ACQUISITION["steps"][6], {"final_score": scoring_resolution["final_score"]}, tenant_id)
        workflow_result["steps"].append(step7)
        
        unified_decision = generate_unified_decision(workflow_id, workflow_result["steps"], scoring_resolution, request.dict())
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["decision"] = unified_decision
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        workflow_result["summary"]["final_decision"] = unified_decision["decision"]
        workflow_result["summary"]["pipeline_value"] = unified_decision["business_impact"]["pipeline_value"]
        
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #3: CUSTOMER LIFECYCLE REVENUE
# ============================================================================

WORKFLOW_CUSTOMER_LIFECYCLE = {
    "id": "customer-lifecycle-revenue",
    "name": "Customer Lifecycle Revenue",
    "version": "1.0.0",
    "description": "Maximiza el valor de cada cliente",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "customersegmentatonia", "name": "Customer Segmentation", "required": True},
        {"order": 2, "core": "marketing", "agent": "productaffinityia", "name": "Product Affinity Analysis", "required": True},
        {"order": 3, "core": "marketing", "agent": "retentionpredictoria", "name": "Retention Prediction", "required": True},
        {"order": 4, "core": "marketing", "agent": "retentionpredictorea", "name": "Retention Analysis", "required": True},
        {"order": 5, "core": "marketing", "agent": "pricingoptimizeria", "name": "Pricing Optimization", "required": True},
        {"order": 6, "core": "marketing", "agent": "journeyoptimizeria", "name": "Journey Optimization", "required": True}
    ]
}

class LifecycleRequest(BaseModel):
    customer_segments: List[str] = Field(default=["all"])
    include_pricing: bool = Field(default=True)
    churn_threshold: float = Field(default=0.3)
    products: List[Dict] = Field(default=[])

@workflow_router.post("/customer-lifecycle-revenue")
async def workflow_customer_lifecycle(request: LifecycleRequest):
    workflow_id = f"CLR-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_result = {"workflow_id": workflow_id, "workflow_name": WORKFLOW_CUSTOMER_LIFECYCLE["name"], "started_at": datetime.utcnow().isoformat() + "Z", "steps": [], "status": "running"}
    
    try:
        prev_result = {}
        for step_config in WORKFLOW_CUSTOMER_LIFECYCLE["steps"]:
            step = await execute_workflow_step(workflow_id, step_config, {"segments": request.customer_segments, "products": request.products, "previous_result": prev_result}, tenant_id)
            workflow_result["steps"].append(step)
            prev_result = step.get("result", {})
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #4: CONTENT PERFORMANCE ENGINE
# ============================================================================

WORKFLOW_CONTENT_PERFORMANCE = {
    "id": "content-performance-engine",
    "name": "Content Performance Engine",
    "version": "1.0.0",
    "description": "Genera y optimiza contenido basado en datos",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "competitoranalyzeria", "name": "Competitor Analysis", "required": True},
        {"order": 2, "core": "marketing", "agent": "sentimentanalyzeria", "name": "Sentiment Analysis", "required": True},
        {"order": 3, "core": "marketing", "agent": "contentgeneratoria", "name": "Content Generation", "required": True},
        {"order": 4, "core": "marketing", "agent": "contentperformanceia", "name": "Content Performance", "required": True},
        {"order": 5, "core": "marketing", "agent": "creativeanalyzeria", "name": "Creative Analysis", "required": False}
    ]
}

class ContentRequest(BaseModel):
    topic: str = Field(default="")
    content_type: str = Field(default="blog")
    target_audience: str = Field(default="B2B")
    competitors: List[str] = Field(default=[])
    existing_content: List[Dict] = Field(default=[])

@workflow_router.post("/content-performance-engine")
async def workflow_content_performance(request: ContentRequest):
    workflow_id = f"CPE-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_result = {"workflow_id": workflow_id, "workflow_name": WORKFLOW_CONTENT_PERFORMANCE["name"], "started_at": datetime.utcnow().isoformat() + "Z", "steps": [], "status": "running"}
    
    try:
        prev_result = {}
        for step_config in WORKFLOW_CONTENT_PERFORMANCE["steps"]:
            step = await execute_workflow_step(workflow_id, step_config, {"topic": request.topic, "content_type": request.content_type, "competitors": request.competitors, "previous_result": prev_result}, tenant_id)
            workflow_result["steps"].append(step)
            prev_result = step.get("result", {})
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #5: SOCIAL MEDIA INTELLIGENCE
# ============================================================================

WORKFLOW_SOCIAL_INTELLIGENCE = {
    "id": "social-media-intelligence",
    "name": "Social Media Intelligence",
    "version": "1.0.0",
    "description": "Domina la presencia social con datos",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "sociallisteningia", "name": "Social Listening", "required": True},
        {"order": 2, "core": "marketing", "agent": "sentimentanalyzeria", "name": "Sentiment Analysis", "required": True},
        {"order": 3, "core": "marketing", "agent": "socialpostgeneratoria", "name": "Social Post Generation", "required": True},
        {"order": 4, "core": "marketing", "agent": "influencermatcheria", "name": "Influencer Matching", "required": False}
    ]
}

class SocialRequest(BaseModel):
    brand_name: str = Field(default="")
    platforms: List[str] = Field(default=["twitter", "linkedin"])
    keywords: List[str] = Field(default=[])
    post_topics: List[str] = Field(default=[])

@workflow_router.post("/social-media-intelligence")
async def workflow_social_intelligence(request: SocialRequest):
    workflow_id = f"SMI-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_result = {"workflow_id": workflow_id, "workflow_name": WORKFLOW_SOCIAL_INTELLIGENCE["name"], "started_at": datetime.utcnow().isoformat() + "Z", "steps": [], "status": "running"}
    
    try:
        prev_result = {}
        for step_config in WORKFLOW_SOCIAL_INTELLIGENCE["steps"]:
            step = await execute_workflow_step(workflow_id, step_config, {"brand_name": request.brand_name, "platforms": request.platforms, "keywords": request.keywords, "previous_result": prev_result}, tenant_id)
            workflow_result["steps"].append(step)
            prev_result = step.get("result", {})
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #6: EMAIL AUTOMATION MASTER
# ============================================================================

WORKFLOW_EMAIL_AUTOMATION = {
    "id": "email-automation-master",
    "name": "Email Automation Master",
    "version": "1.0.0",
    "description": "Automatiza comunicación personalizada a escala",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "customersegmentatonia", "name": "Customer Segmentation", "required": True},
        {"order": 2, "core": "marketing", "agent": "personalizationengineia", "name": "Personalization Engine", "required": True},
        {"order": 3, "core": "marketing", "agent": "emailautomationia", "name": "Email Automation", "required": True},
        {"order": 4, "core": "marketing", "agent": "minimalformia", "name": "Form Optimization", "required": False}
    ]
}

class EmailAutomationRequest(BaseModel):
    campaign_name: str = Field(default="")
    email_type: str = Field(default="nurture")
    segments: List[str] = Field(default=["all"])
    personalization_level: str = Field(default="high")
    email_content: Dict = Field(default={})

@workflow_router.post("/email-automation-master")
async def workflow_email_automation(request: EmailAutomationRequest):
    workflow_id = f"EAM-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_result = {"workflow_id": workflow_id, "workflow_name": WORKFLOW_EMAIL_AUTOMATION["name"], "started_at": datetime.utcnow().isoformat() + "Z", "steps": [], "status": "running"}
    
    try:
        prev_result = {}
        for step_config in WORKFLOW_EMAIL_AUTOMATION["steps"]:
            step = await execute_workflow_step(workflow_id, step_config, {"campaign_name": request.campaign_name, "email_type": request.email_type, "segments": request.segments, "previous_result": prev_result}, tenant_id)
            workflow_result["steps"].append(step)
            prev_result = step.get("result", {})
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #7: MULTI-CHANNEL ATTRIBUTION
# ============================================================================

WORKFLOW_ATTRIBUTION = {
    "id": "multi-channel-attribution",
    "name": "Multi-Channel Attribution",
    "version": "1.0.0",
    "description": "Sabe exactamente qué canal genera revenue",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "channelattributia", "name": "Channel Attribution", "required": True},
        {"order": 2, "core": "marketing", "agent": "attributionmodelia", "name": "Attribution Modeling", "required": True},
        {"order": 3, "core": "marketing", "agent": "marketingmixmodelia", "name": "Marketing Mix Model", "required": True},
        {"order": 4, "core": "marketing", "agent": "budgetforecastia", "name": "Budget Forecast", "required": True}
    ]
}

class AttributionRequest(BaseModel):
    channels: List[str] = Field(default=["paid_search", "organic", "email", "social"])
    conversion_data: List[Dict] = Field(default=[])
    date_range: str = Field(default="last_30_days")
    total_budget: float = Field(default=10000)
    attribution_model: str = Field(default="data_driven")

@workflow_router.post("/multi-channel-attribution")
async def workflow_attribution(request: AttributionRequest):
    workflow_id = f"MCA-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_result = {"workflow_id": workflow_id, "workflow_name": WORKFLOW_ATTRIBUTION["name"], "started_at": datetime.utcnow().isoformat() + "Z", "steps": [], "status": "running"}
    
    try:
        prev_result = {}
        for step_config in WORKFLOW_ATTRIBUTION["steps"]:
            step = await execute_workflow_step(workflow_id, step_config, {"channels": request.channels, "total_budget": request.total_budget, "attribution_model": request.attribution_model, "previous_result": prev_result}, tenant_id)
            workflow_result["steps"].append(step)
            prev_result = step.get("result", {})
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #8: COMPETITIVE INTELLIGENCE HUB
# ============================================================================

WORKFLOW_COMPETITIVE = {
    "id": "competitive-intelligence-hub",
    "name": "Competitive Intelligence Hub",
    "version": "1.0.0",
    "description": "Análisis completo de competencia",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "competitoranalyzeria", "name": "Competitor Analysis", "required": True},
        {"order": 2, "core": "marketing", "agent": "competitorintelligenceia", "name": "Competitor Intelligence", "required": True},
        {"order": 3, "core": "marketing", "agent": "pricingoptimizeria", "name": "Pricing Optimization", "required": True}
    ]
}

class CompetitiveRequest(BaseModel):
    competitors: List[str] = Field(default=[])
    analysis_areas: List[str] = Field(default=["pricing", "features", "marketing"])
    my_products: List[Dict] = Field(default=[])
    market_segment: str = Field(default="")

@workflow_router.post("/competitive-intelligence-hub")
async def workflow_competitive(request: CompetitiveRequest):
    workflow_id = f"CIH-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_result = {"workflow_id": workflow_id, "workflow_name": WORKFLOW_COMPETITIVE["name"], "started_at": datetime.utcnow().isoformat() + "Z", "steps": [], "status": "running"}
    
    try:
        prev_result = {}
        for step_config in WORKFLOW_COMPETITIVE["steps"]:
            step = await execute_workflow_step(workflow_id, step_config, {"competitors": request.competitors, "analysis_areas": request.analysis_areas, "market_segment": request.market_segment, "previous_result": prev_result}, tenant_id)
            workflow_result["steps"].append(step)
            prev_result = step.get("result", {})
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #9: A/B TESTING & EXPERIMENTATION
# ============================================================================

WORKFLOW_EXPERIMENTATION = {
    "id": "ab-testing-experimentation",
    "name": "A/B Testing & Experimentation",
    "version": "1.0.0",
    "description": "Cultura de experimentación basada en datos",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "abtestingia", "name": "A/B Test Design", "required": True},
        {"order": 2, "core": "marketing", "agent": "abtestingimpactia", "name": "A/B Test Impact", "required": True},
        {"order": 3, "core": "marketing", "agent": "conversioncohortia", "name": "Conversion Cohort", "required": True}
    ]
}

class ExperimentationRequest(BaseModel):
    test_name: str = Field(default="")
    hypothesis: str = Field(default="")
    variants: List[Dict] = Field(default=[])
    sample_size: int = Field(default=1000)
    confidence_level: float = Field(default=0.95)

@workflow_router.post("/ab-testing-experimentation")
async def workflow_experimentation(request: ExperimentationRequest):
    workflow_id = f"ABT-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_result = {"workflow_id": workflow_id, "workflow_name": WORKFLOW_EXPERIMENTATION["name"], "started_at": datetime.utcnow().isoformat() + "Z", "steps": [], "status": "running"}
    
    try:
        prev_result = {}
        for step_config in WORKFLOW_EXPERIMENTATION["steps"]:
            step = await execute_workflow_step(workflow_id, step_config, {"test_name": request.test_name, "hypothesis": request.hypothesis, "variants": request.variants, "sample_size": request.sample_size, "previous_result": prev_result}, tenant_id)
            workflow_result["steps"].append(step)
            prev_result = step.get("result", {})
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW #10: INFLUENCER & PARTNERSHIP ENGINE
# ============================================================================

WORKFLOW_INFLUENCER = {
    "id": "influencer-partnership-engine",
    "name": "Influencer & Partnership Engine",
    "version": "1.0.0",
    "description": "Amplifica reach a través de influencers",
    "steps": [
        {"order": 1, "core": "marketing", "agent": "influencermatcheria", "name": "Influencer Search", "required": True},
        {"order": 2, "core": "marketing", "agent": "influencermatchingia", "name": "Influencer Matching", "required": True}
    ]
}

class InfluencerRequest(BaseModel):
    campaign_goals: List[str] = Field(default=["awareness", "engagement"])
    target_audience: str = Field(default="")
    budget_range: Dict = Field(default={"min": 1000, "max": 10000})
    platforms: List[str] = Field(default=["instagram", "youtube"])
    niche: str = Field(default="")

@workflow_router.post("/influencer-partnership-engine")
async def workflow_influencer(request: InfluencerRequest):
    workflow_id = f"IPE-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:8]}"
    tenant_id = "workflow"
    
    workflow_result = {"workflow_id": workflow_id, "workflow_name": WORKFLOW_INFLUENCER["name"], "started_at": datetime.utcnow().isoformat() + "Z", "steps": [], "status": "running"}
    
    try:
        prev_result = {}
        for step_config in WORKFLOW_INFLUENCER["steps"]:
            step = await execute_workflow_step(workflow_id, step_config, {"campaign_goals": request.campaign_goals, "platforms": request.platforms, "niche": request.niche, "previous_result": prev_result}, tenant_id)
            workflow_result["steps"].append(step)
            prev_result = step.get("result", {})
        
        workflow_result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        workflow_result["status"] = "success"
        workflow_result["summary"] = generate_workflow_summary(workflow_result["steps"])
        return workflow_result
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
        return workflow_result


# ============================================================================
# WORKFLOW SCHEMAS & LIST
# ============================================================================

@workflow_router.get("/")
async def list_all_workflows():
    return {
        "workflows": [
            {"id": "campaign-optimization", "name": "Campaign Optimization", "version": "1.0.0", "tier": "CORE", "agents": 5, "status": "active"},
            {"id": "customer-acquisition-intelligence", "name": "Customer Acquisition Intelligence", "version": "1.1.0", "tier": "CORE", "agents": 7, "status": "active"},
            {"id": "customer-lifecycle-revenue", "name": "Customer Lifecycle Revenue", "version": "1.0.0", "tier": "CORE", "agents": 6, "status": "active"},
            {"id": "content-performance-engine", "name": "Content Performance Engine", "version": "1.0.0", "tier": "EXECUTION", "agents": 5, "status": "active"},
            {"id": "social-media-intelligence", "name": "Social Media Intelligence", "version": "1.0.0", "tier": "EXECUTION", "agents": 4, "status": "active"},
            {"id": "email-automation-master", "name": "Email Automation Master", "version": "1.0.0", "tier": "EXECUTION", "agents": 4, "status": "active"},
            {"id": "multi-channel-attribution", "name": "Multi-Channel Attribution", "version": "1.0.0", "tier": "INTELLIGENCE", "agents": 4, "status": "active"},
            {"id": "competitive-intelligence-hub", "name": "Competitive Intelligence Hub", "version": "1.0.0", "tier": "INTELLIGENCE", "agents": 3, "status": "active"},
            {"id": "ab-testing-experimentation", "name": "A/B Testing & Experimentation", "version": "1.0.0", "tier": "INTELLIGENCE", "agents": 3, "status": "active"},
            {"id": "influencer-partnership-engine", "name": "Influencer & Partnership Engine", "version": "1.0.0", "tier": "INTELLIGENCE", "agents": 2, "status": "active"}
        ],
        "total": 10,
        "tiers": {
            "CORE": ["campaign-optimization", "customer-acquisition-intelligence", "customer-lifecycle-revenue"],
            "EXECUTION": ["content-performance-engine", "social-media-intelligence", "email-automation-master"],
            "INTELLIGENCE": ["multi-channel-attribution", "competitive-intelligence-hub", "ab-testing-experimentation", "influencer-partnership-engine"]
        },
        "total_agents_covered": 43
    }

@workflow_router.get("/campaign-optimization/schema")
async def campaign_schema():
    return {"workflow": WORKFLOW_CAMPAIGN_OPTIMIZATION}

@workflow_router.get("/customer-acquisition-intelligence/schema")
async def acquisition_schema():
    return {"workflow": WORKFLOW_CUSTOMER_ACQUISITION}

@workflow_router.get("/customer-lifecycle-revenue/schema")
async def lifecycle_schema():
    return {"workflow": WORKFLOW_CUSTOMER_LIFECYCLE}

@workflow_router.get("/content-performance-engine/schema")
async def content_schema():
    return {"workflow": WORKFLOW_CONTENT_PERFORMANCE}

@workflow_router.get("/social-media-intelligence/schema")
async def social_schema():
    return {"workflow": WORKFLOW_SOCIAL_INTELLIGENCE}

@workflow_router.get("/email-automation-master/schema")
async def email_schema():
    return {"workflow": WORKFLOW_EMAIL_AUTOMATION}

@workflow_router.get("/multi-channel-attribution/schema")
async def attribution_schema():
    return {"workflow": WORKFLOW_ATTRIBUTION}

@workflow_router.get("/competitive-intelligence-hub/schema")
async def competitive_schema():
    return {"workflow": WORKFLOW_COMPETITIVE}

@workflow_router.get("/ab-testing-experimentation/schema")
async def experimentation_schema():
    return {"workflow": WORKFLOW_EXPERIMENTATION}

@workflow_router.get("/influencer-partnership-engine/schema")
async def influencer_schema():
    return {"workflow": WORKFLOW_INFLUENCER}

@workflow_router.get("/health")
async def workflow_health():
    return {"status": "healthy", "engine_version": "2.0.0", "workflows_available": 10, "total_agents_in_workflows": 43}


# ============================================================================
# REGISTER ROUTER & STARTUP
# ============================================================================

app.include_router(workflow_router)

@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("NADAKKI AI SUITE v4.0.0 - STARTING")
    logger.info("=" * 60)
    logger.info(f"✓ {registry.total} agents across {len(registry.cores)} cores")
    logger.info("✓ 10 Marketing Workflows ready")
    for core, agents in sorted(registry.cores.items(), key=lambda x: -len(x[1])):
        logger.info(f"  • {core}: {len(agents)} agents")
    logger.info("=" * 60)
    logger.info("🚀 Server ready at http://localhost:8000")
    logger.info("📚 API docs at http://localhost:8000/docs")
    logger.info("🔄 Workflows (10): http://localhost:8000/workflows")
    logger.info("=" * 60)
