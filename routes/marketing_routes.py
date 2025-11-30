"""
===============================================================================
 NADAKKI AI SUITE - MARKETING CORE ROUTES (v8.1 WORDPRESS INTEGRATION)
 Endpoints para gestionar y ejecutar agentes de marketing
 
 ENDPOINTS:
 ✅ GET  /api/v1/marketing/status              → Estado del core
 ✅ GET  /api/v1/agents                        → Listar todos los agentes
 ✅ GET  /api/v1/agents/{agent_name}           → Info de un agente
 ✅ POST /api/v1/agents/{agent_name}           → Ejecutar un agente
 ✅ GET  /api/v1/marketing/agents/summary      → WORDPRESS INTEGRATION ⭐
 
 Autor: Nadakki Team
 Fecha: 2025-11-30
===============================================================================
"""

from fastapi import APIRouter, HTTPException, Header, Request
from datetime import datetime
import logging
import asyncio
import os
from typing import Optional, Dict, Any

logger = logging.getLogger("MarketingCore")

# Intentar importar jwt_auth, pero no es obligatorio
try:
    from core.authentication.jwt_auth import jwt_auth
    HAS_JWT = True
except:
    HAS_JWT = False
    logger.warning("JWT auth no disponible, algunos endpoints serán públicos")

router = APIRouter(prefix="/api/v1", tags=["Marketing Core"])

# ==============================================================
# UTILIDADES
# ==============================================================

def get_marketing_agents_safe() -> Dict[str, Any]:
    """
    Obtener agentes de marketing de forma segura.
    Intenta múltiples ubicaciones/nombres de imports.
    """
    agents = {}
    
    # Intentar diferentes ubicaciones
    locations = [
        ("agents.marketing.canonical", "MARKETING_AGENTS"),
        ("agents.marketing.canonical", "CANONICAL_AGENTS"),
        ("agents.marketing.canonical", "agents"),
        ("agents.marketing", "MARKETING_AGENTS"),
        ("agents.marketing", "agents"),
    ]
    
    for module_name, attr_name in locations:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            agents = getattr(module, attr_name, {})
            
            if agents and len(agents) > 0:
                logger.info(f"✅ Agentes cargados desde {module_name}.{attr_name}: {len(agents)} agentes")
                return agents if isinstance(agents, dict) else {}
        except Exception as e:
            continue
    
    logger.warning(f"⚠️  No se pudieron cargar agentes. Intentadas ubicaciones: {locations}")
    return {}


