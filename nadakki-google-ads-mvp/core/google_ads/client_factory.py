"""
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
