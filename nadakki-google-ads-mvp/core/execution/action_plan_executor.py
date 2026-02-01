"""
NADAKKI AI Suite - Action Plan Executor
Execute Agent Action Plans with Rollback Support
"""

from typing import List, Dict, Any
from datetime import datetime
import logging

from core.agents.action_plan import ActionPlan, ActionPlanResult, OperationPriority
from core.operations.registry import OperationContext

logger = logging.getLogger(__name__)


class ActionPlanExecutor:
    """Execute action plans with rollback support."""
    
    def __init__(self, connector, telemetry, saga_journal=None):
        self.connector = connector
        self.telemetry = telemetry
        self.saga_journal = saga_journal
    
    async def execute(self, plan: ActionPlan, context: OperationContext = None,
                      stop_on_failure: bool = True, auto_rollback: bool = True) -> ActionPlanResult:
        """Execute an action plan."""
        start_time = datetime.utcnow()
        results = []
        executed = []
        failed_op = None
        
        saga_id = None
        if self.saga_journal:
            saga_id = await self.saga_journal.create_saga(
                plan.tenant_id, f"action_plan:{plan.agent_name}", plan.to_dict()
            )
        
        sorted_ops = sorted(plan.operations, key=lambda op: op.priority.value, reverse=True)
        context = context or OperationContext(tenant_id=plan.tenant_id)
        
        for op in sorted_ops:
            logger.info(f"Executing: {op.operation_name}")
            
            try:
                result = await self.connector.execute(
                    operation_name=op.operation_name,
                    payload=op.params,
                    tenant_id=plan.tenant_id,
                    context=context
                )
                
                op_result = {
                    "operation": op.operation_name,
                    "success": result.success,
                    "data": result.data,
                    "execution_time_ms": result.execution_time_ms
                }
                
                if result.success:
                    executed.append({"operation": op, "result": result})
                else:
                    op_result["error"] = result.error_message
                    if stop_on_failure:
                        failed_op = op
                        results.append(op_result)
                        break
                
                results.append(op_result)
                
            except Exception as e:
                logger.error(f"Operation {op.operation_name} failed: {e}")
                results.append({"operation": op.operation_name, "success": False, "error": str(e)})
                if stop_on_failure:
                    failed_op = op
                    break
        
        compensations = 0
        if failed_op and auto_rollback and executed:
            logger.warning(f"Rolling back {len(executed)} operations")
            compensations = await self._rollback(executed, context)
        
        total_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return ActionPlanResult(
            plan_id=plan.plan_id,
            success=failed_op is None,
            executed_operations=len(executed),
            failed_operations=1 if failed_op else 0,
            results=results,
            compensations_executed=compensations,
            total_execution_time_ms=total_time,
            error_message=f"Failed at: {failed_op.operation_name}" if failed_op else None
        )
    
    async def _rollback(self, executed: List[Dict], context: OperationContext) -> int:
        """Rollback executed operations in reverse order."""
        compensations = 0
        
        for item in reversed(executed):
            result = item["result"]
            if not result.compensable or not result.compensation_data:
                continue
            
            comp_data = result.compensation_data
            try:
                logger.info(f"Compensating: {comp_data['operation']}")
                await self.connector.execute(
                    operation_name=comp_data["operation"],
                    payload=comp_data["payload"],
                    tenant_id=context.tenant_id,
                    context=context
                )
                compensations += 1
            except Exception as e:
                logger.error(f"Compensation failed: {e}")
        
        return compensations
    
    async def validate_plan(self, plan: ActionPlan) -> Dict[str, Any]:
        """Validate an action plan before execution."""
        issues = []
        
        if not plan.operations:
            issues.append("Plan has no operations")
        
        if plan.risk_score > 0.7:
            issues.append(f"High risk score: {plan.risk_score}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "operations_count": len(plan.operations),
            "requires_approval": plan.requires_approval
        }
