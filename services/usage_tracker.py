"""
Usage Tracker Service - Tracking de uso para billing
Registra requests, calcula consumo mensual, genera alertas
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class UsageLog:
    """Log de un request individual"""
    log_id: str
    tenant_id: str
    timestamp: str
    endpoint: str
    method: str
    response_status: int
    response_time_ms: float
    tokens_used: int
    agent_used: Optional[str] = None

@dataclass
class UsageSummary:
    """Resumen mensual de uso"""
    tenant_id: str
    year_month: str
    total_requests: int
    total_tokens: int
    avg_response_time_ms: float
    success_rate: float
    limit: int
    usage_percentage: float
    last_updated: str

class UsageTracker:
    """
    Sistema de tracking de uso para billing multi-tenant
    """
    
    def __init__(self, db_path: str = "usage.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa base de datos de uso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de logs detallados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                log_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                response_status INTEGER NOT NULL,
                response_time_ms REAL NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                agent_used TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Crear índice para búsquedas rápidas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tenant_timestamp 
            ON usage_logs(tenant_id, timestamp)
        """)
        
        # Tabla de resúmenes mensuales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_summary (
                tenant_id TEXT NOT NULL,
                year_month TEXT NOT NULL,
                total_requests INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                avg_response_time_ms REAL DEFAULT 0,
                success_rate REAL DEFAULT 100.0,
                limit INTEGER NOT NULL,
                usage_percentage REAL DEFAULT 0,
                last_updated TEXT NOT NULL,
                PRIMARY KEY (tenant_id, year_month)
            )
        """)
        
        # Tabla de alertas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                threshold_percentage REAL NOT NULL,
                triggered_at TEXT NOT NULL,
                resolved_at TEXT,
                message TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos de uso inicializada")
    
    def log_request(
        self,
        tenant_id: str,
        endpoint: str,
        method: str = "POST",
        response_status: int = 200,
        response_time_ms: float = 0.0,
        tokens_used: int = 0,
        agent_used: Optional[str] = None
    ) -> Dict:
        """
        Registra un request individual
        
        Returns:
            dict: Status del tracking y alertas si aplica
        """
        
        import uuid
        
        log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insertar log
        cursor.execute("""
            INSERT INTO usage_logs (
                log_id, tenant_id, timestamp, endpoint, method,
                response_status, response_time_ms, tokens_used,
                agent_used, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id, tenant_id, timestamp, endpoint, method,
            response_status, response_time_ms, tokens_used,
            agent_used, timestamp
        ))
        
        conn.commit()
        conn.close()
        
        # Actualizar resumen mensual
        self._update_monthly_summary(tenant_id)
        
        # Verificar límites y generar alertas
        alerts = self._check_limits(tenant_id)
        
        return {
            "logged": True,
            "log_id": log_id,
            "timestamp": timestamp,
            "alerts": alerts
        }
    
    def _update_monthly_summary(self, tenant_id: str):
        """Actualiza el resumen mensual del tenant"""
        
        year_month = datetime.now().strftime("%Y-%m")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calcular estadísticas del mes actual
        cursor.execute("""
            SELECT 
                COUNT(*) as total_requests,
                SUM(tokens_used) as total_tokens,
                AVG(response_time_ms) as avg_response_time,
                (SUM(CASE WHEN response_status BETWEEN 200 AND 299 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
            FROM usage_logs
            WHERE tenant_id = ?
            AND strftime('%Y-%m', timestamp) = ?
        """, (tenant_id, year_month))
        
        stats = cursor.fetchone()
        
        if stats and stats[0] > 0:
            # Obtener límite del tenant
            limit = self._get_tenant_limit(tenant_id)
            
            total_requests = stats[0] or 0
            total_tokens = stats[1] or 0
            avg_response_time = stats[2] or 0
            success_rate = stats[3] or 100.0
            usage_percentage = (total_requests / limit * 100) if limit > 0 else 0
            
            # Insertar o actualizar resumen
            cursor.execute("""
                INSERT OR REPLACE INTO usage_summary (
                    tenant_id, year_month, total_requests, total_tokens,
                    avg_response_time_ms, success_rate, limit,
                    usage_percentage, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tenant_id, year_month, total_requests, total_tokens,
                avg_response_time, success_rate, limit,
                usage_percentage, datetime.now().isoformat()
            ))
            
            conn.commit()
        
        conn.close()
    
    def _get_tenant_limit(self, tenant_id: str) -> int:
        """
        Obtiene el límite mensual del tenant
        TODO: Integrar con TenantManager
        """
        return 999999  # Enterprise por defecto
    
    def _check_limits(self, tenant_id: str) -> List[Dict]:
        """
        Verifica límites y genera alertas si es necesario
        """
        
        year_month = datetime.now().strftime("%Y-%m")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT total_requests, limit, usage_percentage
            FROM usage_summary
            WHERE tenant_id = ? AND year_month = ?
        """, (tenant_id, year_month))
        
        result = cursor.fetchone()
        
        alerts = []
        
        if result:
            total_requests, limit, usage_percentage = result
            
            alert_thresholds = [
                (50, "warning", "50% del límite mensual alcanzado"),
                (80, "alert", "80% del límite mensual alcanzado"),
                (95, "critical", "95% del límite mensual - límite próximo"),
                (100, "limit_reached", "Límite mensual alcanzado")
            ]
            
            for threshold, alert_type, message in alert_thresholds:
                if usage_percentage >= threshold:
                    cursor.execute("""
                        SELECT alert_id FROM usage_alerts
                        WHERE tenant_id = ?
                        AND alert_type = ?
                        AND strftime('%Y-%m', triggered_at) = ?
                        AND resolved_at IS NULL
                    """, (tenant_id, alert_type, year_month))
                    
                    existing_alert = cursor.fetchone()
                    
                    if not existing_alert:
                        cursor.execute("""
                            INSERT INTO usage_alerts (
                                tenant_id, alert_type, threshold_percentage,
                                triggered_at, message
                            ) VALUES (?, ?, ?, ?, ?)
                        """, (
                            tenant_id, alert_type, threshold,
                            datetime.now().isoformat(),
                            f"{message} ({total_requests}/{limit} requests)"
                        ))
                        
                        alerts.append({
                            "type": alert_type,
                            "threshold": threshold,
                            "message": message,
                            "usage": f"{total_requests}/{limit}",
                            "percentage": usage_percentage
                        })
        
        conn.commit()
        conn.close()
        
        return alerts
    
    def get_monthly_usage(self, tenant_id: str, year_month: Optional[str] = None) -> Optional[Dict]:
        """Obtiene resumen mensual de uso"""
        
        if year_month is None:
            year_month = datetime.now().strftime("%Y-%m")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM usage_summary
            WHERE tenant_id = ? AND year_month = ?
        """, (tenant_id, year_month))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "tenant_id": row[0],
            "year_month": row[1],
            "total_requests": row[2],
            "total_tokens": row[3],
            "avg_response_time_ms": row[4],
            "success_rate": row[5],
            "limit": row[6],
            "usage_percentage": row[7],
            "last_updated": row[8],
            "remaining_requests": row[6] - row[2],
            "status": self._get_usage_status(row[7])
        }
    
    def _get_usage_status(self, usage_percentage: float) -> str:
        """Determina el status según el porcentaje de uso"""
        if usage_percentage >= 100:
            return "limit_reached"
        elif usage_percentage >= 95:
            return "critical"
        elif usage_percentage >= 80:
            return "high"
        elif usage_percentage >= 50:
            return "moderate"
        else:
            return "normal"
    
    def get_usage_history(
        self,
        tenant_id: str,
        months: int = 6
    ) -> List[Dict]:
        """Obtiene histórico de uso de los últimos N meses"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM usage_summary
            WHERE tenant_id = ?
            ORDER BY year_month DESC
            LIMIT ?
        """, (tenant_id, months))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "year_month": row[1],
                "total_requests": row[2],
                "total_tokens": row[3],
                "avg_response_time_ms": row[4],
                "success_rate": row[5],
                "usage_percentage": row[7]
            })
        
        return history
    
    def get_active_alerts(self, tenant_id: str) -> List[Dict]:
        """Obtiene alertas activas del tenant"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT alert_id, alert_type, threshold_percentage,
                   triggered_at, message
            FROM usage_alerts
            WHERE tenant_id = ?
            AND resolved_at IS NULL
            ORDER BY triggered_at DESC
        """, (tenant_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            alerts.append({
                "alert_id": row[0],
                "type": row[1],
                "threshold": row[2],
                "triggered_at": row[3],
                "message": row[4]
            })
        
        return alerts
    
    def cleanup_old_logs(self, days: int = 90):
        """Elimina logs antiguos para mantener la BD limpia"""
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM usage_logs
            WHERE timestamp < ?
        """, (cutoff_date,))
        
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"🗑️ Eliminados {deleted} logs antiguos (>{days} días)")
        
        return deleted


