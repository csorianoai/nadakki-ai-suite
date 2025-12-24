"""
Authority Layer v2.0 - Capa de autoridad para agentes orquestadores
Mejoras:
- Idempotencia
- Configuración declarativa
- Logging de rechazos
- Métricas de calidad
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib


class RejectionReason(Enum):
    BELOW_IMPROVEMENT_THRESHOLD = "below_improvement_threshold"
    BELOW_CONFIDENCE_THRESHOLD = "below_confidence_threshold"
    HIGH_EFFORT_LOW_IMPACT = "high_effort_low_impact"
    INVALID_STRUCTURE = "invalid_structure"
    DUPLICATE = "duplicate"
    CONFLICTING = "conflicting"


@dataclass
class AuthorityConfig:
    """Configuración declarativa para Authority Layer"""
    
    # Thresholds
    min_improvement_threshold: float = 0.05  # 5% mínimo
    min_confidence_threshold: float = 0.70   # 70% confianza
    max_recommendations: int = 3              # Top N
    
    # Filtros de esfuerzo
    reject_high_effort_low_impact: bool = True
    high_effort_impact_ratio: float = 0.10   # Si effort=high, impact debe ser >10%
    
    # Deduplicación
    deduplicate_similar: bool = True
    similarity_threshold: float = 0.8
    
    # Logging
    log_rejections: bool = True
    include_rejection_details: bool = True
    
    # Scoring
    scoring_weights: Dict[str, float] = field(default_factory=lambda: {
        "improvement": 0.40,
        "confidence": 0.30,
        "effort_penalty": 0.20,
        "source_trust": 0.10
    })
    
    # Fuentes confiables (agentes)
    trusted_sources: List[str] = field(default_factory=list)
    source_trust_bonus: float = 0.05


@dataclass 
class Recommendation:
    """Estructura de una recomendación"""
    id: str
    action: str
    expected_improvement: float
    confidence: float
    effort: str  # low, medium, high
    source_agent: str
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuthorityLayer:
    """
    Capa de autoridad que filtra, prioriza y rechaza recomendaciones.
    Solo las mejores recomendaciones pasan el filtro.
    """
    
    VERSION = "v2.0.0"
    MARKER = "_authority_layer_applied"
    
    EFFORT_PENALTIES = {
        "low": 0.0,
        "medium": 0.05,
        "high": 0.15
    }
    
    def __init__(self, config: Optional[AuthorityConfig] = None):
        self.config = config or AuthorityConfig()
        self.rejection_log: List[Dict[str, Any]] = []
        self._processed_hashes: set = set()
    
    def apply(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica el filtro de autoridad al resultado.
        Es idempotente - no se aplica dos veces.
        """
        # Verificar idempotencia
        if result.get(self.MARKER):
            return result
        
        # Extraer recomendaciones
        recommendations = self._extract_recommendations(result)
        
        if not recommendations:
            result[self.MARKER] = True
            result["_authority_note"] = "No recommendations found to filter"
            return result
        
        # Marcar como aplicado
        result[self.MARKER] = True
        result["_authority_layer_version"] = self.VERSION
        result["_authority_layer_timestamp"] = datetime.now().isoformat()
        
        # Procesar recomendaciones
        filtered = self._filter_and_prioritize(recommendations)
        
        # Actualizar resultado
        result["authority_decision"] = filtered
        result["original_recommendations_count"] = len(recommendations)
        result["approved_recommendations_count"] = len(filtered["approved"])
        
        return result
    
    def _extract_recommendations(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrae recomendaciones del resultado"""
        
        # Buscar en diferentes estructuras
        recommendation_keys = [
            "recommendations",
            "suggested_actions",
            "next_actions",
            "proposed_changes",
            "optimization_suggestions"
        ]
        
        for key in recommendation_keys:
            if key in result and isinstance(result[key], list):
                return result[key]
        
        # Buscar en nested
        if "result" in result and isinstance(result["result"], dict):
            for key in recommendation_keys:
                if key in result["result"] and isinstance(result["result"][key], list):
                    return result["result"][key]
        
        return []
    
    def _filter_and_prioritize(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Filtra y prioriza las recomendaciones"""
        
        approved = []
        rejected = []
        
        for i, rec in enumerate(recommendations):
            # Generar ID si no existe
            if "id" not in rec:
                rec["id"] = f"rec_{i:03d}"
            
            # Validar estructura
            validation = self._validate_recommendation(rec)
            if not validation["valid"]:
                rejected.append({
                    "recommendation": rec,
                    "reason": RejectionReason.INVALID_STRUCTURE.value,
                    "details": validation["error"]
                })
                continue
            
            # Normalizar valores
            rec = self._normalize_recommendation(rec)
            
            # Verificar duplicados
            if self.config.deduplicate_similar:
                if self._is_duplicate(rec, approved):
                    rejected.append({
                        "recommendation": rec,
                        "reason": RejectionReason.DUPLICATE.value,
                        "details": "Similar recommendation already approved"
                    })
                    continue
            
            # Filtrar por threshold de mejora
            improvement = rec.get("expected_improvement", 0)
            if improvement < self.config.min_improvement_threshold:
                rejected.append({
                    "recommendation": rec,
                    "reason": RejectionReason.BELOW_IMPROVEMENT_THRESHOLD.value,
                    "details": f"{improvement:.1%} < {self.config.min_improvement_threshold:.1%}"
                })
                continue
            
            # Filtrar por confianza
            confidence = rec.get("confidence", 0.5)
            if confidence < self.config.min_confidence_threshold:
                rejected.append({
                    "recommendation": rec,
                    "reason": RejectionReason.BELOW_CONFIDENCE_THRESHOLD.value,
                    "details": f"{confidence:.1%} < {self.config.min_confidence_threshold:.1%}"
                })
                continue
            
            # Filtrar alto esfuerzo / bajo impacto
            if self.config.reject_high_effort_low_impact:
                effort = rec.get("effort", "medium")
                if effort == "high" and improvement < self.config.high_effort_impact_ratio:
                    rejected.append({
                        "recommendation": rec,
                        "reason": RejectionReason.HIGH_EFFORT_LOW_IMPACT.value,
                        "details": f"High effort ({effort}) requires >{self.config.high_effort_impact_ratio:.0%} impact"
                    })
                    continue
            
            # Calcular authority score
            rec["authority_score"] = self._calculate_authority_score(rec)
            approved.append(rec)
        
        # Ordenar por score y tomar top N
        approved.sort(key=lambda x: x["authority_score"], reverse=True)
        top_approved = approved[:self.config.max_recommendations]
        
        # Los que no entraron en top N van a rejected
        overflow = approved[self.config.max_recommendations:]
        for rec in overflow:
            rejected.append({
                "recommendation": rec,
                "reason": "exceeded_max_recommendations",
                "details": f"Ranked #{approved.index(rec)+1}, max is {self.config.max_recommendations}"
            })
        
        # Log de rechazos
        if self.config.log_rejections:
            self.rejection_log.extend(rejected)
        
        # Construir respuesta
        return {
            "approved": top_approved,
            "approved_count": len(top_approved),
            "rejected_count": len(rejected),
            "rejection_summary": self._summarize_rejections(rejected),
            "primary_decision": self._make_primary_decision(top_approved),
            "quality_metrics": self._calculate_quality_metrics(top_approved, rejected),
            "audit": {
                "total_evaluated": len(recommendations),
                "thresholds": {
                    "min_improvement": self.config.min_improvement_threshold,
                    "min_confidence": self.config.min_confidence_threshold,
                    "max_recommendations": self.config.max_recommendations
                },
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _validate_recommendation(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Valida estructura de la recomendación"""
        
        required_fields = ["action"]
        optional_with_defaults = {
            "expected_improvement": 0.05,
            "confidence": 0.5,
            "effort": "medium"
        }
        
        # Verificar campos requeridos
        for field in required_fields:
            if field not in rec:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Aplicar defaults
        for field, default in optional_with_defaults.items():
            if field not in rec:
                rec[field] = default
        
        return {"valid": True}
    
    def _normalize_recommendation(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza valores de la recomendación"""
        
        # Normalizar improvement (puede venir como 0.1 o 10)
        improvement = rec.get("expected_improvement", 0)
        if improvement > 1:
            rec["expected_improvement"] = improvement / 100
        
        # Normalizar confidence
        confidence = rec.get("confidence", 0.5)
        if confidence > 1:
            rec["confidence"] = confidence / 100
        
        # Normalizar effort
        effort = str(rec.get("effort", "medium")).lower()
        if effort not in ["low", "medium", "high"]:
            rec["effort"] = "medium"
        else:
            rec["effort"] = effort
        
        return rec
    
    def _is_duplicate(self, rec: Dict[str, Any], approved: List[Dict[str, Any]]) -> bool:
        """Verifica si la recomendación es similar a una ya aprobada"""
        
        rec_action = str(rec.get("action", "")).lower()
        
        for approved_rec in approved:
            approved_action = str(approved_rec.get("action", "")).lower()
            
            # Similitud simple basada en palabras comunes
            rec_words = set(rec_action.split())
            approved_words = set(approved_action.split())
            
            if len(rec_words) > 0 and len(approved_words) > 0:
                intersection = len(rec_words & approved_words)
                union = len(rec_words | approved_words)
                similarity = intersection / union if union > 0 else 0
                
                if similarity >= self.config.similarity_threshold:
                    return True
        
        return False
    
    def _calculate_authority_score(self, rec: Dict[str, Any]) -> float:
        """Calcula el score de autoridad compuesto"""
        
        weights = self.config.scoring_weights
        
        # Score base de improvement
        improvement = rec.get("expected_improvement", 0)
        improvement_score = min(improvement / 0.30, 1.0)  # Normalizado a max 30%
        
        # Score de confidence
        confidence = rec.get("confidence", 0.5)
        confidence_score = confidence
        
        # Penalización por esfuerzo
        effort = rec.get("effort", "medium")
        effort_penalty = self.EFFORT_PENALTIES.get(effort, 0.05)
        
        # Bonus por fuente confiable
        source = rec.get("source_agent", "")
        source_bonus = self.config.source_trust_bonus if source in self.config.trusted_sources else 0
        
        # Calcular score final
        score = (
            improvement_score * weights["improvement"] +
            confidence_score * weights["confidence"] -
            effort_penalty * weights["effort_penalty"] +
            source_bonus * weights["source_trust"]
        )
        
        return round(max(0, min(1, score)), 4)
    
    def _summarize_rejections(self, rejected: List[Dict[str, Any]]) -> Dict[str, int]:
        """Resume razones de rechazo"""
        summary = {}
        for r in rejected:
            reason = r.get("reason", "unknown")
            summary[reason] = summary.get(reason, 0) + 1
        return summary
    
    def _make_primary_decision(self, approved: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Toma la decisión principal basada en recomendaciones aprobadas"""
        
        if not approved:
            return {
                "action": "HOLD",
                "reason": "No recommendations met quality thresholds",
                "confidence": "n/a"
            }
        
        top = approved[0]
        return {
            "action": "EXECUTE",
            "primary_recommendation": top.get("action"),
            "expected_improvement": f"{top.get('expected_improvement', 0):.1%}",
            "confidence": f"{top.get('confidence', 0):.1%}",
            "authority_score": top.get("authority_score"),
            "reason": f"Top-ranked recommendation (score: {top.get('authority_score', 0):.3f})"
        }
    
    def _calculate_quality_metrics(
        self, 
        approved: List[Dict[str, Any]], 
        rejected: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula métricas de calidad del filtrado"""
        
        total = len(approved) + len(rejected)
        
        if total == 0:
            return {"pass_rate": 0, "avg_score": 0}
        
        pass_rate = len(approved) / total
        
        avg_improvement = 0
        avg_confidence = 0
        avg_score = 0
        
        if approved:
            avg_improvement = sum(r.get("expected_improvement", 0) for r in approved) / len(approved)
            avg_confidence = sum(r.get("confidence", 0) for r in approved) / len(approved)
            avg_score = sum(r.get("authority_score", 0) for r in approved) / len(approved)
        
        return {
            "pass_rate": round(pass_rate, 2),
            "approved_count": len(approved),
            "rejected_count": len(rejected),
            "avg_improvement": round(avg_improvement, 3),
            "avg_confidence": round(avg_confidence, 3),
            "avg_authority_score": round(avg_score, 4)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def apply_authority_filter(
    result: Dict[str, Any],
    config: Optional[AuthorityConfig] = None
) -> Dict[str, Any]:
    """
    Función helper para aplicar Authority Layer.
    Uso: result = apply_authority_filter(agent_result)
    """
    layer = AuthorityLayer(config)
    return layer.apply(result)


def create_authority_config(**kwargs) -> AuthorityConfig:
    """
    Crea configuración personalizada.
    Uso: config = create_authority_config(min_improvement_threshold=0.03, max_recommendations=5)
    """
    return AuthorityConfig(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# MIXIN PARA AGENTES
# ═══════════════════════════════════════════════════════════════════════════════

class AuthorityLayerMixin:
    """
    Mixin para agregar Authority Layer a cualquier agente orquestador.
    Uso: class CampaignOptimizerIA(BaseAgent, AuthorityLayerMixin): ...
    """
    
    authority_config: Optional[AuthorityConfig] = None
    
    def post_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Hook de post-procesamiento que aplica Authority Layer"""
        return apply_authority_filter(result, self.authority_config)
