#!/usr/bin/env python3
"""
============================================================================
NADAKKI AI SUITE - PHASE 1 GENERATOR
Core Infrastructure: Credentials -> Client -> Operations
============================================================================
REUSABLE FOR: Multiple Financial Institutions (Multi-Tenant)
============================================================================
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_file(relative_path: str, content: str):
    """Create a file with the given content"""
    full_path = os.path.join(PROJECT_ROOT, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [+] Created: {relative_path}")

# ============================================================================
# CORE/SECURITY/TENANT_VAULT.PY
# ============================================================================
TENANT_VAULT_CODE = '''"""
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
'''

# ============================================================================
# CORE/GOOGLE_ADS/CLIENT_FACTORY.PY
# ============================================================================
CLIENT_FACTORY_CODE = '''"""
============================================================================
NADAKKI AI SUITE - Google Ads Client Factory
Multi-Tenant Client Pool with Auto-Refresh
============================================================================
REUSABLE FOR: Any financial institution requiring Google Ads API access
============================================================================
"""

from google.ads.googleads.client import GoogleAdsClient
from typing import Dict, Optional
from datetime import datetime, timedelta
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

# Configurable API version
GOOGLE_ADS_API_VERSION = os.getenv("GOOGLE_ADS_API_VERSION", "v15")


