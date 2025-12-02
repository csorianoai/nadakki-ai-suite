"""
===============================================================================
 NADAKKI AI SUITE - JWT AUTHENTICATION MODULE (v3.3 Stable)
 Autor: GPT-5 / Elena
 Fecha: 2025-11-07
===============================================================================
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List, Optional

# ==============================================================
# CONFIGURACIÓN PRINCIPAL
# ==============================================================

import os`nSECRET_KEY = os.getenv("JWT_SECRET_KEY", "nadakki-secret-key-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ==============================================================
# CREACIÓN Y VERIFICACIÓN DE TOKENS
# ==============================================================

def create_access_token(data: dict, tenant_id: str, roles: Optional[List[str]] = None):
    """Crea un token JWT de acceso"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "tenant_id": tenant_id,
        "roles": roles or ["user"],
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(username: str, tenant_id: str):
    """Crea un token JWT de actualización"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": username,
        "tenant_id": tenant_id,
        "type": "refresh",
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict:
    """Verifica y decodifica un JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido o expirado: {str(e)}",
        )

# ==============================================================
# DEPENDENCIAS FASTAPI PARA ENDPOINTS PROTEGIDOS
# ==============================================================

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Extrae información del usuario autenticado a partir del token JWT"""
    payload = verify_token(token)
    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Token inválido: usuario no encontrado")
    return payload


def require_roles(required_roles: List[str]):
    """Dependencia que verifica los roles del usuario"""
    def role_checker(current_user: Dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return current_user
    return role_checker


def require_tenant(current_user: Dict = Depends(get_current_user)):
    """Dependencia que verifica el tenant del usuario"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant no especificado en el token")
    return tenant_id


# ==============================================================
# CLASE DE INTERFAZ COMPATIBLE (para legacy code)
# ==============================================================

class jwt_auth:
    """Compatibilidad con versiones anteriores"""
    
    @staticmethod
    def create_access_token(data: dict, tenant_id: str, roles: Optional[List[str]] = None):
        return create_access_token(data, tenant_id, roles)
    
    @staticmethod
    def create_refresh_token(username: str, tenant_id: str):
        return create_refresh_token(username, tenant_id)
    
    @staticmethod
    def verify_token(token: str):
        return verify_token(token)
    
    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme)):
        return get_current_user(token)
    
    @staticmethod
    def require_roles(required_roles: List[str]):
        return require_roles(required_roles)
    
    @staticmethod
    def require_tenant(current_user: Dict = Depends(get_current_user)):
        return require_tenant(current_user)

