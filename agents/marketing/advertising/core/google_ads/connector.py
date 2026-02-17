# ===============================================================================
# NADAKKI AI Suite - GoogleAdsConnector
# core/google_ads/connector.py
# Day 2 - Component 5 of 5
# ===============================================================================

"""
Facade that orchestrates the complete operation pipeline.

Pipeline flow:
    +--------------------------------------------------------------+
    |  PREFLIGHT                                                    |
    |  1. Validate payload (OperationRegistry)                     |
    |  2. Check idempotency (IdempotencyStore)                     |
    |  3. Evaluate policies (PolicyEngine)                         |
    |  4. Create saga (SagaJournal)                                |
    |--------------------------------------------------------------|
    |  EXECUTE                                                      |
    |  5. Get client (GoogleAdsClientFactory)                      |
    |  6. Execute with retry/circuit breaker (GoogleAdsExecutor)   |
    |  7. Record saga step result                                  |
    |--------------------------------------------------------------|
    |  POSTFLIGHT                                                   |
    |  8. Store idempotency result                                 |
    |  9. Record telemetry                                         |
    |  10. Complete/fail saga                                      |
    +--------------------------------------------------------------+

This is the ONLY entry point agents should use to interact with Google Ads.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import time
import uuid
import logging

from ..operations.registry import (
    OperationRegistry, OperationRequest, OperationContext,
    OperationResult, ErrorCode,
)
from ..reliability.idempotency import IdempotencyStore
from ..policies.engine import PolicyEngine, PolicyDecision
from .executor import (
    GoogleAdsExecutor, CircuitBreakerOpenError, MaxRetriesExceededError,
)
from ..saga.journal import SagaJournal, SagaStatus
from ..observability.telemetry import TelemetrySidecar

logger = logging.getLogger("nadakki.google_ads.connector")


# -----------------------------------------------------------------------------
# Connector Result
# -----------------------------------------------------------------------------

@dataclass
class ConnectorResult:
    """Complete result from the connector pipeline."""
    success: bool
    operation_id: str
    operation_name: str
    tenant_id: str
    trace_id: str
    saga_id: str = ""
    
    # Pipeline stages
    idempotency_hit: bool = False
    policy_decision: str = ""
    policy_reason: str = ""
    
    # Execution result
    data: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0
    
    # Saga
    compensable: bool = False
    requires_approval: bool = False
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "operation_id": self.operation_id,
            "operation_name": self.operation_name,
            "tenant_id": self.tenant_id,
            "trace_id": self.trace_id,
            "saga_id": self.saga_id,
            "idempotency_hit": self.idempotency_hit,
            "policy_decision": self.policy_decision,
            "policy_reason": self.policy_reason,
            "data": self.data,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "compensable": self.compensable,
            "requires_approval": self.requires_approval,
        }


# -----------------------------------------------------------------------------
# Connector
# -----------------------------------------------------------------------------

class GoogleAdsConnector:
    """
    Central facade for all Google Ads operations.
    
    Agents and API endpoints call the connector, which handles:
    - Validation, idempotency, policies, execution, saga, telemetry
    
    Usage:
        connector = GoogleAdsConnector(
            registry=registry,
            idempotency=idempotency_store,
            policy_engine=policy_engine,
            executor=executor,
            client_factory=client_factory,
            credential_vault=vault,
            saga_journal=saga_journal,
            telemetry=telemetry,
        )
        
        result = await connector.execute(
            tenant_id="bank01",
            operation_name="update_campaign_budget@v1",
            payload={"budget_id": "b1", "new_budget": 75.0, "previous_budget": 50.0},
        )
    """
    
    def __init__(
        self,
        registry: OperationRegistry,
        idempotency: IdempotencyStore,
        policy_engine: PolicyEngine,
        executor: GoogleAdsExecutor,
        client_factory,
        credential_vault,
        saga_journal: SagaJournal,
        telemetry: TelemetrySidecar,
    ):
        self.registry = registry
        self.idempotency = idempotency
        self.policy_engine = policy_engine
        self.executor = executor
        self.client_factory = client_factory
        self.vault = credential_vault
        self.saga = saga_journal
        self.telemetry = telemetry
        
        logger.info("GoogleAdsConnector initialized (full pipeline)")
    
    async def execute(
        self,
        tenant_id: str,
        operation_name: str,
        payload: dict,
        dry_run: bool = False,
        source: str = "api",
        user_id: str = None,
        trace_id: str = None,
    ) -> ConnectorResult:
        """
        Execute a Google Ads operation through the full pipeline.
        
        This is the main entry point. All operations flow through here.
        """
        start_time = time.time()
        operation_id = str(uuid.uuid4())
        trace_id = trace_id or str(uuid.uuid4())
        
        context = OperationContext(
            tenant_id=tenant_id,
            user_id=user_id,
            trace_id=trace_id,
            dry_run=dry_run,
            source=source,
        )
        
        logger.info(
            f"[{trace_id[:8]}] Pipeline start: {operation_name} "
            f"for {tenant_id} (source: {source})"
        )
        
        # -------------------------------------------------------------
        # PREFLIGHT
        # -------------------------------------------------------------
        
        # 1. Validate operation exists and payload is valid
        op = self.registry.get(operation_name)
        if not op:
            return self._error_result(
                operation_id, operation_name, tenant_id, trace_id,
                ErrorCode.INVALID_PAYLOAD,
                f"Unknown operation: {operation_name}",
                start_time,
            )
        
        idem_key = IdempotencyStore.generate_key(tenant_id, operation_name, payload)
        
        op_request = OperationRequest(
            operation_id=operation_id,
            operation_name=operation_name,
            tenant_id=tenant_id,
            idempotency_key=idem_key,
            payload=payload,
            context=context,
        )
        
        valid, error = self.registry.validate(op_request)
        if not valid:
            return self._error_result(
                operation_id, operation_name, tenant_id, trace_id,
                ErrorCode.INVALID_PAYLOAD, error, start_time,
            )
        
        # 2. Check idempotency
        cached = await self.idempotency.check(idem_key, tenant_id)
        if cached:
            self.telemetry.record_idempotency_hit(tenant_id, operation_name, trace_id)
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(
                f"[{trace_id[:8]}] Idempotency hit for {operation_name} ({elapsed:.0f}ms)"
            )
            
            return ConnectorResult(
                success=cached.get("success", True),
                operation_id=cached.get("operation_id", operation_id),
                operation_name=operation_name,
                tenant_id=tenant_id,
                trace_id=trace_id,
                idempotency_hit=True,
                data=cached.get("data", {}),
                execution_time_ms=elapsed,
            )
        
        # 3. Evaluate policies
        policy_result = self.policy_engine.validate_operation(
            tenant_id, operation_name, payload
        )
        
        self.telemetry.record_policy_decision(
            tenant_id, policy_result.rule_name,
            policy_result.decision.value, operation_name, trace_id,
        )
        
        if policy_result.decision == PolicyDecision.DENY:
            elapsed = (time.time() - start_time) * 1000
            logger.warning(
                f"[{trace_id[:8]}] Policy DENIED: {policy_result.reason}"
            )
            
            return ConnectorResult(
                success=False,
                operation_id=operation_id,
                operation_name=operation_name,
                tenant_id=tenant_id,
                trace_id=trace_id,
                policy_decision="deny",
                policy_reason=policy_result.reason,
                error_code=ErrorCode.POLICY_VIOLATION.value,
                error_message=policy_result.reason,
                execution_time_ms=elapsed,
            )
        
        if policy_result.decision == PolicyDecision.REQUIRE_APPROVAL:
            # Create saga in PENDING_APPROVAL state
            saga = await self.saga.create_saga(
                tenant_id, operation_name, trace_id,
                metadata={"payload": payload, "policy_reason": policy_result.reason},
            )
            await self.saga.set_pending_approval(saga.saga_id)
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(
                f"[{trace_id[:8]}] Requires approval: {policy_result.reason} "
                f"(saga: {saga.saga_id})"
            )
            
            return ConnectorResult(
                success=True,  # Not an error - just needs approval
                operation_id=operation_id,
                operation_name=operation_name,
                tenant_id=tenant_id,
                trace_id=trace_id,
                saga_id=saga.saga_id,
                policy_decision="require_approval",
                policy_reason=policy_result.reason,
                requires_approval=True,
                data={"approval_required": True, "saga_id": saga.saga_id},
                execution_time_ms=elapsed,
            )
        
        # 4. Create saga
        saga = await self.saga.create_saga(
            tenant_id, operation_name, trace_id,
            metadata={"source": source, "dry_run": dry_run},
        )
        
        step = await self.saga.add_step(
            saga.saga_id, operation_name, payload
        )
        
        # -------------------------------------------------------------
        # EXECUTE
        # -------------------------------------------------------------
        
        await self.saga.start_step(step.step_id)
        self.telemetry.active_operations.inc({"tenant_id": tenant_id})
        
        try:
            # Get credentials and client
            creds = await self.vault.get_credentials(tenant_id)
            if not creds:
                raise ValueError(f"No credentials for tenant: {tenant_id}")
            
            customer_id = creds.get("customer_id")
            if not customer_id:
                raise ValueError(f"No customer_id for tenant: {tenant_id}")
            
            client = await self.client_factory.get_client(tenant_id)
            
            # Execute with retry + circuit breaker
            async def _execute_op():
                return await self.registry.execute(op_request, client, customer_id)
            
            result: OperationResult = await self.executor.execute(
                tenant_id=tenant_id,
                operation=_execute_op,
                operation_name=operation_name,
            )
            
        except CircuitBreakerOpenError as e:
            await self._handle_execution_failure(
                saga, step, str(e), ErrorCode.API_ERROR,
                tenant_id, operation_name, trace_id, start_time,
            )
            
            return self._error_result(
                operation_id, operation_name, tenant_id, trace_id,
                ErrorCode.API_ERROR, str(e), start_time,
                saga_id=saga.saga_id,
            )
        
        except MaxRetriesExceededError as e:
            await self._handle_execution_failure(
                saga, step, str(e), ErrorCode.API_ERROR,
                tenant_id, operation_name, trace_id, start_time,
            )
            
            return self._error_result(
                operation_id, operation_name, tenant_id, trace_id,
                ErrorCode.API_ERROR, str(e), start_time,
                saga_id=saga.saga_id,
            )
        
        except Exception as e:
            error_code = self.registry._classify_error(e) if hasattr(self.registry, '_classify_error') else ErrorCode.UNKNOWN
            
            await self._handle_execution_failure(
                saga, step, str(e), error_code,
                tenant_id, operation_name, trace_id, start_time,
            )
            
            return self._error_result(
                operation_id, operation_name, tenant_id, trace_id,
                error_code, str(e), start_time,
                saga_id=saga.saga_id,
            )
        
        finally:
            self.telemetry.active_operations.dec({"tenant_id": tenant_id})
        
        # -------------------------------------------------------------
        # POSTFLIGHT
        # -------------------------------------------------------------
        
        elapsed = (time.time() - start_time) * 1000
        
        if result.success:
            # Complete step and saga
            await self.saga.complete_step(
                step.step_id,
                result=result.to_dict(),
                compensation_data=result.compensation_data,
            )
            await self.saga.complete_saga(saga.saga_id)
            
            # Store idempotency
            await self.idempotency.store(
                idem_key, tenant_id, operation_name,
                result.to_dict(),
            )
            
            logger.info(
                f"[{trace_id[:8]}] Pipeline SUCCESS: {operation_name} "
                f"({elapsed:.0f}ms, saga: {saga.saga_id})"
            )
        else:
            await self.saga.fail_step(step.step_id, result.error_message or "Unknown error")
            await self.saga.fail_saga(saga.saga_id, result.error_message or "Unknown error")
            
            logger.warning(
                f"[{trace_id[:8]}] Pipeline FAILED: {operation_name} "
                f"({elapsed:.0f}ms): {result.error_message}"
            )
        
        # Record telemetry
        self.telemetry.record_operation(
            tenant_id=tenant_id,
            operation_name=operation_name,
            success=result.success,
            duration_ms=elapsed,
            trace_id=trace_id,
            error_code=result.error_code.value if result.error_code else "",
            source=source,
        )
        
        self.telemetry.record_saga_event(
            tenant_id, saga.saga_id,
            "COMPLETED" if result.success else "FAILED",
            operation_name, trace_id,
        )
        
        return ConnectorResult(
            success=result.success,
            operation_id=result.operation_id,
            operation_name=operation_name,
            tenant_id=tenant_id,
            trace_id=trace_id,
            saga_id=saga.saga_id,
            policy_decision="allow",
            data=result.data,
            error_code=result.error_code.value if result.error_code else None,
            error_message=result.error_message,
            execution_time_ms=elapsed,
            compensable=result.compensable,
        )
    
    # ---------------------------------------------------------------------
    # Content Validation (for ad copy operations)
    # ---------------------------------------------------------------------
    
    def validate_content(self, tenant_id: str, content: dict) -> dict:
        """Validate ad copy content through policy engine."""
        result = self.policy_engine.validate_content(tenant_id, content)
        return result.to_dict()
    
    # ---------------------------------------------------------------------
    # Compensation (rollback)
    # ---------------------------------------------------------------------
    
    async def rollback(self, saga_id: str, reason: str = "") -> dict:
        """
        Execute compensation for a failed saga.
        
        Best-effort: attempts all compensations, records any failures.
        """
        compensations = await self.saga.request_compensation(saga_id, reason)
        
        results = []
        for comp in compensations:
            try:
                comp_result = await self.execute(
                    tenant_id=comp.get("tenant_id", ""),
                    operation_name=comp["operation"],
                    payload=comp["payload"],
                    source="compensation",
                )
                
                if comp_result.success:
                    await self.saga.mark_step_compensated(comp["step_id"])
                    results.append({"step_id": comp["step_id"], "status": "compensated"})
                else:
                    await self.saga.mark_step_compensation_failed(
                        comp["step_id"], comp_result.error_message or "Unknown"
                    )
                    results.append({"step_id": comp["step_id"], "status": "failed"})
                    
            except Exception as e:
                await self.saga.mark_step_compensation_failed(comp["step_id"], str(e))
                results.append({"step_id": comp["step_id"], "status": "failed", "error": str(e)})
        
        await self.saga.finalize_compensation(saga_id)
        
        return {
            "saga_id": saga_id,
            "total_steps": len(compensations),
            "results": results,
        }
    
    # ---------------------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------------------
    
    async def _handle_execution_failure(
        self, saga, step, error_msg, error_code,
        tenant_id, operation_name, trace_id, start_time,
    ):
        """Handle execution failure: update saga, record telemetry."""
        elapsed = (time.time() - start_time) * 1000
        
        await self.saga.fail_step(step.step_id, error_msg)
        await self.saga.fail_saga(saga.saga_id, error_msg)
        
        self.telemetry.record_operation(
            tenant_id=tenant_id,
            operation_name=operation_name,
            success=False,
            duration_ms=elapsed,
            trace_id=trace_id,
            error_code=error_code.value if hasattr(error_code, 'value') else str(error_code),
        )
    
    def _error_result(
        self, operation_id, operation_name, tenant_id, trace_id,
        error_code, error_message, start_time, saga_id="",
    ) -> ConnectorResult:
        """Build an error ConnectorResult."""
        elapsed = (time.time() - start_time) * 1000
        
        return ConnectorResult(
            success=False,
            operation_id=operation_id,
            operation_name=operation_name,
            tenant_id=tenant_id,
            trace_id=trace_id,
            saga_id=saga_id,
            error_code=error_code.value if hasattr(error_code, 'value') else str(error_code),
            error_message=error_message,
            execution_time_ms=elapsed,
        )
