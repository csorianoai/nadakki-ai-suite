# agents/marketing/marketingorchestratorea.py
"""MarketingOrchestratorEA v3.0.0 - SUPER AGENT - Orquestador de Marketing"""

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

class MarketingOrchestratorEA:
    VERSION = "3.0.0"
    AGENT_ID = "marketingorchestratorea"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            goal = data.get("goal", "maximize_roi")
            budget = data.get("budget", 100000)
            
            orchestrated_plan = self._orchestrate(goal, budget)
            priorities = self._prioritize_actions(orchestrated_plan)
            timeline = self._generate_timeline(priorities)
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {"orchestration_id": f"orch_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "tenant_id": self.tenant_id, "goal": goal, "budget": budget, "orchestrated_plan": orchestrated_plan, "priorities": priorities, "timeline": timeline, "expected_roi": orchestrated_plan["expected_roi"], "key_insights": [f"Plan orquestado para {goal}", f"Budget: ${budget:,}", f"ROI esperado: {orchestrated_plan['expected_roi']}x"], "decision_trace": [f"goal={goal}", f"budget={budget}"], "version": self.VERSION, "latency_ms": latency_ms}
            
            if DECISION_LAYER_AVAILABLE:
                try: result = apply_decision_layer(result)
                except: pass
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            return {"orchestration_id": "error", "key_insights": [str(e)[:100]], "version": self.VERSION, "latency_ms": 1}
    
    def _orchestrate(self, goal: str, budget: float) -> Dict[str, Any]:
        channels = [
            {"channel": "paid_search", "allocation": 0.30, "expected_roi": 3.2},
            {"channel": "social_ads", "allocation": 0.25, "expected_roi": 2.8},
            {"channel": "email", "allocation": 0.15, "expected_roi": 4.5},
            {"channel": "content", "allocation": 0.20, "expected_roi": 2.0},
            {"channel": "events", "allocation": 0.10, "expected_roi": 1.5}
        ]
        for c in channels:
            c["budget"] = round(budget * c["allocation"], 2)
        return {"channels": channels, "total_budget": budget, "expected_roi": round(sum(c["expected_roi"] * c["allocation"] for c in channels), 2)}
    
    def _prioritize_actions(self, plan: Dict) -> List[Dict]:
        return sorted([{"action": f"Launch {c['channel']}", "priority": 1 if c["expected_roi"] > 3 else 2 if c["expected_roi"] > 2 else 3, "budget": c["budget"], "roi": c["expected_roi"]} for c in plan["channels"]], key=lambda x: x["priority"])
    
    def _generate_timeline(self, priorities: List) -> List[Dict]:
        return [{"week": i+1, "action": p["action"], "status": "planned"} for i, p in enumerate(priorities)]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {"agent_id": self.AGENT_ID, "version": self.VERSION, "status": "healthy", "metrics": {"requests": self.metrics["requests"], "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)}}
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()

def create_agent_instance(tenant_id: str, config: Dict = None):
    return MarketingOrchestratorEA(tenant_id, config)
