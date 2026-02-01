"""
NADAKKI AI Suite - Google Ads Orchestrator Agent
Intelligent Agent Orchestration and Workflow Management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

from core.agents.action_plan import ActionPlan, OperationPriority

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    MAXIMIZE_CONVERSIONS = "maximize_conversions"
    MINIMIZE_CPA = "minimize_cpa"
    MAXIMIZE_ROAS = "maximize_roas"
    BUDGET_EFFICIENCY = "budget_efficiency"
    TRAFFIC_GROWTH = "traffic_growth"


class GoogleAdsOrchestratorAgent:
    """
    Orchestrator agent that:
    - Analyzes account state
    - Selects appropriate agents/workflows
    - Coordinates multi-agent execution
    - Manages campaign optimization cycles
    
    USAGE:
        orchestrator = GoogleAdsOrchestratorAgent(workflow_engine, agents)
        result = await orchestrator.run_optimization_cycle(tenant_id, objective)
    """
    
    AGENT_ID = "google_ads_orchestrator"
    AGENT_NAME = "GoogleAdsOrchestratorAgent"
    
    # Workflow mapping by objective
    WORKFLOW_MAP = {
        OptimizationObjective.BUDGET_EFFICIENCY: "budget_adjustment.yaml",
        OptimizationObjective.MAXIMIZE_CONVERSIONS: "daily_optimization.yaml",
        OptimizationObjective.MINIMIZE_CPA: "daily_optimization.yaml",
        OptimizationObjective.MAXIMIZE_ROAS: "daily_optimization.yaml",
        OptimizationObjective.TRAFFIC_GROWTH: "traffic_growth.yaml"
    }
    
    # Agent mapping by task type
    AGENT_MAP = {
        "budget_pacing": "budget_pacing_agent",
        "ad_copy": "rsa_copy_agent",
        "search_terms": "search_terms_agent",
        "keyword_expansion": "keyword_expansion_agent",
        "bid_adjustment": "bid_adjustment_agent"
    }
    
    def __init__(self, workflow_engine, connector, agents: Dict[str, Any], policy_engine):
        self.workflow_engine = workflow_engine
        self.connector = connector
        self.agents = agents
        self.policy_engine = policy_engine
    
    async def run_optimization_cycle(
        self,
        tenant_id: str,
        objective: OptimizationObjective = OptimizationObjective.BUDGET_EFFICIENCY,
        campaign_ids: List[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Run a complete optimization cycle.
        
        Args:
            tenant_id: Target tenant
            objective: Optimization objective
            campaign_ids: Specific campaigns (optional)
            dry_run: If True, don't execute changes
            
        Returns:
            Summary of optimization actions taken
        """
        logger.info(f"Starting optimization cycle for {tenant_id} with objective: {objective.value}")
        
        cycle_result = {
            "tenant_id": tenant_id,
            "objective": objective.value,
            "started_at": datetime.utcnow().isoformat(),
            "phases": [],
            "total_operations": 0,
            "successful_operations": 0,
            "errors": []
        }
        
        try:
            # Phase 1: Account Analysis
            analysis = await self._analyze_account(tenant_id, campaign_ids)
            cycle_result["phases"].append({
                "name": "account_analysis",
                "status": "completed",
                "data": analysis
            })
            
            # Phase 2: Select and prioritize agents
            agent_sequence = self._select_agents(objective, analysis)
            cycle_result["phases"].append({
                "name": "agent_selection",
                "status": "completed",
                "agents": agent_sequence
            })
            
            # Phase 3: Execute agents in sequence
            for agent_name in agent_sequence:
                agent_result = await self._execute_agent(
                    tenant_id, agent_name, analysis, dry_run
                )
                
                cycle_result["phases"].append({
                    "name": f"agent_{agent_name}",
                    "status": "completed" if agent_result.get("success") else "failed",
                    "data": agent_result
                })
                
                cycle_result["total_operations"] += agent_result.get("operations_count", 0)
                cycle_result["successful_operations"] += agent_result.get("successful_operations", 0)
                
                if agent_result.get("errors"):
                    cycle_result["errors"].extend(agent_result["errors"])
            
            cycle_result["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Optimization cycle failed: {e}")
            cycle_result["status"] = "failed"
            cycle_result["errors"].append(str(e))
        
        cycle_result["completed_at"] = datetime.utcnow().isoformat()
        
        return cycle_result
    
    async def run_workflow(
        self,
        tenant_id: str,
        workflow_name: str,
        input_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Run a specific workflow.
        
        Args:
            tenant_id: Target tenant
            workflow_name: Name of workflow file
            input_data: Input parameters
            
        Returns:
            Workflow execution result
        """
        execution = await self.workflow_engine.start(
            workflow_file=workflow_name,
            input_data=input_data or {},
            tenant_id=tenant_id
        )
        
        return {
            "execution_id": execution.execution_id,
            "workflow": execution.workflow_name,
            "status": execution.status.value,
            "step_results": execution.step_results,
            "output": execution.output_data
        }
    
    async def get_recommendations(
        self,
        tenant_id: str,
        campaign_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Get optimization recommendations without executing.
        
        Returns analysis and recommendations from all relevant agents.
        """
        analysis = await self._analyze_account(tenant_id, campaign_ids)
        
        recommendations = {
            "tenant_id": tenant_id,
            "generated_at": datetime.utcnow().isoformat(),
            "account_health": self._calculate_health_score(analysis),
            "recommendations": []
        }
        
        # Get recommendations from each agent
        if "budget_pacing_agent" in self.agents:
            agent = self.agents["budget_pacing_agent"]
            plan = await agent.analyze_and_plan(tenant_id, analysis.get("campaigns"))
            
            if plan.operations:
                recommendations["recommendations"].append({
                    "agent": "budget_pacing",
                    "priority": "high" if plan.risk_score < 0.5 else "medium",
                    "summary": plan.rationale,
                    "operations": len(plan.operations),
                    "risk_score": plan.risk_score
                })
        
        if "search_terms_agent" in self.agents:
            agent = self.agents["search_terms_agent"]
            plan = await agent.analyze_and_clean(tenant_id)
            
            if plan.operations:
                recommendations["recommendations"].append({
                    "agent": "search_terms",
                    "priority": "medium",
                    "summary": plan.rationale,
                    "operations": len(plan.operations),
                    "potential_savings": plan.analysis.get("potential_savings_usd", 0)
                })
        
        return recommendations
    
    async def schedule_daily_optimization(
        self,
        tenant_id: str,
        objective: OptimizationObjective = OptimizationObjective.BUDGET_EFFICIENCY
    ) -> Dict[str, Any]:
        """Schedule daily optimization workflow."""
        workflow_file = self.WORKFLOW_MAP.get(objective, "daily_optimization.yaml")
        
        return await self.run_workflow(
            tenant_id=tenant_id,
            workflow_name=workflow_file,
            input_data={
                "objective": objective.value,
                "scheduled": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================
    
    async def _analyze_account(
        self,
        tenant_id: str,
        campaign_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze account state."""
        result = await self.connector.get_metrics(tenant_id, campaign_ids)
        
        if not result.success:
            return {"error": result.error_message, "campaigns": []}
        
        campaigns = result.data.get("campaigns", [])
        
        # Calculate aggregates
        total_spend = sum(c.get("cost_micros", 0) for c in campaigns) / 1_000_000
        total_conversions = sum(c.get("conversions", 0) for c in campaigns)
        total_clicks = sum(c.get("clicks", 0) for c in campaigns)
        total_impressions = sum(c.get("impressions", 0) for c in campaigns)
        
        return {
            "campaigns": campaigns,
            "campaign_count": len(campaigns),
            "active_campaigns": len([c for c in campaigns if c.get("status") == "ENABLED"]),
            "total_spend_usd": total_spend,
            "total_conversions": total_conversions,
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "avg_ctr": total_clicks / total_impressions if total_impressions > 0 else 0,
            "avg_cpc": total_spend / total_clicks if total_clicks > 0 else 0,
            "avg_cpa": total_spend / total_conversions if total_conversions > 0 else 0
        }
    
    def _select_agents(
        self,
        objective: OptimizationObjective,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Select and prioritize agents based on objective and analysis."""
        agents = []
        
        # Always run budget pacing for efficiency
        if objective == OptimizationObjective.BUDGET_EFFICIENCY:
            agents.append("budget_pacing_agent")
        
        # Add search terms for CPA optimization
        if objective in [OptimizationObjective.MINIMIZE_CPA, OptimizationObjective.MAXIMIZE_ROAS]:
            agents.append("search_terms_agent")
            agents.append("budget_pacing_agent")
        
        # Add all agents for conversion maximization
        if objective == OptimizationObjective.MAXIMIZE_CONVERSIONS:
            agents.extend(["budget_pacing_agent", "search_terms_agent"])
        
        # Traffic growth focuses on budget and keywords
        if objective == OptimizationObjective.TRAFFIC_GROWTH:
            agents.extend(["budget_pacing_agent"])
        
        # Remove duplicates while preserving order
        seen = set()
        return [a for a in agents if not (a in seen or seen.add(a))]
    
    async def _execute_agent(
        self,
        tenant_id: str,
        agent_name: str,
        analysis: Dict[str, Any],
        dry_run: bool
    ) -> Dict[str, Any]:
        """Execute a single agent."""
        agent = self.agents.get(agent_name)
        if not agent:
            return {"success": False, "error": f"Agent not found: {agent_name}"}
        
        try:
            # Get action plan from agent
            if hasattr(agent, 'analyze_and_plan'):
                plan = await agent.analyze_and_plan(tenant_id, analysis.get("campaigns"))
            elif hasattr(agent, 'analyze_and_clean'):
                plan = await agent.analyze_and_clean(tenant_id)
            else:
                return {"success": False, "error": "Agent has no executable method"}
            
            if dry_run or not plan.operations:
                return {
                    "success": True,
                    "dry_run": True,
                    "operations_count": len(plan.operations),
                    "successful_operations": 0,
                    "plan_id": plan.plan_id,
                    "analysis": plan.analysis
                }
            
            # Execute plan
            from core.execution.action_plan_executor import ActionPlanExecutor
            executor = ActionPlanExecutor(
                self.connector,
                self.workflow_engine.telemetry
            )
            
            result = await executor.execute(plan)
            
            return {
                "success": result.success,
                "operations_count": result.executed_operations + result.failed_operations,
                "successful_operations": result.executed_operations,
                "plan_id": plan.plan_id,
                "results": result.results,
                "errors": [result.error_message] if result.error_message else []
            }
            
        except Exception as e:
            logger.error(f"Agent {agent_name} execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "operations_count": 0,
                "successful_operations": 0
            }
    
    def _calculate_health_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall account health score (0-100)."""
        score = 50.0  # Base score
        
        # CTR contribution (0-20 points)
        ctr = analysis.get("avg_ctr", 0)
        if ctr > 0.05:
            score += 20
        elif ctr > 0.02:
            score += 10
        
        # CPA contribution (0-20 points) - lower is better
        cpa = analysis.get("avg_cpa", 0)
        if cpa > 0 and cpa < 50:
            score += 20
        elif cpa > 0 and cpa < 100:
            score += 10
        
        # Active campaign ratio (0-10 points)
        total = analysis.get("campaign_count", 0)
        active = analysis.get("active_campaigns", 0)
        if total > 0 and active / total > 0.8:
            score += 10
        
        return min(score, 100.0)
