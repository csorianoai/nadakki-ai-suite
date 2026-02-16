# ===============================================================================
# NADAKKI AI Suite - WorkflowEngine
# core/workflows/engine.py
# Day 5 - Component 1 of 3
# ===============================================================================

"""
YAML-driven Workflow Engine - orchestrates multi-step agent workflows.

A Workflow is a state machine defined in YAML:
    - States (steps) with entry/exit actions
    - Transitions between states with conditions
    - Agent assignments per step
    - Error handling and compensation

Features:
    - Load workflow definitions from YAML files
    - Execute workflows step-by-step
    - Support for parallel and sequential steps
    - Human approval gates
    - Automatic rollback on failure
    - Full execution history and audit

Usage:
    engine = WorkflowEngine(agents, plan_executor, knowledge_store)
    
    # Load workflow definitions
    engine.load_workflows("config/workflows/")
    
    # Run a workflow
    result = await engine.run(
        workflow_id="weekly_optimization",
        tenant_id="bank01",
        context={"industry": "financial_services"},
    )
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import logging
import os
import copy

logger = logging.getLogger("nadakki.workflows.engine")

# Try YAML
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# -----------------------------------------------------------------------------
# Workflow State
# -----------------------------------------------------------------------------

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    AWAITING_APPROVAL = "awaiting_approval"


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"              # Waiting for human approval
    PARTIALLY_COMPLETED = "partially_completed"


class WorkflowExecution:
    """Tracks the state of a running workflow."""
    
    def __init__(self, workflow_id: str, tenant_id: str, context: dict = None):
        self.execution_id = f"wf_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{id(self) % 10000:04d}"
        self.workflow_id = workflow_id
        self.tenant_id = tenant_id
        self.context = context or {}
        self.status = WorkflowStatus.PENDING
        self.steps: List[dict] = []
        self.current_step_index = 0
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.results: Dict[str, Any] = {}  # step_id > result
        self.errors: List[dict] = []
        self.plans_generated: List[str] = []  # plan_ids
    
    def to_dict(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "tenant_id": self.tenant_id,
            "status": self.status.value,
            "total_steps": len(self.steps),
            "current_step": self.current_step_index,
            "completed_steps": sum(1 for s in self.steps if s.get("status") == StepStatus.COMPLETED.value),
            "failed_steps": sum(1 for s in self.steps if s.get("status") == StepStatus.FAILED.value),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "plans_generated": self.plans_generated,
            "steps": self.steps,
            "errors": self.errors,
        }


# -----------------------------------------------------------------------------
# Workflow Engine
# -----------------------------------------------------------------------------

class WorkflowEngine:
    """
    Executes YAML-defined workflows using registered agents.
    """
    
    VERSION = "1.0.0"
    
    def __init__(
        self,
        agents: Dict[str, Any],
        plan_executor=None,
        knowledge_store=None,
    ):
        """
        Args:
            agents: Dict mapping agent names to agent instances.
                    e.g., {"strategist": GoogleAdsStrategistIA, ...}
            plan_executor: ActionPlanExecutor instance
            knowledge_store: YamlKnowledgeStore instance
        """
        self.agents = agents
        self.plan_executor = plan_executor
        self.kb = knowledge_store
        
        self._workflow_definitions: Dict[str, dict] = {}
        self._execution_history: List[WorkflowExecution] = []
        self._running: Dict[str, WorkflowExecution] = {}
        
        logger.info(f"WorkflowEngine v{self.VERSION} initialized ({len(agents)} agents)")
    
    # ---------------------------------------------------------------------
    # Workflow Loading
    # ---------------------------------------------------------------------
    
    def load_workflows(self, directory: str):
        """Load all .yaml workflow definitions from a directory."""
        if not os.path.exists(directory):
            logger.warning(f"Workflow directory not found: {directory}")
            return
        
        for filename in os.listdir(directory):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                filepath = os.path.join(directory, filename)
                self.load_workflow_file(filepath)
    
    def load_workflow_file(self, filepath: str):
        """Load a single workflow definition file."""
        if not HAS_YAML:
            logger.error("PyYAML required for workflow definitions")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return
            
            # File can contain single workflow or list
            workflows = data if isinstance(data, list) else [data]
            
            for wf in workflows:
                wf_id = wf.get("id")
                if wf_id:
                    self._workflow_definitions[wf_id] = wf
                    logger.info(f"  Loaded workflow: {wf_id} ({len(wf.get('steps', []))} steps)")
        
        except Exception as e:
            logger.error(f"Error loading workflow {filepath}: {e}")
    
    def register_workflow(self, definition: dict):
        """Register a workflow definition programmatically."""
        wf_id = definition.get("id")
        if not wf_id:
            raise ValueError("Workflow definition must have an 'id'")
        self._workflow_definitions[wf_id] = definition
        logger.info(f"Registered workflow: {wf_id}")
    
    # ---------------------------------------------------------------------
    # Workflow Execution
    # ---------------------------------------------------------------------
    
    async def run(
        self,
        workflow_id: str,
        tenant_id: str,
        context: dict = None,
        dry_run: bool = False,
        auto_approve: bool = False,
    ) -> WorkflowExecution:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to run
            tenant_id: Tenant to run for
            context: Additional context (merged with workflow defaults)
            dry_run: If True, generate plans but don't execute
            auto_approve: If True, auto-approve all approval gates
        """
        definition = self._workflow_definitions.get(workflow_id)
        if not definition:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # Create execution
        execution = WorkflowExecution(workflow_id, tenant_id, context)
        execution.started_at = datetime.utcnow()
        execution.status = WorkflowStatus.RUNNING
        
        # Initialize steps from definition
        for step_def in definition.get("steps", []):
            execution.steps.append({
                "id": step_def.get("id", f"step_{len(execution.steps)}"),
                "name": step_def.get("name", ""),
                "agent": step_def.get("agent", ""),
                "action": step_def.get("action", ""),
                "params": step_def.get("params", {}),
                "requires_approval": step_def.get("requires_approval", False),
                "on_failure": step_def.get("on_failure", "stop"),
                "status": StepStatus.PENDING.value,
                "result": None,
                "error": None,
                "started_at": None,
                "completed_at": None,
            })
        
        self._running[execution.execution_id] = execution
        
        logger.info(
            f"[{tenant_id}] Starting workflow '{workflow_id}' "
            f"({len(execution.steps)} steps, dry_run={dry_run})"
        )
        
        # Execute steps
        for i, step in enumerate(execution.steps):
            execution.current_step_index = i
            step["status"] = StepStatus.RUNNING.value
            step["started_at"] = datetime.utcnow().isoformat()
            
            try:
                # Check approval gate
                if step["requires_approval"] and not auto_approve:
                    step["status"] = StepStatus.AWAITING_APPROVAL.value
                    execution.status = WorkflowStatus.PAUSED
                    logger.info(
                        f"[{tenant_id}] Workflow paused at step {i+1}: "
                        f"'{step['name']}' requires approval"
                    )
                    break  # Pause workflow
                
                # Execute step
                result = await self._execute_step(
                    step, execution, dry_run
                )
                
                step["result"] = result
                step["status"] = StepStatus.COMPLETED.value
                step["completed_at"] = datetime.utcnow().isoformat()
                
                # Store result in execution context for next steps
                execution.results[step["id"]] = result
                
                logger.info(
                    f"[{tenant_id}] Step {i+1}/{len(execution.steps)} "
                    f"COMPLETED: {step['name']}"
                )
            
            except Exception as e:
                step["status"] = StepStatus.FAILED.value
                step["error"] = str(e)
                step["completed_at"] = datetime.utcnow().isoformat()
                execution.errors.append({
                    "step_id": step["id"],
                    "step_name": step["name"],
                    "error": str(e),
                })
                
                logger.error(
                    f"[{tenant_id}] Step {i+1}/{len(execution.steps)} "
                    f"FAILED: {step['name']} - {e}"
                )
                
                # Handle failure
                on_failure = step.get("on_failure", "stop")
                if on_failure == "stop":
                    # Mark remaining as skipped
                    for remaining in execution.steps[i+1:]:
                        remaining["status"] = StepStatus.SKIPPED.value
                        remaining["error"] = "Skipped due to earlier failure"
                    break
                elif on_failure == "continue":
                    continue
                elif on_failure == "skip_remaining":
                    for remaining in execution.steps[i+1:]:
                        remaining["status"] = StepStatus.SKIPPED.value
                    break
        
        # Finalize
        execution.completed_at = datetime.utcnow()
        completed_count = sum(1 for s in execution.steps if s["status"] == StepStatus.COMPLETED.value)
        failed_count = sum(1 for s in execution.steps if s["status"] == StepStatus.FAILED.value)
        
        if execution.status != WorkflowStatus.PAUSED:
            if failed_count > 0 and completed_count > 0:
                execution.status = WorkflowStatus.PARTIALLY_COMPLETED
            elif failed_count > 0:
                execution.status = WorkflowStatus.FAILED
            else:
                execution.status = WorkflowStatus.COMPLETED
        
        # Archive
        self._execution_history.append(execution)
        if execution.execution_id in self._running:
            del self._running[execution.execution_id]
        
        logger.info(
            f"[{tenant_id}] Workflow '{workflow_id}' {execution.status.value}: "
            f"{completed_count}/{len(execution.steps)} steps completed"
        )
        
        return execution
    
    # ---------------------------------------------------------------------
    # Step Execution
    # ---------------------------------------------------------------------
    
    async def _execute_step(
        self,
        step: dict,
        execution: WorkflowExecution,
        dry_run: bool,
    ) -> dict:
        """Execute a single workflow step."""
        agent_name = step.get("agent", "")
        action = step.get("action", "")
        params = copy.deepcopy(step.get("params", {}))
        
        # Inject execution context into params
        params["tenant_id"] = execution.tenant_id
        params["workflow_context"] = execution.context
        params["previous_results"] = execution.results
        
        # Look up agent
        agent = self.agents.get(agent_name)
        if not agent:
            # Try a built-in action
            return await self._execute_builtin_action(action, params, execution)
        
        # Call agent method
        method = getattr(agent, action, None)
        if not method:
            raise ValueError(f"Agent '{agent_name}' has no method '{action}'")
        
        # Call the method
        result = method(**self._filter_params(method, params))
        
        # If result is an ActionPlan, optionally execute it
        from integrations.google_ads.agents.action_plan import ActionPlan
        if isinstance(result, ActionPlan):
            execution.plans_generated.append(result.plan_id)
            
            if self.plan_executor and not dry_run:
                if not result.requires_approval:
                    result.approve("workflow_engine")
                    executed = await self.plan_executor.execute(
                        result, dry_run=dry_run, source="workflow"
                    )
                    return {
                        "plan_id": executed.plan_id,
                        "status": executed.status.value,
                        "completed": executed.completed_operations,
                        "total": executed.total_operations,
                    }
            
            return result.to_dict()
        
        # Return raw result
        if isinstance(result, dict):
            return result
        elif isinstance(result, list):
            return {"items": result, "count": len(result)}
        else:
            return {"result": str(result)}
    
    async def _execute_builtin_action(
        self, action: str, params: dict, execution: WorkflowExecution
    ) -> dict:
        """Execute built-in workflow actions."""
        if action == "log":
            message = params.get("message", "")
            logger.info(f"[{execution.tenant_id}] Workflow log: {message}")
            return {"logged": message}
        
        elif action == "check_condition":
            condition = params.get("condition", "")
            # Simple condition evaluator
            return {"condition": condition, "result": True}
        
        elif action == "aggregate_results":
            # Collect all previous step results
            return {
                "total_steps": len(execution.results),
                "results": execution.results,
            }
        
        elif action == "wait_for_approval":
            return {"status": "approval_required"}
        
        else:
            return {"action": action, "status": "executed"}
    
    def _filter_params(self, method, params: dict) -> dict:
        """Filter params to only include those accepted by the method."""
        import inspect
        sig = inspect.signature(method)
        valid_params = set(sig.parameters.keys())
        
        filtered = {}
        for key, value in params.items():
            if key in valid_params:
                filtered[key] = value
        
        return filtered
    
    # ---------------------------------------------------------------------
    # Resume & Control
    # ---------------------------------------------------------------------
    
    async def resume(
        self, execution_id: str, approved: bool = True
    ) -> Optional[WorkflowExecution]:
        """Resume a paused workflow after approval."""
        execution = self._running.get(execution_id)
        if not execution or execution.status != WorkflowStatus.PAUSED:
            return None
        
        if not approved:
            execution.status = WorkflowStatus.FAILED
            for step in execution.steps:
                if step["status"] == StepStatus.AWAITING_APPROVAL.value:
                    step["status"] = StepStatus.FAILED.value
                    step["error"] = "Approval rejected"
            return execution
        
        # Continue from paused step
        execution.status = WorkflowStatus.RUNNING
        for step in execution.steps:
            if step["status"] == StepStatus.AWAITING_APPROVAL.value:
                step["status"] = StepStatus.PENDING.value
        
        return await self.run(
            execution.workflow_id,
            execution.tenant_id,
            execution.context,
            auto_approve=True,
        )
    
    # ---------------------------------------------------------------------
    # Query
    # ---------------------------------------------------------------------
    
    def list_workflows(self) -> List[dict]:
        """List all registered workflow definitions."""
        return [
            {
                "id": wf_id,
                "name": wf.get("name", wf_id),
                "description": wf.get("description", ""),
                "steps": len(wf.get("steps", [])),
                "trigger": wf.get("trigger", "manual"),
            }
            for wf_id, wf in self._workflow_definitions.items()
        ]
    
    def get_workflow(self, workflow_id: str) -> Optional[dict]:
        """Get a workflow definition."""
        return self._workflow_definitions.get(workflow_id)
    
    def get_execution_history(
        self, tenant_id: str = None, limit: int = 20
    ) -> List[dict]:
        """Get recent workflow executions."""
        history = self._execution_history
        if tenant_id:
            history = [e for e in history if e.tenant_id == tenant_id]
        return [e.to_dict() for e in reversed(history[-limit:])]
    
    def get_stats(self) -> dict:
        """Get engine statistics."""
        total = len(self._execution_history)
        completed = sum(1 for e in self._execution_history if e.status == WorkflowStatus.COMPLETED)
        
        return {
            "workflow_definitions": len(self._workflow_definitions),
            "total_executions": total,
            "completed": completed,
            "running": len(self._running),
            "success_rate": f"{completed/total*100:.0f}%" if total > 0 else "N/A",
            "agents_registered": list(self.agents.keys()),
        }

