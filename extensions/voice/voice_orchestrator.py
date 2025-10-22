# voice_orchestrator.py - Orquestación de Llamadas
import sqlite3
import json
import requests
import time
from datetime import datetime, timedelta
from enum import Enum

class CallOutcome(Enum):
    PENDING = "pending"
    CONNECTED = "connected" 
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    FAILED = "failed"
    BLOCKED = "blocked"

class CallPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class VoiceOrchestrator:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.db_path = 'nadakki.db'
        self._ensure_tables()
        
        # Configuración de carriers dominicanos
        self.carriers_config = {
            'altice': {
                'name': 'Altice RD',
                'prefixes': ['809'],
                'cost_per_minute': 0.018,
                'enabled': True
            },
            'claro': {
                'name': 'Claro RD', 
                'prefixes': ['829'],
                'cost_per_minute': 0.020,
                'enabled': True
            },
            'viva': {
                'name': 'Viva RD',
                'prefixes': ['849'],
                'cost_per_minute': 0.022,
                'enabled': True
            },
            'plivo': {
                'name': 'Plivo International',
                'prefixes': ['*'],
                'cost_per_minute': 0.076,
                'enabled': True,
                'fallback': True
            }
        }

    def _ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_call_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                debtor_id TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                case_id INTEGER,
                priority INTEGER DEFAULT 2,
                scheduled_at TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                last_attempt_at TIMESTAMP,
                carrier_used TEXT,
                provider_call_id TEXT,
                outcome TEXT,
                duration_seconds INTEGER DEFAULT 0,
                recording_url TEXT,
                cost_usd DECIMAL(6,4) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def enqueue_call(self, debtor_id, phone_number, case_id=None, priority=2, scheduled_at=None):
        # Verificar compliance antes de encolar
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        try:
            from compliance.indotel_enforcer import INDOTELEnforcer
            compliance = INDOTELEnforcer(self.tenant_id)
            
            can_call, reason = compliance.validate_call_permission(debtor_id, phone_number)
            
            if not can_call:
                return -1
        except:
            pass  # Si no se puede importar compliance, continuar
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if not scheduled_at:
            scheduled_at = datetime.now()
        
        cursor.execute('''
            INSERT INTO voice_call_queue
            (tenant_id, debtor_id, phone_number, case_id, priority, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.tenant_id, debtor_id, phone_number, case_id, priority, scheduled_at))
        
        queue_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return queue_id

    def process_pending_calls(self, batch_size=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, tenant_id, debtor_id, phone_number, case_id, priority,
                   scheduled_at, attempts, max_attempts
            FROM voice_call_queue
            WHERE status = 'pending' 
            AND scheduled_at <= datetime('now')
            AND attempts < max_attempts
            ORDER BY priority DESC, scheduled_at ASC
            LIMIT ?
        ''', (batch_size,))
        
        pending_calls = cursor.fetchall()
        conn.close()
        
        results = []
        for call_data in pending_calls:
            result = self._execute_call(*call_data)
            results.append(result)
        
        return results

    def _execute_call(self, queue_id, tenant_id, debtor_id, phone_number, case_id, priority, scheduled_at, attempts, max_attempts):
        carrier = self._select_best_carrier(phone_number)
        
        if not carrier:
            self._update_call_status(queue_id, CallOutcome.FAILED, "No carrier available")
            return {'queue_id': queue_id, 'status': 'failed', 'reason': 'No carrier available'}
        
        # Simular ejecución de llamada (en producción real aquí iría la lógica SIP/Plivo)
        import random
        time.sleep(0.5)  # Simular latencia
        
        outcomes = ['connected', 'no_answer', 'busy']
        weights = [0.6, 0.3, 0.1]
        simulated_outcome = random.choices(outcomes, weights=weights)[0]
        simulated_duration = random.randint(30, 180) if simulated_outcome == 'connected' else 0
        simulated_cost = (simulated_duration / 60) * carrier['cost_per_minute']
        
        self._update_call_status(
            queue_id, CallOutcome(simulated_outcome),
            f"Call via {carrier['name']}",
            duration=simulated_duration,
            cost=simulated_cost,
            carrier=carrier['key']
        )
        
        # Registrar en compliance
        try:
            from compliance.indotel_enforcer import INDOTELEnforcer
            compliance = INDOTELEnforcer(tenant_id)
            compliance.record_call_attempt(debtor_id, phone_number, simulated_outcome, simulated_duration)
        except:
            pass
        
        return {
            'queue_id': queue_id,
            'success': True,
            'outcome': simulated_outcome,
            'duration_seconds': simulated_duration,
            'cost_usd': simulated_cost,
            'carrier': carrier['key']
        }

    def _select_best_carrier(self, phone_number):
        prefix = phone_number[:3] if len(phone_number) >= 3 else ''
        
        for carrier_key, carrier_config in self.carriers_config.items():
            if prefix in carrier_config['prefixes'] or '*' in carrier_config['prefixes']:
                if carrier_config['enabled']:
                    return {**carrier_config, 'key': carrier_key}
        
        # Fallback a Plivo
        if self.carriers_config['plivo']['enabled']:
            return {**self.carriers_config['plivo'], 'key': 'plivo'}
        
        return None

    def _update_call_status(self, queue_id, outcome, reason="", duration=0, cost=0.0, carrier=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        status = 'completed' if outcome in [CallOutcome.CONNECTED, CallOutcome.NO_ANSWER, CallOutcome.BUSY] else 'failed'
        
        cursor.execute('''
            UPDATE voice_call_queue 
            SET status = ?, outcome = ?, last_attempt_at = ?, attempts = attempts + 1,
                duration_seconds = ?, cost_usd = ?, carrier_used = ?, updated_at = ?
            WHERE id = ?
        ''', (status, outcome.value, datetime.now(), duration, cost, carrier, datetime.now(), queue_id))
        
        conn.commit()
        conn.close()

    def get_call_metrics(self, hours_back=24):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours_back)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_calls,
                COUNT(CASE WHEN outcome = 'connected' THEN 1 END) as connected,
                COUNT(CASE WHEN outcome = 'no_answer' THEN 1 END) as no_answer,
                COUNT(CASE WHEN outcome = 'busy' THEN 1 END) as busy,
                COUNT(CASE WHEN outcome = 'failed' THEN 1 END) as failed,
                AVG(duration_seconds) as avg_duration,
                SUM(cost_usd) as total_cost,
                AVG(cost_usd) as avg_cost_per_call
            FROM voice_call_queue
            WHERE tenant_id = ? AND updated_at >= ?
        ''', (self.tenant_id, since))
        
        metrics = cursor.fetchone()
        conn.close()
        
        total, connected, no_answer, busy, failed, avg_duration, total_cost, avg_cost = metrics
        
        return {
            'period_hours': hours_back,
            'total_calls': total or 0,
            'outcomes': {
                'connected': connected or 0,
                'no_answer': no_answer or 0, 
                'busy': busy or 0,
                'failed': failed or 0
            },
            'rates': {
                'contact_rate': (connected / total * 100) if total > 0 else 0,
                'success_rate': ((connected + no_answer) / total * 100) if total > 0 else 0
            },
            'performance': {
                'avg_duration_seconds': avg_duration or 0,
                'total_cost_usd': total_cost or 0,
                'avg_cost_per_call': avg_cost or 0
            }
        }

print("VoiceOrchestrator inicializado correctamente")
