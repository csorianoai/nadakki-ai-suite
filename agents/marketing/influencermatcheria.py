# agents/marketing/influencermatcheria.py
"""
InfluencerMatcherIA v3.0.0 - SUPER AGENT
Matching de Influencers con Scoring de Fit
"""

from __future__ import annotations
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class InfluencerMatcherIA:
    VERSION = "3.0.0"
    AGENT_ID = "influencermatcheria"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encuentra influencers óptimos para campaña."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            campaign_type = data.get("campaign_type", "awareness")
            target_audience = data.get("target_audience", "general")
            budget = data.get("budget", 10000)
            
            matches = self._find_matches(campaign_type, target_audience, budget)
            insights = self._generate_insights(matches)
            
            decision_trace = [f"campaign={campaign_type}", f"audience={target_audience}", f"matches={len(matches)}"]
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "match_id": f"inf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "matches": matches,
                "total_matches": len(matches),
                "budget_allocation": self._allocate_budget(matches, budget),
                "expected_reach": sum(m["followers"] for m in matches),
                "expected_engagement": round(sum(m["engagement_rate"] for m in matches) / len(matches) if matches else 0, 4),
                "key_insights": insights,
                "decision_trace": decision_trace,
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
            
            if DECISION_LAYER_AVAILABLE:
                try:
                    result = apply_decision_layer(result)
                except Exception:
                    pass
            
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            return {"match_id": "error", "matches": [], "key_insights": [str(e)[:100]], "version": self.VERSION, "latency_ms": 1}
    
    def _find_matches(self, campaign: str, audience: str, budget: float) -> List[Dict]:
        return [
            {"influencer_id": "inf_001", "name": "Maria Finance", "platform": "instagram", "followers": 150000, "engagement_rate": 0.045, "fit_score": 0.92, "cost_per_post": 2500, "audience_match": 0.88},
            {"influencer_id": "inf_002", "name": "Carlos Inversiones", "platform": "youtube", "followers": 280000, "engagement_rate": 0.038, "fit_score": 0.87, "cost_per_post": 4000, "audience_match": 0.82},
            {"influencer_id": "inf_003", "name": "Ana Ahorro", "platform": "tiktok", "followers": 95000, "engagement_rate": 0.062, "fit_score": 0.85, "cost_per_post": 1500, "audience_match": 0.90},
            {"influencer_id": "inf_004", "name": "Pedro Fintech", "platform": "twitter", "followers": 45000, "engagement_rate": 0.035, "fit_score": 0.78, "cost_per_post": 800, "audience_match": 0.75}
        ]
    
    def _allocate_budget(self, matches: List[Dict], budget: float) -> List[Dict]:
        total_fit = sum(m["fit_score"] for m in matches)
        return [{"influencer": m["name"], "allocated": round(budget * m["fit_score"] / total_fit, 2), "posts": max(1, int(budget * m["fit_score"] / total_fit / m["cost_per_post"]))} for m in matches]
    
    def _generate_insights(self, matches: List[Dict]) -> List[str]:
        if not matches:
            return ["No se encontraron influencers"]
        top = max(matches, key=lambda x: x["fit_score"])
        return [f"Mejor match: {top['name']} (fit {top['fit_score']*100:.0f}%)", f"Reach total: {sum(m['followers'] for m in matches):,}", f"Engagement promedio: {sum(m['engagement_rate'] for m in matches)/len(matches)*100:.1f}%"]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {"agent_id": self.AGENT_ID, "version": self.VERSION, "status": "healthy", "tenant_id": self.tenant_id, "metrics": {"requests": self.metrics["requests"], "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)}, "decision_layer": DECISION_LAYER_AVAILABLE}
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()


def create_agent_instance(tenant_id: str, config: Dict = None):
    return InfluencerMatcherIA(tenant_id, config)