# ============================================================================
# EJEMPLO DE USO - SIMULAR REQUESTS DE CREDICEFI
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("  NADAKKI AI SUITE - USAGE TRACKER SERVICE")
    print("  Simulando uso de Credicefi")
    print("=" * 70)
    
    tracker = UsageTracker()
    
    # Simular 10 requests
    print("\n📊 Simulando 10 requests de Credicefi...")
    
    for i in range(10):
        result = tracker.log_request(
            tenant_id="credicefi_b27fa331",
            endpoint="/api/v1/evaluate",
            method="POST",
            response_status=200,
            response_time_ms=250.0 + (i * 10),
            tokens_used=1500,
            agent_used="credit_evaluator"
        )
        
        if result['alerts']:
            print(f"⚠️ Alerta generada: {result['alerts']}")
    
    print(f"✅ {10} requests registrados")
    
    # Obtener resumen mensual
    print("\n" + "=" * 70)
    print("📈 RESUMEN MENSUAL DE USO")
    print("=" * 70)
    
    usage = tracker.get_monthly_usage("credicefi_b27fa331")
    
    if usage:
        print(f"\nTenant: {usage['tenant_id']}")
        print(f"Periodo: {usage['year_month']}")
        print(f"Requests: {usage['total_requests']:,} / {usage['limit']:,}")
        print(f"Tokens: {usage['total_tokens']:,}")
        print(f"Tiempo promedio: {usage['avg_response_time_ms']:.2f}ms")
        print(f"Tasa de éxito: {usage['success_rate']:.2f}%")
        print(f"Uso: {usage['usage_percentage']:.4f}%")
        print(f"Restantes: {usage['remaining_requests']:,}")
        print(f"Estado: {usage['status']}")
    
    # Alertas activas
    alerts = tracker.get_active_alerts("credicefi_b27fa331")
    
    if alerts:
        print("\n" + "=" * 70)
        print("⚠️ ALERTAS ACTIVAS")
        print("=" * 70)
        for alert in alerts:
            print(f"\n[{alert['type'].upper()}]")
            print(f"  {alert['message']}")
            print(f"  Activada: {alert['triggered_at']}")
    else:
        print("\n✅ No hay alertas activas")
    
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)