class GoogleAdsClientFactory:
    """
    Factory for Google Ads API clients with:
    - Connection pooling per tenant (max 2 per tenant for MVP)
    - Automatic token refresh
    - Health checking
    - Metrics collection
    
    USAGE:
        factory = GoogleAdsClientFactory(credential_vault)
        client = await factory.get_client("sfrentals")
        # Use client...
        factory.return_client("sfrentals", client)  # Optional
    """
    
    MAX_CLIENTS_PER_TENANT = 2
    HEALTH_CHECK_INTERVAL_SECONDS = 60
    CLIENT_TTL_HOURS = 1
    
    def __init__(self, credential_vault):
        self.vault = credential_vault
        self._clients: Dict[str, dict] = {}  # tenant_id -> {client, metadata}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._health_check_task: Optional[asyncio.Task] = None
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    async def get_client(self, tenant_id: str) -> GoogleAdsClient:
        """Get or create a Google Ads client for a tenant.
        
        Args:
            tenant_id: Unique identifier for the financial institution
            
        Returns:
            GoogleAdsClient configured for the tenant
        """
        # Ensure lock exists for tenant
        if tenant_id not in self._locks:
            self._locks[tenant_id] = asyncio.Lock()
        
        async with self._locks[tenant_id]:
            # Check if we have a valid cached client
            if tenant_id in self._clients:
                cached = self._clients[tenant_id]
                if cached["healthy"] and self._is_valid(cached):
                    cached["last_used"] = datetime.utcnow()
                    logger.debug(f"Returning cached client for tenant: {tenant_id}")
                    return cached["client"]
                else:
                    # Invalid or unhealthy - remove from cache
                    del self._clients[tenant_id]
            
            # Create new client
            logger.info(f"Creating new Google Ads client for tenant: {tenant_id}")
            client = await self._create_client(tenant_id)
            
            self._clients[tenant_id] = {
                "client": client,
                "created_at": datetime.utcnow(),
                "last_used": datetime.utcnow(),
                "healthy": True,
                "health_check_count": 0
            }
            
            return client
    
    async def health_check(self, tenant_id: str) -> bool:
        """Check if the client for a tenant is healthy.
        
        Performs a simple query to verify API connectivity.
        """
        try:
            client = await self.get_client(tenant_id)
            creds = await self.vault.get_credentials(tenant_id)
            customer_id = creds.get("customer_id")
            
            if not customer_id:
                return False
            
            # Simple query to verify connection
            ga_service = client.get_service("GoogleAdsService")
            query = "SELECT customer.id FROM customer LIMIT 1"
            
            response = ga_service.search(customer_id=customer_id, query=query)
            list(response)  # Consume iterator to execute query
            
            # Update health status
            if tenant_id in self._clients:
                self._clients[tenant_id]["healthy"] = True
                self._clients[tenant_id]["health_check_count"] += 1
            
            logger.info(f"Health check passed for tenant: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for tenant {tenant_id}: {e}")
            if tenant_id in self._clients:
                self._clients[tenant_id]["healthy"] = False
            return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Run health check on all cached clients."""
        results = {}
        for tenant_id in list(self._clients.keys()):
            results[tenant_id] = await self.health_check(tenant_id)
        return results
    
    def invalidate(self, tenant_id: str):
        """Remove a client from the pool."""
        if tenant_id in self._clients:
            del self._clients[tenant_id]
            logger.info(f"Invalidated client for tenant: {tenant_id}")
    
    def invalidate_all(self):
        """Clear the entire client pool."""
        self._clients.clear()
        logger.info("Invalidated all clients")
    
    def get_stats(self) -> dict:
        """Get statistics about the client pool."""
        return {
            "total_clients": len(self._clients),
            "api_version": GOOGLE_ADS_API_VERSION,
            "by_tenant": {
                tid: {
                    "healthy": data["healthy"],
                    "age_seconds": (datetime.utcnow() - data["created_at"]).total_seconds(),
                    "last_used_seconds_ago": (datetime.utcnow() - data["last_used"]).total_seconds(),
                    "health_check_count": data["health_check_count"]
                }
                for tid, data in self._clients.items()
            }
        }
    
    # ========================================================================
    # BACKGROUND TASKS
    # ========================================================================
    
    async def start_health_check_loop(self):
        """Start background health check loop."""
        if self._health_check_task is not None:
            return
        
        async def health_loop():
            while True:
                await asyncio.sleep(self.HEALTH_CHECK_INTERVAL_SECONDS)
                await self.health_check_all()
        
        self._health_check_task = asyncio.create_task(health_loop())
        logger.info("Started health check background loop")
    
    async def stop_health_check_loop(self):
        """Stop background health check loop."""
        if self._health_check_task:
            self._health_check_task.cancel()
            self._health_check_task = None
            logger.info("Stopped health check background loop")
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    async def _create_client(self, tenant_id: str) -> GoogleAdsClient:
        """Create a new Google Ads client with tenant credentials."""
        # Get and refresh credentials if needed
        creds = await self.vault.refresh_if_needed(tenant_id)
        
        # Build client configuration
        config = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
            "client_id": os.getenv("NADAKKI_GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("NADAKKI_GOOGLE_CLIENT_SECRET"),
            "refresh_token": creds["refresh_token"],
            "use_proto_plus": True
        }
        
        # Add manager customer ID if available (for MCC accounts)
        if "manager_customer_id" in creds:
            config["login_customer_id"] = creds["manager_customer_id"]
        
        # Create client
        client = GoogleAdsClient.load_from_dict(config, version=GOOGLE_ADS_API_VERSION)
        
        return client
    
    def _is_valid(self, cached: dict) -> bool:
        """Check if a cached client is still valid."""
        # Check age
        age = datetime.utcnow() - cached["created_at"]
        if age > timedelta(hours=self.CLIENT_TTL_HOURS):
            return False
        
        # Check inactivity
        inactive = datetime.utcnow() - cached["last_used"]
        if inactive > timedelta(hours=self.CLIENT_TTL_HOURS):
            return False
        
        return True


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def get_customer_info(client: GoogleAdsClient, customer_id: str) -> dict:
    """Helper to get basic customer info."""
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone,
            customer.manager
        FROM customer
    """
    response = ga_service.search(customer_id=customer_id, query=query)
    
    for row in response:
        return {
            "id": str(row.customer.id),
            "name": row.customer.descriptive_name,
            "currency": row.customer.currency_code,
            "timezone": row.customer.time_zone,
            "is_manager": row.customer.manager
        }
    
    return None
