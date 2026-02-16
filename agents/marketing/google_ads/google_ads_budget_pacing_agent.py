# ===============================================================================
# NADAKKI AI Suite - GoogleAdsBudgetPacingIA
# agents/marketing/google_ads_budget_pacing_agent.py
# Day 3 - Component 4 of 4
# ===============================================================================

"""
Budget Pacing Agent - monitors and adjusts campaign budgets.

Responsibilities:
- Analyze current spend vs. budget allocation
- Detect underspending and overspending
- Generate budget adjustment ActionPlans
- Respect guardrails (max change %, min days between changes)

Usage:
    pacing_agent = GoogleAdsBudgetPacingIA(knowledge_store)
    
    plan = pacing_agent.analyze_and_plan(
        tenant_id="bank01",
        campaigns=[
            {"campaign_id": "c1", "daily_budget": 100, "spend_today": 45, "spend_mtd": 1200, "monthly_target": 3000},
        ],
        industry="financial_services",
    )
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from integrations.google_ads.knowledge.yaml_store import YamlKnowledgeStore
from integrations.google_ads.agents.action_plan import ActionPlan, OperationPriority

logger = logging.getLogger("nadakki.agents.budget_pacing")


class GoogleAdsBudgetPacingIA:
    """
    Budget Pacing Agent - keeps campaigns on track.
    """
    
    AGENT_NAME = "GoogleAdsBudgetPacingIA"
    VERSION = "1.0.0"
    
    def __init__(self, knowledge_store: YamlKnowledgeStore):
        self.kb = knowledge_store
        logger.info(f"{self.AGENT_NAME} v{self.VERSION} initialized")
    
    def analyze_and_plan(
        self,
        tenant_id: str,
        campaigns: List[dict],
        industry: str = "financial_services",
        day_of_month: int = None,
        days_in_month: int = 30,
    ) -> ActionPlan:
        """
        Analyze budget pacing for all campaigns and generate adjustment plan.
        
        Args:
            tenant_id: Tenant ID
            campaigns: List of campaign dicts with:
                - campaign_id: str
                - campaign_name: str (optional)
                - daily_budget: float (current daily budget)
                - spend_today: float (spend so far today)
                - spend_mtd: float (month-to-date spend)
                - monthly_target: float (monthly budget target)
                - cpa: float (optional, current CPA)
                - conversions: int (optional)
            industry: For benchmark lookup
            day_of_month: Override current day (for testing)
            days_in_month: Override days in month
        """
        if day_of_month is None:
            day_of_month = datetime.utcnow().day
        
        guardrails = self.kb.get_guardrails(tenant_id, industry)
        budget_rules = guardrails.get("budget_guardrails", {})
        max_change_pct = budget_rules.get("max_single_change_pct", 30)
        
        plan = ActionPlan(
            tenant_id=tenant_id,
            agent_name=self.AGENT_NAME,
            title=f"Budget Pacing Adjustment - Day {day_of_month}/{days_in_month}",
            description="Automated budget pacing analysis and adjustments",
        )
        
        pacing_results = []
        
        for campaign in campaigns:
            result = self._analyze_campaign(
                campaign, day_of_month, days_in_month, max_change_pct
            )
            pacing_results.append(result)
            
            if result["action"] != "no_change":
                self._add_adjustment_operation(plan, campaign, result)
        
        # Set risk based on number of adjustments
        adjustments = sum(1 for r in pacing_results if r["action"] != "no_change")
        plan.risk_score = min(adjustments * 0.15, 0.8)
        plan.requires_approval = any(
            r["action"] == "reduce" and r.get("severity") == "critical"
            for r in pacing_results
        )
        
        plan.rationale = self._build_pacing_rationale(pacing_results)
        plan.propose()
        
        logger.info(
            f"[{tenant_id}] Budget pacing: {len(campaigns)} campaigns analyzed, "
            f"{adjustments} adjustments proposed"
        )
        
        return plan
    
    def _analyze_campaign(
        self,
        campaign: dict,
        day_of_month: int,
        days_in_month: int,
        max_change_pct: float,
    ) -> dict:
        """Analyze a single campaign's pacing."""
        daily_budget = campaign.get("daily_budget", 0)
        spend_mtd = campaign.get("spend_mtd", 0)
        monthly_target = campaign.get("monthly_target", daily_budget * days_in_month)
        spend_today = campaign.get("spend_today", 0)
        campaign_id = campaign.get("campaign_id", "unknown")
        
        # Calculate expected pacing
        expected_spend = (monthly_target / days_in_month) * day_of_month
        remaining_days = days_in_month - day_of_month
        remaining_budget = monthly_target - spend_mtd
        
        # Pacing percentage (100% = on track)
        pacing_pct = (spend_mtd / expected_spend * 100) if expected_spend > 0 else 0
        
        # Ideal daily budget for remaining days
        ideal_daily = (remaining_budget / remaining_days) if remaining_days > 0 else 0
        
        # Determine action
        action = "no_change"
        severity = "info"
        recommended_budget = daily_budget
        reason = ""
        
        if pacing_pct > 120:
            # Overspending
            action = "reduce"
            severity = "warning" if pacing_pct < 150 else "critical"
            recommended_budget = max(ideal_daily, daily_budget * 0.7)
            reason = f"Overspending at {pacing_pct:.0f}% pacing"
        
        elif pacing_pct < 70:
            # Underspending
            action = "increase"
            severity = "warning"
            change = min(max_change_pct / 100, (ideal_daily / daily_budget) - 1) if daily_budget > 0 else 0
            recommended_budget = daily_budget * (1 + min(change, max_change_pct / 100))
            reason = f"Underspending at {pacing_pct:.0f}% pacing"
        
        elif pacing_pct < 85:
            # Slightly behind
            action = "increase"
            severity = "info"
            recommended_budget = daily_budget * 1.1  # Gentle 10% increase
            reason = f"Slightly behind at {pacing_pct:.0f}% pacing"
        
        else:
            reason = f"On track at {pacing_pct:.0f}% pacing"
        
        # Enforce max change limit
        if daily_budget > 0:
            change_pct = abs(recommended_budget - daily_budget) / daily_budget * 100
            if change_pct > max_change_pct:
                recommended_budget = daily_budget * (
                    1 + max_change_pct / 100 if action == "increase"
                    else 1 - max_change_pct / 100
                )
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.get("campaign_name", campaign_id),
            "daily_budget": daily_budget,
            "spend_mtd": spend_mtd,
            "monthly_target": monthly_target,
            "expected_spend": round(expected_spend, 2),
            "pacing_pct": round(pacing_pct, 1),
            "remaining_budget": round(remaining_budget, 2),
            "remaining_days": remaining_days,
            "ideal_daily": round(ideal_daily, 2),
            "recommended_budget": round(recommended_budget, 2),
            "action": action,
            "severity": severity,
            "reason": reason,
        }
    
    def _add_adjustment_operation(
        self, plan: ActionPlan, campaign: dict, result: dict
    ):
        """Add a budget adjustment operation to the plan."""
        priority = {
            "critical": OperationPriority.CRITICAL,
            "warning": OperationPriority.HIGH,
            "info": OperationPriority.MEDIUM,
        }.get(result["severity"], OperationPriority.MEDIUM)
        
        plan.add_operation(
            operation_name="update_campaign_budget@v1",
            payload={
                "budget_id": campaign.get("budget_id", "auto_detect"),
                "campaign_id": campaign.get("campaign_id"),
                "new_budget": result["recommended_budget"],
                "previous_budget": result["daily_budget"],
            },
            description=(
                f"{result['action'].title()} budget for {result['campaign_name']}: "
                f"${result['daily_budget']:.2f} > ${result['recommended_budget']:.2f} "
                f"({result['reason']})"
            ),
            priority=priority,
        )
    
    def _build_pacing_rationale(self, results: List[dict]) -> str:
        """Build human-readable pacing rationale."""
        on_track = sum(1 for r in results if r["action"] == "no_change")
        increases = sum(1 for r in results if r["action"] == "increase")
        decreases = sum(1 for r in results if r["action"] == "reduce")
        
        parts = [f"Analyzed {len(results)} campaigns:"]
        if on_track:
            parts.append(f"  * {on_track} on track")
        if increases:
            parts.append(f"  * {increases} need budget increase (underpacing)")
        if decreases:
            parts.append(f"  * {decreases} need budget reduction (overpacing)")
        
        return "\n".join(parts)
    
    def get_pacing_summary(
        self,
        tenant_id: str,
        campaigns: List[dict],
        day_of_month: int = None,
        days_in_month: int = 30,
    ) -> dict:
        """
        Quick pacing summary without generating an ActionPlan.
        Useful for dashboard widgets.
        """
        if day_of_month is None:
            day_of_month = datetime.utcnow().day
        
        results = []
        for campaign in campaigns:
            result = self._analyze_campaign(campaign, day_of_month, days_in_month, 30)
            results.append(result)
        
        total_budget = sum(c.get("monthly_target", 0) for c in campaigns)
        total_spend = sum(c.get("spend_mtd", 0) for c in campaigns)
        
        return {
            "tenant_id": tenant_id,
            "day_of_month": day_of_month,
            "days_in_month": days_in_month,
            "total_campaigns": len(campaigns),
            "total_monthly_budget": total_budget,
            "total_spend_mtd": total_spend,
            "overall_pacing_pct": round(
                (total_spend / (total_budget / days_in_month * day_of_month)) * 100, 1
            ) if total_budget > 0 else 0,
            "on_track": sum(1 for r in results if r["action"] == "no_change"),
            "underpacing": sum(1 for r in results if r["action"] == "increase"),
            "overpacing": sum(1 for r in results if r["action"] == "reduce"),
            "campaigns": results,
        }

