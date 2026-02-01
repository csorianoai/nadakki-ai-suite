"""
============================================================================
NADAKKI AI SUITE - Idempotency Store
Prevent Duplicate Operations Across All Tenants
============================================================================
REUSABLE FOR: Any system requiring idempotent operations
============================================================================
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class IdempotencyRecord:
    """Record of an idempotent operation."""
    key: str
    tenant_id: str
    operation_name: str
    result: dict
    created_at: datetime
    expires_at: datetime


class IdempotencyStore:
    """
    Store for idempotency keys to prevent duplicate operations.
    
    Features:
    - TTL-based expiration (default 24 hours)
    - Per-tenant isolation
    - Automatic cleanup
    
    USAGE:
        store = IdempotencyStore(db_connection)
        
        # Check before execution
        cached = await store.check(idempotency_key, tenant_id)
        if cached:
            return cached  # Return cached result
        
        # Execute operation...
        
        # Store result
        await store.store(idempotency_key, tenant_id, operation, result)
    """
    
    DEFAULT_TTL_HOURS = 24
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def check(self, key: str, tenant_id: str) -> Optional[dict]:
        """Check if a result exists for this idempotency key.
        
        Returns:
            Cached result if exists and not expired, None otherwise
        """
        row = await self.db.fetchone("""
            SELECT result, operation_name, created_at
            FROM idempotency_keys 
            WHERE key = $1 AND tenant_id = $2 AND expires_at > NOW()
        """, key, tenant_id)
        
        if row:
            logger.info(f"Idempotency cache hit for key: {key[:16]}...")
            return json.loads(row["result"])
        
        return None
    
    async def store(
        self,
        key: str,
        tenant_id: str,
        operation_name: str,
        result: dict,
        ttl_hours: int = None
    ):
        """Store result with TTL.
        
        Args:
            key: Idempotency key
            tenant_id: Tenant identifier
            operation_name: Name of the operation
            result: Result to cache
            ttl_hours: Time to live in hours (default: 24)
        """
        ttl = ttl_hours or self.DEFAULT_TTL_HOURS
        expires_at = datetime.utcnow() + timedelta(hours=ttl)
        
        await self.db.execute("""
            INSERT INTO idempotency_keys (
                key, tenant_id, operation_name, result, created_at, expires_at
            )
            VALUES ($1, $2, $3, $4, NOW(), $5)
            ON CONFLICT (key) 
            DO UPDATE SET result = $4, expires_at = $5
        """, key, tenant_id, operation_name, json.dumps(result), expires_at)
        
        logger.debug(f"Stored idempotency key: {key[:16]}... (TTL: {ttl}h)")
    
    async def invalidate(self, key: str, tenant_id: str):
        """Invalidate a specific idempotency key."""
        await self.db.execute(
            "DELETE FROM idempotency_keys WHERE key = $1 AND tenant_id = $2",
            key, tenant_id
        )
    
    async def cleanup_expired(self) -> int:
        """Clean up expired idempotency keys.
        
        Returns:
            Number of deleted keys
        """
        result = await self.db.execute(
            "DELETE FROM idempotency_keys WHERE expires_at < NOW() RETURNING key"
        )
        count = result.rowcount if hasattr(result, 'rowcount') else 0
        logger.info(f"Cleaned up {count} expired idempotency keys")
        return count
    
    async def get_stats(self) -> dict:
        """Get statistics about stored keys."""
        row = await self.db.fetchone("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT tenant_id) as tenants,
                MIN(created_at) as oldest,
                MAX(created_at) as newest
            FROM idempotency_keys
            WHERE expires_at > NOW()
        """)
        
        return {
            "total_keys": row["total"],
            "unique_tenants": row["tenants"],
            "oldest_key": row["oldest"].isoformat() if row["oldest"] else None,
            "newest_key": row["newest"].isoformat() if row["newest"] else None
        }


def generate_idempotency_key(
    operation_name: str,
    payload: dict,
    tenant_id: str,
    extra: str = ""
) -> str:
    """Generate a deterministic idempotency key.
    
    The key is based on:
    - Operation name
    - Payload (sorted for consistency)
    - Tenant ID
    - Optional extra data
    
    Returns:
        32-character hex string
    """
    # Normalize payload
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    
    # Build key source
    key_source = f"{tenant_id}:{operation_name}:{payload_str}:{extra}"
    
    # Generate hash
    return hashlib.sha256(key_source.encode()).hexdigest()[:32]


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

IDEMPOTENCY_SCHEMA_SQL = """
-- Idempotency Keys Table
CREATE TABLE IF NOT EXISTS idempotency_keys (
    key VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    operation_name VARCHAR(100) NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_idempotency_tenant 
    ON idempotency_keys(tenant_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_expires 
    ON idempotency_keys(expires_at);
CREATE INDEX IF NOT EXISTS idx_idempotency_operation 
    ON idempotency_keys(operation_name);

-- Partial index for non-expired keys
CREATE INDEX IF NOT EXISTS idx_idempotency_active 
    ON idempotency_keys(key, tenant_id) 
    WHERE expires_at > NOW();
"""
