"""
NADAKKI AI Suite - Saga Journal
Audit Trail and Compensation Support
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class SagaStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATED = "COMPENSATED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class SagaJournal:
    """Journal for saga pattern."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def create_saga(self, tenant_id: str, workflow_name: str, input_data: dict) -> str:
        saga_id = str(uuid.uuid4())
        await self.db.execute(
            "INSERT INTO sagas (saga_id, tenant_id, workflow_name, input_data, status, created_at) VALUES ($1, $2, $3, $4, $5, NOW())",
            saga_id, tenant_id, workflow_name, json.dumps(input_data), SagaStatus.RUNNING.value
        )
        return saga_id
    
    async def record_operation(self, request, result, saga_id: str = None) -> str:
        step_id = str(uuid.uuid4())
        await self.db.execute("""
            INSERT INTO saga_steps (step_id, saga_id, tenant_id, operation_id, operation_name, status, payload, result, compensation_data, execution_time_ms, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
        """, step_id, saga_id, request.tenant_id, request.operation_id, request.operation_name,
            SagaStatus.COMPLETED.value if result.success else SagaStatus.FAILED.value,
            json.dumps(request.payload), json.dumps(result.data) if result.data else None,
            json.dumps(result.compensation_data) if result.compensation_data else None, result.execution_time_ms)
        return step_id
    
    async def record_pending_approval(self, request, reason: str) -> str:
        step_id = str(uuid.uuid4())
        await self.db.execute("""
            INSERT INTO saga_steps (step_id, tenant_id, operation_id, operation_name, status, payload, error_message, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
        """, step_id, request.tenant_id, request.operation_id, request.operation_name,
            SagaStatus.PENDING_APPROVAL.value, json.dumps(request.payload), f"Pending: {reason}")
        return step_id
    
    async def get_pending_approvals(self, tenant_id: str, limit: int = 50) -> List[dict]:
        rows = await self.db.fetch(
            "SELECT step_id, operation_name, payload, error_message, created_at FROM saga_steps WHERE tenant_id = $1 AND status = $2 ORDER BY created_at DESC LIMIT $3",
            tenant_id, SagaStatus.PENDING_APPROVAL.value, limit
        )
        return [{"step_id": r["step_id"], "operation_name": r["operation_name"],
                 "payload": json.loads(r["payload"]) if r["payload"] else {}, "reason": r["error_message"]} for r in rows]
    
    async def approve_operation(self, step_id: str) -> bool:
        result = await self.db.execute(
            "UPDATE saga_steps SET status = $1, completed_at = NOW() WHERE step_id = $2 AND status = $3",
            SagaStatus.COMPLETED.value, step_id, SagaStatus.PENDING_APPROVAL.value
        )
        return result.rowcount > 0 if hasattr(result, 'rowcount') else True
