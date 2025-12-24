# agents/marketing/personalizationengineia.py
"""
PersonalizationEngineIA v3.0.0 - SUPER AGENT
Motor de Personalización con Segmentación Dinámica
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


class PersonalizationEngineIA:
    VERSION = "3.0.0"
    AGENT_ID = "personalizationengineia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera contenido personalizado."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            user_id = data.get("user_id", "user_001")
            user_profile = data.get("profile", {})
            context = data.get("context", {})
            
            segment = self._determine_segment(user_profile)
            personalized = self._personalize_content(segment, context)
            recommendations = self._generate_recommendations(segment, user_profile)
            
            decision_trace = [f"user={user_id}", f"segment={segment['id']}", f"recs={len(recommendations)}"]
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "personalization_id": f"pers_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "user_id": user_id,
                "segment": segment,
                "personalized_content": personalized,
                "recommendations": recommendations,
                "personalization_score": round(segment["confidence"], 3),
                "key_insights": self._generate_insights(segment, personalized),
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
            return {"personalization_id": "error", "segment": {}, "key_insights": [str(e)[:100]], "version": self.VERSION, "latency_ms": 1}
    
    def _determine_segment(self, profile: Dict) -> Dict[str, Any]:
        age = profile.get("age", 35)
        income = profile.get("income", 50000)
        behavior = profile.get("behavior", "moderate")
        
        if income >= 80000 and behavior == "active":
            return {"id": "high_value_active", "name": "Alto Valor Activo", "confidence": 0.92, "traits": ["premium", "engagement_high"]}
        elif income >= 50000:
            return {"id": "growth_potential", "name": "Potencial de Crecimiento", "confidence": 0.85, "traits": ["upsell_ready", "nurture"]}
        else:
            return {"id": "value_seeker", "name": "Buscador de Valor", "confidence": 0.78, "traits": ["price_sensitive", "promotions"]}
    
    def _personalize_content(self, segment: Dict, context: Dict) -> Dict[str, Any]:
        content_map = {
            "high_value_active": {"headline": "Acceso Exclusivo Premium", "cta": "Activar Beneficios", "tone": "exclusive", "offer_type": "premium"},
            "growth_potential": {"headline": "Descubre Más Oportunidades", "cta": "Explorar Ahora", "tone": "aspirational", "offer_type": "upgrade"},
            "value_seeker": {"headline": "Las Mejores Ofertas para Ti", "cta": "Ver Ofertas", "tone": "value", "offer_type": "discount"}
        }
        return content_map.get(segment["id"], content_map["growth_potential"])
    
    def _generate_recommendations(self, segment: Dict, profile: Dict) -> List[Dict]:
        base_recs = [
            {"type": "product", "item": "Cuenta Premium", "relevance": 0.88, "reason": "Match con perfil"},
            {"type": "content", "item": "Guía de Inversión", "relevance": 0.82, "reason": "Interés detectado"},
            {"type": "action", "item": "Completar perfil", "relevance": 0.75, "reason": "Mejorar personalización"}
        ]
        return base_recs
    
    def _generate_insights(self, segment: Dict, content: Dict) -> List[str]:
        return [f"Segmento: {segment['name']} (confianza {segment['confidence']*100:.0f}%)", f"Tono recomendado: {content['tone']}", f"Tipo de oferta: {content['offer_type']}"]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {"agent_id": self.AGENT_ID, "version": self.VERSION, "status": "healthy", "tenant_id": self.tenant_id, "metrics": {"requests": self.metrics["requests"], "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)}, "decision_layer": DECISION_LAYER_AVAILABLE}
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()


def create_agent_instance(tenant_id: str, config: Dict = None):
    return PersonalizationEngineIA(tenant_id, config)
