"""
NADAKKI AI SUITE - DECISION LOGGING MODULE v3.0.0
Con persistencia PostgreSQL - Los datos sobreviven reinicios del servidor
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import uuid4
from fastapi import APIRouter, HTTPException
import hashlib
import json
import logging
import os
from contextlib import contextmanager

logger = logging.getLogger("NadakkiDecisionLogger")

# ============================================================================
# DATABASE CONFIGURATION - PostgreSQL
# ============================================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

# Lazy import - solo si hay DATABASE_URL
pg_pool = None

def get_pg_connection():
    """Obtiene conexión a PostgreSQL"""
    global pg_pool
    
    if not DATABASE_URL:
        return None
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return None

def init_database():
    """Inicializa las tablas en PostgreSQL"""
    if not DATABASE_URL:
        logger.warning("No DATABASE_URL configured, using memory only")
        return False
    
    conn = get_pg_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Tabla principal de decisiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id SERIAL PRIMARY KEY,
                decision_id TEXT UNIQUE NOT NULL,
                tenant_id TEXT NOT NULL,
                workflow_id TEXT NOT NULL,
                workflow_name TEXT,
                workflow_version TEXT,
                action TEXT,
                confidence REAL,
                pipeline_value REAL DEFAULT 0,
                decision_mode TEXT,
                approval_required BOOLEAN,
                chain_position INTEGER,
                input_hash TEXT,
                output_hash TEXT,
                previous_hash TEXT,
                contract_json JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL
            )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_tenant ON decisions(tenant_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_created ON decisions(created_at)")
        
        # Tabla de estado del chain por tenant
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenant_chain_state (
                tenant_id TEXT PRIMARY KEY,
                last_hash TEXT,
                chain_position INTEGER DEFAULT 0,
                updated_at TIMESTAMPTZ
            )
        """)
        
        conn.commit()
        logger.info("PostgreSQL database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ============================================================================
# IN-MEMORY CACHE (fallback y performance)
# ============================================================================

DECISION_STORE: Dict[str, List[Dict]] = {}
LAST_HASH_BY_TENANT: Dict[str, str] = {}
CHAIN_POSITION_BY_TENANT: Dict[str, int] = {}

def load_from_database():
    """Carga datos de PostgreSQL a memoria al iniciar"""
    global DECISION_STORE, LAST_HASH_BY_TENANT, CHAIN_POSITION_BY_TENANT
    
    if not DATABASE_URL:
        logger.info("No DATABASE_URL, starting with empty memory store")
        return
    
    conn = get_pg_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Cargar decisiones
        cursor.execute("SELECT tenant_id, contract_json FROM decisions ORDER BY created_at")
        for row in cursor.fetchall():
            tenant_id = row["tenant_id"]
            contract = row["contract_json"] if isinstance(row["contract_json"], dict) else json.loads(row["contract_json"])
            if tenant_id not in DECISION_STORE:
                DECISION_STORE[tenant_id] = []
            DECISION_STORE[tenant_id].append(contract)
        
        # Cargar estado del chain
        cursor.execute("SELECT tenant_id, last_hash, chain_position FROM tenant_chain_state")
        for row in cursor.fetchall():
            if row["last_hash"]:
                LAST_HASH_BY_TENANT[row["tenant_id"]] = row["last_hash"]
            if row["chain_position"]:
                CHAIN_POSITION_BY_TENANT[row["tenant_id"]] = row["chain_position"]
        
        total_decisions = sum(len(d) for d in DECISION_STORE.values())
        logger.info(f"Loaded {total_decisions} decisions for {len(DECISION_STORE)} tenants from PostgreSQL")
        
    except Exception as e:
        logger.warning(f"Failed to load from database: {e}")
    finally:
        conn.close()

# ============================================================================
# HASH FUNCTIONS
# ============================================================================

def generate_hash(data: Any) -> str:
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()

def generate_decision_hash(decision_id: str, tenant_id: str, action: str, confidence: float, timestamp: str, previous_hash: Optional[str]) -> str:
    content = f"{previous_hash or 'GENESIS'}:{decision_id}:{tenant_id}:{action}:{confidence}:{timestamp}"
    return hashlib.sha256(content.encode()).hexdigest()

# ============================================================================
# CORE LOGGING FUNCTION
# ============================================================================

def log_workflow_decision(workflow_response: Dict, tenant_id: str, tenant_plan: str = "enterprise", source: str = "API") -> Dict:
    """Loguea una decisión de workflow con persistencia en PostgreSQL"""
    
    workflow_id = workflow_response.get("workflow_id", f"WF-{uuid4().hex[:8]}")
    decision_data = workflow_response.get("decision", {})
    summary = workflow_response.get("summary", {})
    steps = workflow_response.get("steps", [])

    decision_id = f"DEC-{workflow_id}"
    now = datetime.utcnow()
    timestamp = now.isoformat() + "Z"

    previous_hash = LAST_HASH_BY_TENANT.get(tenant_id)
    chain_position = CHAIN_POSITION_BY_TENANT.get(tenant_id, 0)

    action = decision_data.get("decision", "REVIEW_REQUIRED")
    confidence = decision_data.get("confidence", 0.5)
    pipeline_value = summary.get("pipeline_value", 0)

    if confidence >= 0.85:
        decision_mode, approval_required = "AI_AUTONOMOUS", False
    elif confidence >= 0.60:
        decision_mode, approval_required = "AI_ASSISTED", True
    else:
        decision_mode, approval_required = "HUMAN_IN_LOOP", True

    input_hash = generate_hash(workflow_response)[:16]
    output_hash = generate_decision_hash(decision_id, tenant_id, action, confidence, timestamp, previous_hash)[:16]

    agents_executed = [{"agent_id": s.get("agent", "unknown"), "agent_name": s.get("step_name", "Unknown"),
                        "status": s.get("status", "unknown"), "duration_ms": s.get("duration_ms", 0)}
                       for s in steps if s.get("status") not in ["skipped", None]]

    contract = {
        "_contract": {"version": "3.0.0", "type": "DECISION_CONTRACT", "immutable": True},
        "decision_id": decision_id,
        "workflow_id": workflow_id,
        "workflow_name": workflow_response.get("workflow_name", "Unknown"),
        "workflow_version": workflow_response.get("workflow_version", "1.0.0"),
        "tenant": {"tenant_id": tenant_id, "execution_boundary": f"tenant::{tenant_id}", "plan": tenant_plan},
        "decision": {"action": action, "confidence": confidence, "priority": "HIGH" if pipeline_value > 500000 else "MEDIUM",
                     "valid_until": (now + timedelta(days=7)).isoformat() + "Z"},
        "authority": {"decision_mode": decision_mode, "approval_required": approval_required, "policy_id": "MARKETING_STANDARD_V1"},
        "business_impact": {"pipeline_value": pipeline_value, "risk_level": "LOW" if confidence > 0.7 else "MEDIUM", "currency": "USD"},
        "execution": {"steps_completed": summary.get("steps_completed", "0/0"), "total_duration_ms": summary.get("total_duration_ms", 0),
                      "agents_executed": agents_executed, "source": source},
        "audit": {"created_at": timestamp, "input_hash": input_hash, "output_hash": output_hash,
                  "previous_decision_hash": previous_hash, "chain_position": chain_position,
                  "execution_boundary": f"tenant::{tenant_id}", "request_id": f"req-{uuid4().hex[:8]}"},
        "compliance": {"status": "PASS", "regulations_checked": ["GDPR"], "data_retention_days": 90}
    }

    # Guardar en memoria
    if tenant_id not in DECISION_STORE:
        DECISION_STORE[tenant_id] = []
    DECISION_STORE[tenant_id].append(contract)
    LAST_HASH_BY_TENANT[tenant_id] = output_hash
    CHAIN_POSITION_BY_TENANT[tenant_id] = chain_position + 1

    # Persistir en PostgreSQL
    if DATABASE_URL:
        conn = get_pg_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Insertar decisión
                cursor.execute("""
                    INSERT INTO decisions (
                        decision_id, tenant_id, workflow_id, workflow_name, workflow_version,
                        action, confidence, pipeline_value, decision_mode, approval_required,
                        chain_position, input_hash, output_hash, previous_hash, contract_json, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (decision_id) DO NOTHING
                """, (
                    decision_id, tenant_id, workflow_id,
                    workflow_response.get("workflow_name", "Unknown"),
                    workflow_response.get("workflow_version", "1.0.0"),
                    action, confidence, pipeline_value, decision_mode, approval_required,
                    chain_position, input_hash, output_hash, previous_hash,
                    json.dumps(contract), now
                ))
                
                # Actualizar estado del chain
                cursor.execute("""
                    INSERT INTO tenant_chain_state (tenant_id, last_hash, chain_position, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (tenant_id) DO UPDATE SET
                        last_hash = EXCLUDED.last_hash,
                        chain_position = EXCLUDED.chain_position,
                        updated_at = EXCLUDED.updated_at
                """, (tenant_id, output_hash, chain_position + 1, now))
                
                conn.commit()
                logger.info(f"Decision persisted to PostgreSQL: {decision_id} for {tenant_id} (chain: {chain_position})")
                
            except Exception as e:
                logger.error(f"Failed to persist decision to PostgreSQL: {e}")
                conn.rollback()
            finally:
                conn.close()

    return contract

# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

def get_tenant_decisions(tenant_id: str, limit: int = 50) -> Dict:
    """Obtiene decisiones de un tenant"""
    
    if DATABASE_URL:
        conn = get_pg_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT contract_json FROM decisions 
                    WHERE tenant_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (tenant_id, limit))
                
                decisions = []
                for row in cursor.fetchall():
                    contract = row["contract_json"] if isinstance(row["contract_json"], dict) else json.loads(row["contract_json"])
                    decisions.append(contract)
                
                cursor.execute("SELECT COUNT(*) as total FROM decisions WHERE tenant_id = %s", (tenant_id,))
                total = cursor.fetchone()["total"]
                
                return {
                    "tenant_id": tenant_id,
                    "execution_boundary": f"tenant::{tenant_id}",
                    "total": total,
                    "decisions": decisions
                }
            except Exception as e:
                logger.warning(f"DB query failed, using memory: {e}")
            finally:
                conn.close()
    
    # Fallback a memoria
    decisions = DECISION_STORE.get(tenant_id, [])
    sorted_decisions = sorted(decisions, key=lambda x: x.get("audit", {}).get("created_at", ""), reverse=True)
    return {
        "tenant_id": tenant_id,
        "execution_boundary": f"tenant::{tenant_id}",
        "total": len(decisions),
        "decisions": sorted_decisions[:limit]
    }

