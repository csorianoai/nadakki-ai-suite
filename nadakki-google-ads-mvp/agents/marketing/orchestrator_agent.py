# ===============================================================================
# NADAKKI AI Suite - OrchestratorIA
# agents/marketing/orchestrator_agent.py
# Day 5 - Component 3 of 3
# ===============================================================================

"""
Orchestrator Meta-Agent - decides WHICH workflow to run and WHEN.

This is the "brain" that coordinates all other agents:
1. Receives a high-level request or scheduled trigger
2. Analyzes the situation (performance data, context)
3. Selects the appropriate workflow
4. Triggers execution through the WorkflowEngine

The OrchestratorIA is the only agent a user/scheduler needs to interact with.
All other agents are called indirectly through workflows.

Usage:
    orchestrator = OrchestratorIA(workflow_engine, knowledge_store)
    
    # High-level request
    result = await orchestrator.handle_request(
        tenant_id="bank01",
        request_type="optimize",
        context={"urgency": "normal"},
    )
    
    # Scheduled trigger
    result = await orchestrator.handle_schedule(
        tenant_id="bank01",
        trigger="weekly_optimization",
    )
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from core.workflows.engine import WorkflowEngine
from core.knowledge.yaml_store import YamlKnowledgeStore

logger = logging.getLogger("nadakki.agents.orchestrator")


class OrchestratorIA:
    """
    Meta-Agent that coordinates all Google Ads agents via workflows.
    """
    
    AGENT_NAME = "OrchestratorIA"
    VERSION = "1.0.0"
    
    # Request type > workflow mapping
    REQUEST_WORKFLOW_MAP = {
        "optimize": "weekly_optimization",
        "weekly": "weekly_optimization",
        "launch_campaign": "new_campaign_launch",
        "new_campaign": "new_campaign_launch",
        "adjust_budget": "budget_adjustment",
        "budget": "budget_adjustment",
        "emergency": "emergency_pause",
        "pause": "emergency_pause",
        "clean_search_terms": "search_terms_cleanup",
        "search_terms": "search_terms_cleanup",
        "cleanup": "search_terms_cleanup",
    }
    
    # Priority mapping
    PRIORITY_MAP = {
        "critical": ["emergency_pause"],
        "high": ["budget_adjustment", "search_terms_cleanup"],
        "normal": ["weekly_optimization", "new_campaign_launch"],
    }
    
    def __init__(
        self,
        workflow_engine: WorkflowEngine,
        knowledge_store: YamlKnowledgeStore = None,
    ):
        self.engine = workflow_engine
        self.kb = knowledge_store
        self._request_history: List[dict] = []
        logger.info(f"{self.AGENT_NAME} v{self.VERSION} initialized")
    
    # ---------------------------------------------------------------------
    # Main Entry Points
    # ---------------------------------------------------------------------
    
    async def handle_request(
        self,
        tenant_id: str,
        request_type: str,
        context: dict = None,
        auto_approve: bool = False,
    ) -> dict:
        """
        Handle a high-level request by selecting and running the right workflow.
        
        Args:
            tenant_id: Tenant ID
            request_type: Type of request (optimize, launch_campaign, emergency, etc.)
            context: Additional context to pass to the workflow
            auto_approve: Auto-approve approval gates
        """
        context = context or {}
        
        # 1. Select workflow
        workflow_id = self._select_workflow(request_type, context)
        
        if not workflow_id:
            return {
                "status": "error",
                "message": f"No workflow found for request type: {request_type}",
                "available_types": list(self.REQUEST_WORKFLOW_MAP.keys()),
            }
        
        logger.info(
            f"[{tenant_id}] Orchestrator: request_type='{request_type}' > "
            f"workflow='{workflow_id}'"
        )
        
        # 2. Run workflow
        try:
            execution = await self.engine.run(
                workflow_id=workflow_id,
                tenant_id=tenant_id,
                context=context,
                auto_approve=auto_approve,
            )
            
            result = {
                "status": "success",
                "request_type": request_type,
                "workflow_id": workflow_id,
                "execution_id": execution.execution_id,
                "workflow_status": execution.status.value,
                "steps_completed": sum(
                    1 for s in execution.steps
                    if s.get("status") == "completed"
                ),
                "total_steps": len(execution.steps),
                "plans_generated": execution.plans_generated,
            }
        
        except Exception as e:
            result = {
                "status": "error",
                "request_type": request_type,
                "workflow_id": workflow_id,
                "error": str(e),
            }
            logger.error(f"[{tenant_id}] Orchestrator error: {e}")
        
        # Record
        self._request_history.append({
            "tenant_id": tenant_id,
            "request_type": request_type,
            "workflow_id": workflow_id,
            "result_status": result["status"],
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return result
    
    async def handle_schedule(
        self,
        tenant_id: str,
        trigger: str,
        context: dict = None,
    ) -> dict:
        """
        Handle a scheduled trigger.
        Maps trigger names to workflows.
        """
        trigger_workflow_map = {
            "weekly_optimization": "weekly_optimization",
            "schedule_weekly": "weekly_optimization",
            "search_terms_cleanup": "search_terms_cleanup",
            "every_monday": "weekly_optimization",
            "every_wednesday": "search_terms_cleanup",
        }
        
        workflow_id = trigger_workflow_map.get(trigger)
        if not workflow_id:
            return {
                "status": "error",
                "message": f"No workflow for trigger: {trigger}",
            }
        
        return await self.handle_request(
            tenant_id, workflow_id, context, auto_approve=True
        )
    
    # ---------------------------------------------------------------------
    # Intelligent Routing
    # ---------------------------------------------------------------------
    
    async def auto_triage(
        self,
        tenant_id: str,
        metrics: dict,
        industry: str = "financial_services",
    ) -> dict:
        """
        Automatically assess performance and decide which workflow to run.
        
        Args:
            metrics: Current campaign metrics (ctr, cpa, conv_rate, budget_pacing)
        """
        cpa = metrics.get("cpa", 0)
        ctr = metrics.get("ctr", 0)
        budget_pacing = metrics.get("budget_pacing", 100)
        
        # Get thresholds from KB
        thresholds = {}
        if self.kb:
            benchmarks = self.kb.get_benchmarks(tenant_id, industry)
            thresholds = benchmarks.get("thresholds", {})
        
        critical_thresholds = thresholds.get("critical", {})
        warning_thresholds = thresholds.get("warning", {})
        
        benchmark_cpa = 50.0  # Default
        if self.kb:
            b = self.kb.get_benchmarks(tenant_id, industry)
            benchmark_cpa = b.get("metrics", {}).get("search", {}).get("avg_cpa", 50.0)
        
        # Decision logic
        urgency = "normal"
        recommended_workflows = []
        reasons = []
        
        # Critical: CPA way too high
        cpa_multiplier = critical_thresholds.get("cpa_multiplier", 3.0)
        if cpa > benchmark_cpa * cpa_multiplier:
            urgency = "critical"
            recommended_workflows.append("emergency_pause")
            reasons.append(f"CPA ${cpa:.2f} is {cpa/benchmark_cpa:.1f}x benchmark")
        
        # Critical: Budget overspend
        if budget_pacing > 150:
            urgency = "critical"
            recommended_workflows.append("emergency_pause")
            reasons.append(f"Budget pacing at {budget_pacing}% (critical threshold: 150%)")
        
        # Warning: High CPA
        warn_cpa_mult = warning_thresholds.get("cpa_multiplier", 2.0)
        if cpa > benchmark_cpa * warn_cpa_mult and urgency != "critical":
            urgency = "high"
            recommended_workflows.append("budget_adjustment")
            reasons.append(f"CPA ${cpa:.2f} above warning threshold")
        
        # Warning: Low CTR
        if ctr < warning_thresholds.get("ctr_minimum", 2.0):
            if urgency not in ("critical",):
                urgency = "high"
            recommended_workflows.append("weekly_optimization")
            reasons.append(f"CTR {ctr:.2f}% below minimum")
        
        # Normal: Regular optimization needed
        if not recommended_workflows:
            recommended_workflows.append("weekly_optimization")
            reasons.append("Regular optimization cycle")
        
        # Execute the highest-priority workflow
        primary_workflow = recommended_workflows[0]
        
        result = await self.handle_request(
            tenant_id, primary_workflow,
            context={"urgency": urgency, "metrics": metrics},
            auto_approve=(urgency == "critical"),
        )
        
        result["triage"] = {
            "urgency": urgency,
            "recommended_workflows": recommended_workflows,
            "reasons": reasons,
            "benchmark_cpa": benchmark_cpa,
        }
        
        return result
    
    # ---------------------------------------------------------------------
    # Workflow Selection
    # ---------------------------------------------------------------------
    
    def _select_workflow(self, request_type: str, context: dict) -> Optional[str]:
        """Select the best workflow for a request."""
        # Direct mapping first
        workflow_id = self.REQUEST_WORKFLOW_MAP.get(request_type.lower())
        if workflow_id:
            # Verify it exists in the engine
            if self.engine.get_workflow(workflow_id):
                return workflow_id
        
        # Try request_type as direct workflow_id
        if self.engine.get_workflow(request_type):
            return request_type
        
        return None
    
    # ---------------------------------------------------------------------
    # Status & History
    # ---------------------------------------------------------------------
    
    def get_available_actions(self) -> List[dict]:
        """Get all available request types and their workflows."""
        actions = []
        seen = set()
        
        for request_type, workflow_id in self.REQUEST_WORKFLOW_MAP.items():
            if workflow_id not in seen:
                wf = self.engine.get_workflow(workflow_id)
                actions.append({
                    "request_types": [
                        k for k, v in self.REQUEST_WORKFLOW_MAP.items()
                        if v == workflow_id
                    ],
                    "workflow_id": workflow_id,
                    "name": wf.get("name", workflow_id) if wf else workflow_id,
                    "steps": len(wf.get("steps", [])) if wf else 0,
                })
                seen.add(workflow_id)
        
        return actions
    
    def get_request_history(
        self, tenant_id: str = None, limit: int = 20
    ) -> List[dict]:
        """Get recent orchestrator requests."""
        history = self._request_history
        if tenant_id:
            history = [h for h in history if h["tenant_id"] == tenant_id]
        return list(reversed(history[-limit:]))
    
    def get_stats(self) -> dict:
        """Get orchestrator statistics."""
        total = len(self._request_history)
        success = sum(1 for h in self._request_history if h["result_status"] == "success")
        
        return {
            "total_requests": total,
            "successful": success,
            "available_workflows": len(self.engine.list_workflows()),
            "available_agents": list(self.engine.agents.keys()),
            "success_rate": f"{success/total*100:.0f}%" if total > 0 else "N/A",
        }