'''

# ============================================================================
# CORE/OPERATIONS/REGISTRY.PY
# ============================================================================
OPERATIONS_REGISTRY_CODE = '''"""
============================================================================
NADAKKI AI SUITE - Operation Registry
Typed Operations with Versioning and Validation
============================================================================
REUSABLE FOR: Any operation-based API integration
============================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List, Union
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ERROR CODES
# ============================================================================

class ErrorCode(Enum):
    """Normalized error codes for consistent error handling across all tenants."""
    SUCCESS = "SUCCESS"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    AUTH_FAILED = "AUTH_FAILED"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    NETWORK_ERROR = "NETWORK_ERROR"
    API_ERROR = "API_ERROR"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class OperationContext:
    """Context for operation execution.
    
    Carries metadata through the entire operation lifecycle.
    """
    tenant_id: str
    user_id: Optional[str] = None
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dry_run: bool = False
    source: str = "api"  # api, scheduler, agent, workflow
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationRequest:
    """Standardized operation request.
    
    All operations use this format for consistent processing.
    """
    operation_id: str
    operation_name: str  # Format: "operation_name@version" e.g., "update_budget@v1"
    tenant_id: str
    idempotency_key: str
    payload: Dict[str, Any]
    context: OperationContext
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0  # Higher = more important
    
    @property
    def operation_base(self) -> str:
        """Get operation name without version."""
        return self.operation_name.split("@")[0]
    
    @property
    def operation_version(self) -> str:
        """Get operation version."""
        parts = self.operation_name.split("@")
        return parts[1] if len(parts) > 1 else "v1"


@dataclass
class OperationResult:
    """Standardized operation result.
    
    All operations return this format for consistent handling.
    """
    success: bool
    operation_id: str
    operation_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[ErrorCode] = None
    error_message: Optional[str] = None
    resource_name: Optional[str] = None
    compensable: bool = False
    compensation_data: Optional[Dict[str, Any]] = None
    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "operation_id": self.operation_id,
            "operation_name": self.operation_name,
            "data": self.data,
            "error_code": self.error_code.value if self.error_code else None,
            "error_message": self.error_message,
            "resource_name": self.resource_name,
            "compensable": self.compensable,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "warnings": self.warnings
        }


@dataclass
class OperationSchema:
    """Schema for operation validation."""
    name: str
    version: str
    required_fields: List[str]
    optional_fields: List[str] = field(default_factory=list)
    validators: Dict[str, Callable] = field(default_factory=dict)
    compensation_operation: Optional[str] = None
    description: str = ""
    
    def validate(self, payload: dict) -> tuple[bool, Optional[str]]:
        """Validate payload against schema.
        
        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        for field_name in self.required_fields:
            if field_name not in payload:
                return False, f"Missing required field: {field_name}"
        
        # Run custom validators
        for field_name, validator in self.validators.items():
            if field_name in payload:
                try:
                    if not validator(payload[field_name]):
                        return False, f"Validation failed for field: {field_name}"
                except Exception as e:
                    return False, f"Validator error for {field_name}: {str(e)}"
        
        return True, None


# ============================================================================
# OPERATION REGISTRY
# ============================================================================

