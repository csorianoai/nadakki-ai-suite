"""
Configuration Management - Multi-Tenant Support
Soporta múltiples instituciones financieras.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class TenantConfig:
    """Configuración por tenant (institución financiera)."""
    tenant_id: str
    name: str
    domain: str
    database_url: str
    api_key_prefix: str
    features: Dict[str, bool] = field(default_factory=dict)
    limits: Dict[str, int] = field(default_factory=dict)
    branding: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def default(cls, tenant_id: str, name: str) -> "TenantConfig":
        return cls(
            tenant_id=tenant_id,
            name=name,
            domain=f"{tenant_id}.nadakki.com",
            database_url=f"postgresql://localhost/{tenant_id}_db",
            api_key_prefix=f"ndk_{tenant_id}_",
            features={
                "campaigns": True,
                "scheduler": True,
                "analytics": True,
                "ai_content": True,
                "multi_platform": True
            },
            limits={
                "max_campaigns": 100,
                "max_connections": 20,
                "max_posts_per_day": 50,
                "storage_gb": 10
            },
            branding={
                "primary_color": "#4F46E5",
                "logo_url": "",
                "company_name": name
            }
        )


class Settings:
    """Application Settings."""
    
    def __init__(self):
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.debug = self.environment == Environment.DEVELOPMENT
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.secret_key = os.getenv("SECRET_KEY", "nadakki-secret-key-change-in-production")
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./nadakki.db")
        
        # Redis (para cache y rate limiting)
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # OAuth (credenciales por plataforma)
        self.oauth_credentials: Dict[str, Dict[str, str]] = {}
        
    def get_oauth_credentials(self, platform: str) -> Dict[str, str]:
        """Obtiene credenciales OAuth para una plataforma."""
        return self.oauth_credentials.get(platform, {})


settings = Settings()
