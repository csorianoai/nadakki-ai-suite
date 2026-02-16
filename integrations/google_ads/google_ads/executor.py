# ===============================================================================
# NADAKKI AI Suite - GoogleAdsExecutor
# core/google_ads/executor.py
# Day 2 - Component 1 of 5
# ===============================================================================

"""
Resilient executor for Google Ads operations.

Features:
- Circuit breaker: Opens after 5 consecutive failures, recovers after 60s
- Retry with exponential backoff: max 3 attempts, base 1s, max 30s
- Error classification: Retryable vs non-retryable vs auth failures
- Per-tenant circuit isolation (one tenant failing doesn't break others)

Error Classification:
- RETRYABLE: Rate limits, timeouts, server errors (500, 503)
- NON_RETRYABLE: Bad request, not found, policy violations
- AUTH_FAILURE: Token expired, invalid credentials > triggers refresh
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Callable, Dict, Any
import asyncio
import time
import logging

logger = logging.getLogger("nadakki.google_ads.executor")


# -----------------------------------------------------------------------------
# Error Classification
# -----------------------------------------------------------------------------

class ErrorCategory(Enum):
    """How to handle different error types."""
    RETRYABLE = "retryable"           # Retry with backoff
    NON_RETRYABLE = "non_retryable"   # Fail immediately
    AUTH_FAILURE = "auth_failure"      # Refresh token, then retry once


def classify_error(error: Exception) -> ErrorCategory:
    """
    Classify an exception to determine retry behavior.
    
    Google Ads API errors follow patterns:
    - QuotaError, RateLimitError > RETRYABLE
    - AuthenticationError, AuthorizationError > AUTH_FAILURE  
    - InvalidArgument, NotFound > NON_RETRYABLE
    - InternalError, Unavailable > RETRYABLE
    """
    error_str = str(error).lower()
    error_type = type(error).__name__.lower()
    
    # Auth failures
    auth_keywords = [
        "authentication", "authorization", "token", "expired",
        "invalid_grant", "oauth", "permission_denied", "unauthenticated",
    ]
    if any(kw in error_str or kw in error_type for kw in auth_keywords):
        return ErrorCategory.AUTH_FAILURE
    
    # Retryable errors
    retryable_keywords = [
        "quota", "rate_limit", "rate limit", "too_many_requests",
        "timeout", "timed out", "deadline_exceeded",
        "unavailable", "service_unavailable", "503", "500",
        "internal", "connection", "reset", "broken pipe",
        "resource_exhausted", "temporarily",
    ]
    if any(kw in error_str or kw in error_type for kw in retryable_keywords):
        return ErrorCategory.RETRYABLE
    
    # Everything else is non-retryable
    return ErrorCategory.NON_RETRYABLE


# -----------------------------------------------------------------------------
# Circuit Breaker
# -----------------------------------------------------------------------------

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Blocking all requests
    HALF_OPEN = "half_open" # Testing with one request


@dataclass
class CircuitBreaker:
    """
    Per-tenant circuit breaker.
    
    State machine:
    CLOSED > (5 failures) > OPEN > (60s wait) > HALF_OPEN > (1 success) > CLOSED
                                                           > (1 failure) > OPEN
    """
    tenant_id: str
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    total_trips: int = 0  # How many times circuit has opened
    
    def can_execute(self) -> bool:
        """Check if the circuit allows execution."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    logger.info(
                        f"Circuit HALF_OPEN for tenant {self.tenant_id} "
                        f"(after {elapsed:.0f}s recovery)"
                    )
                    return True
            return False
        
        # HALF_OPEN: allow one request
        return True
    
    def record_success(self):
        """Record a successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit CLOSED for tenant {self.tenant_id} (recovery success)")
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_success_time = datetime.utcnow()
    
    def record_failure(self, error: Exception):
        """Record a failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery test > back to OPEN
            self.state = CircuitState.OPEN
            self.total_trips += 1
            logger.warning(
                f"Circuit OPEN for tenant {self.tenant_id} "
                f"(half-open test failed: {error})"
            )
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.total_trips += 1
            logger.warning(
                f"Circuit OPEN for tenant {self.tenant_id} "
                f"(threshold {self.failure_threshold} reached, "
                f"total trips: {self.total_trips})"
            )
    
    def to_dict(self) -> dict:
        """Serialize state for monitoring."""
        return {
            "tenant_id": self.tenant_id,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "total_trips": self.total_trips,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success": self.last_success_time.isoformat() if self.last_success_time else None,
        }


# -----------------------------------------------------------------------------
# Executor
# -----------------------------------------------------------------------------

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class MaxRetriesExceededError(Exception):
    """Raised when all retries are exhausted."""
    pass


