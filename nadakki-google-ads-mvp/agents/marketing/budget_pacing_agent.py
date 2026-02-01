"""
NADAKKI AI Suite - Budget Pacing Agent
Intelligent Budget Optimization for Google Ads
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from core.agents.action_plan import ActionPlan, OperationPriority

logger = logging.getLogger(__name__)


class GoogleAdsBudgetPacingAgent:
    """
    Budget pacing agent that:
    - Analyzes campaign spending patterns
    - Identifies under/over-pacing
    - Recommends budget adjustments
    - Generates executable action plans
    """
    
    AGENT_ID = "budget_pacing_agent"
    AGENT_NAME = "GoogleAdsBudgetPacingAgent"
    
    UNDERPACING_THRESHOLD = 0.85
    OVERPACING_THRESHOLD = 1.15
    MIN_ADJUSTMENT_PERCENT = 5
    MAX_ADJUSTMENT_PERCENT = 30
    
    def __init__(self, connector, policy_engine):
        self.connector = connector
        self.policy_engine = policy_engine
    
    async def analyze_and_plan(self, tenant_id: str, campaigns: List[Dict[str, Any]] = None,
                               target_date: datetime = None) -> ActionPlan:
        """Analyze campaigns and create budget adjustment plan."""
        plan = ActionPlan(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            tenant_id=tenant_id,
            tags=["budget", "pacing", "optimization"]
        )
        
        if not campaigns:
            result = await self.connector.get_metrics(tenant_id)
            if not result.success:
                plan.analysis = {"error": "Failed to fetch campaigns"}
                return plan
            campaigns = result.data.get("campaigns", [])
        
        target_date = target_date or datetime.utcnow()
        day_of_month = target_date.day
        days_in_month = 30
        expected_spend_pct = day_of_month / days_in_month
        
        analysis = {
            "date": target_date.isoformat(),
            "campaigns_analyzed": len(campaigns),
            "expected_spend_pct": expected_spend_pct,
            "underpacing": [],
            "overpacing": [],
            "on_track": []
        }
        
        recommendations = []
        
        for campaign in campaigns:
            if campaign.get("status") != "ENABLED":
                continue
            
            budget = campaign.get("budget_micros", 0) / 1_000_000
            spent = campaign.get("cost_micros", 0) / 1_000_000
            
            if budget <= 0:
                continue
            
            actual_spend_pct = spent / (budget * days_in_month) if budget > 0 else 0
            pacing_ratio = actual_spend_pct / expected_spend_pct if expected_spend_pct > 0 else 1
            
            campaign_analysis = {
                "id": campaign["id"],
                "name": campaign["name"],
                "budget": budget,
                "spent": spent,
                "pacing_ratio": round(pacing_ratio, 2)
            }
            
            if pacing_ratio < self.UNDERPACING_THRESHOLD:
                analysis["underpacing"].append(campaign_analysis)
                
                target_pct = expected_spend_pct * 1.1
                recommended_budget = (spent / target_pct) if target_pct > 0 else budget
                increase_pct = ((recommended_budget - budget) / budget) * 100 if budget > 0 else 0
                
                if increase_pct >= self.MIN_ADJUSTMENT_PERCENT:
                    increase_pct = min(increase_pct, self.MAX_ADJUSTMENT_PERCENT)
                    new_budget = budget * (1 + increase_pct / 100)
                    
                    recommendations.append({
                        "campaign_id": campaign["id"],
                        "campaign_name": campaign["name"],
                        "action": "increase",
                        "current_budget": budget,
                        "recommended_budget": round(new_budget, 2),
                        "change_pct": round(increase_pct, 1),
                        "reason": f"Underpacing at {pacing_ratio:.0%}"
                    })
            
            elif pacing_ratio > self.OVERPACING_THRESHOLD:
                analysis["overpacing"].append(campaign_analysis)
                
                decrease_pct = min((pacing_ratio - 1) * 100, self.MAX_ADJUSTMENT_PERCENT)
                
                if decrease_pct >= self.MIN_ADJUSTMENT_PERCENT:
                    new_budget = budget * (1 - decrease_pct / 100)
                    
                    recommendations.append({
                        "campaign_id": campaign["id"],
                        "campaign_name": campaign["name"],
                        "action": "decrease",
                        "current_budget": budget,
                        "recommended_budget": round(new_budget, 2),
                        "change_pct": round(-decrease_pct, 1),
                        "reason": f"Overpacing at {pacing_ratio:.0%}"
                    })
            else:
                analysis["on_track"].append(campaign_analysis)
        
        plan.analysis = analysis
        plan.rationale = self._build_rationale(analysis, recommendations)
        
        for rec in recommendations:
            requires_review = abs(rec["change_pct"]) > 20
            
            plan.add_operation(
                operation_name="update_campaign_budget@v1",
                params={
                    "budget_id": rec["campaign_id"],
                    "new_budget": rec["recommended_budget"],
                    "previous_budget": rec["current_budget"],
                    "reason": rec["reason"]
                },
                priority=OperationPriority.HIGH if abs(rec["change_pct"]) > 15 else OperationPriority.MEDIUM,
                estimated_impact={
                    "budget_change_usd": rec["recommended_budget"] - rec["current_budget"],
                    "change_pct": rec["change_pct"]
                },
                requires_review=requires_review
            )
        
        plan.risk_score = self._calculate_risk(recommendations)
        plan.risk_factors = self._identify_risk_factors(recommendations)
        
        return plan
    
    def _build_rationale(self, analysis: Dict, recommendations: List[Dict]) -> str:
        parts = [
            f"Analyzed {analysis['campaigns_analyzed']} campaigns.",
            f"Found {len(analysis['underpacing'])} underpacing,",
            f"{len(analysis['overpacing'])} overpacing,",
            f"{len(analysis['on_track'])} on track."
        ]
        
        if recommendations:
            increases = sum(1 for r in recommendations if r["action"] == "increase")
            decreases = len(recommendations) - increases
            parts.append(f"Recommending {increases} increases and {decreases} decreases.")
        
        return " ".join(parts)
    
    def _calculate_risk(self, recommendations: List[Dict]) -> float:
        if not recommendations:
            return 0.0
        
        risk = sum(abs(r["change_pct"]) / 100 * 0.2 for r in recommendations)
        return min(risk, 1.0)
    
    def _identify_risk_factors(self, recommendations: List[Dict]) -> List[str]:
        factors = []
        large_changes = [r for r in recommendations if abs(r["change_pct"]) > 20]
        if large_changes:
            factors.append(f"{len(large_changes)} large budget changes (>20%)")
        return factors
