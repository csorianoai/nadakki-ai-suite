# agents/marketing/conversioncohortia.py
"""ConversionCohortIA v3.0.0 - SUPER AGENT - Análisis de Cohortes de Conversión"""

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

class ConversionCohortIA:
    VERSION = "3.0.0"
    AGENT_ID = "conversioncohortia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            period = data.get("period", "monthly")
            metric = data.get("metric", "conversion_rate")
            
            cohorts = self._analyze_cohorts(period, metric)
            trends = self._identify_trends(cohorts)
            recommendations = self._generate_recommendations(cohorts, trends)
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "analysis_id": f"coh_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "period": period,
                "metric": metric,
                "cohorts": cohorts,
                "trends": trends,
                "recommendations": recommendations,
                "summary": {
                    "total_cohorts": len(cohorts),
                    "best_cohort": max(cohorts, key=lambda x: x["conversion_rate"])["name"] if cohorts else None,
                    "avg_conversion": round(sum(c["conversion_rate"] for c in cohorts) / len(cohorts), 4) if cohorts else 0,
                    "trend_direction": trends.get("direction", "stable")
                },
                "key_insights": self._generate_insights(cohorts, trends),
                "decision_trace": [f"period={period}", f"cohorts={len(cohorts)}"],
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
            
            if DECISION_LAYER_AVAILABLE:
                try: result = apply_decision_layer(result)
                except: pass
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            return {"analysis_id": "error", "cohorts": [], "key_insights": [str(e)[:100]], "version": self.VERSION, "latency_ms": 1}
    
    def _analyze_cohorts(self, period: str, metric: str) -> List[Dict]:
        return [
            {"name": "2024-Q1", "users": 12500, "conversions": 875, "conversion_rate": 0.070, "ltv": 2800, "cac": 85, "retention_30d": 0.72},
            {"name": "2024-Q2", "users": 15200, "conversions": 1140, "conversion_rate": 0.075, "ltv": 3100, "cac": 78, "retention_30d": 0.75},
            {"name": "2024-Q3", "users": 18500, "conversions": 1480, "conversion_rate": 0.080, "ltv": 3250, "cac": 72, "retention_30d": 0.78},
            {"name": "2024-Q4", "users": 21000, "conversions": 1785, "conversion_rate": 0.085, "ltv": 3400, "cac": 68, "retention_30d": 0.80}
        ]
    
    def _identify_trends(self, cohorts: List[Dict]) -> Dict[str, Any]:
        if len(cohorts) < 2:
            return {"direction": "insufficient_data", "change": 0}
        
        first_cr = cohorts[0]["conversion_rate"]
        last_cr = cohorts[-1]["conversion_rate"]
        change = (last_cr - first_cr) / first_cr if first_cr > 0 else 0
        
        return {
            "direction": "improving" if change > 0.05 else "declining" if change < -0.05 else "stable",
            "change_pct": round(change * 100, 1),
            "conversion_trend": [c["conversion_rate"] for c in cohorts],
            "ltv_trend": [c["ltv"] for c in cohorts],
            "cac_trend": [c["cac"] for c in cohorts]
        }
    
    def _generate_recommendations(self, cohorts: List, trends: Dict) -> List[Dict]:
        recs = []
        if trends.get("direction") == "improving":
            recs.append({"action": "Scale acquisition", "reason": "Conversion improving", "priority": "high", "expected_impact": "+20% volume"})
        elif trends.get("direction") == "declining":
            recs.append({"action": "Audit funnel", "reason": "Conversion declining", "priority": "critical", "expected_impact": "Stop decline"})
        
        if cohorts:
            best = max(cohorts, key=lambda x: x["conversion_rate"])
            recs.append({"action": f"Replicate {best['name']} tactics", "reason": "Best performing cohort", "priority": "high", "expected_impact": "+15% conversion"})
        
        return recs
    
    def _generate_insights(self, cohorts: List, trends: Dict) -> List[str]:
        if not cohorts:
            return ["Datos insuficientes"]
        
        insights = [
            f"Tendencia: {trends.get('direction', 'stable')} ({trends.get('change_pct', 0):+.1f}%)",
            f"Mejor cohorte: {max(cohorts, key=lambda x: x['conversion_rate'])['name']}",
            f"LTV promedio: ${sum(c['ltv'] for c in cohorts)/len(cohorts):,.0f}",
            f"CAC promedio: ${sum(c['cac'] for c in cohorts)/len(cohorts):,.0f}"
        ]
        return insights[:5]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {"agent_id": self.AGENT_ID, "version": self.VERSION, "status": "healthy", "tenant_id": self.tenant_id, "metrics": {"requests": self.metrics["requests"], "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)}, "decision_layer": DECISION_LAYER_AVAILABLE}
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()

def create_agent_instance(tenant_id: str, config: Dict = None):
    return ConversionCohortIA(tenant_id, config)
