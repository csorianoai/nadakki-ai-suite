"""
============================================================================
NADAKKI AI SUITE - Tenant Credential Vault
Multi-Tenant Secure Credential Management with KMS Interface
============================================================================
REUSABLE FOR: Any financial institution requiring secure OAuth storage
============================================================================
"""

from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from typing import Optional, Protocol, Dict, Any
from abc import ABC, abstractmethod
import os
import json
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ABSTRACT INTERFACE (For future KMS migration)
# ============================================================================

class CredentialVaultInterface(Protocol):
    """Interface for credential vault implementations.
    
    This allows easy migration from Fernet to AWS KMS, Azure Key Vault,
    or any other encryption service without changing the calling code.
    """
    async def store_credentials(self, tenant_id: str, credentials: dict) -> None: ...
    async def get_credentials(self, tenant_id: str) -> Optional[dict]: ...
    async def refresh_if_needed(self, tenant_id: str) -> dict: ...
    async def revoke_credentials(self, tenant_id: str) -> None: ...


class EncryptionProvider(ABC):
    """Abstract encryption provider for KMS migration support"""
    
    @abstractmethod
    def encrypt(self, data: bytes) -> bytes: ...
    
    @abstractmethod
    def decrypt(self, encrypted_data: bytes) -> bytes: ...


class FernetEncryption(EncryptionProvider):
    """Fernet-based encryption (MVP - upgrade to KMS in production)"""
    
    def __init__(self, key: bytes = None):
        if key is None:
            key = os.getenv("CREDENTIAL_ENCRYPTION_KEY")
            if key:
                key = key.encode() if isinstance(key, str) else key
            else:
                key = Fernet.generate_key()
                logger.warning("Generated new encryption key - store securely!")
        self.fernet = Fernet(key)
    
    def encrypt(self, data: bytes) -> bytes:
        return self.fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        return self.fernet.decrypt(encrypted_data)


# ============================================================================
# TENANT CREDENTIAL VAULT - MAIN CLASS
# ============================================================================

