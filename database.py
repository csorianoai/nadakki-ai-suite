"""
Database Module - SQLite Persistence for NADAKKI AI Suite
Provides real data persistence across server restarts
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import uuid

# Database file path
DB_PATH = os.environ.get("DATABASE_PATH", "/tmp/nadakki_data.db")

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                description TEXT,
                subject TEXT,
                content TEXT,
                audience_id TEXT,
                audience_size INTEGER DEFAULT 0,
                schedule TEXT,
                settings TEXT,
                version INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT,
                metrics TEXT
            )
        ''')
        
        # Campaign drafts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                content TEXT,
                created_at TEXT,
                tenant_id TEXT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')
        
        # Analytics events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_events (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                event_name TEXT NOT NULL,
                event_data TEXT,
                user_id TEXT,
                session_id TEXT,
                timestamp TEXT
            )
        ''')
        
        # Daily metrics table (aggregated)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                date TEXT NOT NULL,
                users INTEGER DEFAULT 0,
                sessions INTEGER DEFAULT 0,
                new_users INTEGER DEFAULT 0,
                events INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0,
                UNIQUE(tenant_id, date)
            )
        ''')
        
        # Templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT,
                content TEXT,
                metadata TEXT,
                is_ai_generated INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # AI generations log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_generations (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                request_type TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                model_used TEXT,
                tokens_used INTEGER,
                latency_ms INTEGER,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        
        # Seed initial data if empty
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        if cursor.fetchone()[0] == 0:
            seed_initial_data(conn)
        
        # Seed metrics if empty
        cursor.execute("SELECT COUNT(*) FROM daily_metrics")
        if cursor.fetchone()[0] == 0:
            seed_metrics_data(conn)

def seed_initial_data(conn):
    """Seed initial campaign data"""
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    campaigns = [
        {
            "id": f"cmp_{uuid.uuid4().hex[:8]}",
            "tenant_id": "default",
            "name": "Welcome Series - Day 1",
            "type": "email",
            "status": "active",
            "description": "First email in welcome sequence for new users",
            "subject": "Welcome to {{company_name}}! 🎉",
            "content": json.dumps({"body": "Welcome email content", "blocks": []}),
            "audience_size": 12450,
            "metrics": json.dumps({"sent": 12450, "delivered": 12300, "opened": 5535, "clicked": 1230, "converted": 245})
        },
        {
            "id": f"cmp_{uuid.uuid4().hex[:8]}",
            "tenant_id": "default",
            "name": "Cart Abandonment Reminder",
            "type": "multi-channel",
            "status": "active",
            "description": "Multi-channel cart recovery campaign",
            "subject": "You left something behind! 🛒",
            "content": json.dumps({"body": "Cart abandonment content", "blocks": []}),
            "audience_size": 3420,
            "metrics": json.dumps({"sent": 3420, "delivered": 3380, "opened": 1860, "clicked": 680, "converted": 170})
        },
        {
            "id": f"cmp_{uuid.uuid4().hex[:8]}",
            "tenant_id": "default",
            "name": "Monthly Newsletter - January",
            "type": "email",
            "status": "scheduled",
            "description": "January 2026 newsletter with product updates",
            "subject": "Your January Update 📰",
            "content": json.dumps({"body": "Newsletter content", "blocks": []}),
            "audience_size": 45200,
            "metrics": json.dumps({"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0})
        },
        {
            "id": f"cmp_{uuid.uuid4().hex[:8]}",
            "tenant_id": "default",
            "name": "Flash Sale Alert",
            "type": "push",
            "status": "draft",
            "description": "24-hour flash sale notification",
            "subject": "⚡ 50% OFF - 24 Hours Only!",
            "content": json.dumps({"body": "Flash sale content", "blocks": []}),
            "audience_size": 28900,
            "metrics": json.dumps({"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0})
        },
    ]
    
    for c in campaigns:
        cursor.execute('''
            INSERT INTO campaigns (id, tenant_id, name, type, status, description, subject, content, audience_size, metrics, version, created_at, updated_at, created_by, settings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 'system', '{}')
        ''', (c["id"], c["tenant_id"], c["name"], c["type"], c["status"], c["description"], c["subject"], c["content"], c["audience_size"], c["metrics"], now, now))
    
    conn.commit()
    print(f"✅ Seeded {len(campaigns)} campaigns")

def seed_metrics_data(conn):
    """Seed realistic metrics data for last 90 days"""
    cursor = conn.cursor()
    import random
    
    base_users = 8500
    base_sessions = 25000
    
    for i in range(90):
        date = (datetime.now() - timedelta(days=89-i)).strftime("%Y-%m-%d")
        
        # Simulate growth trend with some variance
        growth_factor = 1 + (i * 0.005)  # 0.5% daily growth
        variance = random.uniform(0.85, 1.15)
        
        users = int(base_users * growth_factor * variance)
        sessions = int(base_sessions * growth_factor * variance)
        new_users = int(users * random.uniform(0.05, 0.12))
        events = int(sessions * random.uniform(8, 15))
        revenue = round(users * random.uniform(2.5, 4.5), 2)
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_metrics (tenant_id, date, users, sessions, new_users, events, revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("default", date, users, sessions, new_users, events, revenue))
    
    conn.commit()
    print(f"✅ Seeded 90 days of metrics data")

# Initialize on import
init_database()