class OperationRegistry:
    """
    Central registry for all supported operations.
    
    Features:
    - Schema validation per operation
    - Version management
    - Handler registration
    - Compensation operation mapping
    
    USAGE:
        registry = get_operation_registry()
        registry.register("my_operation", "v1", handler, schema)
        result = await registry.execute(request, client, customer_id)
    """
    
    def __init__(self):
        self._operations: Dict[str, dict] = {}
        self._register_builtin_operations()
    
    def register(
        self,
        name: str,
        version: str,
        handler: Callable,
        schema: OperationSchema,
        description: str = ""
    ):
        """Register a new operation."""
        key = f"{name}@{version}"
        self._operations[key] = {
            "name": name,
            "version": version,
            "handler": handler,
            "schema": schema,
            "description": description
        }
        logger.info(f"Registered operation: {key}")
    
    def get(self, operation_name: str) -> Optional[dict]:
        """Get registered operation."""
        return self._operations.get(operation_name)
    
    def list_operations(self) -> List[str]:
        """List all registered operations."""
        return list(self._operations.keys())
    
    def validate(self, request: OperationRequest) -> tuple[bool, Optional[str]]:
        """Validate request against operation schema."""
        op = self.get(request.operation_name)
        if not op:
            return False, f"Unknown operation: {request.operation_name}"
        
        return op["schema"].validate(request.payload)
    
    async def execute(
        self,
        request: OperationRequest,
        client,
        customer_id: str
    ) -> OperationResult:
        """Execute an operation."""
        import time
        start = time.time()
        
        op = self.get(request.operation_name)
        if not op:
            return OperationResult(
                success=False,
                operation_id=request.operation_id,
                operation_name=request.operation_name,
                error_code=ErrorCode.INVALID_PAYLOAD,
                error_message=f"Unknown operation: {request.operation_name}"
            )
        
        # Validate
        valid, error = op["schema"].validate(request.payload)
        if not valid:
            return OperationResult(
                success=False,
                operation_id=request.operation_id,
                operation_name=request.operation_name,
                error_code=ErrorCode.INVALID_PAYLOAD,
                error_message=error
            )
        
        # Execute
        try:
            result = await op["handler"](
                client, customer_id, request.payload, request.context
            )
            result.operation_id = request.operation_id
            result.operation_name = request.operation_name
            result.execution_time_ms = int((time.time() - start) * 1000)
            return result
            
        except Exception as e:
            logger.error(f"Operation {request.operation_name} failed: {e}")
            return OperationResult(
                success=False,
                operation_id=request.operation_id,
                operation_name=request.operation_name,
                error_code=self._classify_error(e),
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
    
    def _classify_error(self, error: Exception) -> ErrorCode:
        """Classify error into normalized code."""
        error_str = str(error).lower()
        
        if "quota" in error_str or "rate" in error_str:
            return ErrorCode.QUOTA_EXCEEDED
        elif "auth" in error_str or "permission" in error_str or "token" in error_str:
            return ErrorCode.AUTH_FAILED
        elif "not found" in error_str or "does not exist" in error_str:
            return ErrorCode.RESOURCE_NOT_FOUND
        elif "policy" in error_str or "violation" in error_str:
            return ErrorCode.POLICY_VIOLATION
        elif "network" in error_str or "connection" in error_str:
            return ErrorCode.NETWORK_ERROR
        elif "timeout" in error_str:
            return ErrorCode.TIMEOUT
        else:
            return ErrorCode.API_ERROR
    
    # ========================================================================
    # BUILTIN OPERATIONS
    # ========================================================================
    
    def _register_builtin_operations(self):
        """Register all builtin operations."""
        self._register_get_campaign_metrics()
        self._register_update_campaign_budget()
        self._register_get_account_info()
    
    def _register_get_campaign_metrics(self):
        """Register get_campaign_metrics@v1"""
        
        async def handler(client, customer_id, payload, ctx):
            ga_service = client.get_service("GoogleAdsService")
            
            # Build query
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign_budget.amount_micros,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value
                FROM campaign
                WHERE campaign.status != 'REMOVED'
            """
            
            # Filter by campaign IDs if provided
            campaign_ids = payload.get("campaign_ids")
            if campaign_ids:
                ids_str = ",".join(str(cid) for cid in campaign_ids)
                query += f" AND campaign.id IN ({ids_str})"
            
            # Add date range if provided
            date_range = payload.get("date_range")
            if date_range:
                query += f" AND segments.date BETWEEN '{date_range['start']}' AND '{date_range['end']}'"
            
            # Execute
            response = ga_service.search_stream(customer_id=customer_id, query=query)
            
            campaigns = []
            for batch in response:
                for row in batch.results:
                    campaigns.append({
                        "id": str(row.campaign.id),
                        "name": row.campaign.name,
                        "status": row.campaign.status.name,
                        "budget_micros": row.campaign_budget.amount_micros,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost_micros": row.metrics.cost_micros,
                        "conversions": row.metrics.conversions,
                        "conversions_value": row.metrics.conversions_value
                    })
            
            return OperationResult(
                success=True,
                operation_id="",
                operation_name="get_campaign_metrics@v1",
                data={"campaigns": campaigns, "count": len(campaigns)}
            )
        
        self.register(
            name="get_campaign_metrics",
            version="v1",
            handler=handler,
            schema=OperationSchema(
                name="get_campaign_metrics",
                version="v1",
                required_fields=[],
                optional_fields=["campaign_ids", "date_range"],
                validators={
                    "campaign_ids": lambda x: isinstance(x, list)
                }
            ),
            description="Get campaign performance metrics"
        )
    
    def _register_update_campaign_budget(self):
        """Register update_campaign_budget@v1"""
        
        async def handler(client, customer_id, payload, ctx):
            # Dry run mode
            if ctx.dry_run:
                return OperationResult(
                    success=True,
                    operation_id="",
                    operation_name="update_campaign_budget@v1",
                    data={
                        "dry_run": True,
                        "would_update": {
                            "budget_id": payload["budget_id"],
                            "new_amount_micros": int(payload["new_budget"] * 1_000_000)
                        }
                    }
                )
            
            # Real execution
            budget_service = client.get_service("CampaignBudgetService")
            
            operation = client.get_type("CampaignBudgetOperation")
            budget = operation.update
            budget.resource_name = f"customers/{customer_id}/campaignBudgets/{payload['budget_id']}"
            budget.amount_micros = int(payload["new_budget"] * 1_000_000)
            
            client.copy_from(
                operation.update_mask,
                client.get_type("FieldMask")(paths=["amount_micros"])
            )
            
            response = budget_service.mutate_campaign_budgets(
                customer_id=customer_id,
                operations=[operation]
            )
            
            return OperationResult(
                success=True,
                operation_id="",
                operation_name="update_campaign_budget@v1",
                resource_name=response.results[0].resource_name,
                data={
                    "budget_id": payload["budget_id"],
                    "new_budget": payload["new_budget"],
                    "previous_budget": payload.get("previous_budget")
                },
                compensable=True,
                compensation_data={
                    "operation": "update_campaign_budget@v1",
                    "payload": {
                        "budget_id": payload["budget_id"],
                        "new_budget": payload.get("previous_budget", payload["new_budget"])
                    }
                }
            )
        
        self.register(
            name="update_campaign_budget",
            version="v1",
            handler=handler,
            schema=OperationSchema(
                name="update_campaign_budget",
                version="v1",
                required_fields=["budget_id", "new_budget"],
                optional_fields=["previous_budget", "reason"],
                validators={
                    "budget_id": lambda x: isinstance(x, str) and len(x) > 0,
                    "new_budget": lambda x: isinstance(x, (int, float)) and x > 0
                },
                compensation_operation="update_campaign_budget@v1"
            ),
            description="Update campaign budget amount"
        )
    
    def _register_get_account_info(self):
        """Register get_account_info@v1"""
        
        async def handler(client, customer_id, payload, ctx):
            ga_service = client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.manager
                FROM customer
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            for row in response:
                return OperationResult(
                    success=True,
                    operation_id="",
                    operation_name="get_account_info@v1",
                    data={
                        "customer_id": str(row.customer.id),
                        "name": row.customer.descriptive_name,
                        "currency": row.customer.currency_code,
                        "timezone": row.customer.time_zone,
                        "is_manager": row.customer.manager
                    }
                )
            
            return OperationResult(
                success=False,
                operation_id="",
                operation_name="get_account_info@v1",
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                error_message="Customer not found"
            )
        
        self.register(
            name="get_account_info",
            version="v1",
            handler=handler,
            schema=OperationSchema(
                name="get_account_info",
                version="v1",
                required_fields=[],
                optional_fields=[]
            ),
            description="Get Google Ads account information"
        )


# ============================================================================
# SINGLETON
# ============================================================================

_registry: Optional[OperationRegistry] = None

def get_operation_registry() -> OperationRegistry:
    """Get singleton operation registry instance."""
    global _registry
    if _registry is None:
        _registry = OperationRegistry()
    return _registry
'''

# ============================================================================
# CORE/RELIABILITY/IDEMPOTENCY.PY
# ============================================================================
IDEMPOTENCY_CODE = '''"""
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
'''

# ============================================================================
# MIGRATIONS/001_CORE_TABLES.SQL
# ============================================================================
MIGRATION_001_SQL = '''-- ============================================================================
-- NADAKKI AI SUITE - Migration 001: Core Tables
-- Multi-Tenant Google Ads Integration
-- ============================================================================
-- REUSABLE FOR: Multiple Financial Institutions
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- TENANT CREDENTIALS
-- ============================================================================

CREATE TABLE IF NOT EXISTS tenant_credentials (
    tenant_id VARCHAR(100) PRIMARY KEY,
    encrypted_data TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE tenant_credentials IS 'Encrypted OAuth credentials per tenant';
COMMENT ON COLUMN tenant_credentials.tenant_id IS 'Unique identifier for financial institution';
COMMENT ON COLUMN tenant_credentials.encrypted_data IS 'Fernet/KMS encrypted credentials JSON';

CREATE INDEX IF NOT EXISTS idx_tenant_creds_updated 
    ON tenant_credentials(updated_at);

-- ============================================================================
-- CREDENTIAL ACCESS LOG (Compliance/Audit)
-- ============================================================================

CREATE TABLE IF NOT EXISTS credential_access_log (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

COMMENT ON TABLE credential_access_log IS 'Audit trail for credential access';

CREATE INDEX IF NOT EXISTS idx_cred_access_tenant 
    ON credential_access_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cred_access_timestamp 
    ON credential_access_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_cred_access_action 
    ON credential_access_log(action);

-- ============================================================================
-- IDEMPOTENCY KEYS
-- ============================================================================

CREATE TABLE IF NOT EXISTS idempotency_keys (
    key VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    operation_name VARCHAR(100) NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

COMMENT ON TABLE idempotency_keys IS 'Prevent duplicate operation execution';

CREATE INDEX IF NOT EXISTS idx_idempotency_tenant 
    ON idempotency_keys(tenant_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_expires 
    ON idempotency_keys(expires_at);
CREATE INDEX IF NOT EXISTS idx_idempotency_operation 
    ON idempotency_keys(operation_name);

-- ============================================================================
-- TENANTS CONFIGURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'basic',
    status VARCHAR(50) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    google_ads_customer_id VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE tenants IS 'Financial institution configuration';
COMMENT ON COLUMN tenants.plan IS 'Subscription plan: basic, pro, enterprise';
COMMENT ON COLUMN tenants.status IS 'active, suspended, pending, archived';

CREATE INDEX IF NOT EXISTS idx_tenants_status 
    ON tenants(status);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
DROP TRIGGER IF EXISTS update_tenant_credentials_updated_at ON tenant_credentials;
CREATE TRIGGER update_tenant_credentials_updated_at
    BEFORE UPDATE ON tenant_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tenants_updated_at ON tenants;
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert demo tenant for testing
INSERT INTO tenants (tenant_id, name, display_name, plan, status) 
VALUES ('demo_tenant', 'Demo Financial Institution', 'Demo FI', 'basic', 'active')
ON CONFLICT (tenant_id) DO NOTHING;

-- ============================================================================
-- GRANTS (adjust for your database user)
-- ============================================================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nadakki_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nadakki_app;
'''

# ============================================================================
# MAIN GENERATOR
# ============================================================================

def main():
    print("\n" + "=" * 80)
    print("  PHASE 1 GENERATOR: Core Infrastructure")
    print("=" * 80 + "\n")
    
    # Create core files
    create_file("core/security/tenant_vault.py", TENANT_VAULT_CODE)
    create_file("core/google_ads/client_factory.py", CLIENT_FACTORY_CODE)
    create_file("core/operations/registry.py", OPERATIONS_REGISTRY_CODE)
    create_file("core/reliability/idempotency.py", IDEMPOTENCY_CODE)
    create_file("migrations/001_core_tables.sql", MIGRATION_001_SQL)
    
    print("\n" + "-" * 80)
    print("  Phase 1 Complete! Files created:")
    print("  - core/security/tenant_vault.py")
    print("  - core/google_ads/client_factory.py")
    print("  - core/operations/registry.py")
    print("  - core/reliability/idempotency.py")
    print("  - migrations/001_core_tables.sql")
    print("-" * 80 + "\n")

if __name__ == "__main__":
    main()