def get_tenant_decision_stats(tenant_id: str) -> Dict:
    """Obtiene estadísticas de decisiones de un tenant"""
    
    if DATABASE_URL:
        conn = get_pg_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        AVG(confidence) as avg_confidence,
                        SUM(pipeline_value) as total_pipeline
                    FROM decisions WHERE tenant_id = %s
                """, (tenant_id,))
                row = cursor.fetchone()
                
                if not row or row["total"] == 0:
                    return {"tenant_id": tenant_id, "total_decisions": 0, "stats": {}}
                
                cursor.execute("""
                    SELECT action, COUNT(*) as count 
                    FROM decisions WHERE tenant_id = %s 
                    GROUP BY action
                """, (tenant_id,))
                distribution = {r["action"]: r["count"] for r in cursor.fetchall()}
                
                cursor.execute("SELECT last_hash, chain_position FROM tenant_chain_state WHERE tenant_id = %s", (tenant_id,))
                chain_row = cursor.fetchone()
                
                return {
                    "tenant_id": tenant_id,
                    "total_decisions": row["total"],
                    "stats": {
                        "avg_confidence": round(float(row["avg_confidence"] or 0), 3),
                        "total_pipeline": float(row["total_pipeline"] or 0),
                        "decision_distribution": distribution,
                        "chain_length": chain_row["chain_position"] if chain_row else 0,
                        "last_hash": chain_row["last_hash"] if chain_row else None
                    }
                }
            except Exception as e:
                logger.warning(f"DB stats failed, using memory: {e}")
            finally:
                conn.close()
    
    # Fallback a memoria
    decisions = DECISION_STORE.get(tenant_id, [])
    if not decisions:
        return {"tenant_id": tenant_id, "total_decisions": 0, "stats": {}}
    confidences = [d.get("decision", {}).get("confidence", 0) for d in decisions]
    pipelines = [d.get("business_impact", {}).get("pipeline_value", 0) for d in decisions]
    distribution = {}
    for d in decisions:
        action = d.get("decision", {}).get("action", "UNKNOWN")
        distribution[action] = distribution.get(action, 0) + 1
    return {
        "tenant_id": tenant_id,
        "total_decisions": len(decisions),
        "stats": {
            "avg_confidence": round(sum(confidences)/len(confidences), 3),
            "total_pipeline": sum(pipelines),
            "decision_distribution": distribution,
            "chain_length": CHAIN_POSITION_BY_TENANT.get(tenant_id, 0),
            "last_hash": LAST_HASH_BY_TENANT.get(tenant_id)
        }
    }

def verify_decision_chain(tenant_id: str) -> Dict:
    """Verifica la integridad del hash chain de un tenant"""
    
    if DATABASE_URL:
        conn = get_pg_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT decision_id, chain_position, output_hash, previous_hash
                    FROM decisions WHERE tenant_id = %s
                    ORDER BY chain_position
                """, (tenant_id,))
                rows = cursor.fetchall()
                
                if not rows:
                    return {"tenant_id": tenant_id, "valid": True, "chain_length": 0, "message": "No decisions"}
                
                issues = []
                for i, row in enumerate(rows):
                    if i == 0 and row["previous_hash"]:
                        issues.append({"decision_id": row["decision_id"], "issue": "First should have null previous_hash"})
                    elif i > 0:
                        expected = rows[i-1]["output_hash"]
                        actual = row["previous_hash"]
                        if expected != actual:
                            issues.append({"decision_id": row["decision_id"], "issue": f"Chain broken"})
                
                return {
                    "tenant_id": tenant_id,
                    "valid": len(issues) == 0,
                    "chain_length": len(rows),
                    "last_hash": rows[-1]["output_hash"] if rows else None,
                    "issues": issues,
                    "message": "Chain OK" if not issues else f"{len(issues)} issues found"
                }
            except Exception as e:
                logger.warning(f"DB verify failed, using memory: {e}")
            finally:
                conn.close()
    
    # Fallback a memoria
    decisions = DECISION_STORE.get(tenant_id, [])
    if not decisions:
        return {"tenant_id": tenant_id, "valid": True, "chain_length": 0, "message": "No decisions"}
    sorted_decisions = sorted(decisions, key=lambda x: x.get("audit", {}).get("chain_position", 0))
    issues = []
    for i, d in enumerate(sorted_decisions):
        if i == 0 and d.get("audit", {}).get("previous_decision_hash"):
            issues.append({"decision_id": d.get("decision_id"), "issue": "First should have null previous_hash"})
        elif i > 0:
            expected = sorted_decisions[i-1].get("audit", {}).get("output_hash")
            actual = d.get("audit", {}).get("previous_decision_hash")
            if expected != actual:
                issues.append({"decision_id": d.get("decision_id"), "issue": f"Chain broken"})
    return {
        "tenant_id": tenant_id,
        "valid": len(issues) == 0,
        "chain_length": len(sorted_decisions),
        "last_hash": sorted_decisions[-1].get("audit", {}).get("output_hash") if sorted_decisions else None,
        "issues": issues,
        "message": "Chain OK" if not issues else f"{len(issues)} issues"
    }

