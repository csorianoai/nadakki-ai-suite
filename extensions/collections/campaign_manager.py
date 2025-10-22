# campaign_manager.py - Gestión de Campañas Automatizadas
import sqlite3
import json
from datetime import datetime, timedelta
from enum import Enum

class CampaignStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active" 
    PAUSED = "paused"
    COMPLETED = "completed"

class ContactStrategy(Enum):
    VOICE_ONLY = "voice_only"
    SMS_VOICE = "sms_voice"  
    EMAIL_VOICE = "email_voice"
    MULTI_CHANNEL = "multi_channel"

class CampaignManager:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.db_path = 'nadakki.db'
        self._ensure_tables()
    
    def _ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'draft',
                rules TEXT NOT NULL,
                target_cases INTEGER DEFAULT 0,
                contacted_cases INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER REFERENCES campaigns(id),
                case_id INTEGER REFERENCES collections_cases(id),
                debtor_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                scheduled_at TIMESTAMP NOT NULL,
                executed_at TIMESTAMP,
                outcome TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def create_campaign(self, name, description, rules_dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        rules_json = json.dumps(rules_dict)
        
        cursor.execute('''
            INSERT INTO campaigns (tenant_id, name, description, rules)
            VALUES (?, ?, ?, ?)
        ''', (self.tenant_id, name, description, rules_json))
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'campaign_id': campaign_id,
            'name': name,
            'status': CampaignStatus.DRAFT.value,
            'tenant_id': self.tenant_id,
            'created_at': datetime.now().isoformat()
        }

    def get_campaign_metrics(self, campaign_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_executions,
                COUNT(CASE WHEN executed_at IS NOT NULL THEN 1 END) as completed,
                COUNT(CASE WHEN outcome = 'contacted' THEN 1 END) as contacted,
                COUNT(CASE WHEN outcome = 'promise_to_pay' THEN 1 END) as promises
            FROM campaign_executions 
            WHERE campaign_id = ?
        ''', (campaign_id,))
        
        metrics = cursor.fetchone()
        conn.close()
        
        total, completed, contacted, promises = metrics
        
        return {
            'total_executions': total,
            'completed_executions': completed,
            'contact_rate': (contacted / completed * 100) if completed > 0 else 0,
            'promise_rate': (promises / contacted * 100) if contacted > 0 else 0,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }

print("CampaignManager inicializado correctamente")