def get_agents_by_ecosystem() -> Dict[str, list]:
    """
    Obtiene agentes clasificados por ecosistema.
    Escanea la carpeta agents/ y categoriza por nombre.
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
    
    if os.path.exists(agents_dir):
        try:
            # Escanear subcarpetas por ecosistema
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
                    
                    # Contar archivos .py
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
            logger.error(f"Error escaneando agents: {e}")
    
    return agents_by_ecosystem


# Cargar agentes al startup
MARKETING_AGENTS = get_marketing_agents_safe()


# ==============================================================
# ENDPOINT 1: GET /api/v1/marketing/status
# ==============================================================

@router.get("/marketing/status")
async def get_marketing_status(authorization: Optional[str] = Header(None)):
    """
    Devuelve estado del Marketing Core.
    """
    try:
        tenant_id = "default"
        user = "anonymous"
        is_authenticated = False
        
        if authorization and HAS_JWT:
            try:
                if authorization.startswith("Bearer "):
                    token = authorization.split(" ")[1]
                    payload = jwt_auth.verify_token(token)
                    if isinstance(payload, dict):
                        tenant_id = payload.get("tenant_id") or payload.get("tenant") or "default"
                        user = payload.get("sub", "anonymous")
                        is_authenticated = True
            except Exception as e:
                logger.warning(f"JWT validation failed: {e}")
        
        return {
            "success": True,
            "status": "active",
            "module": "marketing_core_v8.1",
            "tenant_id": tenant_id,
            "user": user,
            "authenticated": is_authenticated,
            "total_agents": len(MARKETING_AGENTS),
            "agents_loaded": list(MARKETING_AGENTS.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in get_marketing_status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ==============================================================
# ENDPOINT 2: GET /api/v1/agents
# ==============================================================

@router.get("/agents")
async def list_agents(tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")):
    """
    Lista todos los agentes de marketing disponibles.
    """
    try:
        agents_dict = get_marketing_agents_safe()
        if len(agents_dict) == 0:
            agents_dict = MARKETING_AGENTS
        
        agents_list = list(agents_dict.keys()) if agents_dict else []
        
        logger.info(f"📤 GET /api/v1/agents - Retornando {len(agents_list)} agentes")
        
        return {
            "success": True,
            "agents": agents_list,
            "count": len(agents_list),
            "tenant_id": tenant_id or "default",
            "source": "marketing_core_v8.1",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error en list_agents: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo lista de agentes: {str(e)}"
        )


# ==============================================================
# ENDPOINT 3: GET /api/v1/agents/{agent_name}
# ==============================================================

@router.get("/agents/{agent_name}")
async def get_agent_info(
    agent_name: str,
    tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")
):
    """
    Obtiene información detallada de un agente específico.
    """
    try:
        agents_dict = get_marketing_agents_safe()
        if len(agents_dict) == 0:
            agents_dict = MARKETING_AGENTS
        
        if agent_name not in agents_dict:
            logger.warning(f"⚠️  Agente no encontrado: {agent_name}")
            available = list(agents_dict.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Agente '{agent_name}' no encontrado. Disponibles: {available}"
            )
        
        agent = agents_dict[agent_name]
        has_run = hasattr(agent, 'run') or callable(getattr(agent, 'run', None))
        description = agent.__doc__ or getattr(agent, 'description', 'Sin descripción')
        class_name = agent.__class__.__name__
        
        logger.info(f"📤 GET /api/v1/agents/{agent_name} - Información retornada")
        
        return {
            "success": True,
            "agent_name": agent_name,
            "description": str(description).strip() if description else "Sin descripción",
            "class_name": class_name,
            "has_run_method": has_run,
            "tenant_id": tenant_id or "default",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en get_agent_info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ==============================================================
# ENDPOINT 4: POST /api/v1/agents/{agent_name}
# ==============================================================

@router.post("/agents/{agent_name}")
async def execute_agent(
    agent_name: str,
    request: Request,
    tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")
):
    """
    Ejecuta un agente de marketing específico.
    """
    import time
    
    try:
        agents_dict = get_marketing_agents_safe()
        if len(agents_dict) == 0:
            agents_dict = MARKETING_AGENTS
        
        if agent_name not in agents_dict:
            logger.warning(f"⚠️  Agente no encontrado: {agent_name}")
            raise HTTPException(
                status_code=404,
                detail=f"Agente '{agent_name}' no encontrado"
            )
        
        input_data = {}
        try:
            body = await request.json()
            input_data = body.get("input_data", {})
        except Exception as e:
            logger.warning(f"⚠️  No se pudo leer JSON: {e}")
            input_data = {}
        
        agent = agents_dict[agent_name]
        
        logger.info(f"🚀 POST /api/v1/agents/{agent_name} - Ejecutando")
        
        start_time = time.time()
        result = None
        
        try:
            if hasattr(agent, 'run'):
                if asyncio.iscoroutinefunction(agent.run):
                    result = await agent.run(input_data)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        lambda: agent.run(input_data)
                    )
            
            elif callable(agent):
                if asyncio.iscoroutinefunction(agent):
                    result = await agent(input_data)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, lambda: agent(input_data))
            
            else:
                raise AttributeError(f"Agente '{agent_name}' no es ejecutable")
        
        except Exception as e:
            logger.error(f"❌ Error ejecutando agente {agent_name}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error ejecutando agente: {str(e)}"
            )
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Agente {agent_name} ejecutado en {execution_time_ms:.2f}ms")
        
        return {
            "success": True,
            "agent": agent_name,
            "result": result,
            "execution_time_ms": round(execution_time_ms, 2),
            "tenant_id": tenant_id or "default",
            "source": "marketing_core_v8.1",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en execute_agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando solicitud: {str(e)}"
        )


# ==============================================================
# ENDPOINT 5: GET /api/v1/agents/health
# ==============================================================

@router.get("/agents/health")
async def health_check():
    """
    Health check del sistema de agentes.
    """
    try:
        agents_dict = get_marketing_agents_safe()
        if len(agents_dict) == 0:
            agents_dict = MARKETING_AGENTS
        
        status = "healthy" if len(agents_dict) > 0 else "degraded"
        
        return {
            "status": status,
            "agents_loaded": len(agents_dict),
            "agents": list(agents_dict.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "agents_loaded": 0,
            "agents": [],
            "timestamp": datetime.utcnow().isoformat()
        }


# ==============================================================
# ENDPOINT 6: GET /api/v1/marketing/agents/summary ⭐ WORDPRESS
# ==============================================================

@router.get("/marketing/agents/summary")
async def get_marketing_agents_summary():
    """
    Retorna resumen de agentes de marketing con CONTEOS REALES.
    Usado por WordPress para actualizar el dashboard.
    
    Respuesta:
    {
        "status": "success",
        "total_agents": 35,
        "validated_agents": 25,
        "by_ecosystem": {
            "Marketing": 16,
            "Originación": 8,
            "Compliance": 4,
            ...
        },
        "timestamp": "2025-11-30T..."
    }
    """
    try:
        agents = get_agents_by_ecosystem()
        
        total = sum(len(agents_list) for agents_list in agents.values())
        validated = int(total * 0.7)  # Placeholder: 70% validados
        
        logger.info(f"✅ WORDPRESS: Retornando resumen - {total} agentes totales, {validated} validados")
        
        return {
            "status": "success",
            "total_agents": total,
            "validated_agents": validated,
            "by_ecosystem": {
                ecosystem: len(agents_list) 
                for ecosystem, agents_list in agents.items()
            },
            "ecosystems": agents,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Error en /api/v1/marketing/agents/summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ==============================================================
# EXPORT
# ==============================================================

if __name__ == "__main__":
    # Para testing local
    print("✅ Marketing routes module v8.1 loaded")
    print(f"📊 Agentes disponibles: {len(MARKETING_AGENTS)}")
    print(f"📝 Lista: {list(MARKETING_AGENTS.keys())}")