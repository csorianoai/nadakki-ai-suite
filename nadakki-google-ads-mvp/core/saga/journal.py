# ===============================================================================
# NADAKKI AI Suite - SagaJournal
# core/saga/journal.py
# Day 2 - Component 4 of 5
# ===============================================================================

"""
Saga pattern implementation for operation auditing and compensation.

Every operation that modifies state in Google Ads is recorded as a saga.
If a multi-step operation partially fails, the saga journal enables
best-effort rollback via compensation operations.

Saga States:
    PENDING > EXECUTING > COMPLETED | FAILED | COMPENSATION_PENDING > COMPENSATED

MVP: PostgreSQL-simple with best-effort compensation.
Phase 2: Temporal.io integration for durable workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import uuid
import logging

logger = logging.getLogger("nadakki.saga.journal")


# -----------------------------------------------------------------------------
# Saga States
# -----------------------------------------------------------------------------

class SagaStatus(Enum):
    PENDING = "PENDING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATION_PENDING = "COMPENSATION_PENDING"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    COMPENSATION_FAILED = "COMPENSATION_FAILED"


class StepStatus(Enum):
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    COMPENSATION_FAILED = "COMPENSATION_FAILED"


# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------

@dataclass
class SagaStep:
    """Individual step within a saga."""
    step_id: str
    saga_id: str
    operation_name: str
    payload: dict
    status: StepStatus = StepStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    compensation_data: Optional[dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    order: int = 0
    
    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "saga_id": self.saga_id,
            "operation_name": self.operation_name,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "has_compensation": self.compensation_data is not None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "order": self.order,
        }


@dataclass
class Saga:
    """A saga tracking a multi-step operation."""
    saga_id: str
    tenant_id: str
    operation_name: str
    trace_id: str
    status: SagaStatus = SagaStatus.PENDING
    steps: List[SagaStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "saga_id": self.saga_id,
            "tenant_id": self.tenant_id,
            "operation_name": self.operation_name,
            "status": self.status.value,
            "trace_id": self.trace_id,
            "steps": [s.to_dict() for s in self.steps],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


# -----------------------------------------------------------------------------
# Saga Journal
# -----------------------------------------------------------------------------

class SagaJournal:
    """
    Persistent journal for saga lifecycle tracking.
    
    Usage:
        journal = SagaJournal(db)
        
        # Create saga for an operation
        saga = await journal.create_saga(
            tenant_id="bank01",
            operation_name="update_campaign_budget@v1",
            trace_id="abc-123",
        )
        
        # Add step
        step = await journal.add_step(
            saga_id=saga.saga_id,
            operation_name="update_campaign_budget@v1",
            payload={"budget_id": "b1", "new_budget": 75.0},
        )
        
        # Complete step
        await journal.complete_step(
            step_id=step.step_id,
            result={"resource_name": "..."},
            compensation_data={"operation": "...", "payload": {...}},
        )
        
        # Complete saga
        await journal.complete_saga(saga.saga_id)
        
        # If rollback needed
        await journal.request_compensation(saga.saga_id, "Step 2 failed")
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        # In-memory cache for active sagas (supplements DB)
        self._active_sagas: Dict[str, Saga] = {}
        logger.info("SagaJournal initialized")
    
    # ---------------------------------------------------------------------
    # Saga Lifecycle
    # ---------------------------------------------------------------------
    
    async def create_saga(
        self,
        tenant_id: str,
        operation_name: str,
        trace_id: str = "",
        metadata: dict = None,
    ) -> Saga:
        """Create a new saga."""
        saga_id = f"saga_{uuid.uuid4().hex[:12]}"
        trace_id = trace_id or str(uuid.uuid4())
        
        saga = Saga(
            saga_id=saga_id,
            tenant_id=tenant_id,
            operation_name=operation_name,
            trace_id=trace_id,
            metadata=metadata or {},
        )
        
        await self.db.execute("""
            INSERT INTO sagas 
            (saga_id, tenant_id, operation_name, trace_id, status, metadata, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
            saga_id, tenant_id, operation_name, trace_id,
            SagaStatus.PENDING.value, json.dumps(metadata or {}),
            saga.created_at, saga.updated_at,
        )
        
        self._active_sagas[saga_id] = saga
        
        logger.info(
            f"Saga created: {saga_id} for {operation_name} "
            f"(tenant: {tenant_id}, trace: {trace_id})"
        )
        
        return saga
    
    async def add_step(
        self,
        saga_id: str,
        operation_name: str,
        payload: dict,
        order: int = None,
    ) -> SagaStep:
        """Add a step to a saga."""
        step_id = f"step_{uuid.uuid4().hex[:12]}"
        
        # Auto-order
        saga = self._active_sagas.get(saga_id)
        if order is None and saga:
            order = len(saga.steps)
        
        step = SagaStep(
            step_id=step_id,
            saga_id=saga_id,
            operation_name=operation_name,
            payload=payload,
            order=order or 0,
        )
        
        await self.db.execute("""
            INSERT INTO saga_steps 
            (step_id, saga_id, operation_name, payload, status, step_order, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
            step_id, saga_id, operation_name,
            json.dumps(payload, default=str),
            StepStatus.PENDING.value,
            step.order, datetime.utcnow(),
        )
        
        if saga:
            saga.steps.append(step)
        
        return step
    
    async def start_step(self, step_id: str):
        """Mark a step as executing."""
        now = datetime.utcnow()
        
        await self.db.execute("""
            UPDATE saga_steps SET status = $1, started_at = $2
            WHERE step_id = $3
        """, StepStatus.EXECUTING.value, now, step_id)
        
        # Update in-memory
        step = self._find_step(step_id)
        if step:
            step.status = StepStatus.EXECUTING
            step.started_at = now
    
    async def complete_step(
        self,
        step_id: str,
        result: dict = None,
        compensation_data: dict = None,
    ):
        """Mark a step as completed with optional compensation data."""
        now = datetime.utcnow()
        
        await self.db.execute("""
            UPDATE saga_steps 
            SET status = $1, result = $2, compensation_data = $3, completed_at = $4
            WHERE step_id = $5
        """,
            StepStatus.COMPLETED.value,
            json.dumps(result or {}, default=str),
            json.dumps(compensation_data, default=str) if compensation_data else None,
            now, step_id,
        )
        
        step = self._find_step(step_id)
        if step:
            step.status = StepStatus.COMPLETED
            step.result = result
            step.compensation_data = compensation_data
            step.completed_at = now
    
    async def fail_step(self, step_id: str, error: str):
        """Mark a step as failed."""
        now = datetime.utcnow()
        
        await self.db.execute("""
            UPDATE saga_steps 
            SET status = $1, error = $2, completed_at = $3
            WHERE step_id = $4
        """, StepStatus.FAILED.value, error, now, step_id)
        
        step = self._find_step(step_id)
        if step:
            step.status = StepStatus.FAILED
            step.error = error
            step.completed_at = now
    
    async def complete_saga(self, saga_id: str):
        """Mark a saga as completed."""
        now = datetime.utcnow()
        
        await self.db.execute("""
            UPDATE sagas SET status = $1, updated_at = $2, completed_at = $3
            WHERE saga_id = $4
        """, SagaStatus.COMPLETED.value, now, now, saga_id)
        
        saga = self._active_sagas.get(saga_id)
        if saga:
            saga.status = SagaStatus.COMPLETED
            saga.updated_at = now
            saga.completed_at = now
        
        logger.info(f"Saga completed: {saga_id}")
    
    async def fail_saga(self, saga_id: str, error: str):
        """Mark a saga as failed."""
        now = datetime.utcnow()
        
        await self.db.execute("""
            UPDATE sagas SET status = $1, error = $2, updated_at = $3
            WHERE saga_id = $4
        """, SagaStatus.FAILED.value, error, now, saga_id)
        
        saga = self._active_sagas.get(saga_id)
        if saga:
            saga.status = SagaStatus.FAILED
            saga.error = error
            saga.updated_at = now
        
        logger.warning(f"Saga failed: {saga_id} - {error}")
    
    async def set_pending_approval(self, saga_id: str):
        """Set saga to pending approval status."""
        now = datetime.utcnow()
        
        await self.db.execute("""
            UPDATE sagas SET status = $1, updated_at = $2
            WHERE saga_id = $3
        """, SagaStatus.PENDING_APPROVAL.value, now, saga_id)
        
        saga = self._active_sagas.get(saga_id)
        if saga:
            saga.status = SagaStatus.PENDING_APPROVAL
            saga.updated_at = now
        
        logger.info(f"Saga pending approval: {saga_id}")
    
    # ---------------------------------------------------------------------
    # Compensation
    # ---------------------------------------------------------------------
    
    async def request_compensation(self, saga_id: str, reason: str = "") -> List[dict]:
        """
        Request compensation (rollback) for a saga.
        
        Returns list of compensation operations that need to be executed.
        Compensation is best-effort: if it fails, status goes to COMPENSATION_FAILED.
        """
        saga = self._active_sagas.get(saga_id)
        if not saga:
            logger.warning(f"Saga {saga_id} not found in active sagas for compensation")
            return []
        
        # Update status
        await self.db.execute("""
            UPDATE sagas SET status = $1, updated_at = $2, error = $3
            WHERE saga_id = $4
        """,
            SagaStatus.COMPENSATION_PENDING.value,
            datetime.utcnow(), reason, saga_id,
        )
        saga.status = SagaStatus.COMPENSATION_PENDING
        
        # Collect compensation operations (reverse order)
        compensations = []
        for step in reversed(saga.steps):
            if step.status == StepStatus.COMPLETED and step.compensation_data:
                compensations.append({
                    "step_id": step.step_id,
                    "saga_id": saga_id,
                    **step.compensation_data,
                })
        
        logger.info(
            f"Compensation requested for saga {saga_id}: "
            f"{len(compensations)} steps to compensate. Reason: {reason}"
        )
        
        return compensations
    
    async def mark_step_compensated(self, step_id: str):
        """Mark a step as successfully compensated."""
        await self.db.execute("""
            UPDATE saga_steps SET status = $1
            WHERE step_id = $2
        """, StepStatus.COMPENSATED.value, step_id)
        
        step = self._find_step(step_id)
        if step:
            step.status = StepStatus.COMPENSATED
    
    async def mark_step_compensation_failed(self, step_id: str, error: str):
        """Mark a step's compensation as failed."""
        await self.db.execute("""
            UPDATE saga_steps SET status = $1, error = $2
            WHERE step_id = $3
        """, StepStatus.COMPENSATION_FAILED.value, error, step_id)
        
        step = self._find_step(step_id)
        if step:
            step.status = StepStatus.COMPENSATION_FAILED
            step.error = error
        
        logger.error(f"Compensation failed for step {step_id}: {error}")
    
    async def finalize_compensation(self, saga_id: str):
        """
        Check all compensation steps and update saga status.
        COMPENSATED if all done, COMPENSATION_FAILED if any failed.
        """
        saga = self._active_sagas.get(saga_id)
        if not saga:
            return
        
        any_failed = any(
            s.status == StepStatus.COMPENSATION_FAILED 
            for s in saga.steps
        )
        
        new_status = (
            SagaStatus.COMPENSATION_FAILED if any_failed
            else SagaStatus.COMPENSATED
        )
        
        await self.db.execute("""
            UPDATE sagas SET status = $1, updated_at = $2
            WHERE saga_id = $3
        """, new_status.value, datetime.utcnow(), saga_id)
        
        saga.status = new_status
        
        if any_failed:
            logger.error(f"Saga {saga_id}: compensation partially failed")
        else:
            logger.info(f"Saga {saga_id}: fully compensated")
    
    # ---------------------------------------------------------------------
    # Query
    # ---------------------------------------------------------------------
    
    async def get_saga(self, saga_id: str) -> Optional[Saga]:
        """Get a saga by ID."""
        return self._active_sagas.get(saga_id)
    
    async def get_tenant_sagas(
        self,
        tenant_id: str,
        status: SagaStatus = None,
        limit: int = 50,
    ) -> List[dict]:
        """Get sagas for a tenant, optionally filtered by status."""
        sagas = [
            s.to_dict() for s in self._active_sagas.values()
            if s.tenant_id == tenant_id
            and (status is None or s.status == status)
        ]
        return sagas[:limit]
    
    async def get_pending_compensations(self) -> List[dict]:
        """Get all sagas with COMPENSATION_PENDING status (for admin dashboard)."""
        return [
            s.to_dict() for s in self._active_sagas.values()
            if s.status in (
                SagaStatus.COMPENSATION_PENDING,
                SagaStatus.COMPENSATION_FAILED,
            )
        ]
    
    # ---------------------------------------------------------------------
    # Internal
    # ---------------------------------------------------------------------
    
    def _find_step(self, step_id: str) -> Optional[SagaStep]:
        """Find a step across all active sagas."""
        for saga in self._active_sagas.values():
            for step in saga.steps:
                if step.step_id == step_id:
                    return step
        return None


# -----------------------------------------------------------------------------
# Database Schema
# -----------------------------------------------------------------------------

SAGA_SCHEMA = """
-- Sagas
CREATE TABLE IF NOT EXISTS sagas (
    saga_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    operation_name VARCHAR(200) NOT NULL,
    trace_id VARCHAR(64),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    metadata JSONB DEFAULT '{}',
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_sagas_tenant ON sagas(tenant_id);
CREATE INDEX IF NOT EXISTS idx_sagas_status ON sagas(status);
CREATE INDEX IF NOT EXISTS idx_sagas_trace ON sagas(trace_id);

-- Saga Steps
CREATE TABLE IF NOT EXISTS saga_steps (
    step_id VARCHAR(64) PRIMARY KEY,
    saga_id VARCHAR(64) NOT NULL REFERENCES sagas(saga_id),
    operation_name VARCHAR(200) NOT NULL,
    payload JSONB,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    result JSONB,
    error TEXT,
    compensation_data JSONB,
    step_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_saga_steps_saga ON saga_steps(saga_id);
CREATE INDEX IF NOT EXISTS idx_saga_steps_status ON saga_steps(status);
"""
