# ===============================================================================
# NADAKKI AI Suite - TelemetrySidecar
# core/observability/telemetry.py
# Day 2 - Component 3 of 5
# ===============================================================================

"""
Observability layer for all Google Ads operations.

MVP Implementation:
- JSON structured logs with trace_id for correlation
- In-memory Prometheus-compatible metrics (counters, histograms, gauges)
- Operation-level recording (latency, success/failure, policy decisions)
- /metrics endpoint output (Prometheus text format)

Phase 2 (future): Full OpenTelemetry integration with distributed tracing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
import time
import json
import logging
import uuid

logger = logging.getLogger("nadakki.observability.telemetry")


# -----------------------------------------------------------------------------
# Metric Types
# -----------------------------------------------------------------------------

class Counter:
    """Monotonically increasing counter."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._values: Dict[str, float] = defaultdict(float)
    
    def inc(self, labels: dict = None, amount: float = 1.0):
        key = self._label_key(labels)
        self._values[key] += amount
    
    def get(self, labels: dict = None) -> float:
        return self._values.get(self._label_key(labels), 0.0)
    
    def to_prometheus(self) -> str:
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} counter"]
        for key, value in sorted(self._values.items()):
            label_str = key if key else ""
            lines.append(f"{self.name}{{{label_str}}} {value}")
        return "\n".join(lines)
    
    @staticmethod
    def _label_key(labels: dict = None) -> str:
        if not labels:
            return ""
        return ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))


class Histogram:
    """Histogram for latency/duration tracking."""
    
    DEFAULT_BUCKETS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]  # ms
    
    def __init__(self, name: str, description: str = "", buckets: list = None):
        self.name = name
        self.description = description
        self.buckets = buckets or self.DEFAULT_BUCKETS
        self._observations: Dict[str, List[float]] = defaultdict(list)
    
    def observe(self, value: float, labels: dict = None):
        key = Counter._label_key(labels)
        self._observations[key].append(value)
    
    def get_stats(self, labels: dict = None) -> dict:
        key = Counter._label_key(labels)
        values = self._observations.get(key, [])
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0}
        
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return {
            "count": n,
            "sum": sum(sorted_vals),
            "avg": sum(sorted_vals) / n,
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
            "p50": sorted_vals[int(n * 0.5)],
            "p95": sorted_vals[min(int(n * 0.95), n - 1)],
            "p99": sorted_vals[min(int(n * 0.99), n - 1)],
        }
    
    def to_prometheus(self) -> str:
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} histogram"]
        for key, values in sorted(self._observations.items()):
            label_str = key if key else ""
            sorted_vals = sorted(values)
            count = len(sorted_vals)
            total = sum(sorted_vals)
            
            for bucket in self.buckets:
                bucket_count = len([v for v in sorted_vals if v <= bucket])
                lines.append(f'{self.name}_bucket{{{label_str},le="{bucket}"}} {bucket_count}')
            
            lines.append(f'{self.name}_bucket{{{label_str},le="+Inf"}} {count}')
            lines.append(f"{self.name}_sum{{{label_str}}} {total}")
            lines.append(f"{self.name}_count{{{label_str}}} {count}")
        
        return "\n".join(lines)