class GoogleAdsExecutor:
    """
    Resilient executor with circuit breaker and retry.
    
    Usage:
        executor = GoogleAdsExecutor(client_factory)
        
        result = await executor.execute(
            tenant_id="bank01",
            operation=my_async_function,
            operation_name="update_campaign_budget@v1",
        )
    """
    
    # Retry configuration
    MAX_RETRIES = 3
    BASE_DELAY_SECONDS = 1.0
    MAX_DELAY_SECONDS = 30.0
    BACKOFF_MULTIPLIER = 2.0
    JITTER_MAX_SECONDS = 0.5
    
    # Circuit breaker defaults
    CB_FAILURE_THRESHOLD = 5
    CB_RECOVERY_SECONDS = 60
    
    def __init__(self, client_factory, on_auth_failure: Callable = None):
        """
        Args:
            client_factory: GoogleAdsClientFactory for token refresh
            on_auth_failure: Optional callback when auth fails (for alerts)
        """
        self.client_factory = client_factory
        self.on_auth_failure = on_auth_failure
        self._circuits: Dict[str, CircuitBreaker] = {}
    
    async def execute(
        self,
        tenant_id: str,
        operation: Callable,
        operation_name: str = "",
        **kwargs,
    ) -> Any:
        """
        Execute an operation with circuit breaker and retry.
        
        Args:
            tenant_id: Tenant identifier for circuit isolation
            operation: Async callable to execute
            operation_name: Name for logging
            **kwargs: Arguments passed to operation
            
        Returns:
            Result from the operation
            
        Raises:
            CircuitBreakerOpenError: Circuit is open
            MaxRetriesExceededError: All retries exhausted
        """
        circuit = self._get_circuit(tenant_id)
        
        # Check circuit
        if not circuit.can_execute():
            logger.warning(
                f"Circuit OPEN for {tenant_id}, "
                f"rejecting {operation_name}"
            )
            raise CircuitBreakerOpenError(
                f"Circuit breaker is open for tenant {tenant_id}. "
                f"Will retry after {circuit.recovery_timeout_seconds}s."
            )
        
        last_error = None
        auth_refreshed = False
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                start = time.time()
                result = await operation(**kwargs)
                elapsed = (time.time() - start) * 1000
                
                circuit.record_success()
                
                logger.info(
                    f"[{tenant_id}] {operation_name} succeeded "
                    f"(attempt {attempt}, {elapsed:.0f}ms)"
                )
                
                return result
                
            except Exception as e:
                last_error = e
                category = classify_error(e)
                elapsed = (time.time() - start) * 1000
                
                logger.warning(
                    f"[{tenant_id}] {operation_name} failed "
                    f"(attempt {attempt}/{self.MAX_RETRIES}, "
                    f"{category.value}, {elapsed:.0f}ms): {e}"
                )
                
                if category == ErrorCategory.NON_RETRYABLE:
                    circuit.record_failure(e)
                    raise
                
                if category == ErrorCategory.AUTH_FAILURE:
                    if not auth_refreshed:
                        # Try refreshing token once
                        logger.info(f"[{tenant_id}] Refreshing auth token...")
                        try:
                            self.client_factory.invalidate(tenant_id)
                            auth_refreshed = True
                            
                            if self.on_auth_failure:
                                await self.on_auth_failure(tenant_id, e)
                            
                            # Don't count auth retry as a regular attempt
                            continue
                        except Exception as refresh_err:
                            logger.error(
                                f"[{tenant_id}] Token refresh failed: {refresh_err}"
                            )
                            circuit.record_failure(e)
                            raise e
                    else:
                        # Already refreshed once, fail
                        circuit.record_failure(e)
                        raise
                
                # RETRYABLE: backoff and retry
                if attempt < self.MAX_RETRIES:
                    delay = self._calculate_delay(attempt)
                    logger.info(
                        f"[{tenant_id}] Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    circuit.record_failure(e)
        
        raise MaxRetriesExceededError(
            f"Operation {operation_name} failed after "
            f"{self.MAX_RETRIES} attempts for tenant {tenant_id}: {last_error}"
        )
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        import random
        
        delay = self.BASE_DELAY_SECONDS * (self.BACKOFF_MULTIPLIER ** (attempt - 1))
        delay = min(delay, self.MAX_DELAY_SECONDS)
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, self.JITTER_MAX_SECONDS)
        return delay + jitter
    
    def _get_circuit(self, tenant_id: str) -> CircuitBreaker:
        """Get or create circuit breaker for a tenant."""
        if tenant_id not in self._circuits:
            self._circuits[tenant_id] = CircuitBreaker(
                tenant_id=tenant_id,
                failure_threshold=self.CB_FAILURE_THRESHOLD,
                recovery_timeout_seconds=self.CB_RECOVERY_SECONDS,
            )
        return self._circuits[tenant_id]
    
    def get_circuit_status(self, tenant_id: str = None) -> dict:
        """Get circuit breaker status for monitoring."""
        if tenant_id:
            circuit = self._circuits.get(tenant_id)
            return circuit.to_dict() if circuit else {"tenant_id": tenant_id, "state": "no_circuit"}
        
        return {
            tid: cb.to_dict() 
            for tid, cb in self._circuits.items()
        }
    
    def reset_circuit(self, tenant_id: str):
        """Manually reset a circuit breaker (admin operation)."""
        if tenant_id in self._circuits:
            self._circuits[tenant_id] = CircuitBreaker(
                tenant_id=tenant_id,
                failure_threshold=self.CB_FAILURE_THRESHOLD,
                recovery_timeout_seconds=self.CB_RECOVERY_SECONDS,
            )
            logger.info(f"Circuit breaker manually reset for tenant: {tenant_id}")

