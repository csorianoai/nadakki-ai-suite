"""
NADAKKI AI Suite - Workflow Definition & Engine
YAML-based Workflow Execution System
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid
import yaml
import re
import asyncio
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class StepType(Enum):
    OPERATION = "operation"
    AGENT = "agent"
    CONDITION = "condition"
    APPROVAL = "approval"
    PARALLEL = "parallel"


class WorkflowStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED_APPROVAL = "PAUSED_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    name: str
    type: StepType
    config: Dict[str, Any] = field(default_factory=dict)
    
    # For operations
    operation: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    
    # For agents
    agent: Optional[str] = None
    agent_params: Dict[str, Any] = field(default_factory=dict)
    
    # For conditions
    condition: Optional[str] = None
    on_true: Optional[str] = None
    on_false: Optional[str] = None
    
    # For approvals
    approval_message: Optional[str] = None
    timeout_hours: int = 24
    
    # Control flow
    next_step: Optional[str] = None
    on_error: Optional[str] = None
    retries: int = 0


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    name: str
    version: str
    description: str = ""
    
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    
    steps: List[WorkflowStep] = field(default_factory=list)
    start_step: str = ""
    
    timeout_minutes: int = 60
    tags: List[str] = field(default_factory=list)
    
    def get_step(self, name: str) -> Optional[WorkflowStep]:
        for step in self.steps:
            if step.name == name:
                return step
        return None


@dataclass
class WorkflowExecution:
    """State of a workflow execution."""
    execution_id: str
    workflow_name: str
    workflow_version: str
    tenant_id: str
    
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: Optional[str] = None
    
    input_data: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ============================================================================
# WORKFLOW PARSER
# ============================================================================

class WorkflowParser:
    """Parse YAML workflows with simple variable interpolation."""
    
    VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')
    
    def __init__(self, workflows_dir: str = "config/workflows"):
        self.workflows_dir = workflows_dir
        self._cache: Dict[str, WorkflowDefinition] = {}
    
    def parse_file(self, filename: str) -> WorkflowDefinition:
        """Parse a workflow YAML file."""
        import os
        filepath = os.path.join(self.workflows_dir, filename)
        
        if filename in self._cache:
            return self._cache[filename]
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        workflow = self._parse_definition(data)
        self._cache[filename] = workflow
        return workflow
    
    def parse_string(self, yaml_content: str) -> WorkflowDefinition:
        """Parse workflow from YAML string."""
        data = yaml.safe_load(yaml_content)
        return self._parse_definition(data)
    
    def _parse_definition(self, data: Dict) -> WorkflowDefinition:
        """Parse workflow definition from dict."""
        steps = [self._parse_step(s) for s in data.get("steps", [])]
        
        return WorkflowDefinition(
            name=data.get("name", "unnamed"),
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            steps=steps,
            start_step=data.get("start_step", steps[0].name if steps else ""),
            timeout_minutes=data.get("timeout_minutes", 60),
            tags=data.get("tags", [])
        )
    
    def _parse_step(self, data: Dict) -> WorkflowStep:
        """Parse a single step."""
        step_type = StepType(data.get("type", "operation"))
        
        return WorkflowStep(
            name=data.get("name", "unnamed_step"),
            type=step_type,
            config=data.get("config", {}),
            operation=data.get("operation"),
            params=data.get("params", {}),
            agent=data.get("agent"),
            agent_params=data.get("agent_params", {}),
            condition=data.get("condition"),
            on_true=data.get("on_true"),
            on_false=data.get("on_false"),
            approval_message=data.get("approval_message"),
            timeout_hours=data.get("timeout_hours", 24),
            next_step=data.get("next_step"),
            on_error=data.get("on_error"),
            retries=data.get("retries", 0)
        )
    
    def interpolate(self, value: Any, input_data: Dict[str, Any], step_results: Dict[str, Any]) -> Any:
        """Interpolate variables in a value."""
        if isinstance(value, str):
            return self._interpolate_string(value, input_data, step_results)
        elif isinstance(value, dict):
            return {k: self.interpolate(v, input_data, step_results) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.interpolate(v, input_data, step_results) for v in value]
        return value
    
    def _interpolate_string(self, value: str, input_data: Dict, step_results: Dict) -> str:
        """Interpolate variables in a string."""
        def replace_var(match):
            path = match.group(1)
            parts = path.split(".")
            
            try:
                if parts[0] == "input":
                    return str(self._get_nested(input_data, parts[1:]))
                elif parts[0] == "steps" and len(parts) >= 3:
                    step_name = parts[1]
                    if step_name in step_results:
                        return str(self._get_nested(step_results[step_name], parts[2:]))
            except (KeyError, IndexError, TypeError):
                logger.warning(f"Failed to interpolate: {path}")
            
            return match.group(0)
        
        return self.VAR_PATTERN.sub(replace_var, value)
    
    def _get_nested(self, data: Dict, keys: List[str]) -> Any:
        """Get nested value from dict."""
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            else:
                raise KeyError(key)
        return current
    
    def invalidate_cache(self, filename: str = None):
        if filename:
            self._cache.pop(filename, None)
        else:
            self._cache.clear()


# ============================================================================
# WORKFLOW ENGINE
# ============================================================================

class WorkflowEngine:
    """
    Workflow execution engine with:
    - State machine management
    - Step execution
    - Variable interpolation
    - Approval gates
    """
    
    def __init__(self, connector, parser: WorkflowParser, action_plan_executor,
                 saga_journal, telemetry, agents: Dict[str, Any] = None):
        self.connector = connector
        self.parser = parser
        self.action_plan_executor = action_plan_executor
        self.saga_journal = saga_journal
        self.telemetry = telemetry
        self.agents = agents or {}
        self._executions: Dict[str, WorkflowExecution] = {}
    
    async def start(self, workflow_file: str, input_data: Dict[str, Any],
                    tenant_id: str) -> WorkflowExecution:
        """Start a workflow execution."""
        workflow = self.parser.parse_file(workflow_file)
        
        execution = WorkflowExecution(
            execution_id=str(uuid.uuid4()),
            workflow_name=workflow.name,
            workflow_version=workflow.version,
            tenant_id=tenant_id,
            status=WorkflowStatus.RUNNING,
            current_step=workflow.start_step,
            input_data=input_data,
            started_at=datetime.utcnow().isoformat()
        )
        
        self._executions[execution.execution_id] = execution
        
        # Create saga
        if self.saga_journal:
            await self.saga_journal.create_saga(
                tenant_id, workflow.name,
                {"workflow": workflow.name, "input": input_data}
            )
        
        self.telemetry.log_event(
            "workflow_started", tenant_id, execution.execution_id,
            {"workflow": workflow.name, "version": workflow.version}
        )
        
        # Execute workflow
        await self._execute_workflow(execution, workflow)
        
        return execution
    
    async def resume(self, execution_id: str) -> WorkflowExecution:
        """Resume a paused workflow."""
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")
        
        if execution.status != WorkflowStatus.PAUSED_APPROVAL:
            raise ValueError(f"Cannot resume execution in status: {execution.status}")
        
        execution.status = WorkflowStatus.RUNNING
        workflow = self.parser.parse_file(f"{execution.workflow_name}.yaml")
        
        await self._execute_workflow(execution, workflow)
        return execution
    
    async def cancel(self, execution_id: str) -> WorkflowExecution:
        """Cancel a workflow execution."""
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")
        
        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.utcnow().isoformat()
        
        self.telemetry.log_event(
            "workflow_cancelled", execution.tenant_id, execution_id,
            {"workflow": execution.workflow_name}
        )
        
        return execution
    
    async def _execute_workflow(self, execution: WorkflowExecution,
                                workflow: WorkflowDefinition):
        """Execute workflow steps."""
        while execution.status == WorkflowStatus.RUNNING and execution.current_step:
            step = workflow.get_step(execution.current_step)
            if not step:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = f"Step not found: {execution.current_step}"
                break
            
            try:
                result = await self._execute_step(step, execution)
                execution.step_results[step.name] = result
                
                # Determine next step
                next_step = self._get_next_step(step, result)
                
                if next_step:
                    execution.current_step = next_step
                else:
                    execution.status = WorkflowStatus.COMPLETED
                    execution.completed_at = datetime.utcnow().isoformat()
                    execution.current_step = None
                    
            except ApprovalRequiredException as e:
                execution.status = WorkflowStatus.PAUSED_APPROVAL
                self.telemetry.log_event(
                    "workflow_paused", execution.tenant_id, execution.execution_id,
                    {"step": step.name, "reason": str(e)}
                )
                break
                
            except Exception as e:
                logger.error(f"Step {step.name} failed: {e}")
                
                if step.on_error:
                    execution.current_step = step.on_error
                else:
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = str(e)
                    execution.completed_at = datetime.utcnow().isoformat()
        
        if execution.status == WorkflowStatus.COMPLETED:
            self.telemetry.log_event(
                "workflow_completed", execution.tenant_id, execution.execution_id,
                {"workflow": execution.workflow_name, "steps_executed": len(execution.step_results)}
            )
    
    async def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a single workflow step."""
        logger.info(f"Executing step: {step.name} ({step.type.value})")
        
        # Interpolate parameters
        params = self.parser.interpolate(
            step.params, execution.input_data, execution.step_results
        )
        
        if step.type == StepType.OPERATION:
            result = await self.connector.execute(
                operation_name=step.operation,
                payload=params,
                tenant_id=execution.tenant_id
            )
            return {"success": result.success, "data": result.data, "error": result.error_message}
        
        elif step.type == StepType.AGENT:
            agent = self.agents.get(step.agent)
            if not agent:
                raise ValueError(f"Agent not found: {step.agent}")
            
            agent_params = self.parser.interpolate(
                step.agent_params, execution.input_data, execution.step_results
            )
            
            # Execute agent's main method
            if hasattr(agent, 'analyze_and_plan'):
                plan = await agent.analyze_and_plan(execution.tenant_id, **agent_params)
            elif hasattr(agent, 'generate_ad_copy'):
                plan = await agent.generate_ad_copy(execution.tenant_id, **agent_params)
            else:
                raise ValueError(f"Agent {step.agent} has no executable method")
            
            # Execute the action plan
            if plan.operations:
                plan_result = await self.action_plan_executor.execute(plan)
                return {"plan_id": plan.plan_id, "success": plan_result.success,
                        "executed": plan_result.executed_operations, "results": plan_result.results}
            
            return {"plan_id": plan.plan_id, "analysis": plan.analysis, "no_operations": True}
        
        elif step.type == StepType.CONDITION:
            condition_result = self._evaluate_condition(
                step.condition, execution.input_data, execution.step_results
            )
            return {"condition": step.condition, "result": condition_result}
        
        elif step.type == StepType.APPROVAL:
            raise ApprovalRequiredException(step.approval_message or "Approval required")
        
        return {}
    
    def _get_next_step(self, step: WorkflowStep, result: Dict[str, Any]) -> Optional[str]:
        """Determine the next step based on result."""
        if step.type == StepType.CONDITION:
            if result.get("result"):
                return step.on_true
            return step.on_false
        
        return step.next_step
    
    def _evaluate_condition(self, condition: str, input_data: Dict, step_results: Dict) -> bool:
        """Evaluate a simple condition."""
        # Simple evaluation - in production use a proper expression parser
        try:
            interpolated = self.parser._interpolate_string(condition, input_data, step_results)
            # Very basic evaluation
            if ">" in interpolated:
                left, right = interpolated.split(">")
                return float(left.strip()) > float(right.strip())
            elif "<" in interpolated:
                left, right = interpolated.split("<")
                return float(left.strip()) < float(right.strip())
            elif "==" in interpolated:
                left, right = interpolated.split("==")
                return left.strip() == right.strip()
            return bool(interpolated)
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return False
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution by ID."""
        return self._executions.get(execution_id)
    
    def list_executions(self, tenant_id: str = None) -> List[WorkflowExecution]:
        """List all executions, optionally filtered by tenant."""
        executions = list(self._executions.values())
        if tenant_id:
            executions = [e for e in executions if e.tenant_id == tenant_id]
        return executions


class ApprovalRequiredException(Exception):
    """Raised when a workflow step requires approval."""
    pass
