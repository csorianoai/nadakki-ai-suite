# ===============================================================================
# NADAKKI AI Suite - IdempotencyStore
# core/reliability/idempotency.py
# Day 1 - Component 4 of 4
# ===============================================================================

"""
Idempotency key storage to prevent duplicate operations.

When an operation is executed, its result is stored with a deterministic key.
If the same operation is requested again within the TTL window, the cached
result is returned instead of re-executing.

Key generation: SHA-256(tenant_id + operation_name + sorted_payload_json)
TTL: 24 hours by default (configurable per operation).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import json
import hashlib
import logging

logger = logging.getLogger("nadakki.reliability.idempotency")


@dataclass
class IdempotencyRecord:
    """Record of a cached operation result."""
    key: str
    tenant_id: str
    operation_name: str
    result: dict
    created_at: datetime
    expires_at: datetime


class IdempotencyStore:
    """
    Deduplication store for Google Ads operations.
    
    Usage:
        store = IdempotencyStore(db)
        
        # Check before executing
        cached = await store.check(key, tenant_id)
        if cached:
            return cached  # Don't re-execute
        
        # After executing
        await store.store(key, tenant_id, operation_name, result)
    """
    
    DEFAULT_TTL_HOURS = 24
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def check(self, key: str, tenant_id: str) -> Optional[dict]:
        """
        Check if an operation result exists for this key.
        
        Returns the cached result dict if found and not expired,
        or None if no cache hit.
        """
        row = await self.db.fetchone("""
            SELECT result, created_at FROM idempotency_keys
            WHERE key = $1 AND tenant_id = $2 AND expires_at > NOW()
        """, key, tenant_id)
        
        if row:
            logger.info(
                f"Idempotency hit: key={key[:12]}... "
                f"tenant={tenant_id} created={row['created_at']}"
            )
            return json.loads(row["result"])
        
        return None
    
    async def store(
        self,
        key: str,
        tenant_id: str,
        operation_name: str,
        result: dict,
        ttl_hours: int = None,
    ):
        """
        Store operation result with TTL.
        Uses upsert to handle concurrent writes.
        """
        ttl = ttl_hours or self.DEFAULT_TTL_HOURS
        expires_at = datetime.utcnow() + timedelta(hours=ttl)
        result_json = json.dumps(result, default=str)
        
        await self.db.execute("""
            INSERT INTO idempotency_keys 
            (key, tenant_id, operation_name, result, created_at, expires_at)
            VALUES ($1, $2, $3, $4, NOW(), $5)
            ON CONFLICT (key) 
            DO UPDATE SET result = $4, expires_at = $5
        """, key, tenant_id, operation_name, result_json, expires_at)
        
        logger.debug(
            f"Idempotency stored: key={key[:12]}... "
            f"tenant={tenant_id} ttl={ttl}h"
        )
    
    async def invalidate(self, key: str):
        """Remove a specific idempotency key (force re-execution)."""
        result = await self.db.execute(
            "DELETE FROM idempotency_keys WHERE key = $1", key
        )
        logger.info(f"Idempotency key invalidated: {key[:12]}...")
        return result
    
    async def invalidate_tenant(self, tenant_id: str):
        """Remove all idempotency keys for a tenant."""
        result = await self.db.execute(
            "DELETE FROM idempotency_keys WHERE tenant_id = $1", tenant_id
        )
        logger.info(f"All idempotency keys invalidated for tenant: {tenant_id}")
        return result
    
    async def cleanup_expired(self) -> int:
        """
        Remove expired keys. Should be called periodically (e.g., hourly cron).
        Returns number of keys deleted.
        """
        result = await self.db.execute(
            "DELETE FROM idempotency_keys WHERE expires_at < NOW()"
        )
        count = result if isinstance(result, int) else 0
        if count > 0:
            logger.info(f"Cleaned up {count} expired idempotency keys")
        return count
    
    async def get_stats(self, tenant_id: str = None) -> dict:
        """Get idempotency store statistics."""
        if tenant_id:
            row = await self.db.fetchone("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE expires_at > NOW()) as active,
                    COUNT(*) FILTER (WHERE expires_at <= NOW()) as expired
                FROM idempotency_keys
                WHERE tenant_id = $1
            """, tenant_id)
        else:
            row = await self.db.fetchone("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE expires_at > NOW()) as active,
                    COUNT(*) FILTER (WHERE expires_at <= NOW()) as expired
                FROM idempotency_keys
            """)
        
        return {
            "total": row["total"] if row else 0,
            "active": row["active"] if row else 0,
            "expired": row["expired"] if row else 0,
        }
    
    # ---------------------------------------------------------------------
    # Key Generation
    # ---------------------------------------------------------------------
    
    @staticmethod
    def generate_key(
        tenant_id: str,
        operation_name: str,
        payload: dict,
    ) -> str:
        """
        Generate a deterministic idempotency key.
        
        Key = SHA-256(tenant_id + operation_name + sorted_json(payload))
        
        Truncated to 32 chars for storage efficiency while maintaining
        collision resistance.
        """
        # Normalize payload: sort keys, serialize consistently
        payload_normalized = json.dumps(payload, sort_keys=True, default=str)
        
        source = f"{tenant_id}:{operation_name}:{payload_normalized}"
        full_hash = hashlib.sha256(source.encode()).hexdigest()
        
        return full_hash[:32]
    
    @staticmethod
    def generate_key_with_time(
        tenant_id: str,
        operation_name: str,
        payload: dict,
        time_window_minutes: int = 60,
    ) -> str:
        """
        Generate an idempotency key scoped to a time window.
        
        Useful for operations where the same request within X minutes
        should be deduplicated, but after that window it's a new request.
        
        Example: Budget changes within the same hour are considered
        duplicates, but the same change next hour is a new intent.
        """
        now = datetime.utcnow()
        window = now.replace(
            minute=(now.minute // time_window_minutes) * time_window_minutes,
            second=0,
            microsecond=0,
        )
        
        payload_normalized = json.dumps(payload, sort_keys=True, default=str)
        source = (
            f"{tenant_id}:{operation_name}:{payload_normalized}"
            f":{window.isoformat()}"
        )
        
        return hashlib.sha256(source.encode()).hexdigest()[:32]


# -----------------------------------------------------------------------------
# Database Schema
# -----------------------------------------------------------------------------

IDEMPOTENCY_SCHEMA = """
-- Idempotency key storage
CREATE TABLE IF NOT EXISTS idempotency_keys (
    key VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    operation_name VARCHAR(100),
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_idempotency_tenant 
    ON idempotency_keys(tenant_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_expires 
    ON idempotency_keys(expires_at);
CREATE INDEX IF NOT EXISTS idx_idempotency_operation 
    ON idempotency_keys(operation_name);
"""

