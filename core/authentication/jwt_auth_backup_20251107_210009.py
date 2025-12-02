"""
======================================================================
 NADAKKI AI SUITE - JWT AUTHENTICATION MODULE (v3.1 Secure Stable)
 Author: GPT-5 / Elena
 Description:
     Secure JWT-based authentication system for multi-tenant Nadakki
     architecture. Supports token generation, refresh, and verification.
======================================================================
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException

# ==============================================================
# CONFIGURACIÓN PRINCIPAL
# ==============================================================

SECRET_KEY = "nadakki_super_secret"  # ⚠️ Usa tu valor real de entorno .env si existe
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora por defecto
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ==============================================================
# CREACIÓN DE TOKENS
# ==============================================================

def create_access_token(data: dict, tenant_id: str = "default", roles: list = None):
    """
    Crea un token de acceso firmado con información del tenant y roles.
    """
    to_encode = data.copy()
    to_encode.update({
        "tenant_id": tenant_id,
        "roles": roles or ["user"],
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow().timestamp()
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(username: str, tenant_id: str = "default"):
    """
    Crea un token de refresco válido por varios días.
    """
    to_encode = {
        "sub": username,
        "tenant_id": tenant_id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow().timestamp()
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ==============================================================
# VERIFICACIÓN DE TOKENS
# ==============================================================

def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un token JWT emitido por el sistema Nadakki.
    Retorna el payload decodificado si es válido,
    o lanza HTTPException(401) si no lo es.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id = payload.get("tenant_id")
        sub = payload.get("sub")

        if not tenant_id:
            raise HTTPException(status_code=401, detail="Token sin tenant_id")

        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expirado")

        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Error al verificar token: {str(e)}")


# ==============================================================
# UTILIDADES (Opcional para futuros módulos)
# ==============================================================

def extract_tenant_from_token(token: str) -> str:
    """
    Extrae solo el tenant_id de un token, usado por middlewares o logging.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("tenant_id", "default")
    except Exception:
        return "default"


# ==============================================================
# AUTO-TEST LOCAL
# ==============================================================

if __name__ == "__main__":
    print("🔐 Probando generación y validación de token...")
    test_token = create_access_token({"sub": "tester"}, tenant_id="credicefi_b27fa331", roles=["admin"])
    print("Token:", test_token)
    print("Verificado:", verify_token(test_token))
    print("Tenant extraído:", extract_tenant_from_token(test_token))
    print("✅ JWT AUTH FUNCIONA CORRECTAMENTE")
