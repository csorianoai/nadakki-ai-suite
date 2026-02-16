# ===============================================================================
# NADAKKI AI Suite - OperationRegistry
# core/operations/registry.py
# Day 1 - Component 3 of 4
# ===============================================================================

"""
Central registry of all Google Ads operations.

Each operation has:
- Versioned name (e.g., "get_campaign_metrics@v1")
- Schema with required/optional fields and validators
- Async handler function
- Optional compensation operation for rollback

Operations are registered at startup and looked up by name during execution.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime
from enum import Enum
import uuid
import time
import logging

logger = logging.getLogger("nadakki.operations.registry")


# -----------------------------------------------------------------------------
# Error Codes
# -----------------------------------------------------------------------------

class ErrorCode(Enum):
    """Normalized error codes for all operations."""
    SUCCESS = "SUCCESS"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    AUTH_FAILED = "AUTH_FAILED"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    NETWORK_ERROR = "NETWORK_ERROR"
    API_ERROR = "API_ERROR"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    UNKNOWN = "UNKNOWN"


# -----------------------------------------------------------------------------
# Data Transfer Objects
# -----------------------------------------------------------------------------

@dataclass
class OperationContext:
    """Execution context propagated through the pipeline."""
    tenant_id: str
    user_id: Optional[str] = None
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dry_run: bool = False
    source: str = "api"  # api | scheduler | agent | workflow


@dataclass
class OperationRequest:
    """Standardized operation request."""
    operation_id: str
    operation_name: str  # Format: "name@version" e.g. "update_campaign_budget@v1"
    tenant_id: str
    idempotency_key: str
    payload: Dict[str, Any]
    context: OperationContext
    created_at: datetime = field(default_factory=datetime.utcnow)
    
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
    """Standardized operation result."""
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
    
    def to_dict(self) -> dict:
        """Serialize to dict for storage/transport."""
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
        }


# -----------------------------------------------------------------------------
# Operation Schema & Validation
# -----------------------------------------------------------------------------

@dataclass
class OperationSchema:
    """
    Schema definition for operation payload validation.
    
    Each operation defines:
    - required_fields: Must be present in payload
    - optional_fields: May be present
    - validators: Dict of field_name -> validation function
    - compensation_operation: Name of operation to undo this one
    """
    name: str
    version: str
    required_fields: List[str]
    optional_fields: List[str] = field(default_factory=list)
    validators: Dict[str, Callable] = field(default_factory=dict)
    compensation_operation: Optional[str] = None
    
    def validate(self, payload: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate payload against schema.
        Returns (True, None) on success or (False, error_message) on failure.
        """
        # Check required fields
        for field_name in self.required_fields:
            if field_name not in payload:
                return False, f"Missing required field: {field_name}"
        
        # Check for unknown fields
        known = set(self.required_fields + self.optional_fields)
        unknown = set(payload.keys()) - known
        if unknown:
            logger.warning(f"Unknown fields in payload: {unknown}")
            # Don't fail - just warn. Extensibility.
        
        # Run validators
        for field_name, validator_fn in self.validators.items():
            if field_name in payload:
                try:
                    if not validator_fn(payload[field_name]):
                        return False, f"Validation failed for field: {field_name}"
                except Exception as e:
                    return False, f"Validator error for {field_name}: {str(e)}"
        
        return True, None
    
    @property
    def full_name(self) -> str:
        return f"{self.name}@{self.version}"


# -----------------------------------------------------------------------------
# Operation Registry
# -----------------------------------------------------------------------------

