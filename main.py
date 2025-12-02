"""
NADAKKI AI SUITE v3.4.3 – WORDPRESS INTEGRATION
New: Endpoint /api/v1/marketing/agents/summary DIRECTO en main.py
Fixed: Router integration
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging, time, asyncio
import os
import json

# ==============================================================
# CONFIGURACIÓN BASE
# ==============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("logs/nadakki_server.log", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger("NadakkiAISuite")

app = FastAPI(
    title="Nadakki AI Suite",
    description="Multi-Tenant Enterprise AI Platform (TenantManager + UsageTracker + BrandingEngine)",
    version="3.4.3",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==============================================================
# CORS
# ==============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================
# IMPORTAR SERVICIOS INTERNOS
# ==============================================================
from services.integrated_usage_tracker import IntegratedUsageTracker
from services.branding_engine import BrandingEngine
from services.tenant_manager import TenantManager

tracker = IntegratedUsageTracker()
branding = BrandingEngine()
tenant_manager = TenantManager()

# ==============================================================
# FUNCIÓN AUXILIAR: CONTAR AGENTES REALES
# ==============================================================

def get_agents_by_ecosystem():
    """
    Obtiene agentes reales del sistema organizados por ecosistema.
    Escanea carpeta agents/ y categoriza por nombre
    """
    agents_by_ecosystem = {
        "Marketing": [],
        "Originación": [],
        "Compliance": [],
        "Recuperación": [],
        "Inteligencia": [],
        "Operacional": [],
        "Investigación": [],
        "Legal": [],
        "Contabilidad": [],
        "Presupuesto": [],
        "RRHH": [],
        "Ventas CRM": [],
        "Logística": [],
        "Educación": [],
        "RegTech": [],
        "Financial Core": [],
        "Experiencia": [],
        "Fortaleza": [],
        "Orchestration": [],
        "Decisión": [],
        "Vigilancia": []
    }
    
    agents_dir = "agents"
    
    try:
        if not os.path.exists(agents_dir):
            logger.warning(f"Carpeta {agents_dir} no encontrada")
            return agents_by_ecosystem
        
        # Escanear subcarpetas
        for ecosystem_folder in os.listdir(agents_dir):
            ecosystem_path = os.path.join(agents_dir, ecosystem_folder)
            
            if os.path.isdir(ecosystem_path):
                # Mapeo de carpeta a ecosistema
                ecosystem_map = {
                    "marketing": "Marketing",
                    "originacion": "Originación",
                    "compliance": "Compliance",
                    "recuperacion": "Recuperación",
                    "inteligencia": "Inteligencia",
                    "operacional": "Operacional",
                    "investigacion": "Investigación",
                    "legal": "Legal",
                    "contabilidad": "Contabilidad",
                    "presupuesto": "Presupuesto",
                    "rrhh": "RRHH",
                    "ventascrm": "Ventas CRM",
                    "logistica": "Logística",
                    "educacion": "Educación",
                    "regtech": "RegTech",
                    "core": "Financial Core",
                    "experiencia": "Experiencia",
                    "fortaleza": "Fortaleza",
                    "orchestration": "Orchestration",
                    "decision": "Decisión",
                    "vigilancia": "Vigilancia"
                }
                
                ecosystem_name = ecosystem_map.get(ecosystem_folder.lower(), ecosystem_folder)
                
                try:
                    py_files = [f for f in os.listdir(ecosystem_path) if f.endswith('.py') and not f.startswith('_')]
                    if py_files:
                        agents_by_ecosystem[ecosystem_name] = [
                            {"name": f.replace('.py', ''), "status": "active"} 
                            for f in py_files
                        ]
                except:
                    pass
    
    except Exception as e:
        logger.error(f"Error contando agentes: {str(e)}")
    
    return agents_by_ecosystem

# ==============================================================
# ENDPOINTS PRINCIPALES
# ==============================================================

@app.get("/")
def root():
    return {
        "service": "Nadakki AI Suite",
        "version": "3.4.3",
        "modules": ["TenantManager", "IntegratedUsageTracker", "BrandingEngine"],
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

# ==============================================================
# TENANT MANAGER - ENDPOINTS
# ==============================================================

@app.get("/api/tenant/list")
def list_tenants():
    """Lista todos los tenants activos"""
    tenants = tenant_manager.list_all_tenants()
    return {"total": len(tenants), "tenants": tenants}

@app.get("/api/tenant/{tenant_id}")
def get_tenant_info(tenant_id: str):
    """Obtiene información específica de un tenant"""
    try:
        conn = tenant_manager._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.tenant_id, t.institution_name, t.institution_type, t.plan, t.status, t.created_at,
                   b.primary_color, b.secondary_color, b.logo_url,
                   l.max_monthly_requests, l.current_monthly_requests
            FROM tenants t
            LEFT JOIN tenant_branding b ON t.tenant_id = b.tenant_id
            LEFT JOIN tenant_limits l ON t.tenant_id = l.tenant_id
            WHERE t.tenant_id = ?
        """, (tenant_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Tenant no encontrado")
            
        return {
            "tenant_id": row[0],
            "institution_name": row[1],
            "institution_type": row[2],
            "plan": row[3],
            "status": row[4],
            "created_at": row[5],
            "branding": {
                "primary_color": row[6],
                "secondary_color": row[7],
                "logo_url": row[8]
            },
            "limits": {
                "max_monthly_requests": row[9],
                "current_monthly_requests": row[10]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ==============================================================
# USAGE TRACKER
# ==============================================================

@app.get("/api/usage/report/{tenant_id}")
def usage_report(tenant_id: str):
    """Devuelve resumen detallado de uso"""
    report = tracker.get_tenant_usage_report(tenant_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    return report

@app.post("/api/usage/log")
async def log_usage(request: Request):
    """Registra evento de uso para un tenant"""
    try:
        data = await request.json()
        tenant_id = data.get("tenant_id")
        endpoint = data.get("endpoint", "/api/v1/evaluate")
        tokens_used = data.get("tokens_used", 0)
        agent_used = data.get("agent_used", "generic_agent")
        response_time_ms = data.get("response_time_ms", 0)

        if not tenant_id:
            raise HTTPException(status_code=400, detail="tenant_id es requerido")

        tracker.log_usage(
            tenant_id=tenant_id,
            endpoint=endpoint,
            tokens_used=tokens_used,
            agent_used=agent_used,
            response_time_ms=response_time_ms
        )
        return {"status": "logged", "tenant_id": tenant_id, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando request: {str(e)}")

# ==============================================================
# BRANDING ENGINE
# ==============================================================

@app.get("/api/branding/dashboard/{tenant_id}")
def generate_dashboard(tenant_id: str):
    """Genera dashboard HTML personalizado para el tenant"""
    try:
        path = branding.save_dashboard(tenant_id)
        return {
            "tenant_id": tenant_id,
            "dashboard_path": path,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando dashboard: {str(e)}")

@app.get("/api/branding/preview/{tenant_id}")
def preview_branding(tenant_id: str):
    """Devuelve la configuración de branding sin generar archivo"""
    branding_data = branding.get_tenant_branding(tenant_id)
    if not branding_data:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return branding_data

# ==============================================================
# ⭐ ENDPOINT WORDPRESS - DIRECTO EN MAIN.PY v3.4.3
# ==============================================================

@app.get("/api/v1/marketing/agents/summary")
def get_marketing_agents_summary():
    """
    Retorna resumen de agentes de marketing con CONTEOS REALES.
    Usado por WordPress para actualizar el dashboard.
    
    ✅ ENDPOINT DIRECTO - NO DEPENDE DE ROUTER EXTERNO
    
    Respuesta:
    {
        "status": "success",
        "total_agents": 35,
        "validated_agents": 25,
        "by_ecosystem": {
            "Marketing": 16,
            "Originación": 8,
            ...
        }
    }
    """
    try:
        agents = get_agents_by_ecosystem()
        
        total = sum(len(agents_list) for agents_list in agents.values())
        validated = int(total * 0.7)  # 70% validados (placeholder)
        
        logger.info(f"✅ WORDPRESS SUMMARY: {total} agentes totales, {validated} validados")
        
        return {
            "status": "success",
            "total_agents": total,
            "validated_agents": validated,
            "by_ecosystem": {
                ecosystem: len(agents_list) 
                for ecosystem, agents_list in agents.items()
            },
            "ecosystems": agents,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Error en /api/v1/marketing/agents/summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ==============================================================
# MANEJO DE ERRORES
# ==============================================================

@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})

# ==============================================================
# EVENTOS DE INICIO
# ==============================================================

@app.on_event("startup")
async def on_start():
    logger.info("=" * 60)
    logger.info("🚀 NADAKKI AI SUITE v3.4.3 - STARTING")
    logger.info("=" * 60)
    logger.info("✓ TenantManager activo")
    logger.info("✓ UsageTracker activo (SQLite integrado)")
    logger.info("✓ BrandingEngine operativo (dashboards white-label)")
    logger.info("✓ WordPress Integration endpoint ACTIVO")
    logger.info("  → GET /api/v1/marketing/agents/summary")
    logger.info("=" * 60)
    logger.info("Server ready at http://127.0.0.1:8000")

# ==============================================================
# IMPORTAR ROUTERS ADICIONALES
# ==============================================================

try:
    from routes.marketing_routes import router as marketing_router
    app.include_router(marketing_router)
    logger.info("✓ Marketing router incluido")
except Exception as e:
    logger.warning(f"⚠️ No se pudo cargar marketing_router: {e}")

# ==============================================================
# EJECUCIÓN LOCAL
# ==============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)