# cost_governor.py - Control de Costos en Tiempo Real
import sqlite3
import json
from datetime import datetime, timedelta

class CostGovernor:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.db_path = 'nadakki.db'
        self._ensure_tables()
        
        # Configuración de costos target
        self.cost_targets = {
            'call_max_usd': 0.043,
            'daily_budget_usd': 500.0,
            'monthly_budget_usd': 12000.0,
            'sip_local_rate': 0.025,
            'plivo_fallback_rate': 0.076,
            'target_sip_percentage': 85
        }

    def _ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                date DATE NOT NULL,
                total_calls INTEGER DEFAULT 0,
                total_cost_usd DECIMAL(10,4) DEFAULT 0,
                avg_cost_per_call DECIMAL(6,4) DEFAULT 0,
                sip_calls INTEGER DEFAULT 0,
                sip_cost_usd DECIMAL(10,4) DEFAULT 0,
                plivo_calls INTEGER DEFAULT 0,
                plivo_cost_usd DECIMAL(10,4) DEFAULT 0,
                budget_remaining_usd DECIMAL(10,2) DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tenant_id, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                threshold_percentage REAL NOT NULL,
                current_usage_usd DECIMAL(10,4) NOT NULL,
                limit_usd DECIMAL(10,2) NOT NULL,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()

    def validate_call_cost(self, estimated_duration_seconds, carrier):
        carrier_rates = {
            'altice': 0.018,
            'claro': 0.020,
            'viva': 0.022,
            'plivo': 0.076
        }
        
        rate_per_minute = carrier_rates.get(carrier, 0.076)
        estimated_cost = (estimated_duration_seconds / 60) * rate_per_minute
        
        # Verificar límite por llamada
        if estimated_cost > self.cost_targets['call_max_usd']:
            return False, f"Costo estimado ${estimated_cost:.4f} excede límite por llamada", estimated_cost
        
        # Verificar presupuesto diario
        daily_spent = self._get_daily_spending()
        if daily_spent + estimated_cost > self.cost_targets['daily_budget_usd']:
            return False, f"Excedería presupuesto diario (${daily_spent:.2f} + ${estimated_cost:.4f})", estimated_cost
        
        return True, "Llamada aprobada", estimated_cost

    def record_call_cost(self, carrier, duration_seconds, actual_cost):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        is_sip = carrier in ['altice', 'claro', 'viva']
        
        cursor.execute('''
            INSERT OR REPLACE INTO cost_tracking
            (tenant_id, date, total_calls, total_cost_usd, 
             sip_calls, sip_cost_usd, plivo_calls, plivo_cost_usd)
            VALUES (?, ?, 
                COALESCE((SELECT total_calls FROM cost_tracking WHERE tenant_id = ? AND date = ?), 0) + 1,
                COALESCE((SELECT total_cost_usd FROM cost_tracking WHERE tenant_id = ? AND date = ?), 0) + ?,
                COALESCE((SELECT sip_calls FROM cost_tracking WHERE tenant_id = ? AND date = ?), 0) + ?,
                COALESCE((SELECT sip_cost_usd FROM cost_tracking WHERE tenant_id = ? AND date = ?), 0) + ?,
                COALESCE((SELECT plivo_calls FROM cost_tracking WHERE tenant_id = ? AND date = ?), 0) + ?,
                COALESCE((SELECT plivo_cost_usd FROM cost_tracking WHERE tenant_id = ? AND date = ?), 0) + ?
            )
        ''', (
            self.tenant_id, today,
            self.tenant_id, today,
            self.tenant_id, today, actual_cost,
            self.tenant_id, today, 1 if is_sip else 0,
            self.tenant_id, today, actual_cost if is_sip else 0,
            self.tenant_id, today, 0 if is_sip else 1,
            self.tenant_id, today, 0 if is_sip else actual_cost
        ))
        
        # Actualizar promedio
        cursor.execute('''
            UPDATE cost_tracking 
            SET avg_cost_per_call = total_cost_usd / total_calls,
                budget_remaining_usd = ? - total_cost_usd,
                updated_at = ?
            WHERE tenant_id = ? AND date = ?
        ''', (self.cost_targets['daily_budget_usd'], datetime.now(), self.tenant_id, today))
        
        conn.commit()
        conn.close()

    def get_current_spending_status(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        # Gastos del día
        cursor.execute('''
            SELECT total_calls, total_cost_usd, avg_cost_per_call,
                   sip_calls, sip_cost_usd, plivo_calls, plivo_cost_usd,
                   budget_remaining_usd
            FROM cost_tracking
            WHERE tenant_id = ? AND date = ?
        ''', (self.tenant_id, today))
        
        daily_data = cursor.fetchone()
        
        # Gastos del mes
        cursor.execute('''
            SELECT 
                SUM(total_calls) as monthly_calls,
                SUM(total_cost_usd) as monthly_cost,
                AVG(avg_cost_per_call) as monthly_avg_cost,
                SUM(sip_calls) as monthly_sip_calls,
                SUM(plivo_calls) as monthly_plivo_calls
            FROM cost_tracking
            WHERE tenant_id = ? AND date >= ?
        ''', (self.tenant_id, month_start))
        
        monthly_data = cursor.fetchone()
        conn.close()
        
        # Procesar datos
        if daily_data:
            daily_calls, daily_cost, daily_avg, sip_calls, sip_cost, plivo_calls, plivo_cost, remaining = daily_data
        else:
            daily_calls = daily_cost = daily_avg = sip_calls = sip_cost = plivo_calls = plivo_cost = remaining = 0
        
        if monthly_data and monthly_data[0]:
            monthly_calls, monthly_cost, monthly_avg, monthly_sip, monthly_plivo = monthly_data
        else:
            monthly_calls = monthly_cost = monthly_avg = monthly_sip = monthly_plivo = 0
        
        sip_percentage = (sip_calls / daily_calls * 100) if daily_calls > 0 else 0
        plivo_percentage = (plivo_calls / daily_calls * 100) if daily_calls > 0 else 0
        
        return {
            'daily': {
                'calls': daily_calls or 0,
                'cost_usd': float(daily_cost or 0),
                'avg_cost_per_call': float(daily_avg or 0),
                'budget_remaining_usd': float(remaining or self.cost_targets['daily_budget_usd']),
                'budget_used_percentage': ((daily_cost or 0) / self.cost_targets['daily_budget_usd'] * 100)
            },
            'monthly': {
                'calls': monthly_calls or 0,
                'cost_usd': float(monthly_cost or 0),
                'avg_cost_per_call': float(monthly_avg or 0),
                'budget_remaining_usd': float(self.cost_targets['monthly_budget_usd'] - (monthly_cost or 0)),
                'budget_used_percentage': ((monthly_cost or 0) / self.cost_targets['monthly_budget_usd'] * 100)
            },
            'carrier_distribution': {
                'sip_local_percentage': sip_percentage,
                'plivo_fallback_percentage': plivo_percentage,
                'target_sip_percentage': self.cost_targets['target_sip_percentage'],
                'distribution_healthy': sip_percentage >= self.cost_targets['target_sip_percentage']
            },
            'cost_efficiency': {
                'target_cost_per_call': self.cost_targets['call_max_usd'],
                'actual_avg_cost_per_call': float(daily_avg or 0),
                'efficiency_score': min(100, (self.cost_targets['call_max_usd'] / (daily_avg or self.cost_targets['call_max_usd'])) * 100)
            }
        }

    def get_cost_optimization_recommendations(self):
        status = self.get_current_spending_status()
        recommendations = []
        
        if status['carrier_distribution']['sip_local_percentage'] < 80:
            recommendations.append({
                'type': 'carrier_optimization',
                'priority': 'high',
                'message': f"Solo {status['carrier_distribution']['sip_local_percentage']:.1f}% de llamadas usan SIP local. Target: 85%+",
                'action': 'Revisar configuración de routing de carriers'
            })
        
        if status['cost_efficiency']['actual_avg_cost_per_call'] > self.cost_targets['call_max_usd']:
            recommendations.append({
                'type': 'call_duration_optimization', 
                'priority': 'medium',
                'message': f"Costo promedio ${status['cost_efficiency']['actual_avg_cost_per_call']:.4f} excede target ${self.cost_targets['call_max_usd']:.4f}",
                'action': 'Optimizar duración de llamadas y scripts'
            })
        
        if status['daily']['budget_used_percentage'] > 80:
            recommendations.append({
                'type': 'budget_management',
                'priority': 'high', 
                'message': f"Uso diario de presupuesto: {status['daily']['budget_used_percentage']:.1f}%",
                'action': 'Considerar ajustar presupuesto diario o reducir volumen de llamadas'
            })
        
        return recommendations

    def _get_daily_spending(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('''
            SELECT COALESCE(total_cost_usd, 0) FROM cost_tracking
            WHERE tenant_id = ? AND date = ?
        ''', (self.tenant_id, today))
        
        result = cursor.fetchone()
        conn.close()
        
        return float(result[0] if result else 0)

print("CostGovernor inicializado correctamente")
