"""
Tenant Onboarding Service - Automatiza creaciÃ³n de nuevos clientes
De 48 horas manual â†’ 5 minutos automatizado
"""

import uuid
import json
import secrets
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict

@dataclass
class TenantConfig:
    """ConfiguraciÃ³n de un tenant"""
    tenant_id: str
    institution_name: str
    institution_type: str
    primary_color: str
    secondary_color: str
    logo_url: str
    contact_email: str
    contact_phone: str
    plan: str
    max_monthly_requests: int
    enabled_agents: list
    custom_risk_thresholds: Dict
    created_at: str
    status: str

class TenantManager:
    """Gestor de tenants multi-instituciÃ³n"""
    
    def __init__(self, config_dir: str = "config/tenants", db_path: str = "tenants.db"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa base de datos de tenants"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id TEXT PRIMARY KEY,
                institution_name TEXT NOT NULL,
                institution_type TEXT NOT NULL,
                plan TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenant_branding (
                tenant_id TEXT PRIMARY KEY,
                primary_color TEXT,
                secondary_color TEXT,
                logo_url TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenant_limits (
                tenant_id TEXT PRIMARY KEY,
                max_monthly_requests INTEGER,
                current_monthly_requests INTEGER DEFAULT 0,
                last_reset TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("âœ… Base de datos inicializada correctamente")
    
    def create_tenant(
        self,
        institution_name: str,
        institution_type: str,
        plan: str,
        contact_email: str,
        contact_phone: str,
        primary_color: str = "#1e40af",
        secondary_color: str = "#3b82f6",
        logo_url: Optional[str] = None,
        enabled_agents: Optional[list] = None
    ) -> Dict:
        """Crea un nuevo tenant en 5 minutos"""
        
        print(f"\nðŸ”§ Creando tenant para {institution_name}...")
        
        tenant_id = self._generate_tenant_id(institution_name)
        api_key = self._generate_api_key()
        plan_config = self._get_plan_config(plan)
        
        if enabled_agents is None:
            enabled_agents = self._get_default_agents_for_plan(plan)
        
        risk_thresholds = {
            "auto_reject": 90,
            "high_risk": 80,
            "additional_analysis": 70,
            "second_evaluation": 50,
            "low_risk": 0
        }
        
        tenant_config = TenantConfig(
            tenant_id=tenant_id,
            institution_name=institution_name,
            institution_type=institution_type,
            primary_color=primary_color,
            secondary_color=secondary_color,
            logo_url=logo_url or f"https://ui-avatars.com/api/?name={institution_name}",
            contact_email=contact_email,
            contact_phone=contact_phone,
            plan=plan,
            max_monthly_requests=plan_config['max_requests'],
            enabled_agents=enabled_agents,
            custom_risk_thresholds=risk_thresholds,
            created_at=datetime.now().isoformat(),
            status="trial"
        )
        
        self._save_tenant_to_db(tenant_config, api_key)
        self._save_tenant_config_file(tenant_config)
        
        print(f"âœ… Tenant ID generado: {tenant_id}")
        print(f"âœ… API Key generada: {api_key[:20]}...")
        print(f"âœ… Plan: {plan} ({plan_config['max_requests']} requests/mes)")
        
        return {
            "success": True,
            "tenant_id": tenant_id,
            "api_key": api_key,
            "dashboard_url": f"https://nadakki.com/{tenant_id}",
            "api_endpoint": f"https://api.nadakki.com/v1/{tenant_id}",
            "plan": plan,
            "monthly_limit": plan_config['max_requests'],
            "trial_days": 60,
            "status": "active",
            "onboarding_time": "< 5 minutes"
        }
    
    def _generate_tenant_id(self, institution_name: str) -> str:
        """Genera ID Ãºnico para tenant"""
        base = institution_name.lower().replace(" ", "_")
        unique_suffix = str(uuid.uuid4())[:8]
        return f"{base}_{unique_suffix}"
    
    def _generate_api_key(self) -> str:
        """Genera API key segura"""
        return f"nadakki_{secrets.token_urlsafe(32)}"
    
    def _get_plan_config(self, plan: str) -> Dict:
        """Retorna configuraciÃ³n segÃºn el plan"""
        plans = {
            "starter": {
                "max_requests": 5000,
                "price_monthly": 997,
                "features": ["basic_agents", "email_support"]
            },
            "professional": {
                "max_requests": 20000,
                "price_monthly": 2997,
                "features": ["all_agents", "priority_support", "custom_thresholds"]
            },
            "enterprise": {
                "max_requests": 999999,
                "price_monthly": 9997,
                "features": [
                    "all_agents",
                    "white_label",
                    "dedicated_support",
                    "custom_integrations",
                    "sla_guarantee"
                ]
            }
        }
        return plans.get(plan, plans["starter"])
    
    def _get_default_agents_for_plan(self, plan: str) -> list:
        """Agentes incluidos por plan"""
        if plan == "starter":
            return [
                "credit_evaluator",
                "fraud_detector",
                "risk_assessor",
                "document_validator",
                "score_calculator"
            ]
        elif plan == "professional":
            return [
                "credit_evaluator",
                "fraud_detector",
                "risk_assessor",
                "document_validator",
                "score_calculator",
                "early_warning",
                "recovery_optimizer",
                "collateral_analyzer",
                "compliance_checker"
            ]
        else:
            return "all"
    
    def _save_tenant_to_db(self, config: TenantConfig, api_key: str):
        """Guarda tenant en base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tenants (
                tenant_id, institution_name, institution_type,
                plan, api_key, status, created_at, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.tenant_id,
            config.institution_name,
            config.institution_type,
            config.plan,
            api_key,
            config.status,
            config.created_at,
            datetime.now().isoformat()
        ))
        
        cursor.execute("""
            INSERT INTO tenant_branding (
                tenant_id, primary_color, secondary_color, logo_url
            ) VALUES (?, ?, ?, ?)
        """, (
            config.tenant_id,
            config.primary_color,
            config.secondary_color,
            config.logo_url
        ))
        
        cursor.execute("""
            INSERT INTO tenant_limits (
                tenant_id, max_monthly_requests, current_monthly_requests, last_reset
            ) VALUES (?, ?, 0, ?)
        """, (
            config.tenant_id,
            config.max_monthly_requests,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        print(f"âœ… Datos guardados en base de datos: {self.db_path}")
    
    def _save_tenant_config_file(self, config: TenantConfig):
        """Guarda archivo JSON de configuraciÃ³n"""
        config_file = self.config_dir / f"{config.tenant_id}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=2, ensure_ascii=False)
        
        print(f"âœ… Archivo de configuraciÃ³n guardado: {config_file}")
    
    def get_tenant_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Obtiene tenant por API key"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.*, b.primary_color, b.secondary_color, b.logo_url,
                   l.max_monthly_requests, l.current_monthly_requests
            FROM tenants t
            LEFT JOIN tenant_branding b ON t.tenant_id = b.tenant_id
            LEFT JOIN tenant_limits l ON t.tenant_id = l.tenant_id
            WHERE t.api_key = ?
        """, (api_key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "tenant_id": row[0],
            "institution_name": row[1],
            "institution_type": row[2],
            "plan": row[3],
            "status": row[5],
            "branding": {
                "primary_color": row[8],
                "secondary_color": row[9],
                "logo_url": row[10]
            },
            "limits": {
                "max_monthly": row[11],
                "current_monthly": row[12]
            }
        }
    
    def list_all_tenants(self) -> list:
        """Lista todos los tenants"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tenant_id, institution_name, plan, status, created_at
            FROM tenants
            ORDER BY created_at DESC
        """)
        
        tenants = []
        for row in cursor.fetchall():
            tenants.append({
                "tenant_id": row[0],
                "institution_name": row[1],
                "plan": row[2],
                "status": row[3],
                "created_at": row[4]
            })
        
        conn.close()
        return tenants


# ============================================================================
# EJEMPLO DE USO - CREAR CREDICEFI
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("  NADAKKI AI SUITE - TENANT ONBOARDING SERVICE")
    print("  Creando tenant: CREDICEFI")
    print("=" * 70)
    
    manager = TenantManager()
    
    # Crear tenant para Credicefi
    result = manager.create_tenant(
        institution_name="Credicefi",
        institution_type="fintech",
        plan="enterprise",
        contact_email="tech@credicefi.com",
        contact_phone="+1-809-000-0000",
        primary_color="#1e40af",
        secondary_color="#3b82f6",
        logo_url="https://credicefi.com/logo.png"
    )
    
    print("\n" + "=" * 70)
    print("âœ… TENANT CREADO EXITOSAMENTE")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    
    # Listar todos los tenants
    print("\n" + "=" * 70)
    print("ðŸ“‹ TENANTS ACTUALES EN EL SISTEMA")
    print("=" * 70)
    all_tenants = manager.list_all_tenants()
    
    if all_tenants:
        for i, tenant in enumerate(all_tenants, 1):
            print(f"\n{i}. {tenant['institution_name']}")
            print(f"   - ID: {tenant['tenant_id']}")
            print(f"   - Plan: {tenant['plan']}")
            print(f"   - Status: {tenant['status']}")
            print(f"   - Creado: {tenant['created_at']}")
    else:
        print("\nâš ï¸ No hay tenants registrados aÃºn")
    
    print("\n" + "=" * 70)
    print("âœ… PROCESO COMPLETADO")
    print("=" * 70)

