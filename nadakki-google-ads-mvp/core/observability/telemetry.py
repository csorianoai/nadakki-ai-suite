"""
NADAKKI AI Suite - Telemetry
Structured Logging and Metrics
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger("nadakki.telemetry")


class TelemetrySidecar:
    """Telemetry for logging and metrics."""
    
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._active_ops: Dict[str, int] = defaultdict(int)
    
    def log_operation(self, request, result: Optional[Any], status: str, extra: Dict[str, Any] = None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "operation",
            "tenant_id": request.tenant_id,
            "operation_id": request.operation_id,
            "operation_name": request.operation_name,
            "trace_id": request.context.trace_id,
            "status": status,
            "dry_run": request.context.dry_run
        }
        
        if result:
            log_entry["success"] = result.success
            log_entry["execution_time_ms"] = result.execution_time_ms
            if result.error_code:
                log_entry["error_code"] = result.error_code.value
        
        if extra:
            log_entry.update(extra)
        
        logger.info(json.dumps(log_entry))
        self._counters[f"ops_{request.operation_base}_{'success' if result and result.success else 'failed'}"] += 1
    
    def log_event(self, event_type: str, tenant_id: str, trace_id: str, data: Dict[str, Any] = None):
        log_entry = {"timestamp": datetime.utcnow().isoformat() + "Z", "event": event_type, "tenant_id": tenant_id, "trace_id": trace_id}
        if data:
            log_entry["data"] = data
        logger.info(json.dumps(log_entry))
    
    def log_error(self, error_type: str, tenant_id: str, trace_id: str, error_message: str):
        logger.error(json.dumps({"timestamp": datetime.utcnow().isoformat() + "Z", "event": "error", "error_type": error_type,
                                 "tenant_id": tenant_id, "trace_id": trace_id, "error_message": error_message}))
    
    def record_latency(self, operation: str, latency_seconds: float):
        pass  # Would record to histogram
    
    def increment_active_ops(self, tenant_id: str):
        self._active_ops[tenant_id] += 1
    
    def decrement_active_ops(self, tenant_id: str):
        self._active_ops[tenant_id] = max(0, self._active_ops[tenant_id] - 1)
    
    def get_metrics(self) -> dict:
        return {"counters": dict(self._counters), "active_ops": dict(self._active_ops)}


_telemetry: Optional[TelemetrySidecar] = None

def get_telemetry() -> TelemetrySidecar:
    global _telemetry
    if _telemetry is None:
        _telemetry = TelemetrySidecar()
    return _telemetry
