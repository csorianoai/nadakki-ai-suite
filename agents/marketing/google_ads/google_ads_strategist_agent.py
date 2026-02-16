# ===============================================================================
# NADAKKI AI Suite - GoogleAdsStrategistIA
# agents/marketing/google_ads_strategist_agent.py
# Day 3 - Component 3 of 4
# ===============================================================================

"""
Knowledge-Based Agent: Strategist + Builder combined.

This agent:
1. Reads the Knowledge Base (rules, playbooks, benchmarks, guardrails)
2. Matches rules to the current campaign context
3. Generates a strategy recommendation
4. Produces an ActionPlan with concrete operations

It does NOT execute operations - it only proposes plans.
The ActionPlanExecutor (Day 4) handles execution.

Usage:
    strategist = GoogleAdsStrategistIA(knowledge_store)
    
    plan = strategist.propose_strategy(
        tenant_id="bank01",
        context={
            "goal": "leads",
            "channel": "search",
            "monthly_budget": 5000,
            "industry": "financial_services",
        }
    )
    
    if plan.requires_approval:
        # Send to dashboard for human review
        pass
    else:
        # Auto-execute via ActionPlanExecutor
        pass
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from integrations.google_ads.knowledge.yaml_store import YamlKnowledgeStore
from integrations.google_ads.agents.action_plan import ActionPlan, PlannedOperation, OperationPriority, PlanStatus

logger = logging.getLogger("nadakki.agents.strategist")


class GoogleAdsStrategistIA:
    """
    Knowledge-Based Google Ads Strategist Agent.
    
    Combines Strategist + Builder in one agent:
    - Strategist: Reads rules, matches context, generates recommendations
    - Builder: Translates recommendations into ActionPlan operations
    """
    
    AGENT_NAME = "GoogleAdsStrategistIA"
    VERSION = "1.0.0"
    
    def __init__(self, knowledge_store: YamlKnowledgeStore):
        self.kb = knowledge_store
        logger.info(f"{self.AGENT_NAME} v{self.VERSION} initialized")
    
    # ---------------------------------------------------------------------
    # Main Entry Point
    # ---------------------------------------------------------------------
    
    def propose_strategy(
        self,
        tenant_id: str,
        context: dict,
    ) -> ActionPlan:
        """
        Generate a strategy and ActionPlan based on context.
        
        Args:
            tenant_id: Tenant identifier
            context: Campaign context dict. Expected keys:
                - goal: "leads" | "sales" | "awareness"
                - channel: "search" | "display" | "pmax"
                - monthly_budget: float (USD)
                - industry: str (e.g., "financial_services")
                - phase: "launch" | "optimization" | "scaling" (optional)
                - current_cpa: float (optional)
                - current_ctr: float (optional)
                - current_quality_score: int (optional)
                - conversions_last_30d: int (optional)
                
        Returns:
            ActionPlan with proposed operations
        """
        industry = context.get("industry", "financial_services")
        goal = context.get("goal", "leads")
        channel = context.get("channel", "search")
        budget = context.get("monthly_budget", 0)
        
        logger.info(
            f"[{tenant_id}] Generating strategy: "
            f"goal={goal}, channel={channel}, budget=${budget}, industry={industry}"
        )
        
        # 1. Match applicable rules
        matched_rules = self.kb.match_rules(tenant_id, context, industry)
        
        # 2. Get benchmarks
        benchmarks = self.kb.get_benchmarks(tenant_id, industry)
        
        # 3. Get guardrails
        guardrails = self.kb.get_guardrails(tenant_id, industry)
        
        # 4. Build strategy
        plan = ActionPlan(
            tenant_id=tenant_id,
            agent_name=self.AGENT_NAME,
            title=f"{goal.title()} Strategy - {channel.title()} - ${budget:,.0f}/mo",
            description=self._build_description(context, matched_rules, benchmarks),
            rationale=self._build_rationale(matched_rules, benchmarks),
            rules_consulted=[r["id"] for r in matched_rules],
            benchmarks_referenced=benchmarks.get("metrics", {}),
        )
        
        # 5. Generate operations based on context
        self._add_budget_operations(plan, context, guardrails)
        self._add_optimization_operations(plan, context, matched_rules)
        self._add_monitoring_operations(plan, context, benchmarks)
        
        # 6. Calculate risk and set approval
        plan.risk_score = self._calculate_risk(plan, context)
        plan.requires_approval = budget > 5000 or plan.risk_score > 0.5
        
        plan.propose()
        
        logger.info(
            f"[{tenant_id}] Strategy proposed: {plan.title} "
            f"({plan.total_operations} ops, risk={plan.risk_score:.1%}, "
            f"approval={'required' if plan.requires_approval else 'auto'})"
        )
        
        return plan
    
    # ---------------------------------------------------------------------
    # Strategy Building
    # ---------------------------------------------------------------------
    
    def _build_description(
        self, context: dict, rules: list, benchmarks: dict
    ) -> str:
        """Build a human-readable strategy description."""
        goal = context.get("goal", "leads")
        channel = context.get("channel", "search")
        budget = context.get("monthly_budget", 0)
        industry = context.get("industry", "unknown")
        
        metrics = benchmarks.get("metrics", {}).get(channel, {})
        avg_cpa = metrics.get("avg_cpa", "N/A")
        avg_ctr = metrics.get("avg_ctr", "N/A")
        
        desc = (
            f"Strategy for {goal} generation via {channel} campaigns "
            f"with a ${budget:,.0f}/month budget in the {industry} vertical. "
            f"Based on {len(rules)} matched rules from the knowledge base. "
            f"Industry benchmarks: avg CPA ${avg_cpa}, avg CTR {avg_ctr}%."
        )
        
        return desc
    
    def _build_rationale(self, rules: list, benchmarks: dict) -> str:
        """Build the rationale from matched rules."""
        if not rules:
            return "No specific rules matched. Using general best practices."
        
        rationale_parts = []
        for rule in rules[:5]:  # Top 5 rules
            name = rule.get("name", rule.get("id", ""))
            confidence = rule.get("confidence", 0)
            recs = rule.get("then", {}).get("recommendations", [])
            
            if recs:
                rationale_parts.append(
                    f"* {name} (confidence: {confidence:.0%}): {recs[0]}"
                )
        
        return "Applied rules:\n" + "\n".join(rationale_parts)
    
    # ---------------------------------------------------------------------
    # Operation Generation
    # ---------------------------------------------------------------------
    
    def _add_budget_operations(
        self, plan: ActionPlan, context: dict, guardrails: dict
    ):
        """Generate budget-related operations."""
        budget = context.get("monthly_budget", 0)
        if budget <= 0:
            return
        
        daily_budget = round(budget / 30.4, 2)
        
        budget_guardrails = guardrails.get("budget_guardrails", {})
        max_daily = budget_guardrails.get("max_daily_budget_usd", 50000)
        
        if daily_budget > max_daily:
            daily_budget = max_daily
        
        # Set initial daily budget
        plan.add_operation(
            operation_name="update_campaign_budget@v1",
            payload={
                "budget_id": "auto_detect",
                "new_budget": daily_budget,
                "previous_budget": 0,
            },
            description=f"Set daily budget to ${daily_budget:.2f} (${budget:,.0f}/month / 30.4)",
            priority=OperationPriority.HIGH,
        )
    
    def _add_optimization_operations(
        self, plan: ActionPlan, context: dict, rules: list
    ):
        """Generate optimization operations based on matched rules."""
        current_ctr = context.get("current_ctr")
        current_cpa = context.get("current_cpa")
        quality_score = context.get("current_quality_score")
        
        # If CTR is low, recommend ad copy review
        if current_ctr is not None and current_ctr < 2.0:
            plan.add_operation(
                operation_name="get_campaign_metrics@v1",
                payload={"metrics": ["ctr", "impressions", "clicks"]},
                description="Fetch current CTR metrics for underperforming campaigns",
                priority=OperationPriority.HIGH,
            )
        
        # If CPA is high, recommend budget adjustment
        if current_cpa is not None:
            benchmarks = self.kb.get_benchmarks(
                plan.tenant_id, context.get("industry")
            )
            metrics = benchmarks.get("metrics", {}).get(
                context.get("channel", "search"), {}
            )
            avg_cpa = metrics.get("avg_cpa", 50)
            
            if current_cpa > avg_cpa * 1.5:
                plan.add_operation(
                    operation_name="get_campaign_metrics@v1",
                    payload={"metrics": ["cpa", "conversions", "cost"]},
                    description=f"Audit high CPA (${current_cpa:.2f} vs benchmark ${avg_cpa:.2f})",
                    priority=OperationPriority.HIGH,
                )
        
        # If quality score is low
        if quality_score is not None and quality_score < 6:
            plan.add_operation(
                operation_name="get_campaign_metrics@v1",
                payload={"metrics": ["quality_score", "ad_relevance", "landing_page_experience"]},
                description=f"Investigate low quality score ({quality_score})",
                priority=OperationPriority.MEDIUM,
            )
    
    def _add_monitoring_operations(
        self, plan: ActionPlan, context: dict, benchmarks: dict
    ):
        """Add monitoring/metrics operations."""
        plan.add_operation(
            operation_name="get_campaign_metrics@v1",
            payload={},
            description="Fetch baseline metrics for strategy tracking",
            priority=OperationPriority.LOW,
        )
    
    # ---------------------------------------------------------------------
    # Risk Calculation
    # ---------------------------------------------------------------------
    
    def _calculate_risk(self, plan: ActionPlan, context: dict) -> float:
        """
        Calculate risk score (0.0 to 1.0) based on:
        - Budget amount
        - Number of write operations
        - Whether it's a new campaign vs optimization
        """
        risk = 0.0
        budget = context.get("monthly_budget", 0)
        
        # Budget risk
        if budget > 10000:
            risk += 0.3
        elif budget > 5000:
            risk += 0.2
        elif budget > 1000:
            risk += 0.1
        
        # Write operation risk
        write_ops = sum(
            1 for op in plan.operations
            if "update" in op.operation_name or "create" in op.operation_name
        )
        risk += write_ops * 0.1
        
        # Phase risk
        phase = context.get("phase", "optimization")
        if phase == "launch":
            risk += 0.15
        elif phase == "scaling":
            risk += 0.1
        
        return min(risk, 1.0)
    
    # ---------------------------------------------------------------------
    # Convenience Methods
    # ---------------------------------------------------------------------
    
    def get_recommendations(
        self,
        tenant_id: str,
        context: dict,
    ) -> List[dict]:
        """
        Get recommendations without generating a full ActionPlan.
        Useful for dashboard display.
        """
        industry = context.get("industry", "financial_services")
        rules = self.kb.match_rules(tenant_id, context, industry)
        
        recommendations = []
        for rule in rules:
            recs = rule.get("then", {}).get("recommendations", [])
            for rec in recs:
                recommendations.append({
                    "rule_id": rule.get("id"),
                    "rule_name": rule.get("name"),
                    "recommendation": rec,
                    "confidence": rule.get("confidence", 0),
                    "kpis": rule.get("then", {}).get("kpis", []),
                    "tags": rule.get("tags", []),
                })
        
        return recommendations
    
    def analyze_performance(
        self,
        tenant_id: str,
        metrics: dict,
        industry: str = "financial_services",
    ) -> dict:
        """
        Analyze current performance against benchmarks.
        
        Args:
            metrics: {"ctr": 2.5, "cpa": 45, "conv_rate": 4.2, ...}
            industry: Industry for benchmark comparison
            
        Returns:
            Analysis dict with comparisons and recommendations
        """
        benchmarks = self.kb.get_benchmarks(tenant_id, industry)
        benchmark_metrics = benchmarks.get("metrics", {}).get("search", {})
        thresholds = benchmarks.get("thresholds", {})
        
        analysis = {"comparisons": [], "alerts": [], "overall": "good"}
        
        metric_map = {
            "ctr": ("avg_ctr", "higher_is_better"),
            "cpa": ("avg_cpa", "lower_is_better"),
            "conv_rate": ("avg_conv_rate", "higher_is_better"),
        }
        
        for metric_name, (bench_key, direction) in metric_map.items():
            if metric_name in metrics and bench_key in benchmark_metrics:
                actual = metrics[metric_name]
                benchmark = benchmark_metrics[bench_key]
                
                if direction == "higher_is_better":
                    pct_diff = ((actual - benchmark) / benchmark) * 100
                    status = "above" if actual >= benchmark else "below"
                else:
                    pct_diff = ((benchmark - actual) / benchmark) * 100
                    status = "above" if actual <= benchmark else "below"
                
                comparison = {
                    "metric": metric_name,
                    "actual": actual,
                    "benchmark": benchmark,
                    "difference_pct": round(pct_diff, 1),
                    "status": status,
                }
                analysis["comparisons"].append(comparison)
                
                # Check thresholds
                warning_thresholds = thresholds.get("warning", {})
                critical_thresholds = thresholds.get("critical", {})
                
                if metric_name == "cpa" and actual > benchmark * critical_thresholds.get("cpa_multiplier", 3):
                    analysis["alerts"].append({
                        "severity": "critical",
                        "message": f"CPA (${actual:.2f}) is {actual/benchmark:.1f}x above benchmark (${benchmark:.2f})",
                    })
                    analysis["overall"] = "critical"
                elif metric_name == "ctr" and actual < critical_thresholds.get("ctr_minimum", 1.0):
                    analysis["alerts"].append({
                        "severity": "critical",
                        "message": f"CTR ({actual:.2f}%) is critically low",
                    })
                    analysis["overall"] = "critical"
        
        return analysis