class Gauge:
    """Value that can go up and down."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._values: Dict[str, float] = defaultdict(float)
    
    def set(self, value: float, labels: dict = None):
        self._values[Counter._label_key(labels)] = value
    
    def inc(self, labels: dict = None, amount: float = 1.0):
        self._values[Counter._label_key(labels)] += amount
    
    def dec(self, labels: dict = None, amount: float = 1.0):
        self._values[Counter._label_key(labels)] -= amount
    
    def get(self, labels: dict = None) -> float:
        return self._values.get(Counter._label_key(labels), 0.0)
    
    def to_prometheus(self) -> str:
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} gauge"]
        for key, value in sorted(self._values.items()):
            label_str = key if key else ""
            lines.append(f"{self.name}{{{label_str}}} {value}")
        return "\n".join(lines)


# -----------------------------------------------------------------------------
# Telemetry Sidecar
# -----------------------------------------------------------------------------

class TelemetrySidecar:
    """
    Central telemetry collector for all NADAKKI operations.
    
    Usage:
        telemetry = TelemetrySidecar()
        
        # Record operation
        telemetry.record_operation(
            tenant_id="bank01",
            operation_name="update_campaign_budget@v1",
            success=True,
            duration_ms=145,
            trace_id="abc-123",
        )
        
        # Record policy decision
        telemetry.record_policy_decision(
            tenant_id="bank01",
            rule_name="daily_max_usd",
            decision="allow",
        )
        
        # Get Prometheus metrics
        print(telemetry.get_prometheus_metrics())
    """
    
    def __init__(self):
        # Counters
        self.operations_total = Counter(
            "nadakki_operations_total",
            "Total number of Google Ads operations executed"
        )
        self.operations_errors = Counter(
            "nadakki_operations_errors_total",
            "Total number of failed operations"
        )
        self.policy_decisions = Counter(
            "nadakki_policy_decisions_total",
            "Total policy decisions by type"
        )
        self.retries_total = Counter(
            "nadakki_retries_total",
            "Total number of operation retries"
        )
        self.circuit_breaker_trips = Counter(
            "nadakki_circuit_breaker_trips_total",
            "Total circuit breaker trip events"
        )
        self.idempotency_hits = Counter(
            "nadakki_idempotency_hits_total",
            "Total idempotency cache hits"
        )
        
        # Histograms
        self.operation_duration = Histogram(
            "nadakki_operation_duration_ms",
            "Operation execution duration in milliseconds"
        )
        
        # Gauges
        self.active_operations = Gauge(
            "nadakki_active_operations",
            "Currently executing operations"
        )
        self.circuit_state = Gauge(
            "nadakki_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=half_open, 2=open)"
        )
        
        # Event log (last N events for debugging)
        self._events: List[dict] = []
        self._max_events = 1000
        
        logger.info("TelemetrySidecar initialized")
    
    # ---------------------------------------------------------------------
    # Recording Methods
    # ---------------------------------------------------------------------
    
    def record_operation(
        self,
        tenant_id: str,
        operation_name: str,
        success: bool,
        duration_ms: float,
        trace_id: str = "",
        error_code: str = "",
        source: str = "api",
    ):
        """Record an operation execution."""
        labels = {
            "tenant_id": tenant_id,
            "operation": operation_name,
            "source": source,
        }
        
        self.operations_total.inc(labels)
        self.operation_duration.observe(duration_ms, labels)
        
        if not success:
            error_labels = {**labels, "error_code": error_code}
            self.operations_errors.inc(error_labels)
        
        # JSON structured log
        self._log_event({
            "event": "operation_executed",
            "tenant_id": tenant_id,
            "operation": operation_name,
            "success": success,
            "duration_ms": round(duration_ms, 2),
            "error_code": error_code,
            "trace_id": trace_id or str(uuid.uuid4()),
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
    
    def record_policy_decision(
        self,
        tenant_id: str,
        rule_name: str,
        decision: str,
        operation_name: str = "",
        trace_id: str = "",
    ):
        """Record a policy evaluation."""
        labels = {
            "tenant_id": tenant_id,
            "rule": rule_name,
            "decision": decision,
        }
        self.policy_decisions.inc(labels)
        
        self._log_event({
            "event": "policy_decision",
            "tenant_id": tenant_id,
            "rule": rule_name,
            "decision": decision,
            "operation": operation_name,
            "trace_id": trace_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
    
    def record_retry(
        self,
        tenant_id: str,
        operation_name: str,
        attempt: int,
        error: str = "",
        trace_id: str = "",
    ):
        """Record a retry attempt."""
        labels = {
            "tenant_id": tenant_id,
            "operation": operation_name,
        }
        self.retries_total.inc(labels)
        
        self._log_event({
            "event": "operation_retry",
            "tenant_id": tenant_id,
            "operation": operation_name,
            "attempt": attempt,
            "error": error,
            "trace_id": trace_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
    
    def record_circuit_trip(
        self,
        tenant_id: str,
        new_state: str,
        reason: str = "",
    ):
        """Record a circuit breaker state change."""
        labels = {"tenant_id": tenant_id}
        self.circuit_breaker_trips.inc(labels)
        
        state_value = {"closed": 0, "half_open": 1, "open": 2}.get(new_state, -1)
        self.circuit_state.set(state_value, labels)
        
        self._log_event({
            "event": "circuit_breaker_trip",
            "tenant_id": tenant_id,
            "new_state": new_state,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
    
    def record_idempotency_hit(
        self,
        tenant_id: str,
        operation_name: str,
        trace_id: str = "",
    ):
        """Record an idempotency cache hit."""
        labels = {
            "tenant_id": tenant_id,
            "operation": operation_name,
        }
        self.idempotency_hits.inc(labels)
    
    def record_saga_event(
        self,
        tenant_id: str,
        saga_id: str,
        status: str,
        operation_name: str = "",
        trace_id: str = "",
    ):
        """Record a saga lifecycle event."""
        self._log_event({
            "event": "saga_event",
            "tenant_id": tenant_id,
            "saga_id": saga_id,
            "status": status,
            "operation": operation_name,
            "trace_id": trace_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
    
    # ---------------------------------------------------------------------
    # Output
    # ---------------------------------------------------------------------
    
    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus text format output."""
        sections = [
            self.operations_total.to_prometheus(),
            self.operations_errors.to_prometheus(),
            self.policy_decisions.to_prometheus(),
            self.retries_total.to_prometheus(),
            self.circuit_breaker_trips.to_prometheus(),
            self.idempotency_hits.to_prometheus(),
            self.operation_duration.to_prometheus(),
            self.active_operations.to_prometheus(),
            self.circuit_state.to_prometheus(),
        ]
        return "\n\n".join(sections)
    
    def get_stats(self, tenant_id: str = None) -> dict:
        """Get summary stats, optionally filtered by tenant."""
        labels = {"tenant_id": tenant_id} if tenant_id else None
        
        return {
            "operations_total": self.operations_total.get(labels),
            "operations_errors": self.operations_errors.get(labels),
            "retries_total": self.retries_total.get(labels),
            "idempotency_hits": self.idempotency_hits.get(labels),
            "duration_stats": self.operation_duration.get_stats(labels),
        }
    
    def get_recent_events(self, n: int = 50, tenant_id: str = None) -> List[dict]:
        """Get recent telemetry events."""
        events = self._events
        if tenant_id:
            events = [e for e in events if e.get("tenant_id") == tenant_id]
        return events[-n:]
    
    # ---------------------------------------------------------------------
    # Internal
    # ---------------------------------------------------------------------
    
    def _log_event(self, event: dict):
        """Store event and emit structured JSON log."""
        self._events.append(event)
        
        # Trim if over limit
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
        
        # Emit JSON log
        logger.info(json.dumps(event, default=str))
