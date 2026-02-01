"""
NADAKKI AI Suite - Action Plan
Standardized Agent Output Format
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


class OperationPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class PlannedOperation:
    """A single operation planned by an agent."""
    operation_name: str
    params: Dict[str, Any]
    priority: OperationPriority = OperationPriority.MEDIUM
    estimated_impact: Dict[str, Any] = field(default_factory=dict)
    requires_manual_review: bool = False
    compensation_operation: Optional[str] = None
    compensation_params: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "operation_name": self.operation_name,
            "params": self.params,
            "priority": self.priority.value,
            "estimated_impact": self.estimated_impact,
            "requires_manual_review": self.requires_manual_review
        }


@dataclass
class ActionPlan:
    """Complete action plan from an agent."""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    agent_name: str = ""
    tenant_id: str = ""
    
    analysis: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    operations: List[PlannedOperation] = field(default_factory=list)
    
    risk_score: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    
    requires_approval: bool = False
    approval_reason: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    
    def add_operation(self, operation_name: str, params: Dict[str, Any],
                      priority: OperationPriority = OperationPriority.MEDIUM,
                      estimated_impact: Dict[str, Any] = None, requires_review: bool = False):
        op = PlannedOperation(
            operation_name=operation_name, params=params, priority=priority,
            estimated_impact=estimated_impact or {}, requires_manual_review=requires_review
        )
        self.operations.append(op)
        if requires_review:
            self.requires_approval = True
    
    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "tenant_id": self.tenant_id,
            "analysis": self.analysis,
            "rationale": self.rationale,
            "operations": [op.to_dict() for op in self.operations],
            "risk_score": self.risk_score,
            "requires_approval": self.requires_approval,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ActionPlanResult:
    """Result of executing an action plan."""
    plan_id: str
    success: bool
    executed_operations: int
    failed_operations: int
    results: List[Dict[str, Any]] = field(default_factory=list)
    compensations_executed: int = 0
    total_execution_time_ms: int = 0
    error_message: Optional[str] = None
