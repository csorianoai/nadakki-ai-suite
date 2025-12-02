# JWT Authentication using PyJWT
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

class JWTAuth:
    def __init__(self):
        self.secret_key = \"nadakki-secret-key-2025\"
        self.algorithm = \"HS256\"
        self.access_token_expire_minutes = 30
    
    def create_access_token(self, data: Dict[str, Any], tenant_id: str = None, roles: list = None) -> str:
        to_encode = data.copy()
        if tenant_id:
            to_encode.update({\"tenant_id\": tenant_id})
        if roles:
            to_encode.update({\"roles\": roles})
        
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({\"exp\": expire, \"type\": \"access\"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, username: str, tenant_id: str) -> str:
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode = {
            \"sub\": username,
            \"tenant_id\": tenant_id,
            \"exp\": expire,
            \"type\": \"refresh\"
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception(\"Token expirado\")
        except jwt.InvalidTokenError:
            raise Exception(\"Token inválido\")

# Instancia global
jwt_auth = JWTAuth()
