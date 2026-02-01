"""
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
