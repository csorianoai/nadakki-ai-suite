"""
Tenant Manager - Gestión de múltiples instituciones financieras.
"""
import logging
from typing import Dict, Optional, List
from .config import TenantConfig

logger = logging.getLogger(__name__)


class TenantManager:
    """Gestor de tenants (instituciones financieras)."""
    
    _instance: Optional["TenantManager"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._tenants: Dict[str, TenantConfig] = {}
        self._initialized = True
        logger.info("TenantManager initialized")
    
    def register_tenant(self, config: TenantConfig) -> TenantConfig:
        """Registra un nuevo tenant."""
        if config.tenant_id in self._tenants:
            raise ValueError(f"Tenant {config.tenant_id} already exists")
        self._tenants[config.tenant_id] = config
        logger.info(f"Tenant registered: {config.tenant_id} ({config.name})")
        return config
    
    def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """Obtiene configuración de un tenant."""
        return self._tenants.get(tenant_id)
    
    def list_tenants(self) -> List[TenantConfig]:
        """Lista todos los tenants."""
        return list(self._tenants.values())
    
    def update_tenant(self, tenant_id: str, updates: Dict) -> Optional[TenantConfig]:
        """Actualiza configuración de un tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return None
        for key, value in updates.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        return tenant
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Elimina un tenant."""
        if tenant_id in self._tenants:
            del self._tenants[tenant_id]
            logger.info(f"Tenant deleted: {tenant_id}")
            return True
        return False
    
    def check_feature(self, tenant_id: str, feature: str) -> bool:
        """Verifica si un tenant tiene una feature habilitada."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        return tenant.features.get(feature, False)
    
    def check_limit(self, tenant_id: str, limit: str, current: int) -> bool:
        """Verifica si un tenant está dentro de sus límites."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        max_value = tenant.limits.get(limit, 0)
        return current < max_value


tenant_manager = TenantManager()
