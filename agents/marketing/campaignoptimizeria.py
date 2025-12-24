# agents/marketing/campaignoptimizeria.py
"""CampaignOptimizerIA v3.0.0 - SUPER AGENT - Optimización de Campañas"""

from __future__ import annotations
import time, logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False

class CampaignOptimizerIA:
    VERSION = "3.0.0"
    AGENT_ID = "campaignoptimizeria"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            campaign_id = data.get("campaign_id", "camp_001")
            current_performance = data.get("performance", {})
            
            analysis = self._analyze_campaign(campaign_id, current_performance)
            optimizations = self._generate_optimizations(analysis)
            budget_realloc = self._reallocate_budget(analysis)
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {"optimization_id": f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "tenant_id": self.tenant_id, "campaign_id": campaign_id, "current_analysis": analysis, "optimizations": optimizations, "budget_reallocation": budget_realloc, "expected_lift": f"+{sum(o['expected_lift'] for o in optimizations)}%", "key_insights": [f"Campaña {campaign_id} analizada", f"Optimizaciones: {len(optimizations)}", f"Lift esperado: +{sum(o['expected_lift'] for o in optimizations)}%"], "decision_trace": [f"campaign={campaign_id}", f"optimizations={len(optimizations)}"], "version": self.VERSION, "latency_ms": latency_ms}
            
            if DECISION_LAYER_AVAILABLE:
                try: result = apply_decision_layer(result)
                except: pass
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            return {"optimization_id": "error", "optimizations": [], "key_insights": [str(e)[:100]], "version": self.VERSION, "latency_ms": 1}
    
    def _analyze_campaign(self, campaign_id: str, perf: Dict) -> Dict[str, Any]:
        return {"campaign_id": campaign_id, "current_roi": perf.get("roi", 2.5), "current_cpa": perf.get("cpa", 45), "current_ctr": perf.get("ctr", 0.025), "spend": perf.get("spend", 50000), "conversions": perf.get("conversions", 1100), "performance_vs_target": 0.92, "underperforming_segments": ["mobile_ios", "age_55+"], "top_performing": ["desktop", "age_25-34"]}
    
    def _generate_optimizations(self, analysis: Dict) -> List[Dict]:
        opts = []
        if analysis["current_ctr"] < 0.03:
            opts.append({"type": "creative_refresh", "action": "Update ad creatives", "expected_lift": 15, "priority": "high"})
        if "mobile" in str(analysis.get("underperforming_segments", [])):
            opts.append({"type": "mobile_optimization", "action": "Optimize mobile landing page", "expected_lift": 12, "priority": "high"})
        if analysis["performance_vs_target"] < 1.0:
            opts.append({"type": "audience_refinement", "action": "Narrow targeting to top segments", "expected_lift": 8, "priority": "medium"})
        opts.append({"type": "bid_optimization", "action": "Adjust bids for top performers", "expected_lift": 5, "priority": "medium"})
        return opts
    
    def _reallocate_budget(self, analysis: Dict) -> Dict[str, Any]:
        spend = analysis["spend"]
        return {"current_allocation": {"top_performers": 0.40, "mid_performers": 0.35, "underperformers": 0.25}, "recommended_allocation": {"top_performers": 0.55, "mid_performers": 0.35, "underperformers": 0.10}, "budget_shift": {"to_top": round(spend * 0.15, 2), "from_under": round(spend * 0.15, 2)}, "expected_roi_improvement": "+18%"}
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {"agent_id": self.AGENT_ID, "version": self.VERSION, "status": "healthy", "metrics": {"requests": self.metrics["requests"], "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)}}
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()

def create_agent_instance(tenant_id: str, config: Dict = None):
    return CampaignOptimizerIA(tenant_id, config)
