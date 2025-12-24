# agents/marketing/leadscoringia.py
"""
LeadScoringIA v3.0.0 - SUPER AGENT
Scoring de Leads con Explicabilidad Completa
"""

from __future__ import annotations
import time
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class LeadScoringIA:
    VERSION = "3.0.0"
    AGENT_ID = "leadscoringia"
    
    BUCKETS = {
        "A": {"min": 0.8, "action": "immediate_contact", "priority": "critical"},
        "B": {"min": 0.6, "action": "nurture_high", "priority": "high"},
        "C": {"min": 0.4, "action": "nurture", "priority": "medium"},
        "D": {"min": 0.2, "action": "monitor", "priority": "low"},
        "F": {"min": 0.0, "action": "disqualify", "priority": "none"}
    }
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """Ejecuta scoring de lead."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            lead_data = data.get("lead", data)
            
            lead_id = data.get("lead_id", f"L-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            credit_score = lead_data.get("credit_score", 680)
            income = lead_data.get("income", 50000)
            employment = lead_data.get("employment_status", "employed")
            
            # Calcular score
            score, reasons = self._calculate_score(credit_score, income, employment)
            bucket = self._get_bucket(score)
            action = self.BUCKETS[bucket]["action"]
            
            decision_trace = [f"credit={credit_score}", f"income={income}", f"bucket={bucket}"]
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "lead_id": lead_id,
                "tenant_id": self.tenant_id,
                "score": round(score, 3),
                "bucket": bucket,
                "reasons": reasons,
                "recommended_action": action,
                "priority": self.BUCKETS[bucket]["priority"],
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
            return {"lead_id": "error", "score": 0, "bucket": "F", "reasons": [str(e)[:100]], "version": self.VERSION, "latency_ms": 1}
    
    def _calculate_score(self, credit: float, income: float, employment: str) -> tuple:
        score, reasons = 0.0, []
        
        if credit >= 750:
            score += 0.35
            reasons.append("Excelente historial crediticio (750+)")
        elif credit >= 700:
            score += 0.25
            reasons.append("Buen historial crediticio (700-749)")
        elif credit >= 650:
            score += 0.15
            reasons.append("Historial crediticio aceptable (650-699)")
        else:
            score += 0.05
            reasons.append("Historial crediticio bajo (<650)")
        
        if income >= 80000:
            score += 0.35
            reasons.append("Ingresos altos ($80k+)")
        elif income >= 50000:
            score += 0.25
            reasons.append("Ingresos moderados-altos ($50k-$80k)")
        elif income >= 30000:
            score += 0.15
            reasons.append("Ingresos moderados ($30k-$50k)")
        else:
            score += 0.05
            reasons.append("Ingresos bajos (<$30k)")
        
        if employment == "employed":
            score += 0.20
            reasons.append("Empleado actualmente")
        elif employment == "self_employed":
            score += 0.15
            reasons.append("Trabajador independiente")
        
        return min(1.0, score), reasons
    
    def _get_bucket(self, score: float) -> str:
        for bucket, data in self.BUCKETS.items():
            if score >= data["min"]:
                return bucket
        return "F"
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {"agent_id": self.AGENT_ID, "version": self.VERSION, "status": "healthy", "tenant_id": self.tenant_id, "metrics": {"requests": self.metrics["requests"], "errors": self.metrics["errors"], "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)}, "decision_layer": DECISION_LAYER_AVAILABLE}
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()


def create_agent_instance(tenant_id: str, config: Dict = None):
    return LeadScoringIA(tenant_id, config)
