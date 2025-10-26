"""
Usage Tracker Integrado - Conecta con sistema Nadakki existente
Usa la misma base de datos (tenants.db) para mantener consistencia
"""

import sqlite3
from datetime import datetime
from typing import Dict, Optional, List
import json

class IntegratedUsageTracker:
    """
    Usage Tracker que se integra con tu sistema multi-tenant existente
    """
    
    def __init__(self, db_path: str = "tenants.db"):
        self.db_path = db_path
        self._ensure_usage_tables()
    
    def _ensure_usage_tables(self):
        """Asegura que las tablas de uso existan en tu DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar si las tablas de uso ya existen
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='usage_logs'
        """)
        
        if not cursor.fetchone():
            print("🔄 Creando tablas de uso en tenants.db...")
            
            # Tabla de logs de uso
            cursor.execute("""
                CREATE TABLE usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    method TEXT DEFAULT 'POST',
                    response_status INTEGER DEFAULT 200,
                    response_time_ms REAL DEFAULT 0,
                    tokens_used INTEGER DEFAULT 0,
                    agent_used TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Tabla de resumen mensual
            cursor.execute("""
                CREATE TABLE usage_monthly_summary (
                    tenant_id TEXT NOT NULL,
                    year_month TEXT NOT NULL,
                    total_requests INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    last_updated TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, year_month)
                )
            """)
            
            # Índices para optimización
            cursor.execute("""
                CREATE INDEX idx_usage_tenant_time 
                ON usage_logs(tenant_id, timestamp)
            """)
            
            print("✅ Tablas de uso creadas en tenants.db")
        else:
            print("✅ Tablas de uso ya existen en tenants.db")
        
        conn.commit()
        conn.close()
    
    def log_usage(
        self,
        tenant_id: str,
        endpoint: str,
        tokens_used: int = 0,
        agent_used: str = None,
        response_time_ms: float = 0
    ):
        """Registra uso y actualiza contadores en tenant_limits"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            timestamp = datetime.now().isoformat()
            year_month = datetime.now().strftime("%Y-%m")
            
            # 1. Insertar en log de uso
            cursor.execute("""
                INSERT INTO usage_logs (
                    tenant_id, timestamp, endpoint, tokens_used,
                    agent_used, created_at, response_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tenant_id, timestamp, endpoint, tokens_used, agent_used, timestamp, response_time_ms))
            
            # 2. Actualizar resumen mensual
            cursor.execute("""
                INSERT INTO usage_monthly_summary (
                    tenant_id, year_month, total_requests, total_tokens, last_updated
                ) VALUES (?, ?, 1, ?, ?)
                ON CONFLICT(tenant_id, year_month) DO UPDATE SET
                    total_requests = total_requests + 1,
                    total_tokens = total_tokens + ?,
                    last_updated = ?
            """, (tenant_id, year_month, tokens_used, timestamp, tokens_used, timestamp))
            
            # 3. Actualizar contador en tenant_limits (tu tabla existente)
            cursor.execute("""
                UPDATE tenant_limits 
                SET current_monthly_requests = current_monthly_requests + 1
                WHERE tenant_id = ?
            """, (tenant_id,))
            
            conn.commit()
            print(f"✅ Uso registrado para {tenant_id}")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error registrando uso: {e}")
        finally:
            conn.close()
    
    def get_tenant_usage_report(self, tenant_id: str) -> Dict:
        """Genera reporte completo de uso para un tenant"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener límites del tenant
        cursor.execute("""
            SELECT max_monthly_requests, current_monthly_requests
            FROM tenant_limits 
            WHERE tenant_id = ?
        """, (tenant_id,))
        
        limits = cursor.fetchone()
        
        if not limits:
            return {"error": "Tenant no encontrado"}
        
        max_requests, current_requests = limits
        
        # Obtener resumen del mes actual
        year_month = datetime.now().strftime("%Y-%m")
        cursor.execute("""
            SELECT total_requests, total_tokens
            FROM usage_monthly_summary
            WHERE tenant_id = ? AND year_month = ?
        """, (tenant_id, year_month))
        
        summary = cursor.fetchone()
        total_requests = summary[0] if summary else 0
        total_tokens = summary[1] if summary else 0
        
        # Obtener agentes más usados
        cursor.execute("""
            SELECT agent_used, COUNT(*) as usage_count
            FROM usage_logs
            WHERE tenant_id = ? AND strftime('%Y-%m', timestamp) = ?
            GROUP BY agent_used
            ORDER BY usage_count DESC
            LIMIT 5
        """, (tenant_id, year_month))
        
        top_agents = [{"agent": row[0], "requests": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "tenant_id": tenant_id,
            "period": year_month,
            "usage": {
                "current_requests": current_requests,
                "max_requests": max_requests,
                "remaining_requests": max_requests - current_requests,
                "percentage_used": round((current_requests / max_requests * 100), 2),
                "total_tokens": total_tokens
            },
            "top_agents": top_agents,
            "status": "over_limit" if current_requests >= max_requests else "active"
        }

# Prueba de integración con tu sistema real
if __name__ == "__main__":
    print("🧪 INTEGRACIÓN CON SISTEMA EXISTENTE")
    print("=" * 50)
    
    tracker = IntegratedUsageTracker()
    
    # Probar con tenants reales de tu sistema
    test_tenants = ["credicefi_b27fa331", "banco-popular-rd", "banreservas-rd"]
    
    for tenant in test_tenants:
        print(f"\n--- Probando con {tenant} ---")
        
        # Simular algunos requests
        for i in range(3):
            tracker.log_usage(
                tenant_id=tenant,
                endpoint="/api/v1/evaluate",
                tokens_used=1500,
                agent_used="credit_evaluator",
                response_time_ms=200 + (i * 10)
            )
        
        # Generar reporte
        report = tracker.get_tenant_usage_report(tenant)
        print("📊 Reporte de uso:")
        print(json.dumps(report, indent=2))
    
    print("\n✅ Integración completada exitosamente")
