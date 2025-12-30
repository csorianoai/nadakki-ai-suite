"""
NADAKKI AI SUITE - ADMIN AUTH MODULE v1.0.0
============================================
Protección básica de endpoints administrativos.
"""
from fastapi import Header, HTTPException, Depends
from typing import Optional
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger("NadakkiAdminAuth")

# Admin API Keys (en producción usar variables de entorno)
ADMIN_KEYS = {
    "nadakki_admin_2025_master": {"role": "super_admin", "name": "Master Admin"},
    "nadakki_admin_credicefi_2025": {"role": "tenant_admin", "tenant_id": "credicefi", "name": "Credicefi Admin"},
}

# Audit log de accesos admin
ADMIN_AUDIT_LOG = []

def log_admin_access(key_used: str, endpoint: str, action: str, success: bool):
    """Registra acceso administrativo"""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "key_hash": hashlib.sha256(key_used.encode()).hexdigest()[:16] if key_used else "none",
        "endpoint": endpoint,
        "action": action,
        "success": success
    }
    ADMIN_AUDIT_LOG.append(entry)
    if len(ADMIN_AUDIT_LOG) > 1000:
        ADMIN_AUDIT_LOG.pop(0)
    logger.info(f"Admin access: {action} on {endpoint} - {'SUCCESS' if success else 'DENIED'}")

async def verify_admin_key(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """
    Verifica que el request tenga una API key de admin válida.
    Usar en endpoints sensibles como crear/editar/suspender tenants.
    """
    if not x_admin_key:
        log_admin_access("", "unknown", "access_attempt", False)
        raise HTTPException(
            status_code=401,
            detail={"error": "Admin key required", "header": "X-Admin-Key"}
        )
    
    if x_admin_key not in ADMIN_KEYS:
        log_admin_access(x_admin_key, "unknown", "invalid_key", False)
        raise HTTPException(
            status_code=403,
            detail={"error": "Invalid admin key", "message": "Access denied"}
        )
    
    admin_info = ADMIN_KEYS[x_admin_key]
    logger.info(f"Admin authenticated: {admin_info['name']} ({admin_info['role']})")
    return admin_info

async def verify_super_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """Solo permite super_admin"""
    admin_info = await verify_admin_key(x_admin_key)
    if admin_info["role"] != "super_admin":
        raise HTTPException(403, {"error": "Super admin access required"})
    return admin_info

def get_admin_audit_log(limit: int = 50):
    """Obtiene el log de auditoría de accesos admin"""
    return {
        "total": len(ADMIN_AUDIT_LOG),
        "entries": ADMIN_AUDIT_LOG[-limit:][::-1]
    }

__all__ = ["verify_admin_key", "verify_super_admin", "log_admin_access", "get_admin_audit_log", "ADMIN_KEYS"]
