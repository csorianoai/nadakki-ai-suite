"""
NADAKKI AI SUITE - Tenant Management System
Gestión de tenants, módulos y permisos
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])

# Base de datos simple en archivo JSON (en producción usar PostgreSQL/MongoDB)
TENANTS_DB_FILE = "tenants_db.json"

class TenantCreate(BaseModel):
    tenant_id: str = Field(..., description="ID único del tenant")
    name: str = Field(..., description="Nombre de la empresa")
    email: str = Field(..., description="Email de contacto")
    website: Optional[str] = None
    plan: str = Field(default="starter", description="Plan: starter, professional, enterprise")
    modules: List[str] = Field(default=["marketing"], description="Módulos habilitados")
    industry: Optional[str] = None
    timezone: str = Field(default="America/Mexico_City")
    language: str = Field(default="es")

class TenantResponse(BaseModel):
    tenant_id: str
    name: str
    email: str
    website: Optional[str]
    plan: str
    modules: List[str]
    api_key: str
    created_at: str
    status: str

class TenantIntegration(BaseModel):
    integration_type: str  # meta, twitter, google, sendgrid, hubspot
    credentials: Dict
    status: str = "pending"

def load_tenants_db() -> Dict:
    """Cargar base de datos de tenants"""
    if os.path.exists(TENANTS_DB_FILE):
        with open(TENANTS_DB_FILE, "r") as f:
            return json.load(f)
    return {"tenants": {}, "integrations": {}}

def save_tenants_db(data: Dict):
    """Guardar base de datos de tenants"""
    with open(TENANTS_DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_api_key(tenant_id: str) -> str:
    """Generar API key único para el tenant"""
    import hashlib
    import secrets
    base = f"{tenant_id}_{secrets.token_urlsafe(16)}"
    return f"{tenant_id}_ndk_{hashlib.sha256(base.encode()).hexdigest()[:24]}"

@router.get("/")
async def list_tenants():
    """Listar todos los tenants (solo admin)"""
    db = load_tenants_db()
    return {
        "total": len(db["tenants"]),
        "tenants": [
            {
                "tenant_id": tid,
                "name": t.get("name"),
                "plan": t.get("plan"),
                "modules": t.get("modules", []),
                "status": t.get("status", "active")
            }
            for tid, t in db["tenants"].items()
        ]
    }

@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Obtener información de un tenant"""
    db = load_tenants_db()
    if tenant_id not in db["tenants"]:
        raise HTTPException(404, f"Tenant {tenant_id} not found")
    
    tenant = db["tenants"][tenant_id]
    return {
        "tenant_id": tenant_id,
        "name": tenant.get("name"),
        "email": tenant.get("email"),
        "website": tenant.get("website"),
        "plan": tenant.get("plan"),
        "modules": tenant.get("modules", []),
        "integrations": db.get("integrations", {}).get(tenant_id, {}),
        "created_at": tenant.get("created_at"),
        "status": tenant.get("status", "active")
    }

@router.post("/", response_model=TenantResponse)
async def create_tenant(tenant: TenantCreate):
    """Crear un nuevo tenant"""
    db = load_tenants_db()
    
    if tenant.tenant_id in db["tenants"]:
        raise HTTPException(400, f"Tenant {tenant.tenant_id} already exists")
    
    api_key = generate_api_key(tenant.tenant_id)
    
    db["tenants"][tenant.tenant_id] = {
        "name": tenant.name,
        "email": tenant.email,
        "website": tenant.website,
        "plan": tenant.plan,
        "modules": tenant.modules,
        "api_key": api_key,
        "settings": {
            "industry": tenant.industry,
            "timezone": tenant.timezone,
            "language": tenant.language
        },
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    db["integrations"][tenant.tenant_id] = {}
    
    save_tenants_db(db)
    
    return TenantResponse(
        tenant_id=tenant.tenant_id,
        name=tenant.name,
        email=tenant.email,
        website=tenant.website,
        plan=tenant.plan,
        modules=tenant.modules,
        api_key=api_key,
        created_at=db["tenants"][tenant.tenant_id]["created_at"],
        status="active"
    )

@router.put("/{tenant_id}/modules")
async def update_tenant_modules(tenant_id: str, modules: List[str]):
    """Actualizar módulos habilitados para un tenant"""
    db = load_tenants_db()
    
    if tenant_id not in db["tenants"]:
        raise HTTPException(404, f"Tenant {tenant_id} not found")
    
    valid_modules = ["marketing", "legal", "finanzas", "compliance", "regtech", "contabilidad", 
                     "rrhh", "operaciones", "logistica", "ventas", "all"]
    
    for mod in modules:
        if mod not in valid_modules:
            raise HTTPException(400, f"Invalid module: {mod}")
    
    db["tenants"][tenant_id]["modules"] = modules
    save_tenants_db(db)
    
    return {"tenant_id": tenant_id, "modules": modules, "status": "updated"}

@router.post("/{tenant_id}/integrations/{integration_type}")
async def add_integration(tenant_id: str, integration_type: str, credentials: Dict):
    """Agregar una integración a un tenant (Meta, Twitter, Google, etc.)"""
    db = load_tenants_db()
    
    if tenant_id not in db["tenants"]:
        raise HTTPException(404, f"Tenant {tenant_id} not found")
    
    valid_integrations = ["meta", "twitter", "google_analytics", "google_ads", 
                         "sendgrid", "mailchimp", "hubspot", "salesforce"]
    
    if integration_type not in valid_integrations:
        raise HTTPException(400, f"Invalid integration type: {integration_type}")
    
    if tenant_id not in db["integrations"]:
        db["integrations"][tenant_id] = {}
    
    db["integrations"][tenant_id][integration_type] = {
        "credentials": credentials,
        "status": "connected",
        "connected_at": datetime.now().isoformat()
    }
    
    save_tenants_db(db)
    
    return {
        "tenant_id": tenant_id,
        "integration": integration_type,
        "status": "connected"
    }

@router.get("/{tenant_id}/integrations")
async def get_integrations(tenant_id: str):
    """Obtener integraciones de un tenant"""
    db = load_tenants_db()
    
    if tenant_id not in db["tenants"]:
        raise HTTPException(404, f"Tenant {tenant_id} not found")
    
    return {
        "tenant_id": tenant_id,
        "integrations": db.get("integrations", {}).get(tenant_id, {})
    }

@router.delete("/{tenant_id}/integrations/{integration_type}")
async def remove_integration(tenant_id: str, integration_type: str):
    """Eliminar una integración"""
    db = load_tenants_db()
    
    if tenant_id not in db["tenants"]:
        raise HTTPException(404, f"Tenant {tenant_id} not found")
    
    if tenant_id in db["integrations"] and integration_type in db["integrations"][tenant_id]:
        del db["integrations"][tenant_id][integration_type]
        save_tenants_db(db)
    
    return {"tenant_id": tenant_id, "integration": integration_type, "status": "removed"}

def register_tenant_management_routes(app):
    """Registrar rutas de gestión de tenants"""
    app.include_router(router)
