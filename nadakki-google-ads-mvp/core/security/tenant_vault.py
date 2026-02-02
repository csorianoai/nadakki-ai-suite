# ===============================================================================
# NADAKKI AI Suite - TenantCredentialVault
# core/security/tenant_vault.py
# Day 1 - Component 1 of 4
# ===============================================================================

"""
Multi-tenant credential management with encryption.

MVP: Fernet symmetric encryption with interface extensible to AWS KMS.
Each tenant's Google Ads credentials are stored encrypted at rest.

Security Model:
- Encryption key from env var CREDENTIAL_ENCRYPTION_KEY
- In-memory TTL cache (5 min) to reduce DB reads
- Audit log of every credential access
- Automatic OAuth token refresh when within 5 min of expiry
"""

from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from typing import Optional, Protocol, Dict, Any
import os
import json
import logging
import hashlib

logger = logging.getLogger("nadakki.security.vault")


# -----------------------------------------------------------------------------
# Interface for future KMS migration
# -----------------------------------------------------------------------------

class CredentialVaultInterface(Protocol):
    """Protocol for credential vault implementations."""
    async def store_credentials(self, tenant_id: str, credentials: dict) -> None: ...
    async def get_credentials(self, tenant_id: str) -> Optional[dict]: ...
    async def refresh_if_needed(self, tenant_id: str) -> dict: ...
    async def delete_credentials(self, tenant_id: str) -> bool: ...


# -----------------------------------------------------------------------------
# MVP Implementation
# -----------------------------------------------------------------------------

