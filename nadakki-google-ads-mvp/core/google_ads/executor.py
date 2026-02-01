"""
NADAKKI AI Suite - Google Ads Executor
Resilient Execution with Circuit Breaker
"""

from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime, timedelta
from typing import Optional
import asyncio
import time
import logging

from core.operations.registry import OperationRequest, OperationResult, ErrorCode, get_operation_registry

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker for resilience."""
    
    CLOSED, OPEN, HALF_OPEN = "CLOSED", "OPEN", "HALF_OPEN"
    
    def __init__(self, name: str = "default", failure_threshold: int = 5, recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        if self.state == self.CLOSED:
            return True
        if self.state == self.OPEN:
            if self.last_failure_time and (datetime.utcnow() - self.last_failure_time).total_seconds() >= self.recovery_timeout:
                self.state = self.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        return self.half_open_calls < 3
    
    def record_success(self):
        if self.state == self.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= 3:
                self.state = self.CLOSED
                self.failure_count = 0
        elif self.state == self.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.state == self.HALF_OPEN or (self.state == self.CLOSED and self.failure_count >= self.failure_threshold):
            self.state = self.OPEN
            logger.warning(f"Circuit breaker '{self.name}' OPENED")


class RetryManager:
    """Retry with exponential backoff."""
    
    NON_RETRYABLE = {ErrorCode.POLICY_VIOLATION, ErrorCode.INVALID_PAYLOAD, ErrorCode.AUTH_FAILED, ErrorCode.RESOURCE_NOT_FOUND}
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def should_retry(self, attempt: int, error_code: ErrorCode) -> bool:
        return attempt < self.max_retries and error_code not in self.NON_RETRYABLE
    
    async def wait(self, attempt: int):
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        await asyncio.sleep(delay)


class GoogleAdsExecutor:
    """Executor with circuit breaker and retry."""
    
    def __init__(self, client_factory, telemetry):
        self.client_factory = client_factory
        self.telemetry = telemetry
        self.registry = get_operation_registry()
        self.circuit_breaker = CircuitBreaker("google_ads")
        self.retry_manager = RetryManager()
    
    async def execute(self, request: OperationRequest, customer_id: str) -> OperationResult:
        if not self.circuit_breaker.can_execute():
            self.telemetry.log_operation(request, None, "circuit_open")
            return OperationResult(success=False, operation_id=request.operation_id, operation_name=request.operation_name,
                                   error_code=ErrorCode.API_ERROR, error_message="Circuit breaker is open")
        
        try:
            client = await self.client_factory.get_client(request.tenant_id)
        except Exception as e:
            return OperationResult(success=False, operation_id=request.operation_id, operation_name=request.operation_name,
                                   error_code=ErrorCode.AUTH_FAILED, error_message=str(e))
        
        attempt = 0
        while True:
            start_time = time.time()
            try:
                result = await self.registry.execute(request, client, customer_id)
                
                if result.success:
                    self.circuit_breaker.record_success()
                    self.telemetry.log_operation(request, result, "success")
                    return result
                
                if self.retry_manager.should_retry(attempt, result.error_code):
                    attempt += 1
                    await self.retry_manager.wait(attempt - 1)
                    self.telemetry.log_operation(request, result, f"retry_{attempt}")
                    continue
                
                self.circuit_breaker.record_failure()
                self.telemetry.log_operation(request, result, "failed")
                return result
                
            except GoogleAdsException as e:
                error_code = ErrorCode.QUOTA_EXCEEDED if "quota" in str(e).lower() else ErrorCode.API_ERROR
                
                if self.retry_manager.should_retry(attempt, error_code):
                    attempt += 1
                    await self.retry_manager.wait(attempt - 1)
                    continue
                
                self.circuit_breaker.record_failure()
                return OperationResult(success=False, operation_id=request.operation_id, operation_name=request.operation_name,
                                       error_code=error_code, error_message=str(e), execution_time_ms=int((time.time() - start_time) * 1000))
            
            except Exception as e:
                self.circuit_breaker.record_failure()
                return OperationResult(success=False, operation_id=request.operation_id, operation_name=request.operation_name,
                                       error_code=ErrorCode.UNKNOWN, error_message=str(e))