class TenantCredentialVault:
    """
    Multi-tenant credential vault with:
    - Encryption at rest (Fernet/KMS)
    - TTL-based caching
    - Automatic OAuth token refresh
    - Audit logging for compliance
    - Institution-agnostic design
    
    USAGE:
        vault = TenantCredentialVault(db_connection)
        await vault.store_credentials("sfrentals", {...})
        creds = await vault.get_credentials("sfrentals")
    """
    
    CACHE_TTL_SECONDS = 300  # 5 minutes
    TOKEN_REFRESH_BUFFER_MINUTES = 5
    
    def __init__(
        self,
        db_connection,
        encryption_provider: EncryptionProvider = None,
        oauth_config: Dict[str, str] = None
    ):
        self.db = db_connection
        self.encryption = encryption_provider or FernetEncryption()
        self.oauth_config = oauth_config or {
            "client_id": os.getenv("NADAKKI_GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("NADAKKI_GOOGLE_CLIENT_SECRET"),
            "token_endpoint": "https://oauth2.googleapis.com/token"
        }
        self._cache: Dict[str, dict] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    async def store_credentials(
        self,
        tenant_id: str,
        credentials: dict,
        metadata: dict = None
    ) -> None:
        """Store encrypted credentials for a tenant.
        
        Args:
            tenant_id: Unique identifier for the financial institution
            credentials: OAuth credentials (access_token, refresh_token, etc.)
            metadata: Optional metadata (institution_name, plan, etc.)
        """
        # Validate required fields
        required = ["refresh_token", "customer_id"]
        for field in required:
            if field not in credentials:
                raise ValueError(f"Missing required credential field: {field}")
        
        # Add timestamps
        credentials["stored_at"] = datetime.utcnow().isoformat()
        if "expires_at" not in credentials and "expires_in" in credentials:
            expires_at = datetime.utcnow() + timedelta(seconds=credentials["expires_in"])
            credentials["expires_at"] = expires_at.isoformat()
        
        # Encrypt
        encrypted = self.encryption.encrypt(json.dumps(credentials).encode())
        
        # Store in database
        await self.db.execute("""
            INSERT INTO tenant_credentials (
                tenant_id, encrypted_data, metadata, created_at, updated_at
            ) VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT (tenant_id) 
            DO UPDATE SET 
                encrypted_data = $2,
                metadata = COALESCE($3, tenant_credentials.metadata),
                updated_at = NOW()
        """, tenant_id, encrypted.decode(), json.dumps(metadata or {}))
        
        # Audit log
        await self._log_access(tenant_id, "store", {"has_refresh_token": True})
        
        # Invalidate cache
        self._cache.pop(tenant_id, None)
        
        logger.info(f"Stored credentials for tenant: {tenant_id}")
    
    async def get_credentials(self, tenant_id: str) -> Optional[dict]:
        """Get decrypted credentials for a tenant.
        
        Returns cached version if available and not expired.
        """
        # Check cache
        if tenant_id in self._cache:
            cached = self._cache[tenant_id]
            if datetime.utcnow() < cached["cache_expires"]:
                await self._log_access(tenant_id, "read_cached")
                return cached["data"]
        
        # Fetch from DB
        row = await self.db.fetchone(
            "SELECT encrypted_data FROM tenant_credentials WHERE tenant_id = $1",
            tenant_id
        )
        
        if not row:
            logger.warning(f"No credentials found for tenant: {tenant_id}")
            return None
        
        # Decrypt
        decrypted = json.loads(
            self.encryption.decrypt(row["encrypted_data"].encode())
        )
        
        # Update cache
        self._cache[tenant_id] = {
            "data": decrypted,
            "cache_expires": datetime.utcnow() + timedelta(seconds=self.CACHE_TTL_SECONDS)
        }
        
        await self._log_access(tenant_id, "read")
        return decrypted
    
    async def refresh_if_needed(self, tenant_id: str) -> dict:
        """Refresh OAuth token if it's about to expire.
        
        Returns credentials with valid access_token.
        """
        # Get lock for this tenant to prevent concurrent refreshes
        if tenant_id not in self._locks:
            self._locks[tenant_id] = asyncio.Lock()
        
        async with self._locks[tenant_id]:
            creds = await self.get_credentials(tenant_id)
            
            if not creds:
                raise ValueError(f"No credentials for tenant: {tenant_id}")
            
            # Check if refresh needed
            expires_at = datetime.fromisoformat(
                creds.get("expires_at", "2000-01-01T00:00:00")
            )
            refresh_threshold = datetime.utcnow() + timedelta(
                minutes=self.TOKEN_REFRESH_BUFFER_MINUTES
            )
            
            if datetime.utcnow() < refresh_threshold < expires_at:
                # Token still valid
                return creds
            
            # Need to refresh
            logger.info(f"Refreshing OAuth token for tenant: {tenant_id}")
            new_creds = await self._refresh_oauth_token(creds)
            await self.store_credentials(tenant_id, new_creds)
            
            return new_creds
    
    async def revoke_credentials(self, tenant_id: str) -> None:
        """Revoke and delete credentials for a tenant."""
        await self.db.execute(
            "DELETE FROM tenant_credentials WHERE tenant_id = $1",
            tenant_id
        )
        self._cache.pop(tenant_id, None)
        await self._log_access(tenant_id, "revoke")
        logger.info(f"Revoked credentials for tenant: {tenant_id}")
    
    async def get_all_tenants(self) -> list:
        """Get list of all tenant IDs with stored credentials."""
        rows = await self.db.fetch(
            "SELECT tenant_id FROM tenant_credentials ORDER BY tenant_id"
        )
        return [row["tenant_id"] for row in rows]
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    async def _refresh_oauth_token(self, creds: dict) -> dict:
        """Refresh OAuth token with Google."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.oauth_config["token_endpoint"],
                data={
                    "client_id": self.oauth_config["client_id"],
                    "client_secret": self.oauth_config["client_secret"],
                    "refresh_token": creds["refresh_token"],
                    "grant_type": "refresh_token"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.text}")
                raise Exception(f"Token refresh failed: {response.status_code}")
            
            data = response.json()
            
            return {
                **creds,
                "access_token": data["access_token"],
                "expires_at": (
                    datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
                ).isoformat(),
                "token_type": data.get("token_type", "Bearer"),
                "refreshed_at": datetime.utcnow().isoformat()
            }
    
    async def _log_access(
        self,
        tenant_id: str,
        action: str,
        details: dict = None
    ):
        """Audit log of credential access for compliance."""
        await self.db.execute("""
            INSERT INTO credential_access_log (
                tenant_id, action, details, timestamp, ip_address
            ) VALUES ($1, $2, $3, NOW(), $4)
        """, tenant_id, action, json.dumps(details or {}), None)


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

VAULT_SCHEMA_SQL = """
-- Tenant Credentials Table
CREATE TABLE IF NOT EXISTS tenant_credentials (
    tenant_id VARCHAR(100) PRIMARY KEY,
    encrypted_data TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_tenant_creds_updated 
    ON tenant_credentials(updated_at);

-- Credential Access Log for Compliance
CREATE TABLE IF NOT EXISTS credential_access_log (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET
);

-- Index for audit queries
CREATE INDEX IF NOT EXISTS idx_cred_access_tenant 
    ON credential_access_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cred_access_timestamp 
    ON credential_access_log(timestamp);

-- Partition by month for large-scale deployments (optional)
-- CREATE TABLE credential_access_log_2026_01 PARTITION OF credential_access_log
--     FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
"""

# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

async def create_vault(db_connection, use_kms: bool = False) -> TenantCredentialVault:
    """Factory to create appropriate vault instance.
    
    Args:
        db_connection: Database connection
        use_kms: If True, use AWS KMS (requires boto3)
    """
    if use_kms:
        # Future: Import and use KMS provider
        # from .kms_provider import AWSKMSEncryption
        # encryption = AWSKMSEncryption(key_id=os.getenv("KMS_KEY_ID"))
        raise NotImplementedError("KMS provider coming in Phase 2")
    
    return TenantCredentialVault(db_connection)
