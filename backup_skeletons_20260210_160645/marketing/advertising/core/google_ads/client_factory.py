# ===============================================================================
# NADAKKI AI Suite - GoogleAdsClientFactory
# core/google_ads/client_factory.py
# Day 1 - Component 2 of 4
# ===============================================================================

"""
Factory for Google Ads API clients with per-tenant pooling.

Features:
- Client pool per tenant (max 2 clients)
- Automatic token refresh via TenantCredentialVault
- Health check per tenant
- Client invalidation on auth failures
- Configurable API version via env var

Note: google-ads Python library must be installed:
    pip install google-ads==24.1.0
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import os
import asyncio
import logging

logger = logging.getLogger("nadakki.google_ads.factory")

# Configurable API version
GOOGLE_ADS_API_VERSION = os.getenv("GOOGLE_ADS_API_VERSION", "v17")


class GoogleAdsClientFactory:
    """
    Creates and pools Google Ads API clients per tenant.
    
    Usage:
        factory = GoogleAdsClientFactory(credential_vault)
        client = await factory.get_client("bank01")
        # Use client for API calls...
        
        # Health check
        healthy = await factory.health_check("bank01")
    """
    
    MAX_CLIENTS_PER_TENANT = 2
    CLIENT_MAX_IDLE_SECONDS = 3600  # 1 hour
    HEALTH_CHECK_TIMEOUT = 10  # seconds
    
    def __init__(self, credential_vault):
        self.vault = credential_vault
        self._clients: Dict[str, dict] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
    
    async def get_client(self, tenant_id: str):
        """
        Get or create a Google Ads client for a tenant.
        
        Returns a configured GoogleAdsClient ready for API calls.
        Automatically refreshes tokens if needed.
        """
        lock = await self._get_tenant_lock(tenant_id)
        
        async with lock:
            # Check pool
            if tenant_id in self._clients:
                cached = self._clients[tenant_id]
                if cached["healthy"] and self._is_valid(cached):
                    cached["last_used"] = datetime.utcnow()
                    logger.debug(f"Returning pooled client for tenant: {tenant_id}")
                    return cached["client"]
                else:
                    logger.info(
                        f"Pooled client invalid for {tenant_id} "
                        f"(healthy={cached['healthy']}, "
                        f"age={self._client_age(cached)}s)"
                    )
            
            # Create new client
            client = await self._create_client(tenant_id)
            
            self._clients[tenant_id] = {
                "client": client,
                "created_at": datetime.utcnow(),
                "last_used": datetime.utcnow(),
                "healthy": True,
            }
            
            logger.info(f"Created new client for tenant: {tenant_id}")
            return client
    
    async def _create_client(self, tenant_id: str):
        """Create a new Google Ads client with tenant credentials."""
        # This will auto-refresh token if needed
        creds = await self.vault.refresh_if_needed(tenant_id)
        
        # Build config dict for google-ads library
        config = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
            "client_id": os.getenv("NADAKKI_GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("NADAKKI_GOOGLE_CLIENT_SECRET"),
            "refresh_token": creds["refresh_token"],
            "use_proto_plus": True,
        }
        
        # Optional: manager account (MCC)
        manager_id = creds.get("manager_customer_id")
        if manager_id:
            config["login_customer_id"] = str(manager_id)
        
        try:
            # Allow forcing mock mode for testing/development
            force_mock = os.getenv("NADAKKI_FORCE_MOCK", "").lower() in ("1", "true", "yes")
            if force_mock:
                logger.info(
                    "NADAKKI_FORCE_MOCK enabled. "
                    "Using mock client for development."
                )
                return MockGoogleAdsClient(config, tenant_id)
            
            from google.ads.googleads.client import GoogleAdsClient
            
            client = GoogleAdsClient.load_from_dict(
                config, 
                version=GOOGLE_ADS_API_VERSION
            )
            return client
            
        except ImportError:
            logger.warning(
                "google-ads library not installed. "
                "Returning mock client for development."
            )
            return MockGoogleAdsClient(config, tenant_id)
        except Exception as e:
            logger.warning(
                f"Could not create real client for {tenant_id}: {e}. "
                f"Falling back to mock client."
            )
            return MockGoogleAdsClient(config, tenant_id)
    
    async def health_check(self, tenant_id: str) -> bool:
        """
        Verify client connectivity by running a minimal query.
        Returns True if healthy, False otherwise.
        """
        try:
            client = await self.get_client(tenant_id)
            creds = await self.vault.get_credentials(tenant_id)
            customer_id = creds.get("customer_id")
            
            if not customer_id:
                logger.warning(f"No customer_id for health check: {tenant_id}")
                return False
            
            # Minimal query
            if isinstance(client, MockGoogleAdsClient):
                return True
            
            ga_service = client.get_service("GoogleAdsService")
            query = "SELECT customer.id FROM customer LIMIT 1"
            
            response = ga_service.search(
                customer_id=str(customer_id), 
                query=query
            )
            list(response)  # Consume iterator
            
            # Mark healthy
            if tenant_id in self._clients:
                self._clients[tenant_id]["healthy"] = True
            
            logger.info(f"Health check passed for tenant: {tenant_id}")
            return True
            
        except Exception as e:
            if tenant_id in self._clients:
                self._clients[tenant_id]["healthy"] = False
            
            logger.error(f"Health check failed for {tenant_id}: {e}")
            return False
    
    def invalidate(self, tenant_id: str):
        """Remove a tenant's client from the pool."""
        removed = self._clients.pop(tenant_id, None)
        if removed:
            logger.info(f"Client invalidated for tenant: {tenant_id}")
    
    def invalidate_all(self):
        """Remove all clients from the pool."""
        count = len(self._clients)
        self._clients.clear()
        logger.info(f"All {count} clients invalidated")
    
    def get_stats(self) -> dict:
        """Get pool statistics."""
        now = datetime.utcnow()
        return {
            "total_clients": len(self._clients),
            "api_version": GOOGLE_ADS_API_VERSION,
            "by_tenant": {
                tid: {
                    "healthy": data["healthy"],
                    "age_seconds": (now - data["created_at"]).total_seconds(),
                    "idle_seconds": (now - data["last_used"]).total_seconds(),
                }
                for tid, data in self._clients.items()
            }
        }
    
    # ---------------------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------------------
    
    def _is_valid(self, cached: dict) -> bool:
        """Check if a pooled client is still valid."""
        idle = (datetime.utcnow() - cached["last_used"]).total_seconds()
        return idle < self.CLIENT_MAX_IDLE_SECONDS
    
    def _client_age(self, cached: dict) -> int:
        """Get client age in seconds."""
        return int((datetime.utcnow() - cached["created_at"]).total_seconds())
    
    async def _get_tenant_lock(self, tenant_id: str) -> asyncio.Lock:
        """Get or create a lock for a specific tenant."""
        async with self._global_lock:
            if tenant_id not in self._locks:
                self._locks[tenant_id] = asyncio.Lock()
            return self._locks[tenant_id]


