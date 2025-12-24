"""
Authority Layer - Capa de autoridad para agentes orquestadores
Filtra, prioriza y rechaza recomendaciones de baja calidad
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Recommendation:
    id: str
    source_agent: str
    action: str
    expected_improvement: float
    confidence: float
    effort: str  # low, medium, high
    timestamp: datetime

class AuthorityLayer:
    """Capa de autoridad que filtra y prioriza recomendaciones"""
    
    # Configuración
    MIN_IMPROVEMENT_THRESHOLD = 0.05  # 5% mínimo para considerar
    MIN_CONFIDENCE_THRESHOLD = 0.70   # 70% confianza mínima
    MAX_RECOMMENDATIONS = 3           # Top 3 máximo
    
    def __init__(self, config: Optional[Dict] = None):
        if config:
            self.MIN_IMPROVEMENT_THRESHOLD = config.get("min_improvement", 0.05)
            self.MIN_CONFIDENCE_THRESHOLD = config.get("min_confidence", 0.70)
            self.MAX_RECOMMENDATIONS = config.get("max_recommendations", 3)
        
        self.rejection_log = []
    
    def filter_and_prioritize(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Filtra y prioriza recomendaciones, rechazando las de baja calidad"""
        
        accepted = []
        rejected = []
        
        for rec in recommendations:
            # Validar estructura
            if not self._validate_recommendation(rec):
                rejected.append({"recommendation": rec, "reason": "invalid_structure"})
                continue
            
            # Filtrar por threshold de mejora
            improvement = rec.get("expected_improvement", 0)
            if improvement < self.MIN_IMPROVEMENT_THRESHOLD:
                rejected.append({
                    "recommendation": rec,
                    "reason": f"below_improvement_threshold ({improvement:.1%} < {self.MIN_IMPROVEMENT_THRESHOLD:.1%})"
                })
                continue
            
            # Filtrar por confianza
            confidence = rec.get("confidence", 0)
            if confidence < self.MIN_CONFIDENCE_THRESHOLD:
                rejected.append({
                    "recommendation": rec,
                    "reason": f"below_confidence_threshold ({confidence:.1%} < {self.MIN_CONFIDENCE_THRESHOLD:.1%})"
                })
                continue
            
            # Calcular score compuesto
            rec["authority_score"] = self._calculate_authority_score(rec)
            accepted.append(rec)
        
        # Ordenar por score y tomar top N
        accepted.sort(key=lambda x: x["authority_score"], reverse=True)
        top_recommendations = accepted[:self.MAX_RECOMMENDATIONS]
        
        # Log de rechazos
        self.rejection_log.extend(rejected)
        
        return {
            "approved_recommendations": top_recommendations,
            "approved_count": len(top_recommendations),
            "rejected_count": len(rejected),
            "rejection_summary": self._summarize_rejections(rejected),
            "authority_decision": self._make_authority_decision(top_recommendations),
            "audit": {
                "total_evaluated": len(recommendations),
                "threshold_improvement": self.MIN_IMPROVEMENT_THRESHOLD,
                "threshold_confidence": self.MIN_CONFIDENCE_THRESHOLD,
                "max_allowed": self.MAX_RECOMMENDATIONS
            }
        }
    
    def _validate_recommendation(self, rec: Dict) -> bool:
        """Valida que la recomendación tenga estructura correcta"""
        required_fields = ["action", "expected_improvement"]
        return all(field in rec for field in required_fields)
    
    def _calculate_authority_score(self, rec: Dict) -> float:
        """Calcula score de autoridad compuesto"""
        improvement = rec.get("expected_improvement", 0)
        confidence = rec.get("confidence", 0.5)
        
        # Penalizar alto esfuerzo
        effort_penalty = {"low": 0, "medium": 0.1, "high": 0.2}.get(rec.get("effort", "medium"), 0.1)
        
        # Score: improvement * confidence - effort_penalty
        return (improvement * confidence) - effort_penalty
    
    def _summarize_rejections(self, rejected: List[Dict]) -> Dict[str, int]:
        """Resume razones de rechazo"""
        summary = {}
        for r in rejected:
            reason = r["reason"].split(" ")[0]  # Primera palabra
            summary[reason] = summary.get(reason, 0) + 1
        return summary
    
    def _make_authority_decision(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Toma decisión de autoridad final"""
        if not recommendations:
            return {
                "action": "HOLD",
                "reason": "No hay recomendaciones que cumplan los criterios mínimos"
            }
        
        top = recommendations[0]
        return {
            "action": "EXECUTE",
            "primary_recommendation": top["action"],
            "expected_improvement": f"{top['expected_improvement']:.1%}",
            "confidence": f"{top.get('confidence', 0.5):.1%}",
            "reason": f"Recomendación con mayor score de autoridad ({top['authority_score']:.3f})"
        }


# Función helper
def apply_authority_filter(recommendations: List[Dict], config: Optional[Dict] = None) -> Dict[str, Any]:
    """Aplica filtro de autoridad a lista de recomendaciones"""
    layer = AuthorityLayer(config)
    return layer.filter_and_prioritize(recommendations)