class OperationRegistry:
    """
    Central registry for all Google Ads operations.
    
    Operations are registered at startup and looked up by name.
    Each operation has a schema, handler, and optional compensation.
    
    Usage:
        registry = get_operation_registry()
        
        # Register custom operation
        registry.register(
            name="pause_campaign",
            version="v1",
            handler=my_handler,
            schema=my_schema,
        )
        
        # Validate + execute
        valid, error = registry.validate(request)
        result = await registry.execute(request, client, customer_id)
    """
    
    def __init__(self):
        self._operations: Dict[str, dict] = {}
        self._register_builtin_operations()
        logger.info(
            f"OperationRegistry initialized with "
            f"{len(self._operations)} operations"
        )
    
    def register(
        self,
        name: str,
        version: str,
        handler: Callable,
        schema: OperationSchema,
        description: str = "",
    ):
        """Register an operation."""
        key = f"{name}@{version}"
        
        if key in self._operations:
            logger.warning(f"Overwriting existing operation: {key}")
        
        self._operations[key] = {
            "name": name,
            "version": version,
            "handler": handler,
            "schema": schema,
            "description": description,
        }
        
        logger.info(f"Registered operation: {key}")
    
    def get(self, operation_name: str) -> Optional[dict]:
        """Get registered operation by name@version."""
        return self._operations.get(operation_name)
    
    def list_operations(self) -> List[dict]:
        """List all registered operations."""
        return [
            {
                "name": op["name"],
                "version": op["version"],
                "full_name": f"{op['name']}@{op['version']}",
                "description": op["description"],
                "required_fields": op["schema"].required_fields,
                "optional_fields": op["schema"].optional_fields,
            }
            for op in self._operations.values()
        ]
    
    def validate(self, request: OperationRequest) -> Tuple[bool, Optional[str]]:
        """Validate a request against its operation schema."""
        op = self.get(request.operation_name)
        if not op:
            return False, f"Unknown operation: {request.operation_name}"
        return op["schema"].validate(request.payload)
    
    async def execute(
        self,
        request: OperationRequest,
        client,
        customer_id: str,
    ) -> OperationResult:
        """Execute an operation through its registered handler."""
        start = time.time()
        
        op = self.get(request.operation_name)
        if not op:
            return OperationResult(
                success=False,
                operation_id=request.operation_id,
                operation_name=request.operation_name,
                error_code=ErrorCode.INVALID_PAYLOAD,
                error_message=f"Unknown operation: {request.operation_name}",
            )
        
        # Validate
        valid, error = op["schema"].validate(request.payload)
        if not valid:
            return OperationResult(
                success=False,
                operation_id=request.operation_id,
                operation_name=request.operation_name,
                error_code=ErrorCode.INVALID_PAYLOAD,
                error_message=error,
            )
        
        # Execute handler
        try:
            result = await op["handler"](
                client, customer_id, request.payload, request.context
            )
            result.operation_id = request.operation_id
            result.operation_name = request.operation_name
            result.execution_time_ms = int((time.time() - start) * 1000)
            return result
            
        except Exception as e:
            return OperationResult(
                success=False,
                operation_id=request.operation_id,
                operation_name=request.operation_name,
                error_code=self._classify_error(e),
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000),
            )
    
    # ---------------------------------------------------------------------
    # Error Classification
    # ---------------------------------------------------------------------
    
    @staticmethod
    def _classify_error(error: Exception) -> ErrorCode:
        """Classify an exception into a normalized error code."""
        error_str = str(error).lower()
        
        if "quota" in error_str or "rate" in error_str:
            return ErrorCode.QUOTA_EXCEEDED
        elif "auth" in error_str or "permission" in error_str or "token" in error_str:
            return ErrorCode.AUTH_FAILED
        elif "not found" in error_str or "does not exist" in error_str:
            return ErrorCode.RESOURCE_NOT_FOUND
        elif "policy" in error_str or "violation" in error_str:
            return ErrorCode.POLICY_VIOLATION
        elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
            return ErrorCode.NETWORK_ERROR
        else:
            return ErrorCode.API_ERROR
    
    # ---------------------------------------------------------------------
    # Built-in Operations
    # ---------------------------------------------------------------------
    
    def _register_builtin_operations(self):
        """Register the 2 core operations for Day 1."""
        self._register_get_campaign_metrics()
        self._register_update_campaign_budget()
    
    def _register_get_campaign_metrics(self):
        """
        GET CAMPAIGN METRICS @v1
        
        Read-only operation that fetches campaign performance data.
        No side effects, no compensation needed.
        """
        
        async def handler(client, customer_id, payload, ctx):
            # Check for mock client
            if hasattr(client, 'tenant_id'):  # MockGoogleAdsClient
                return OperationResult(
                    success=True,
                    operation_id="",
                    operation_name="get_campaign_metrics@v1",
                    data={
                        "campaigns": [
                            {
                                "id": "mock_campaign_001",
                                "name": "Mock Campaign - Search",
                                "status": "ENABLED",
                                "budget_micros": 50000000,
                                "impressions": 12500,
                                "clicks": 340,
                                "cost_micros": 28500000,
                                "conversions": 18.5,
                            }
                        ],
                        "count": 1,
                        "mock": True,
                    }
                )
            
            ga_service = client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign_budget.amount_micros,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign
                WHERE campaign.status != 'REMOVED'
            """
            
            # Filter by campaign IDs if provided
            campaign_ids = payload.get("campaign_ids")
            if campaign_ids:
                ids_str = ",".join(str(cid) for cid in campaign_ids)
                query += f" AND campaign.id IN ({ids_str})"
            
            # Date range filter
            date_range = payload.get("date_range")
            if date_range:
                query += (
                    f" AND segments.date >= '{date_range['start']}'"
                    f" AND segments.date <= '{date_range['end']}'"
                )
            
            response = ga_service.search_stream(
                customer_id=str(customer_id), query=query
            )
            
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
                    })
            
            return OperationResult(
                success=True,
                operation_id="",
                operation_name="get_campaign_metrics@v1",
                data={"campaigns": campaigns, "count": len(campaigns)},
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
                    "campaign_ids": lambda x: isinstance(x, list),
                    "date_range": lambda x: (
                        isinstance(x, dict) 
                        and "start" in x 
                        and "end" in x
                    ),
                },
            ),
            description="Get campaign performance metrics (read-only)",
        )
    
    def _register_update_campaign_budget(self):
        """
        UPDATE CAMPAIGN BUDGET @v1
        
        Write operation that modifies campaign budget.
        Compensable: stores previous budget for rollback.
        """
        
        async def handler(client, customer_id, payload, ctx):
            budget_id = payload["budget_id"]
            new_budget = payload["new_budget"]
            previous_budget = payload.get("previous_budget")
            
            # Dry run mode
            if ctx.dry_run:
                return OperationResult(
                    success=True,
                    operation_id="",
                    operation_name="update_campaign_budget@v1",
                    data={
                        "dry_run": True,
                        "would_update": {
                            "budget_id": budget_id,
                            "new_amount_micros": int(new_budget * 1_000_000),
                            "previous_budget": previous_budget,
                        },
                    },
                )
            
            # Mock client
            if hasattr(client, 'tenant_id'):
                return OperationResult(
                    success=True,
                    operation_id="",
                    operation_name="update_campaign_budget@v1",
                    resource_name=f"customers/{customer_id}/campaignBudgets/{budget_id}",
                    data={
                        "budget_id": budget_id,
                        "new_budget": new_budget,
                        "previous_budget": previous_budget,
                        "mock": True,
                    },
                    compensable=True,
                    compensation_data={
                        "operation": "update_campaign_budget@v1",
                        "payload": {
                            "budget_id": budget_id,
                            "new_budget": previous_budget or new_budget,
                        },
                    },
                )
            
            # Real execution
            budget_service = client.get_service("CampaignBudgetService")
            
            operation = client.get_type("CampaignBudgetOperation")
            budget = operation.update
            budget.resource_name = (
                f"customers/{customer_id}/campaignBudgets/{budget_id}"
            )
            budget.amount_micros = int(new_budget * 1_000_000)
            
            client.copy_from(
                operation.update_mask,
                client.get_type("FieldMask")(paths=["amount_micros"]),
            )
            
            response = budget_service.mutate_campaign_budgets(
                customer_id=str(customer_id),
                operations=[operation],
            )
            
            return OperationResult(
                success=True,
                operation_id="",
                operation_name="update_campaign_budget@v1",
                resource_name=response.results[0].resource_name,
                data={
                    "budget_id": budget_id,
                    "new_budget": new_budget,
                    "previous_budget": previous_budget,
                },
                compensable=True,
                compensation_data={
                    "operation": "update_campaign_budget@v1",
                    "payload": {
                        "budget_id": budget_id,
                        "new_budget": previous_budget or new_budget,
                    },
                },
            )
        
        self.register(
            name="update_campaign_budget",
            version="v1",
            handler=handler,
            schema=OperationSchema(
                name="update_campaign_budget",
                version="v1",
                required_fields=["budget_id", "new_budget"],
                optional_fields=["previous_budget"],
                validators={
                    "budget_id": lambda x: isinstance(x, str) and len(x) > 0,
                    "new_budget": lambda x: isinstance(x, (int, float)) and x > 0,
                    "previous_budget": lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
                },
                compensation_operation="update_campaign_budget@v1",
            ),
            description="Update campaign daily budget (compensable)",
        )


# -----------------------------------------------------------------------------
# Singleton
# -----------------------------------------------------------------------------

_registry: Optional[OperationRegistry] = None


def get_operation_registry() -> OperationRegistry:
    """Get or create the singleton OperationRegistry."""
    global _registry
    if _registry is None:
        _registry = OperationRegistry()
    return _registry