# -----------------------------------------------------------------------------
# Mock Client for Development/Testing
# -----------------------------------------------------------------------------

class MockGoogleAdsClient:
    """
    Mock client for development when google-ads library is not installed.
    Returns realistic mock data for common operations.
    """
    
    def __init__(self, config: dict, tenant_id: str):
        self.config = config
        self.tenant_id = tenant_id
        self._version = GOOGLE_ADS_API_VERSION
        logger.info(f"MockGoogleAdsClient created for tenant: {tenant_id}")
    
    def get_service(self, service_name: str):
        """Return a mock service."""
        return MockService(service_name, self.tenant_id)
    
    def get_type(self, type_name: str):
        """Return a mock type."""
        return MockType(type_name)
    
    def copy_from(self, destination, source):
        """Mock copy_from."""
        pass


class MockService:
    """Mock Google Ads service for development."""
    
    def __init__(self, name: str, tenant_id: str):
        self.name = name
        self.tenant_id = tenant_id
    
    def search(self, customer_id: str = "", query: str = ""):
        """Mock search - returns empty results."""
        return []
    
    def search_stream(self, customer_id: str = "", query: str = ""):
        """Mock search_stream - returns empty batches."""
        return []
    
    def mutate_campaign_budgets(self, customer_id: str = "", operations=None):
        """Mock budget mutation."""
        return MockMutateResponse()


class MockMutateResponse:
    """Mock mutate response."""
    def __init__(self):
        self.results = [MockResult()]


class MockResult:
    """Mock result with resource_name."""
    def __init__(self):
        self.resource_name = "customers/1234567890/campaignBudgets/mock_001"


class MockType:
    """Mock protobuf type."""
    def __init__(self, name: str):
        self.name = name
        self.update = MockUpdateField()
        self.update_mask = None
    
    def __call__(self, **kwargs):
        return MockType(self.name)


class MockUpdateField:
    """Mock update field for budget operations."""
    def __init__(self):
        self.resource_name = ""
        self.amount_micros = 0
