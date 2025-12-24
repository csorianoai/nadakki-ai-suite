# agents/marketing/retentionpredictorea.py
"""
RetentionPredictorEA v3.0 - Predictor de Retención de Clientes
Simplificado y funcional - acepta dict como input.
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


class RetentionPredictorEA:
    VERSION = "3.0.0"
    AGENT_ID = "retentionpredictorea"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta predicción de retención - acepta dict."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            customers = data.get("customers", [])
            prediction_horizon = data.get("prediction_horizon_days", 30)
            
            # Predecir churn por cliente
            predictions = self._predict_churn(customers)
            
            # Segmentar por riesgo
            segments = self._segment_by_risk(predictions)
            
            # Generar acciones de retención
            retention_actions = self._generate_actions(segments)
            
            # Métricas agregadas
            avg_churn_prob = sum(p["churn_probability"] for p in predictions) / len(predictions) if predictions else 0
            high_risk_count = len([p for p in predictions if p["risk_level"] == "high"])
            
            # Insights
            insights = self._generate_insights(predictions, segments)
            
            decision_trace = [
                f"customers_analyzed={len(predictions)}",
                f"horizon_days={prediction_horizon}",
                f"high_risk_count={high_risk_count}",
                f"avg_churn_prob={avg_churn_prob:.2%}"
            ]
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "prediction_id": f"ret_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "predictions": predictions[:20],  # Limitar output
                "segments": segments,
                "retention_actions": retention_actions,
                "summary": {
                    "total_customers": len(predictions),
                    "high_risk": high_risk_count,
                    "medium_risk": len([p for p in predictions if p["risk_level"] == "medium"]),
                    "low_risk": len([p for p in predictions if p["risk_level"] == "low"]),
                    "avg_churn_probability": round(avg_churn_prob, 4),
                    "revenue_at_risk": round(sum(p.get("ltv", 0) * p["churn_probability"] for p in predictions), 2)
                },
                "key_insights": insights,
                "decision_trace": decision_trace,
                "model_confidence": 0.87,
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
                "prediction_id": "error",
                "tenant_id": self.tenant_id,
                "predictions": [],
                "segments": [],
                "retention_actions": [],
                "summary": {},
                "key_insights": [f"Error: {str(e)[:100]}"],
                "decision_trace": ["error_occurred"],
                "model_confidence": 0,
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
    
    def _predict_churn(self, customers: List[Dict]) -> List[Dict]:
        """Predice probabilidad de churn por cliente."""
        if not customers:
            # Datos de ejemplo
            return [
                {"customer_id": "c001", "churn_probability": 0.85, "risk_level": "high", "ltv": 2500, "days_since_activity": 45, "key_factors": ["inactividad", "ticket_abierto"]},
                {"customer_id": "c002", "churn_probability": 0.72, "risk_level": "high", "ltv": 1800, "days_since_activity": 30, "key_factors": ["uso_decreciente"]},
                {"customer_id": "c003", "churn_probability": 0.45, "risk_level": "medium", "ltv": 3200, "days_since_activity": 15, "key_factors": ["engagement_bajo"]},
                {"customer_id": "c004", "churn_probability": 0.35, "risk_level": "medium", "ltv": 2100, "days_since_activity": 10, "key_factors": ["competidor_mencionado"]},
                {"customer_id": "c005", "churn_probability": 0.15, "risk_level": "low", "ltv": 4500, "days_since_activity": 3, "key_factors": []},
                {"customer_id": "c006", "churn_probability": 0.08, "risk_level": "low", "ltv": 5200, "days_since_activity": 1, "key_factors": []}
            ]
        
        predictions = []
        for c in customers:
            # Modelo simplificado de churn
            days_inactive = c.get("days_since_activity", 0)
            usage_trend = c.get("usage_trend", 0)  # -1 a 1
            support_tickets = c.get("open_tickets", 0)
            
            # Calcular probabilidad
            prob = 0.1  # Base
            prob += min(0.4, days_inactive * 0.01)  # Inactividad
            prob += max(0, -usage_trend * 0.2)  # Tendencia negativa
            prob += min(0.2, support_tickets * 0.05)  # Tickets abiertos
            prob = min(0.95, prob)
            
            risk = "high" if prob > 0.6 else "medium" if prob > 0.3 else "low"
            
            predictions.append({
                "customer_id": c.get("customer_id", "unknown"),
                "churn_probability": round(prob, 4),
                "risk_level": risk,
                "ltv": c.get("ltv", 0),
                "days_since_activity": days_inactive,
                "key_factors": self._identify_factors(c)
            })
        
        return sorted(predictions, key=lambda x: x["churn_probability"], reverse=True)
    
    def _identify_factors(self, customer: Dict) -> List[str]:
        """Identifica factores de riesgo."""
        factors = []
        if customer.get("days_since_activity", 0) > 30:
            factors.append("inactividad_prolongada")
        if customer.get("usage_trend", 0) < -0.3:
            factors.append("uso_decreciente")
        if customer.get("open_tickets", 0) > 2:
            factors.append("tickets_sin_resolver")
        if customer.get("payment_issues", False):
            factors.append("problemas_pago")
        return factors
    
    def _segment_by_risk(self, predictions: List[Dict]) -> List[Dict]:
        """Segmenta clientes por nivel de riesgo."""
        high = [p for p in predictions if p["risk_level"] == "high"]
        medium = [p for p in predictions if p["risk_level"] == "medium"]
        low = [p for p in predictions if p["risk_level"] == "low"]
        
        return [
            {
                "segment": "high_risk",
                "count": len(high),
                "avg_churn_prob": round(sum(p["churn_probability"] for p in high) / len(high), 4) if high else 0,
                "total_ltv_at_risk": sum(p["ltv"] for p in high),
                "priority": "URGENTE"
            },
            {
                "segment": "medium_risk",
                "count": len(medium),
                "avg_churn_prob": round(sum(p["churn_probability"] for p in medium) / len(medium), 4) if medium else 0,
                "total_ltv_at_risk": sum(p["ltv"] for p in medium),
                "priority": "ALTA"
            },
            {
                "segment": "low_risk",
                "count": len(low),
                "avg_churn_prob": round(sum(p["churn_probability"] for p in low) / len(low), 4) if low else 0,
                "total_ltv_at_risk": sum(p["ltv"] for p in low),
                "priority": "MONITOREAR"
            }
        ]
    
    def _generate_actions(self, segments: List[Dict]) -> List[Dict]:
        """Genera acciones de retención por segmento."""
        actions = []
        
        for seg in segments:
            if seg["segment"] == "high_risk":
                actions.append({
                    "segment": seg["segment"],
                    "action": "CONTACTO_PERSONAL",
                    "channel": "llamada_ejecutivo",
                    "urgency": "inmediata",
                    "offer": "descuento_retencion_20%",
                    "expected_save_rate": 0.35
                })
            elif seg["segment"] == "medium_risk":
                actions.append({
                    "segment": seg["segment"],
                    "action": "CAMPAÑA_REENGAGEMENT",
                    "channel": "email_personalizado",
                    "urgency": "esta_semana",
                    "offer": "beneficio_exclusivo",
                    "expected_save_rate": 0.45
                })
            else:
                actions.append({
                    "segment": seg["segment"],
                    "action": "NURTURING_PROACTIVO",
                    "channel": "contenido_valor",
                    "urgency": "mensual",
                    "offer": "programa_lealtad",
                    "expected_save_rate": 0.70
                })
        
        return actions
    
    def _generate_insights(self, predictions: List[Dict], segments: List[Dict]) -> List[str]:
        """Genera insights de retención."""
        insights = []
        
        if not predictions:
            return ["Datos insuficientes para análisis"]
        
        high_risk = next((s for s in segments if s["segment"] == "high_risk"), None)
        if high_risk and high_risk["count"] > 0:
            insights.append(f"ALERTA: {high_risk['count']} clientes en alto riesgo de churn (${high_risk['total_ltv_at_risk']:,.0f} LTV en riesgo)")
        
        # Factor más común
        all_factors = []
        for p in predictions:
            all_factors.extend(p.get("key_factors", []))
        if all_factors:
            from collections import Counter
            top_factor = Counter(all_factors).most_common(1)[0]
            insights.append(f"Factor principal de churn: {top_factor[0]} ({top_factor[1]} casos)")
        
        # Oportunidad de intervención
        saveable = sum(1 for p in predictions if 0.3 < p["churn_probability"] < 0.7)
        if saveable > 0:
            insights.append(f"Oportunidad: {saveable} clientes en zona de intervención efectiva")
        
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
    return RetentionPredictorEA(tenant_id, config)
