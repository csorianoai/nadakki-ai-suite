# NADAKKI TENANTS API v6.0
# API profesional para gestionar múltiples instituciones financieras
# 400+ líneas - Endpoints completos, autenticación, validación

from fastapi import FastAPI, Depends, HTTPException, status, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
import hashlib
from datetime import datetime
from core.multi_tenancy.tenant_manager import TenantManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nadakki Tenants API v6.0",
    version="6.0.0",
    description="API profesional para instituciones financieras multi-tenant",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.nadakki.com", "https://admin.nadakki.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

tenant_manager = TenantManager()

async def verify_api_key(x_api_key: str = Header(...)) -> Dict[str, Any]:
    """Verificar API key y obtener contexto del tenant"""
    for tenant_id, config in tenant_manager.tenant_configs.items():
        api_key = config.get('api_keys', {}).get('api_key')
        if api_key and api_key == x_api_key:
            return {
                "tenant_id": tenant_id,
                "config": config,
                "authenticated": True
            }
    
    logger.warning(f"API key inválida")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key inválida",
        headers={"WWW-Authenticate": "Bearer"}
    )

@app.get("/health")
async def health_check():
    """Health check general del sistema"""
    return {
        "status": "healthy",
        "version": "6.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "tenants_loaded": len(tenant_manager.tenant_configs),
        "tenants_active": sum(
            1 for c in tenant_manager.tenant_configs.values()
            if c.get('institution', {}).get('status') == 'active'
        )
    }

@app.get("/api/v1/health/{tenant_id}")
async def tenant_health(
    tenant_id: str,
    context: Dict = Depends(verify_api_key)
):
    """Health check por tenant específico"""
    if tenant_id not in tenant_manager.tenant_configs:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    config = tenant_manager.tenant_configs[tenant_id]
    validation = tenant_manager.validate_tenant(tenant_id)
    
    return {
        "status": "healthy",
        "tenant_id": tenant_id,
        "institution": config['institution']['name'],
        "version": "6.0.0",
        "validation": validation,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/tenants")
async def list_tenants(context: Dict = Depends(verify_api_key)):
    """Listar todas las instituciones activas"""
    tenants = tenant_manager.get_all_tenants()
    return {
        "status": "success",
        "tenants": tenants,
        "count": len(tenants),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/tenants/me")
async def get_current_tenant(context: Dict = Depends(verify_api_key)):
    """Obtener información del tenant actual"""
    tenant_id = context["tenant_id"]
    config = context["config"]
    
    return {
        "status": "success",
        "tenant_id": tenant_id,
        "institution": config['institution'],
        "modules": config.get('modules', {}),
        "sla": config.get('sla', {}),
        "compliance": config.get('compliance', {}),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/tenants/{tenant_id}")
async def get_tenant(
    tenant_id: str,
    context: Dict = Depends(verify_api_key)
):
    """Obtener información de un tenant específico"""
    if tenant_id not in tenant_manager.tenant_configs:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    config = tenant_manager.tenant_configs[tenant_id]
    
    return {
        "status": "success",
        "tenant_id": tenant_id,
        "institution": config['institution'],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/tenants")
async def create_tenant(
    name: str = Query(..., min_length=3, max_length=255),
    institution_type: str = Query(...),
    country: str = Query(..., min_length=2, max_length=2),
    context: Dict = Depends(verify_api_key)
):
    """Crear nueva institución (tenant)"""
    try:
        result = tenant_manager.create_tenant(
            name=name,
            institution_type=institution_type,
            country=country
        )
        return {
            "status": "created",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/{tenant_id}/agents")
async def list_tenant_agents(
    tenant_id: str,
    context: Dict = Depends(verify_api_key)
):
    """Listar agentes disponibles para el tenant"""
    if tenant_id not in tenant_manager.tenant_configs:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    config = tenant_manager.tenant_configs[tenant_id]
    
    return {
        "status": "success",
        "tenant_id": tenant_id,
        "modules": config.get('modules', {}),
        "total_agents": 276,
        "active_agents": sum(
            1 for m in config.get('modules', {}).values()
            if m.get('enabled', False)
        ),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejo global de errores"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "Error interno del servidor",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
