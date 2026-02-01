"""
NADAKKI AI Suite - Google Ads Connector
Complete Pipeline: Preflight -> Execute -> Postflight
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import uuid
import hashlib
import json
import logging

from core.operations.registry import OperationRequest, OperationResult, OperationContext, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class ConnectorConfig:
    enable_dry_run: bool = False
    enable_idempotency: bool = True
    enable_policy_check: bool = True
    enable_saga_journal: bool = True


class GoogleAdsConnector:
    """Connector with complete pipeline."""
    
    def __init__(self, executor, policy_engine, idempotency_store, saga_journal, telemetry, credential_vault, config: ConnectorConfig = None):
        self.executor = executor
        self.policy_engine = policy_engine
        self.idempotency_store = idempotency_store
        self.saga_journal = saga_journal
        self.telemetry = telemetry
        self.credential_vault = credential_vault
        self.config = config or ConnectorConfig()
    
    async def execute(self, operation_name: str, payload: Dict[str, Any], tenant_id: str,
                      context: OperationContext = None, current_state: Dict[str, Any] = None) -> OperationResult:
        operation_id = str(uuid.uuid4())
        idempotency_key = hashlib.sha256(f"{tenant_id}:{operation_name}:{json.dumps(payload, sort_keys=True)}".encode()).hexdigest()[:32]
        context = context or OperationContext(tenant_id=tenant_id)
        
        request = OperationRequest(operation_id=operation_id, operation_name=operation_name, tenant_id=tenant_id,
                                   idempotency_key=idempotency_key, payload=payload, context=context)
        
        self.telemetry.increment_active_ops(tenant_id)
        
        try:
            # Idempotency check
            if self.config.enable_idempotency:
                cached = await self.idempotency_store.check(idempotency_key, tenant_id)
                if cached:
                    self.telemetry.log_event("idempotency_hit", tenant_id, context.trace_id)
                    return OperationResult(success=cached.get("success", True), operation_id=operation_id,
                                           operation_name=operation_name, data=cached.get("data", {}))
            
            # Policy check
            if self.config.enable_policy_check:
                policy_result = await self.policy_engine.validate(request, current_state)
                if not policy_result.approved:
                    result = OperationResult(success=False, operation_id=operation_id, operation_name=operation_name,
                                             error_code=ErrorCode.POLICY_VIOLATION,
                                             error_message="; ".join(v.message for v in policy_result.violations))
                    self.telemetry.log_operation(request, result, "policy_rejected")
                    return result
                
                if policy_result.requires_approval:
                    await self.saga_journal.record_pending_approval(request, policy_result.approval_reason)
                    return OperationResult(success=False, operation_id=operation_id, operation_name=operation_name,
                                           error_code=ErrorCode.POLICY_VIOLATION,
                                           error_message=f"Requires approval: {policy_result.approval_reason}",
                                           data={"pending_approval": True})
            
            # Get customer ID
            creds = await self.credential_vault.get_credentials(tenant_id)
            if not creds or "customer_id" not in creds:
                return OperationResult(success=False, operation_id=operation_id, operation_name=operation_name,
                                       error_code=ErrorCode.AUTH_FAILED, error_message="No customer_id for tenant")
            
            # Execute
            result = await self.executor.execute(request, creds["customer_id"])
            
            # Store idempotency
            if self.config.enable_idempotency:
                await self.idempotency_store.store(idempotency_key, tenant_id, operation_name,
                                                   {"success": result.success, "data": result.data})
            
            # Record saga
            if self.config.enable_saga_journal:
                await self.saga_journal.record_operation(request, result)
            
            return result
            
        except Exception as e:
            self.telemetry.log_error("connector_exception", tenant_id, context.trace_id, str(e))
            return OperationResult(success=False, operation_id=operation_id, operation_name=operation_name,
                                   error_code=ErrorCode.UNKNOWN, error_message=str(e))
        finally:
            self.telemetry.decrement_active_ops(tenant_id)
    
    async def get_metrics(self, tenant_id: str, campaign_ids: list = None) -> OperationResult:
        return await self.execute("get_campaign_metrics@v1", {"campaign_ids": campaign_ids}, tenant_id)
    
    async def update_budget(self, tenant_id: str, budget_id: str, new_budget: float, current_budget: float = None) -> OperationResult:
        return await self.execute("update_campaign_budget@v1",
                                  {"budget_id": budget_id, "new_budget": new_budget, "previous_budget": current_budget},
                                  tenant_id, current_state={"current_budget": current_budget} if current_budget else None)
