# agents/marketing/customersegmentatonia.py
"""
CustomerSegmentationIA v3.0.0 - SUPER AGENT
Segmentación de Clientes con Explicabilidad
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


class CustomerSegmentationIA:
    VERSION = "3.0.0"
    AGENT_ID = "customersegmentatonia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta segmentación de clientes."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            customers = data.get("customers", [])
            strategy = data.get("strategy", "behavioral")
            
            # Segmentar clientes
            segments = self._segment_customers(customers, strategy)
            
            # Calcular métricas de calidad
            quality_metrics = self._calculate_quality_metrics(segments)
            
            # Generar recomendaciones por segmento
            recommendations = self._generate_segment_recommendations(segments)
            
            # Insights
            insights = self._generate_insights(segments, quality_metrics)
            
            decision_trace = [
                f"customers_analyzed={len(customers) if customers else 'sample'}",
                f"strategy={strategy}",
                f"segments_created={len(segments)}"
            ]
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "segmentation_id": f"seg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "strategy": strategy,
                "segments": segments,
                "segment_count": len(segments),
                "quality_metrics": quality_metrics,
                "recommendations": recommendations,
                "summary": {
                    "total_customers": sum(s["size"] for s in segments),
                    "largest_segment": max(segments, key=lambda x: x["size"])["name"] if segments else None,
                    "highest_value_segment": max(segments, key=lambda x: x["avg_ltv"])["name"] if segments else None
                },
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
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            return {
                "segmentation_id": "error",
                "tenant_id": self.tenant_id,
                "segments": [],
                "key_insights": [f"Error: {str(e)[:100]}"],
                "decision_trace": ["error_occurred"],
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
    
    def _segment_customers(self, customers: List[Dict], strategy: str) -> List[Dict]:
        """Segmenta clientes según estrategia."""
        if not customers:
            # Datos de ejemplo
            return [
                {
                    "segment_id": "seg_champions",
                    "name": "Champions",
                    "size": 850,
                    "pct": 0.17,
                    "avg_ltv": 4500,
                    "avg_frequency": 12,
                    "avg_recency_days": 5,
                    "characteristics": ["Alta frecuencia", "Alto valor", "Muy recientes"],
                    "reason_codes": [{"code": "RFM_HIGH", "description": "RFM score >90"}]
                },
                {
                    "segment_id": "seg_loyal",
                    "name": "Loyal Customers",
                    "size": 1200,
                    "pct": 0.24,
                    "avg_ltv": 2800,
                    "avg_frequency": 8,
                    "avg_recency_days": 15,
                    "characteristics": ["Frecuencia media-alta", "Consistentes"],
                    "reason_codes": [{"code": "LOYALTY_HIGH", "description": "Tenure >2 años"}]
                },
                {
                    "segment_id": "seg_potential",
                    "name": "Potential Loyalists",
                    "size": 1500,
                    "pct": 0.30,
                    "avg_ltv": 1500,
                    "avg_frequency": 4,
                    "avg_recency_days": 25,
                    "characteristics": ["Nuevos con potencial", "Engagement creciente"],
                    "reason_codes": [{"code": "GROWTH_TREND", "description": "Tendencia positiva"}]
                },
                {
                    "segment_id": "seg_at_risk",
                    "name": "At Risk",
                    "size": 800,
                    "pct": 0.16,
                    "avg_ltv": 2200,
                    "avg_frequency": 6,
                    "avg_recency_days": 60,
                    "characteristics": ["Fueron buenos", "Inactivos recientemente"],
                    "reason_codes": [{"code": "CHURN_RISK", "description": "Sin actividad 60+ días"}]
                },
                {
                    "segment_id": "seg_hibernating",
                    "name": "Hibernating",
                    "size": 650,
                    "pct": 0.13,
                    "avg_ltv": 800,
                    "avg_frequency": 2,
                    "avg_recency_days": 120,
                    "characteristics": ["Muy inactivos", "Bajo valor histórico"],
                    "reason_codes": [{"code": "DORMANT", "description": "Sin actividad 120+ días"}]
                }
            ]
        
        # Implementación real de segmentación
        # Por simplicidad, usar RFM básico
        return self._rfm_segmentation(customers)
    
    def _rfm_segmentation(self, customers: List[Dict]) -> List[Dict]:
        """Segmentación RFM básica."""
        segments = {}
        
        for c in customers:
            recency = c.get("days_since_purchase", 30)
            frequency = c.get("purchase_count", 1)
            monetary = c.get("total_spent", 100)
            
            # Score RFM simple
            r_score = 5 if recency < 30 else 4 if recency < 60 else 3 if recency < 90 else 2 if recency < 180 else 1
            f_score = 5 if frequency > 10 else 4 if frequency > 6 else 3 if frequency > 3 else 2 if frequency > 1 else 1
            m_score = 5 if monetary > 3000 else 4 if monetary > 1500 else 3 if monetary > 500 else 2 if monetary > 100 else 1
            
            total_score = r_score + f_score + m_score
            
            # Asignar segmento
            if total_score >= 13:
                seg = "Champions"
            elif total_score >= 10:
                seg = "Loyal"
            elif total_score >= 7:
                seg = "Potential"
            elif total_score >= 5:
                seg = "At Risk"
            else:
                seg = "Hibernating"
            
            if seg not in segments:
                segments[seg] = {"customers": [], "ltv_sum": 0}
            segments[seg]["customers"].append(c)
            segments[seg]["ltv_sum"] += monetary
        
        result = []
        total = sum(len(s["customers"]) for s in segments.values())
        
        for name, data in segments.items():
            size = len(data["customers"])
            result.append({
                "segment_id": f"seg_{name.lower()}",
                "name": name,
                "size": size,
                "pct": round(size / total, 2) if total > 0 else 0,
                "avg_ltv": round(data["ltv_sum"] / size, 2) if size > 0 else 0,
                "avg_frequency": round(sum(c.get("purchase_count", 0) for c in data["customers"]) / size, 1) if size > 0 else 0,
                "avg_recency_days": round(sum(c.get("days_since_purchase", 0) for c in data["customers"]) / size, 0) if size > 0 else 0,
                "characteristics": [],
                "reason_codes": []
            })
        
        return sorted(result, key=lambda x: x["avg_ltv"], reverse=True)
    
    def _calculate_quality_metrics(self, segments: List[Dict]) -> Dict[str, Any]:
        """Calcula métricas de calidad de segmentación."""
        if not segments:
            return {"coverage": 0, "balance": 0, "distinctiveness": 0}
        
        sizes = [s["size"] for s in segments]
        total = sum(sizes)
        
        # Coverage: todos los clientes asignados
        coverage = 1.0  # Asumimos 100% asignación
        
        # Balance: qué tan equilibrados son los segmentos
        avg_size = total / len(segments)
        variance = sum((s - avg_size) ** 2 for s in sizes) / len(sizes)
        balance = max(0, 1 - (variance ** 0.5) / avg_size) if avg_size > 0 else 0
        
        # Distinctiveness: diferencia en LTV entre segmentos
        ltvs = [s["avg_ltv"] for s in segments]
        ltv_range = max(ltvs) - min(ltvs) if ltvs else 0
        distinctiveness = min(1, ltv_range / 5000)
        
        return {
            "coverage": round(coverage, 3),
            "balance": round(balance, 3),
            "distinctiveness": round(distinctiveness, 3),
            "overall_quality": round((coverage + balance + distinctiveness) / 3, 3)
        }
    
    def _generate_segment_recommendations(self, segments: List[Dict]) -> List[Dict]:
        """Genera recomendaciones por segmento."""
        recommendations = []
        
        actions = {
            "Champions": {"action": "RETAIN", "strategy": "Programa VIP, acceso anticipado", "priority": "high"},
            "Loyal": {"action": "UPSELL", "strategy": "Cross-sell productos premium", "priority": "high"},
            "Potential": {"action": "NURTURE", "strategy": "Onboarding personalizado", "priority": "medium"},
            "At Risk": {"action": "REACTIVATE", "strategy": "Campaña de recuperación urgente", "priority": "critical"},
            "Hibernating": {"action": "WIN_BACK", "strategy": "Oferta agresiva de reactivación", "priority": "low"}
        }
        
        for seg in segments:
            name = seg["name"]
            if name in actions:
                recommendations.append({
                    "segment": name,
                    "segment_size": seg["size"],
                    "action": actions[name]["action"],
                    "strategy": actions[name]["strategy"],
                    "priority": actions[name]["priority"],
                    "expected_impact": f"+{int(seg['avg_ltv'] * 0.1):,} LTV potencial"
                })
        
        return sorted(recommendations, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x["priority"]])
    
    def _generate_insights(self, segments: List[Dict], quality: Dict) -> List[str]:
        """Genera insights de segmentación."""
        insights = []
        
        if not segments:
            return ["Datos insuficientes para segmentación"]
        
        # Distribución
        total = sum(s["size"] for s in segments)
        insights.append(f"Segmentación de {total:,} clientes en {len(segments)} grupos")
        
        # Segmento más valioso
        top_seg = max(segments, key=lambda x: x["avg_ltv"])
        insights.append(f"Segmento más valioso: {top_seg['name']} (LTV ${top_seg['avg_ltv']:,.0f})")
        
        # At Risk
        at_risk = next((s for s in segments if "risk" in s["name"].lower()), None)
        if at_risk:
            insights.append(f"Alerta: {at_risk['size']:,} clientes en riesgo ({at_risk['pct']*100:.0f}%)")
        
        # Calidad
        insights.append(f"Calidad de segmentación: {quality['overall_quality']*100:.0f}%")
        
        return insights[:5]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {
            "agent_id": self.AGENT_ID,
            "version": self.VERSION,
            "status": "healthy",
            "tenant_id": self.tenant_id,
            "metrics": {
                "requests": self.metrics["requests"],
                "errors": self.metrics["errors"],
                "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)
            },
            "decision_layer": DECISION_LAYER_AVAILABLE
        }
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()


def create_agent_instance(tenant_id: str, config: Dict = None):
    return CustomerSegmentationIA(tenant_id, config)
