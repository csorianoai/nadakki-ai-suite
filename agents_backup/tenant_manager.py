"""
Tenant Manager para Nadakki AI Suite
Maneja configuraciones específicas por institución financiera
"""

import json
from pathlib import Path
from typing import Dict, Optional, List

class TenantManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_dir = self.base_dir / "config" / "tenants"
        self._config_cache = {}
        
        # Crear directorio si no existe
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_tenant_config(self, tenant_id: str) -> Optional[Dict]:
        """Carga configuración específica de un tenant"""
        try:
            # Verificar cache primero
            if tenant_id in self._config_cache:
                return self._config_cache[tenant_id]
            
            config_file = self.config_dir / f"{tenant_id}.json"
            
            if not config_file.exists():
                print(f"⚠️  Configuración no encontrada para tenant: {tenant_id}")
                return None
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Guardar en cache
            self._config_cache[tenant_id] = config
            return config
            
        except Exception as e:
            print(f"❌ Error cargando configuración de {tenant_id}: {str(e)}")
            return None
    
    def get_ai_thresholds(self, tenant_id: str) -> Dict:
        """Obtiene umbrales de IA específicos del tenant"""
        config = self.load_tenant_config(tenant_id)
        
        # Defaults si no hay configuración
        defaults = {
            "reject_auto": 0.90,
            "high_risk": 0.80,
            "risky": 0.70,
            "medium_risk": 0.50,
            "low_risk": 0.00
        }
        
        if not config:
            return defaults
        
        return config.get("ai_engine", {}).get("similarity_thresholds", defaults)
    
    def get_algorithm_weights(self, tenant_id: str) -> Dict:
        """Obtiene pesos de algoritmos específicos del tenant"""
        config = self.load_tenant_config(tenant_id)
        
        defaults = {
            "cosine": 0.4,
            "euclidean": 0.3, 
            "jaccard": 0.3
        }
        
        if not config:
            return defaults
        
        return config.get("ai_engine", {}).get("algorithm_weights", defaults)
    
    def get_business_rules(self, tenant_id: str) -> Dict:
        """Obtiene reglas de negocio específicas del tenant"""
        config = self.load_tenant_config(tenant_id)
        
        defaults = {
            "max_loan_amount": 1000000,
            "min_credit_score": 600,
            "max_debt_to_income": 0.40
        }
        
        if not config:
            return defaults
        
        return config.get("business_rules", defaults)
    
    def get_pricing_plan(self, tenant_id: str) -> Dict:
        """Obtiene plan de pricing del tenant"""
        config = self.load_tenant_config(tenant_id)
        
        defaults = {
            "tier": "starter",
            "monthly_evaluations_limit": 1000,
            "price_per_month": 999
        }
        
        if not config:
            return defaults
        
        return config.get("pricing_plan", defaults)
    
    def get_tenant_info(self, tenant_id: str) -> Dict:
        """Obtiene información básica del tenant"""
        config = self.load_tenant_config(tenant_id)
        
        if not config:
            return {
                "id": tenant_id,
                "name": "Unknown",
                "type": "financial",
                "status": "unknown"
            }
        
        return config.get("tenant_info", {})
    
    def list_all_tenants(self) -> List[Dict]:
        """Lista todos los tenants configurados"""
        tenants = []
        
        try:
            for config_file in self.config_dir.glob("*.json"):
                tenant_id = config_file.stem
                config = self.load_tenant_config(tenant_id)
                
                if config:
                    tenant_info = config.get("tenant_info", {})
                    pricing = config.get("pricing_plan", {})
                    
                    tenants.append({
                        "tenant_id": tenant_id,
                        "name": tenant_info.get("name", ""),
                        "type": tenant_info.get("type", ""),
                        "status": tenant_info.get("status", ""),
                        "tier": pricing.get("tier", ""),
                        "monthly_limit": pricing.get("monthly_evaluations_limit", 0)
                    })
        
        except Exception as e:
            print(f"❌ Error listando tenants: {str(e)}")
        
        return tenants
    
    def validate_tenant(self, tenant_id: str) -> bool:
        """Valida que un tenant existe y está activo"""
        config = self.load_tenant_config(tenant_id)
        
        if not config:
            return False
        
        tenant_info = config.get("tenant_info", {})
        return tenant_info.get("status") == "active"

# Instancia global del tenant manager
tenant_manager = TenantManager()