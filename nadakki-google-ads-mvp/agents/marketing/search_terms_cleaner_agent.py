"""
NADAKKI AI Suite - Search Terms Cleaner Agent
Analyze and Optimize Search Terms / Negative Keywords
"""

from typing import Dict, Any, List
from enum import Enum
import logging

from core.agents.action_plan import ActionPlan, OperationPriority

logger = logging.getLogger(__name__)


class SearchTermClassification(Enum):
    KEEP = "keep"
    NEGATIVE = "negative"
    REVIEW = "review"
    EXPAND = "expand"


class SearchTermsCleanerAgent:
    """
    Search terms analysis agent that:
    - Analyzes search term performance
    - Identifies wasteful terms for negatives
    - Finds high-performing terms to add
    - Creates cleanup action plans
    """
    
    AGENT_ID = "search_terms_agent"
    AGENT_NAME = "SearchTermsCleanerAgent"
    
    MIN_IMPRESSIONS = 100
    LOW_CTR_THRESHOLD = 0.01
    HIGH_CTR_THRESHOLD = 0.05
    LOW_CONVERSION_RATE = 0.001
    HIGH_COST_NO_CONV = 50
    
    def __init__(self, connector, policy_engine=None):
        self.connector = connector
        self.policy_engine = policy_engine
    
    async def analyze_and_clean(self, tenant_id: str, campaign_ids: List[str] = None,
                                search_terms: List[Dict] = None) -> ActionPlan:
        """Analyze search terms and create cleanup plan."""
        plan = ActionPlan(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            tenant_id=tenant_id,
            tags=["search_terms", "negatives", "optimization"]
        )
        
        if not search_terms:
            search_terms = await self._fetch_search_terms(tenant_id, campaign_ids)
        
        classifications = self._classify_terms(search_terms)
        
        plan.analysis = {
            "total_terms_analyzed": len(search_terms),
            "keep": len([c for c in classifications if c["classification"] == SearchTermClassification.KEEP]),
            "negative": len([c for c in classifications if c["classification"] == SearchTermClassification.NEGATIVE]),
            "review": len([c for c in classifications if c["classification"] == SearchTermClassification.REVIEW]),
            "expand": len([c for c in classifications if c["classification"] == SearchTermClassification.EXPAND]),
            "potential_savings_usd": sum(c["cost"] for c in classifications if c["classification"] == SearchTermClassification.NEGATIVE)
        }
        
        plan.rationale = self._build_rationale(plan.analysis)
        
        negatives = [c for c in classifications if c["classification"] == SearchTermClassification.NEGATIVE]
        
        if negatives:
            by_ad_group = {}
            for neg in negatives:
                ag_id = neg.get("ad_group_id", "default")
                if ag_id not in by_ad_group:
                    by_ad_group[ag_id] = []
                by_ad_group[ag_id].append(neg)
            
            for ad_group_id, terms in by_ad_group.items():
                plan.add_operation(
                    operation_name="add_negative_keywords@v1",
                    params={
                        "ad_group_id": ad_group_id,
                        "keywords": [{"text": t["term"], "match_type": "EXACT"} for t in terms]
                    },
                    priority=OperationPriority.MEDIUM,
                    estimated_impact={
                        "keywords_added": len(terms),
                        "estimated_savings_usd": sum(t["cost"] for t in terms)
                    },
                    requires_review=len(terms) > 20
                )
        
        plan.risk_score = self._calculate_risk(classifications)
        plan.risk_factors = self._identify_risk_factors(classifications)
        
        return plan
    
    async def _fetch_search_terms(self, tenant_id: str, campaign_ids: List[str] = None) -> List[Dict]:
        """Fetch search term report (mock for MVP)."""
        return [
            {"term": "buy cheap loans", "impressions": 500, "clicks": 2, "cost": 45.0, "conversions": 0, "ad_group_id": "ag1"},
            {"term": "best mortgage rates", "impressions": 1000, "clicks": 80, "cost": 120.0, "conversions": 5, "ad_group_id": "ag1"},
            {"term": "free money no credit", "impressions": 200, "clicks": 10, "cost": 30.0, "conversions": 0, "ad_group_id": "ag2"},
        ]
    
    def _classify_terms(self, search_terms: List[Dict]) -> List[Dict]:
        """Classify each search term."""
        return [
            {**term, "classification": self._classify_single_term(term),
             "reasons": self._get_classification_reasons(term, self._classify_single_term(term))}
            for term in search_terms
        ]
    
    def _classify_single_term(self, term: Dict) -> SearchTermClassification:
        """Classify a single search term."""
        impressions = term.get("impressions", 0)
        clicks = term.get("clicks", 0)
        cost = term.get("cost", 0)
        conversions = term.get("conversions", 0)
        
        if impressions < self.MIN_IMPRESSIONS:
            return SearchTermClassification.REVIEW
        
        ctr = clicks / impressions if impressions > 0 else 0
        conv_rate = conversions / clicks if clicks > 0 else 0
        
        if cost > self.HIGH_COST_NO_CONV and conversions == 0:
            return SearchTermClassification.NEGATIVE
        
        if ctr < self.LOW_CTR_THRESHOLD and impressions > 200:
            return SearchTermClassification.NEGATIVE
        
        if ctr > self.HIGH_CTR_THRESHOLD and conversions > 0:
            return SearchTermClassification.EXPAND
        
        if conv_rate < self.LOW_CONVERSION_RATE and clicks > 20:
            return SearchTermClassification.NEGATIVE
        
        return SearchTermClassification.KEEP
    
    def _get_classification_reasons(self, term: Dict, classification: SearchTermClassification) -> List[str]:
        """Get reasons for classification."""
        reasons = []
        if classification == SearchTermClassification.NEGATIVE:
            if term.get("cost", 0) > self.HIGH_COST_NO_CONV and term.get("conversions", 0) == 0:
                reasons.append(f"High cost (${term['cost']:.2f}) with no conversions")
            impressions = term.get("impressions", 0)
            clicks = term.get("clicks", 0)
            if impressions > 0 and clicks / impressions < self.LOW_CTR_THRESHOLD:
                reasons.append(f"Low CTR ({clicks/impressions:.2%})")
        return reasons
    
    def _build_rationale(self, analysis: Dict) -> str:
        return (
            f"Analyzed {analysis['total_terms_analyzed']} search terms. "
            f"Found {analysis['negative']} terms to add as negatives "
            f"(potential savings: ${analysis['potential_savings_usd']:.2f}). "
            f"{analysis['expand']} high-performing terms for expansion."
        )
    
    def _calculate_risk(self, classifications: List[Dict]) -> float:
        negatives = len([c for c in classifications if c["classification"] == SearchTermClassification.NEGATIVE])
        if negatives > 50:
            return 0.6
        elif negatives > 20:
            return 0.4
        return 0.2
    
    def _identify_risk_factors(self, classifications: List[Dict]) -> List[str]:
        factors = []
        negatives = [c for c in classifications if c["classification"] == SearchTermClassification.NEGATIVE]
        if len(negatives) > 50:
            factors.append(f"Large number of negatives ({len(negatives)})")
        return factors
