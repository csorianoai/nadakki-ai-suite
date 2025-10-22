import json
import os
from datetime import datetime

class TenantManager:
    def __init__(self):
        self.tenants = {
            "demo": {
                "name": "Demo Bank", 
                "status": "active",
                "plan": "starter",
                "created_at": "2025-07-01T00:00:00"
            },
            "banco_demo": {
                "name": "Banco Demo", 
                "status": "active",
                "plan": "professional",
                "created_at": "2025-07-01T00:00:00"
            }
        }
    
    def get_tenant_config(self, tenant_id):
        tenant = self.tenants.get(tenant_id, {})
        return tenant.get("config", {})
    
    def validate_tenant(self, tenant_id):
        tenant = self.tenants.get(tenant_id)
        return tenant and tenant.get("status") == "active"
    
    def list_tenants(self):
        return [
            {
                "id": tid,
                "name": tenant.get("name"),
                "status": tenant.get("status"),
                "plan": tenant.get("plan")
            }
            for tid, tenant in self.tenants.items()
        ]
