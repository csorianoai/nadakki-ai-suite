"""
Advanced CORS Configuration for Nadakki Enterprise
"""
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

class EnterprisesCORSConfig:
    def __init__(self):
        self.allowed_origins = self._get_allowed_origins()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allowed_headers = [
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-WordPress-Site",
            "X-WordPress-User", 
            "X-WP-Nonce",
            "X-Tenant-ID",
            "X-API-Key",
            "X-Client-Version"
        ]
        self.expose_headers = [
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset", 
            "X-Response-Time"
        ]
    
    def _get_allowed_origins(self) -> List[str]:
        """Get allowed origins from environment or defaults"""
        env_origins = os.getenv('CORS_ALLOWED_ORIGINS')
        if env_origins:
            return env_origins.split(',')
        
        return [
            "https://nadakki.com",
            "https://www.nadakki.com",
            "https://admin.nadakki.com",
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080"
        ]
    
    def add_cors_middleware(self, app):
        """Add CORS middleware to FastAPI app"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allowed_origins,
            allow_credentials=True,
            allow_methods=self.allowed_methods,
            allow_headers=self.allowed_headers,
            expose_headers=self.expose_headers,
            max_age=86400  # 24 hours
        )
        
        return app

# Global configuration instance
cors_config = EnterprisesCORSConfig()
