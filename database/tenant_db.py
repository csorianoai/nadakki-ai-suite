"""
Tenant Database Management - Nadakki AI Suite v3.3.2 Enterprise
Enterprise-Grade Multi-Tenant System with Monitoring Tenant (SQLite)
"""

import sqlite3
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# ==========================================================
# CONFIGURACIÓN Y LOGGING
# ==========================================================
logger = logging.getLogger("TenantDB")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# ==========================================================
# CLASE PRINCIPAL: TenantDatabase
# ==========================================================
class TenantDatabase:
    """Manages tenant data in SQLite"""

    def __init__(self, db_path: str = "tenants.db"):
        self.db_path = db_path
        self._init_database()
        self.ensure_monitor_tenant()

    # ==========================================================
    # INIT / SCHEMA CREATION
    # ==========================================================
    def _init_database(self):
        """Initialize database schema (robust version)"""
        # Ruta absoluta segura
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Crear tablas base
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                country TEXT,
                region TEXT,
                plan TEXT DEFAULT 'starter',
                api_key TEXT UNIQUE NOT NULL,
                config TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenant_cores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                core_name TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                config TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
                UNIQUE(tenant_id, core_name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenant_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                execution_time_ms REAL,
                success BOOLEAN,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenant_usage_tenant ON tenant_usage(tenant_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenant_usage_timestamp ON tenant_usage(timestamp)")

        conn.commit()
        conn.close()

        logger.info(f"✓ Database initialized successfully at: {os.path.abspath(self.db_path)}")

    # ==========================================================
    # CRUD: Tenants
    # ==========================================================
    def create_tenant(self, name: str, email: str, country: str = None,
                      region: str = None, plan: str = "starter",
                      config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new tenant"""
        tenant_id = str(uuid.uuid4())
        api_key = f"sk-{uuid.uuid4().hex}"
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO tenants (
                    tenant_id, name, email, country, region,
                    plan, api_key, config, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tenant_id, name, email, country, region,
                plan, api_key, json.dumps(config or {}), now, now
            ))

            conn.commit()
            logger.info(f"✓ Tenant created: {tenant_id} ({name})")

            return {
                "tenant_id": tenant_id,
                "name": name,
                "email": email,
                "country": country,
                "region": region,
                "plan": plan,
                "api_key": api_key,
                "created_at": now
            }

        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating tenant: {e}")
            raise
        finally:
            conn.close()

    def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tenants WHERE tenant_id = ?", (tenant_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_tenant_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get tenant by API key"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tenants WHERE api_key = ?", (api_key,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def list_tenants(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all tenants"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM tenants"
        params = []

        if active_only:
            query += " WHERE active = 1"

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_tenant(self, tenant_id: str, **kwargs) -> bool:
        """Update tenant"""
        allowed_fields = ['name', 'email', 'country', 'region', 'plan', 'config', 'active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        updates['updated_at'] = datetime.now().isoformat()

        if 'config' in updates and isinstance(updates['config'], dict):
            updates['config'] = json.dumps(updates['config'])

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [tenant_id]

            cursor.execute(f"UPDATE tenants SET {set_clause} WHERE tenant_id = ?", values)
            conn.commit()

            logger.info(f"✓ Tenant updated: {tenant_id}")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating tenant: {e}")
            raise
        finally:
            conn.close()

    # ==========================================================
    # MONITOR TENANT AUTO-CREATION
    # ==========================================================
    def ensure_monitor_tenant(self):
        """Creates special monitor tenant if not exists"""
        monitor_email = "monitor@nadakki.ai"
        monitor_api_key = "monitor-key-9999"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tenants WHERE email = ?", (monitor_email,))
        existing = cursor.fetchone()

        if existing:
            logger.info("🔍 Monitor tenant already exists.")
        else:
            now = datetime.now().isoformat()
            monitor_id = "monitor_admin"
            cursor.execute("""
                INSERT INTO tenants (
                    tenant_id, name, email, country, region,
                    plan, api_key, config, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                monitor_id,
                "Nadakki Monitor Admin",
                monitor_email,
                "DO",
                "latam",
                "enterprise",
                monitor_api_key,
                json.dumps({"role": "system", "access": "monitoring"}),
                now, now
            ))
            conn.commit()
            logger.info(f"✅ Monitor tenant created successfully (API Key: {monitor_api_key})")

        conn.close()

    # ==========================================================
    # CORES / USAGE / STATS
    # ==========================================================
    def provision_core(self, tenant_id: str, core_name: str, config: Dict[str, Any] = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO tenant_cores (
                    tenant_id, core_name, enabled, config, created_at
                ) VALUES (?, ?, 1, ?, ?)
            """, (tenant_id, core_name, json.dumps(config or {}), datetime.now().isoformat()))
            conn.commit()
            logger.info(f"✓ Core provisioned: {core_name} for {tenant_id}")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Error provisioning core: {e}")
            raise
        finally:
            conn.close()

    def log_usage(self, tenant_id: str, agent_id: str, execution_time_ms: float, success: bool):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tenant_usage (tenant_id, agent_id, timestamp, execution_time_ms, success)
            VALUES (?, ?, ?, ?, ?)
        """, (tenant_id, agent_id, datetime.now().isoformat(), execution_time_ms, success))
        conn.commit()
        conn.close()

    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as total_requests,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                   AVG(execution_time_ms) as avg_execution_time
            FROM tenant_usage WHERE tenant_id = ?
        """, (tenant_id,))
        stats = cursor.fetchone()

        cursor.execute("""
            SELECT agent_id, COUNT(*) as count
            FROM tenant_usage WHERE tenant_id = ?
            GROUP BY agent_id ORDER BY count DESC LIMIT 10
        """, (tenant_id,))
        top_agents = cursor.fetchall()
        conn.close()

        return {
            "total_requests": stats[0] or 0,
            "successful_requests": stats[1] or 0,
            "avg_execution_time_ms": round(stats[2], 2) if stats[2] else 0,
            "top_agents": [{"agent_id": row[0], "count": row[1]} for row in top_agents]
        }

# ==========================================================
# GLOBAL INSTANCE
# ==========================================================
tenant_db = TenantDatabase()