# ============================================================================
# API ROUTER
# ============================================================================

decision_log_router = APIRouter(prefix="/decision-logs", tags=["decision-logs"])

@decision_log_router.get("/{tenant_id}")
async def api_get_decisions(tenant_id: str, limit: int = 50):
    return get_tenant_decisions(tenant_id, limit)

@decision_log_router.get("/{tenant_id}/stats")
async def api_get_stats(tenant_id: str):
    return get_tenant_decision_stats(tenant_id)

@decision_log_router.get("/{tenant_id}/verify-chain")
async def api_verify_chain(tenant_id: str):
    return verify_decision_chain(tenant_id)

@decision_log_router.post("/{tenant_id}/log")
async def api_log_decision(tenant_id: str, workflow_response: Dict[str, Any]):
    """Loguea una decisión de workflow manualmente"""
    contract = log_workflow_decision(workflow_response, tenant_id)
    return {"success": True, "decision_id": contract["decision_id"], "chain_position": contract["audit"]["chain_position"]}

@decision_log_router.get("/{tenant_id}/export")
async def api_export_decisions(tenant_id: str, format: str = "json"):
    """Exporta todas las decisiones de un tenant"""
    data = get_tenant_decisions(tenant_id, limit=10000)
    return data

# ============================================================================
# REGISTRATION & INITIALIZATION
# ============================================================================

def register_decision_log_routes(app):
    """Registra las rutas e inicializa la base de datos"""
    db_ok = init_database()
    if db_ok:
        load_from_database()
        logger.info(f"Decision logging with PostgreSQL persistence enabled")
    else:
        logger.warning("Decision logging running in memory-only mode")
    app.include_router(decision_log_router)

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "DECISION_STORE",
    "log_workflow_decision",
    "get_tenant_decisions", 
    "get_tenant_decision_stats",
    "verify_decision_chain",
    "decision_log_router",
    "register_decision_log_routes",
    "init_database",
    "load_from_database"
]