class TenantCredentialVault:
    """
    Fernet-based credential vault with TTL cache and audit logging.
    
    Usage:
        vault = TenantCredentialVault(db)
        await vault.store_credentials("bank01", {
            "refresh_token": "...",
            "customer_id": "1234567890",
            "manager_customer_id": "9876543210",
            "access_token": "...",
            "expires_at": "2026-02-01T20:00:00"
        })
        
        creds = await vault.refresh_if_needed("bank01")
    """
    
    CACHE_TTL_SECONDS = 300  # 5 minutes
    TOKEN_REFRESH_BUFFER_MINUTES = 5
    
    def __init__(self, db_connection, encryption_key: str = None):
        self.db = db_connection
        
        # Encryption setup
        key = encryption_key or os.getenv("CREDENTIAL_ENCRYPTION_KEY")
        if not key:
            logger.warning(
                "CREDENTIAL_ENCRYPTION_KEY not set. Generating ephemeral key. "
                "DO NOT use this in production."
            )
            key = Fernet.generate_key()
        
        if isinstance(key, str):
            key = key.encode()
        
        self.fernet = Fernet(key)
        self._cache: Dict[str, dict] = {}
    
    # ---------------------------------------------------------------------
    # Core Operations
    # ---------------------------------------------------------------------
    
    async def store_credentials(self, tenant_id: str, credentials: dict) -> None:
        """Store encrypted credentials for a tenant."""
        self._validate_tenant_id(tenant_id)
        
        # Encrypt
        plaintext = json.dumps(credentials, default=str).encode()
        encrypted = self.fernet.encrypt(plaintext).decode()
        
        # Upsert
        await self.db.execute("""
            INSERT INTO tenant_credentials (tenant_id, encrypted_data, updated_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (tenant_id)
            DO UPDATE SET encrypted_data = $2, updated_at = NOW()
        """, tenant_id, encrypted)
        
        # Invalidate cache
        self._cache.pop(tenant_id, None)
        
        # Audit
        await self._audit_log(tenant_id, "store", {
            "has_refresh_token": "refresh_token" in credentials,
            "has_customer_id": "customer_id" in credentials,
        })
        
        logger.info(f"Credentials stored for tenant: {tenant_id}")
    
    async def get_credentials(self, tenant_id: str) -> Optional[dict]:
        """Get decrypted credentials for a tenant."""
        self._validate_tenant_id(tenant_id)
        
        # Check cache
        cached = self._get_from_cache(tenant_id)
        if cached is not None:
            await self._audit_log(tenant_id, "read_cached")
            return cached
        
        # Fetch from DB
        row = await self.db.fetchone(
            "SELECT encrypted_data FROM tenant_credentials WHERE tenant_id = $1",
            tenant_id
        )
        
        if not row:
            logger.warning(f"No credentials found for tenant: {tenant_id}")
            return None
        
        # Decrypt
        try:
            decrypted = json.loads(
                self.fernet.decrypt(row["encrypted_data"].encode())
            )
        except Exception as e:
            logger.error(f"Decryption failed for tenant {tenant_id}: {e}")
            raise ValueError(f"Cannot decrypt credentials for tenant: {tenant_id}")
        
        # Cache
        self._put_in_cache(tenant_id, decrypted)
        
        await self._audit_log(tenant_id, "read")
        return decrypted
    
    async def refresh_if_needed(self, tenant_id: str) -> dict:
        """Get credentials, refreshing OAuth token if near expiry."""
        creds = await self.get_credentials(tenant_id)
        
        if not creds:
            raise ValueError(f"No credentials for tenant: {tenant_id}")
        
        # Check expiry
        expires_at_str = creds.get("expires_at")
        if not expires_at_str:
            # No expiry tracked - assume needs refresh
            return await self._do_refresh(tenant_id, creds)
        
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
        except (ValueError, TypeError):
            return await self._do_refresh(tenant_id, creds)
        
        buffer = timedelta(minutes=self.TOKEN_REFRESH_BUFFER_MINUTES)
        if datetime.utcnow() > expires_at - buffer:
            return await self._do_refresh(tenant_id, creds)
        
        return creds
    
    async def delete_credentials(self, tenant_id: str) -> bool:
        """Delete credentials for a tenant (GDPR right-to-erasure)."""
        self._validate_tenant_id(tenant_id)
        
        result = await self.db.execute(
            "DELETE FROM tenant_credentials WHERE tenant_id = $1",
            tenant_id
        )
        
        self._cache.pop(tenant_id, None)
        
        await self._audit_log(tenant_id, "delete")
        logger.info(f"Credentials deleted for tenant: {tenant_id}")
        
        return result > 0 if isinstance(result, int) else True
    
    async def list_tenants(self) -> list:
        """List all tenants with stored credentials."""
        rows = await self.db.fetch(
            "SELECT tenant_id, updated_at FROM tenant_credentials ORDER BY tenant_id"
        )
        return [{"tenant_id": r["tenant_id"], "updated_at": r["updated_at"]} for r in rows]
    
    # ---------------------------------------------------------------------
    # OAuth Token Refresh
    # ---------------------------------------------------------------------
    
    async def _do_refresh(self, tenant_id: str, creds: dict) -> dict:
        """Refresh OAuth token with Google."""
        import httpx
        
        refresh_token = creds.get("refresh_token")
        if not refresh_token:
            raise ValueError(f"No refresh_token for tenant: {tenant_id}")
        
        client_id = os.getenv("NADAKKI_GOOGLE_CLIENT_ID")
        client_secret = os.getenv("NADAKKI_GOOGLE_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise EnvironmentError(
                "NADAKKI_GOOGLE_CLIENT_ID and NADAKKI_GOOGLE_CLIENT_SECRET must be set"
            )
        
        logger.info(f"Refreshing OAuth token for tenant: {tenant_id}")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            
            if response.status_code != 200:
                error_body = response.text
                logger.error(
                    f"Token refresh failed for {tenant_id}: "
                    f"status={response.status_code} body={error_body}"
                )
                raise Exception(
                    f"Token refresh failed for tenant {tenant_id}: {response.status_code}"
                )
            
            data = response.json()
        
        # Update credentials
        new_creds = {
            **creds,
            "access_token": data["access_token"],
            "expires_at": (
                datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
            ).isoformat(),
        }
        
        # If Google returned a new refresh token, update it
        if "refresh_token" in data:
            new_creds["refresh_token"] = data["refresh_token"]
        
        # Persist
        await self.store_credentials(tenant_id, new_creds)
        
        await self._audit_log(tenant_id, "token_refresh", {
            "new_expiry": new_creds["expires_at"]
        })
        
        return new_creds
    
    # ---------------------------------------------------------------------
    # Cache Management
    # ---------------------------------------------------------------------
    
    def _get_from_cache(self, tenant_id: str) -> Optional[dict]:
        """Get from TTL cache."""
        entry = self._cache.get(tenant_id)
        if entry and datetime.utcnow() < entry["expires"]:
            return entry["data"]
        
        # Expired - remove
        self._cache.pop(tenant_id, None)
        return None
    
    def _put_in_cache(self, tenant_id: str, data: dict):
        """Put in TTL cache."""
        self._cache[tenant_id] = {
            "data": data,
            "expires": datetime.utcnow() + timedelta(seconds=self.CACHE_TTL_SECONDS)
        }
    
    def clear_cache(self, tenant_id: str = None):
        """Clear cache for one or all tenants."""
        if tenant_id:
            self._cache.pop(tenant_id, None)
        else:
            self._cache.clear()
    
    # ---------------------------------------------------------------------
    # Audit & Validation
    # ---------------------------------------------------------------------
    
    async def _audit_log(self, tenant_id: str, action: str, metadata: dict = None):
        """Record credential access in audit log."""
        try:
            await self.db.execute("""
                INSERT INTO credential_access_log 
                (tenant_id, action, metadata, timestamp)
                VALUES ($1, $2, $3, NOW())
            """, tenant_id, action, json.dumps(metadata or {}))
        except Exception as e:
            # Audit failure should not block operation
            logger.error(f"Audit log failed: {e}")
    
    @staticmethod
    def _validate_tenant_id(tenant_id: str):
        """Validate tenant_id format."""
        if not tenant_id or not isinstance(tenant_id, str):
            raise ValueError("tenant_id must be a non-empty string")
        if len(tenant_id) > 100:
            raise ValueError("tenant_id must be <= 100 characters")
        if not all(c.isalnum() or c in ('-', '_') for c in tenant_id):
            raise ValueError("tenant_id must contain only alphanumeric, hyphens, underscores")


# -----------------------------------------------------------------------------
# Database Schema
# -----------------------------------------------------------------------------

VAULT_SCHEMA = """
-- Tenant credentials (encrypted at rest)
CREATE TABLE IF NOT EXISTS tenant_credentials (
    tenant_id VARCHAR(100) PRIMARY KEY,
    encrypted_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for credential access
CREATE TABLE IF NOT EXISTS credential_access_log (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cred_access_tenant 
    ON credential_access_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cred_access_timestamp 
    ON credential_access_log(timestamp);
"""
