# indotel_enforcer.py - Cumplimiento INDOTEL República Dominicana
import sqlite3
import json
from datetime import datetime, time, timedelta
import pytz

class INDOTELEnforcer:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.db_path = 'nadakki.db'
        self._ensure_tables()
        
        # Configuración INDOTEL
        self.CALL_WINDOW_START = time(7, 0)   # 07:00 AM
        self.CALL_WINDOW_END = time(19, 0)    # 07:00 PM
        self.TIMEZONE = "America/Santo_Domingo"
        self.MAX_DAILY_ATTEMPTS = 3
        self.DR_PREFIXES = ['809', '829', '849']
    
    def _ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indotel_compliance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                debtor_id TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                action TEXT NOT NULL,
                rule_applied TEXT NOT NULL,
                violation_type TEXT,
                details TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opt_out_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                debtor_id TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                opt_out_method TEXT NOT NULL,
                opt_out_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                permanent BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()

    def is_within_call_window(self):
        try:
            import pytz
            tz = pytz.timezone(self.TIMEZONE)
            now = datetime.now(tz).time()
            return self.CALL_WINDOW_START <= now <= self.CALL_WINDOW_END
        except:
            # Fallback sin pytz
            now = datetime.now().time()
            return self.CALL_WINDOW_START <= now <= self.CALL_WINDOW_END

    def validate_call_permission(self, debtor_id, phone_number):
        # Verificar ventana de llamadas
        if not self.is_within_call_window():
            self._log_compliance_action(
                debtor_id, phone_number, "call_blocked", 
                "outside_calling_window", {"current_time": datetime.now().isoformat()}
            )
            return False, "Fuera de ventana permitida INDOTEL (07:00-19:00)"
        
        # Verificar opt-out
        if self._is_opted_out(debtor_id, phone_number):
            return False, "Deudor en lista de opt-out"
        
        # Verificar límite diario de intentos
        daily_attempts = self._get_daily_attempts(debtor_id, phone_number)
        if daily_attempts >= self.MAX_DAILY_ATTEMPTS:
            self._log_compliance_action(
                debtor_id, phone_number, "call_blocked",
                "max_daily_attempts_exceeded", 
                {"attempts_today": daily_attempts}
            )
            return False, f"Límite diario excedido ({daily_attempts}/3)"
        
        # Llamada permitida
        self._log_compliance_action(
            debtor_id, phone_number, "call_approved", 
            "all_validations_passed",
            {"daily_attempts": daily_attempts}
        )
        
        return True, "Llamada aprobada"

    def record_call_attempt(self, debtor_id, phone_number, outcome, duration_seconds=0, recording_url=None):
        # Registrar en tabla principal de intentos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO contact_attempts 
            (tenant_id, debtor_id, phone_number, attempt_date, outcome, created_at)
            VALUES (?, ?, ?, DATE('now'), ?, ?)
        ''', (self.tenant_id, debtor_id, phone_number, outcome, datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Log de compliance
        self._log_compliance_action(
            debtor_id, phone_number, "call_completed", "call_attempt_recorded",
            {
                "outcome": outcome,
                "duration_seconds": duration_seconds,
                "recording_available": recording_url is not None
            }
        )

    def process_opt_out(self, debtor_id, phone_number, method="DTMF"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO opt_out_registry
            (tenant_id, debtor_id, phone_number, opt_out_method)
            VALUES (?, ?, ?, ?)
        ''', (self.tenant_id, debtor_id, phone_number, method))
        
        conn.commit()
        conn.close()
        
        self._log_compliance_action(
            debtor_id, phone_number, "opt_out_processed", "opt_out_registered",
            {"method": method, "permanent": True}
        )
        
        return True

    def get_compliance_report(self, start_date, end_date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Métricas de llamadas
        cursor.execute('''
            SELECT 
                COUNT(*) as total_calls,
                COUNT(CASE WHEN action = 'call_blocked' THEN 1 END) as blocked_calls,
                COUNT(CASE WHEN rule_applied = 'outside_calling_window' THEN 1 END) as window_violations
            FROM indotel_compliance_log
            WHERE tenant_id = ? AND DATE(timestamp) BETWEEN DATE(?) AND DATE(?)
        ''', (self.tenant_id, start_date.date(), end_date.date()))
        
        call_metrics = cursor.fetchone()
        total_calls, blocked_calls, window_violations = call_metrics
        
        conn.close()
        
        return {
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat()
            },
            'call_metrics': {
                'total_attempts': total_calls,
                'blocked_calls': blocked_calls,
                'approval_rate': ((total_calls - blocked_calls) / total_calls * 100) if total_calls > 0 else 0
            },
            'violation_metrics': {
                'window_violations': window_violations,
                'total_violations': window_violations
            },
            'compliance_score': self._calculate_compliance_score(total_calls, blocked_calls, window_violations)
        }

    def _is_opted_out(self, debtor_id, phone_number):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM opt_out_registry
            WHERE tenant_id = ? AND (debtor_id = ? OR phone_number = ?)
            AND permanent = 1
        ''', (self.tenant_id, debtor_id, phone_number))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result > 0

    def _get_daily_attempts(self, debtor_id, phone_number):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM contact_attempts
            WHERE tenant_id = ? AND debtor_id = ? AND phone_number = ?
            AND attempt_date = DATE('now')
        ''', (self.tenant_id, debtor_id, phone_number))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result

    def _log_compliance_action(self, debtor_id, phone_number, action, rule, details):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO indotel_compliance_log
            (tenant_id, debtor_id, phone_number, action, rule_applied, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.tenant_id, debtor_id, phone_number, action, rule, json.dumps(details)))
        
        conn.commit()
        conn.close()

    def _calculate_compliance_score(self, total_calls, blocked_calls, window_violations):
        if total_calls == 0:
            return 100.0
        
        window_penalty = (window_violations / total_calls) * 50
        block_penalty = (blocked_calls / total_calls) * 50
        
        score = 100 - (window_penalty + block_penalty)
        return max(0.0, min(100.0, score))

print("INDOTELEnforcer inicializado correctamente")
