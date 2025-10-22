"""
Sistema de Billing y Rate Limiting Enterprise
Manejo automático de facturación, límites de uso y alertas por tenant
"""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
from dataclasses import dataclass
from enum import Enum

class PlanType(Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"  
    ENTERPRISE = "enterprise"

@dataclass
class PlanConfig:
    name: str
    monthly_price: float
    monthly_evaluations: int
    features: List[str]
    support_level: str

class BillingManager:
    """Gestor de facturación y límites por tenant"""
    
    def __init__(self, db_path="billing.db"):
        self.db_path = db_path
        self.plans = {
            PlanType.STARTER: PlanConfig(
                name="Lambda Starter",
                monthly_price=999.0,
                monthly_evaluations=1000,
                features=["basic_evaluation", "email_support"],
                support_level="email"
            ),
            PlanType.PROFESSIONAL: PlanConfig(
                name="Lambda Professional", 
                monthly_price=1999.0,
                monthly_evaluations=10000,
                features=["advanced_evaluation", "bureau_integration", "priority_support"],
                support_level="priority"
            ),
            PlanType.ENTERPRISE: PlanConfig(
                name="Enterprise Unlimited",
                monthly_price=4999.0,
                monthly_evaluations=100000,
                features=["unlimited_evaluation", "custom_algorithms", "dedicated_support"],
                support_level="dedicated"
            )
        }
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Inicializa base de datos de billing"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tenant_usage (
                    tenant_id TEXT,
                    year_month TEXT,
                    evaluations_count INTEGER DEFAULT 0,
                    plan_type TEXT,
                    monthly_limit INTEGER,
                    overage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (tenant_id, year_month)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS billing_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT,
                    event_type TEXT,
                    event_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def track_evaluation(self, tenant_id: str, tenant_config: dict = None) -> Dict:
        """Registra una evaluación y verifica límites"""
        with self.lock:
            current_month = datetime.now().strftime('%Y-%m')
            
            # Obtener configuración del plan
            plan_type = self._get_tenant_plan(tenant_id, tenant_config)
            plan_config = self.plans[plan_type]
            
            with sqlite3.connect(self.db_path) as conn:
                # Obtener o crear registro de uso mensual
                cursor = conn.execute('''
                    SELECT evaluations_count, overage_count 
                    FROM tenant_usage 
                    WHERE tenant_id = ? AND year_month = ?
                ''', (tenant_id, current_month))
                
                row = cursor.fetchone()
                
                if row:
                    current_count, overage_count = row
                    new_count = current_count + 1
                    new_overage = max(0, new_count - plan_config.monthly_evaluations)
                    
                    conn.execute('''
                        UPDATE tenant_usage 
                        SET evaluations_count = ?, overage_count = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE tenant_id = ? AND year_month = ?
                    ''', (new_count, new_overage, tenant_id, current_month))
                else:
                    new_count = 1
                    new_overage = max(0, new_count - plan_config.monthly_evaluations)
                    
                    conn.execute('''
                        INSERT INTO tenant_usage 
                        (tenant_id, year_month, evaluations_count, plan_type, monthly_limit, overage_count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (tenant_id, current_month, new_count, plan_type.value, 
                         plan_config.monthly_evaluations, new_overage))
                
                # Registrar evento
                event_data = json.dumps({
                    'evaluations_count': new_count,
                    'monthly_limit': plan_config.monthly_evaluations,
                    'overage_count': new_overage,
                    'plan_type': plan_type.value
                })
                
                conn.execute('''
                    INSERT INTO billing_events (tenant_id, event_type, event_data)
                    VALUES (?, ?, ?)
                ''', (tenant_id, 'evaluation_tracked', event_data))
                
                conn.commit()
                
                # Verificar límites y generar alertas
                usage_status = self._check_usage_limits(tenant_id, new_count, plan_config)
                
                return {
                    'allowed': usage_status['allowed'],
                    'current_usage': new_count,
                    'monthly_limit': plan_config.monthly_evaluations,
                    'overage_count': new_overage,
                    'plan_type': plan_type.value,
                    'warnings': usage_status.get('warnings', []),
                    'actions': usage_status.get('actions', [])
                }
    
    def _get_tenant_plan(self, tenant_id: str, tenant_config: dict = None) -> PlanType:
        """Obtiene el plan del tenant desde configuración"""
        if tenant_config and 'plan_type' in tenant_config:
            plan_str = tenant_config['plan_type'].lower()
            for plan_type in PlanType:
                if plan_type.value == plan_str:
                    return plan_type
        
        # Plan por defecto basado en tenant_id
        if 'enterprise' in tenant_id.lower():
            return PlanType.ENTERPRISE
        elif 'professional' in tenant_id.lower() or 'pro' in tenant_id.lower():
            return PlanType.PROFESSIONAL
        else:
            return PlanType.STARTER
    
    def _check_usage_limits(self, tenant_id: str, current_usage: int, plan_config: PlanConfig) -> Dict:
        """Verifica límites de uso y genera alertas"""
        monthly_limit = plan_config.monthly_evaluations
        usage_percentage = (current_usage / monthly_limit) * 100 if monthly_limit > 0 else 0
        
        warnings = []
        actions = []
        allowed = True
        
        # Sistema de alertas escalonadas
        if usage_percentage >= 100:
            if plan_config.name != "Enterprise Unlimited":
                allowed = False
                warnings.append(f"LÍMITE EXCEDIDO: {current_usage}/{monthly_limit} evaluaciones")
                actions.append("Suspender evaluaciones adicionales")
            else:
                warnings.append(f"Uso intensivo: {current_usage} evaluaciones")
        elif usage_percentage >= 90:
            warnings.append(f"ALERTA 90%: {current_usage}/{monthly_limit} evaluaciones")
            actions.append("Considerar upgrade de plan")
        elif usage_percentage >= 75:
            warnings.append(f"Alerta 75%: {current_usage}/{monthly_limit} evaluaciones")
        elif usage_percentage >= 50:
            warnings.append(f"Uso moderado: {current_usage}/{monthly_limit} evaluaciones")
        
        return {
            'allowed': allowed,
            'usage_percentage': round(usage_percentage, 2),
            'warnings': warnings,
            'actions': actions
        }
    
    def get_tenant_usage_summary(self, tenant_id: str) -> Dict:
        """Obtiene resumen de uso del tenant"""
        current_month = datetime.now().strftime('%Y-%m')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT evaluations_count, plan_type, monthly_limit, overage_count, updated_at
                FROM tenant_usage 
                WHERE tenant_id = ? AND year_month = ?
            ''', (tenant_id, current_month))
            
            row = cursor.fetchone()
            
            if row:
                evaluations, plan_type, monthly_limit, overage, updated_at = row
                usage_percentage = (evaluations / monthly_limit * 100) if monthly_limit > 0 else 0
                
                return {
                    'tenant_id': tenant_id,
                    'current_month': current_month,
                    'evaluations_used': evaluations,
                    'monthly_limit': monthly_limit,
                    'overage_count': overage,
                    'usage_percentage': round(usage_percentage, 2),
                    'plan_type': plan_type,
                    'last_updated': updated_at,
                    'remaining_evaluations': max(0, monthly_limit - evaluations)
                }
            else:
                return {
                    'tenant_id': tenant_id,
                    'current_month': current_month,
                    'evaluations_used': 0,
                    'monthly_limit': 1000,  # Default starter
                    'usage_percentage': 0.0,
                    'plan_type': 'starter',
                    'remaining_evaluations': 1000
                }
    
    def generate_monthly_bill(self, tenant_id: str, year_month: str = None) -> Dict:
        """Genera factura mensual para un tenant"""
        if not year_month:
            year_month = datetime.now().strftime('%Y-%m')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT evaluations_count, plan_type, monthly_limit, overage_count
                FROM tenant_usage 
                WHERE tenant_id = ? AND year_month = ?
            ''', (tenant_id, year_month))
            
            row = cursor.fetchone()
            
            if not row:
                return {'error': f'No usage data for {tenant_id} in {year_month}'}
            
            evaluations, plan_type, monthly_limit, overage = row
            
            # Obtener configuración del plan
            plan_enum = PlanType(plan_type)
            plan_config = self.plans[plan_enum]
            
            # Calcular factura
            base_cost = plan_config.monthly_price
            overage_rate = 0.10  # .10 por evaluación adicional
            overage_cost = overage * overage_rate
            total_cost = base_cost + overage_cost
            
            bill = {
                'tenant_id': tenant_id,
                'billing_period': year_month,
                'plan': {
                    'name': plan_config.name,
                    'base_cost': base_cost,
                    'included_evaluations': monthly_limit
                },
                'usage': {
                    'evaluations_used': evaluations,
                    'overage_evaluations': overage,
                    'overage_rate': overage_rate,
                    'overage_cost': round(overage_cost, 2)
                },
                'billing': {
                    'subtotal': round(base_cost + overage_cost, 2),
                    'tax': round(total_cost * 0.18, 2),  # ITBIS 18%
                    'total': round(total_cost * 1.18, 2)
                },
                'generated_at': datetime.now().isoformat()
            }
            
            # Registrar evento de facturación
            conn.execute('''
                INSERT INTO billing_events (tenant_id, event_type, event_data)
                VALUES (?, ?, ?)
            ''', (tenant_id, 'bill_generated', json.dumps(bill)))
            
            conn.commit()
            
            return bill

class RateLimiter:
    """Rate limiter por tenant"""
    
    def __init__(self):
        self.requests = {}
        self.lock = threading.Lock()
    
    def is_allowed(self, tenant_id: str, max_requests_per_minute: int = 60) -> Tuple[bool, Dict]:
        """Verifica si la request está dentro de los límites"""
        with self.lock:
            current_time = time.time()
            minute_ago = current_time - 60
            
            # Limpiar requests antiguas
            if tenant_id in self.requests:
                self.requests[tenant_id] = [
                    req_time for req_time in self.requests[tenant_id] 
                    if req_time > minute_ago
                ]
            else:
                self.requests[tenant_id] = []
            
            # Verificar límite
            current_requests = len(self.requests[tenant_id])
            
            if current_requests < max_requests_per_minute:
                self.requests[tenant_id].append(current_time)
                return True, {
                    'allowed': True,
                    'current_requests': current_requests + 1,
                    'limit': max_requests_per_minute,
                    'reset_in_seconds': 60
                }
            else:
                return False, {
                    'allowed': False,
                    'current_requests': current_requests,
                    'limit': max_requests_per_minute,
                    'reset_in_seconds': 60,
                    'error': 'Rate limit exceeded'
                }

# Instancias globales
billing_manager = BillingManager()
rate_limiter = RateLimiter()

def track_tenant_evaluation(tenant_id: str, tenant_config: dict = None) -> Dict:
    """Función principal para tracking de evaluaciones"""
    return billing_manager.track_evaluation(tenant_id, tenant_config)

def check_rate_limit(tenant_id: str, max_requests: int = 60) -> Tuple[bool, Dict]:
    """Función principal para verificar rate limiting"""
    return rate_limiter.is_allowed(tenant_id, max_requests)

def get_tenant_billing_summary(tenant_id: str) -> Dict:
    """Función principal para obtener resumen de billing"""
    return billing_manager.get_tenant_usage_summary(tenant_id)
