"""
Reason Codes Layer v2.0 - Capa de explicabilidad para agentes de riesgo
Mejoras:
- Idempotencia
- Configuración declarativa
- Audit trail completo
- Compliance-ready
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class ImpactDirection(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class RiskBucket(Enum):
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    VERY_POOR = "very_poor"


@dataclass
class ReasonCode:
    """Estructura de un reason code individual"""
    code: str
    factor: str
    value: Any
    impact: float
    direction: ImpactDirection
    weight: float
    explanation: str
    category: str = "general"


@dataclass
class ReasonCodesConfig:
    """Configuración declarativa para Reason Codes Layer"""
    
    # Pesos de factores (deben sumar ~1.0)
    factor_weights: Dict[str, float] = field(default_factory=lambda: {
        "credit_score": 0.25,
        "income": 0.20,
        "debt_to_income": 0.15,
        "employment_months": 0.10,
        "age": 0.05,
        "previous_defaults": 0.15,
        "account_age": 0.05,
        "payment_history": 0.05
    })
    
    # Buckets de score
    score_buckets: Dict[Tuple[int, int], str] = field(default_factory=lambda: {
        (90, 100): "excellent",
        (80, 89): "very_good",
        (70, 79): "good",
        (60, 69): "fair",
        (50, 59): "poor",
        (0, 49): "very_poor"
    })
    
    # Configuración de compliance
    require_audit_trail: bool = True
    require_all_factors: bool = False
    min_factors_for_decision: int = 3
    include_improvement_suggestions: bool = True
    
    # Configuración de output
    max_positive_factors: int = 3
    max_negative_factors: int = 3
    include_neutral_factors: bool = False


class ReasonCodesLayer:
    """
    Capa de explicabilidad que genera reason codes para decisiones de scoring.
    Diseñada para compliance y auditoría.
    """
    
    VERSION = "v2.0.0"
    MARKER = "_reason_codes_applied"
    
    def __init__(self, config: Optional[ReasonCodesConfig] = None):
        self.config = config or ReasonCodesConfig()
        self._reason_code_counter = 0
    
    def apply(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica reason codes al resultado.
        Es idempotente - no se aplica dos veces.
        """
        # Verificar idempotencia
        if result.get(self.MARKER):
            return result
        
        # Extraer score y factores
        score = self._extract_score(result)
        factors = self._extract_factors(result)
        
        if score is None:
            result["_reason_codes_error"] = "No score found in result"
            return result
        
        # Marcar como aplicado
        result[self.MARKER] = True
        result["_reason_codes_version"] = self.VERSION
        result["_reason_codes_timestamp"] = datetime.now().isoformat()
        
        # Generar explicación
        explanation = self._generate_explanation(score, factors)
        
        # Agregar al resultado
        result["explanation"] = explanation
        result["explainable"] = True
        
        return result
    
    def _extract_score(self, result: Dict[str, Any]) -> Optional[float]:
        """Extrae el score del resultado"""
        score_keys = ["score", "risk_score", "lead_score", "credit_score", "final_score"]
        
        for key in score_keys:
            if key in result:
                return float(result[key])
        
        # Buscar en nested
        if "result" in result and isinstance(result["result"], dict):
            for key in score_keys:
                if key in result["result"]:
                    return float(result["result"][key])
        
        return None
    
    def _extract_factors(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae los factores del resultado"""
        factors = {}
        
        # Buscar factores conocidos
        known_factors = list(self.config.factor_weights.keys())
        
        def search_dict(d: dict, prefix: str = ""):
            for key, value in d.items():
                if key in known_factors:
                    factors[key] = value
                elif isinstance(value, dict):
                    search_dict(value, f"{prefix}{key}.")
        
        search_dict(result)
        
        # También buscar en input_data si existe
        if "input_data" in result:
            search_dict(result["input_data"])
        
        return factors
    
    def _generate_explanation(self, score: float, factors: Dict[str, Any]) -> Dict[str, Any]:
        """Genera la explicación completa"""
        
        # Calcular reason codes
        reason_codes = self._calculate_reason_codes(factors)
        
        # Clasificar por bucket
        bucket = self._get_bucket(score)
        
        # Separar positivos, negativos, neutrales
        positives = [r for r in reason_codes if r.direction == ImpactDirection.POSITIVE]
        negatives = [r for r in reason_codes if r.direction == ImpactDirection.NEGATIVE]
        neutrals = [r for r in reason_codes if r.direction == ImpactDirection.NEUTRAL]
        
        # Ordenar por impacto
        positives.sort(key=lambda x: abs(x.impact), reverse=True)
        negatives.sort(key=lambda x: abs(x.impact), reverse=True)
        
        # Construir explicación
        explanation = {
            "score": round(score, 2),
            "bucket": bucket,
            "bucket_description": self._get_bucket_description(bucket),
            "reason_codes": [self._reason_to_dict(r) for r in reason_codes],
            "top_positive_factors": [
                self._reason_to_dict(r) 
                for r in positives[:self.config.max_positive_factors]
            ],
            "top_negative_factors": [
                self._reason_to_dict(r) 
                for r in negatives[:self.config.max_negative_factors]
            ],
            "factors_evaluated": len(factors),
            "factors_with_impact": len([r for r in reason_codes if r.impact != 0])
        }
        
        # Agregar neutrales si está configurado
        if self.config.include_neutral_factors:
            explanation["neutral_factors"] = [self._reason_to_dict(r) for r in neutrals]
        
        # Generar recomendación
        explanation["recommendation"] = self._generate_recommendation(score, bucket, positives, negatives)
        
        # Sugerencias de mejora
        if self.config.include_improvement_suggestions:
            explanation["improvement_suggestions"] = self._suggest_improvements(negatives)
        
        # Calcular confianza
        explanation["confidence"] = self._calculate_confidence(factors, reason_codes)
        
        # Audit trail
        if self.config.require_audit_trail:
            explanation["audit_trail"] = self._generate_audit_trail(score, factors, reason_codes)
        
        return explanation
    
    def _calculate_reason_codes(self, factors: Dict[str, Any]) -> List[ReasonCode]:
        """Calcula reason codes para cada factor"""
        codes = []
        
        for factor, value in factors.items():
            weight = self.config.factor_weights.get(factor, 0.05)
            impact, direction, explanation = self._evaluate_factor(factor, value)
            
            self._reason_code_counter += 1
            code = f"RC{self._reason_code_counter:04d}"
            
            codes.append(ReasonCode(
                code=code,
                factor=factor,
                value=value,
                impact=round(impact * weight, 3),
                direction=direction,
                weight=weight,
                explanation=explanation,
                category=self._get_factor_category(factor)
            ))
        
        return codes
    
    def _evaluate_factor(self, factor: str, value: Any) -> Tuple[float, ImpactDirection, str]:
        """Evalúa un factor individual"""
        
        evaluators = {
            "credit_score": self._eval_credit_score,
            "income": self._eval_income,
            "debt_to_income": self._eval_dti,
            "employment_months": self._eval_employment,
            "age": self._eval_age,
            "previous_defaults": self._eval_defaults,
            "payment_history": self._eval_payment_history,
            "account_age": self._eval_account_age
        }
        
        if factor in evaluators:
            return evaluators[factor](value)
        
        # Evaluador genérico para factores desconocidos
        return self._eval_generic(factor, value)
    
    def _eval_credit_score(self, value: float) -> Tuple[float, ImpactDirection, str]:
        if value >= 750:
            return (15, ImpactDirection.POSITIVE, "Excelente historial crediticio (750+)")
        elif value >= 700:
            return (10, ImpactDirection.POSITIVE, "Buen historial crediticio (700-749)")
        elif value >= 650:
            return (0, ImpactDirection.NEUTRAL, "Historial crediticio aceptable (650-699)")
        elif value >= 600:
            return (-10, ImpactDirection.NEGATIVE, "Historial crediticio limitado (600-649)")
        else:
            return (-20, ImpactDirection.NEGATIVE, "Historial crediticio deficiente (<600)")
    
    def _eval_income(self, value: float) -> Tuple[float, ImpactDirection, str]:
        if value >= 100000:
            return (15, ImpactDirection.POSITIVE, "Ingresos muy altos (>$100k)")
        elif value >= 70000:
            return (12, ImpactDirection.POSITIVE, "Ingresos altos ($70k-$100k)")
        elif value >= 50000:
            return (8, ImpactDirection.POSITIVE, "Ingresos moderados-altos ($50k-$70k)")
        elif value >= 30000:
            return (0, ImpactDirection.NEUTRAL, "Ingresos moderados ($30k-$50k)")
        else:
            return (-10, ImpactDirection.NEGATIVE, "Ingresos por debajo del umbral (<$30k)")
    
    def _eval_dti(self, value: float) -> Tuple[float, ImpactDirection, str]:
        # DTI = Debt to Income ratio (menor es mejor)
        if value <= 0.20:
            return (12, ImpactDirection.POSITIVE, "Muy bajo nivel de endeudamiento (≤20%)")
        elif value <= 0.30:
            return (8, ImpactDirection.POSITIVE, "Bajo nivel de endeudamiento (21-30%)")
        elif value <= 0.40:
            return (0, ImpactDirection.NEUTRAL, "Endeudamiento moderado (31-40%)")
        elif value <= 0.50:
            return (-8, ImpactDirection.NEGATIVE, "Endeudamiento elevado (41-50%)")
        else:
            return (-15, ImpactDirection.NEGATIVE, "Sobreendeudamiento (>50%)")
    
    def _eval_employment(self, value: int) -> Tuple[float, ImpactDirection, str]:
        if value >= 60:
            return (10, ImpactDirection.POSITIVE, "Empleo muy estable (5+ años)")
        elif value >= 36:
            return (8, ImpactDirection.POSITIVE, "Empleo estable (3-5 años)")
        elif value >= 24:
            return (5, ImpactDirection.POSITIVE, "Empleo establecido (2-3 años)")
        elif value >= 12:
            return (0, ImpactDirection.NEUTRAL, "Empleo reciente (1-2 años)")
        elif value >= 6:
            return (-5, ImpactDirection.NEGATIVE, "Empleo muy reciente (6-12 meses)")
        else:
            return (-10, ImpactDirection.NEGATIVE, "Empleo nuevo (<6 meses)")
    
    def _eval_age(self, value: int) -> Tuple[float, ImpactDirection, str]:
        if 30 <= value <= 55:
            return (5, ImpactDirection.POSITIVE, "Edad óptima de ingresos (30-55)")
        elif 25 <= value < 30 or 55 < value <= 65:
            return (0, ImpactDirection.NEUTRAL, "Edad aceptable")
        elif 18 <= value < 25:
            return (-3, ImpactDirection.NEGATIVE, "Joven, historial limitado (<25)")
        else:
            return (-5, ImpactDirection.NEGATIVE, "Fuera del rango óptimo")
    
    def _eval_defaults(self, value: int) -> Tuple[float, ImpactDirection, str]:
        if value == 0:
            return (12, ImpactDirection.POSITIVE, "Sin incumplimientos previos")
        elif value == 1:
            return (-12, ImpactDirection.NEGATIVE, "Un incumplimiento previo registrado")
        elif value == 2:
            return (-20, ImpactDirection.NEGATIVE, "Dos incumplimientos previos")
        else:
            return (-30, ImpactDirection.NEGATIVE, f"Múltiples incumplimientos ({value})")
    
    def _eval_payment_history(self, value: Any) -> Tuple[float, ImpactDirection, str]:
        if isinstance(value, str):
            value = value.lower()
            if value in ["excellent", "excelente"]:
                return (10, ImpactDirection.POSITIVE, "Historial de pagos excelente")
            elif value in ["good", "bueno"]:
                return (5, ImpactDirection.POSITIVE, "Buen historial de pagos")
            elif value in ["fair", "regular"]:
                return (-5, ImpactDirection.NEGATIVE, "Historial de pagos irregular")
            else:
                return (-12, ImpactDirection.NEGATIVE, "Historial de pagos deficiente")
        return (0, ImpactDirection.NEUTRAL, "Historial de pagos no evaluable")
    
    def _eval_account_age(self, value: int) -> Tuple[float, ImpactDirection, str]:
        # Account age in months
        if value >= 60:
            return (8, ImpactDirection.POSITIVE, "Cuenta establecida (5+ años)")
        elif value >= 24:
            return (4, ImpactDirection.POSITIVE, "Cuenta con antigüedad (2-5 años)")
        elif value >= 12:
            return (0, ImpactDirection.NEUTRAL, "Cuenta reciente (1-2 años)")
        else:
            return (-5, ImpactDirection.NEGATIVE, "Cuenta nueva (<1 año)")
    
    def _eval_generic(self, factor: str, value: Any) -> Tuple[float, ImpactDirection, str]:
        """Evaluador genérico para factores no definidos"""
        return (0, ImpactDirection.NEUTRAL, f"Factor '{factor}' evaluado sin reglas específicas")
    
    def _get_factor_category(self, factor: str) -> str:
        """Categoriza el factor"""
        categories = {
            "credit_score": "credit",
            "previous_defaults": "credit",
            "payment_history": "credit",
            "income": "financial",
            "debt_to_income": "financial",
            "employment_months": "stability",
            "account_age": "stability",
            "age": "demographic"
        }
        return categories.get(factor, "other")
    
    def _get_bucket(self, score: float) -> str:
        """Determina el bucket del score"""
        for (low, high), bucket in self.config.score_buckets.items():
            if low <= score <= high:
                return bucket
        return "unknown"
    
    def _get_bucket_description(self, bucket: str) -> str:
        """Descripción del bucket"""
        descriptions = {
            "excellent": "Cliente premium - Máxima confianza, mejores condiciones",
            "very_good": "Cliente preferente - Alta confianza, condiciones favorables",
            "good": "Cliente estándar - Confianza moderada, condiciones normales",
            "fair": "Cliente con observaciones - Revisar condiciones, posibles restricciones",
            "poor": "Cliente de alto riesgo - Condiciones restrictivas, garantías requeridas",
            "very_poor": "No recomendado - Riesgo muy alto, requiere análisis especial"
        }
        return descriptions.get(bucket, "Sin clasificación")
    
    def _generate_recommendation(
        self, 
        score: float, 
        bucket: str, 
        positives: List[ReasonCode], 
        negatives: List[ReasonCode]
    ) -> Dict[str, Any]:
        """Genera recomendación basada en el análisis"""
        
        recommendations = {
            "excellent": {
                "action": "APROBAR",
                "conditions": "Mejores tasas y límites disponibles",
                "confidence": "very_high"
            },
            "very_good": {
                "action": "APROBAR",
                "conditions": "Condiciones preferenciales",
                "confidence": "high"
            },
            "good": {
                "action": "APROBAR",
                "conditions": "Condiciones estándar",
                "confidence": "high"
            },
            "fair": {
                "action": "APROBAR_CON_CONDICIONES",
                "conditions": "Límite reducido o tasa ajustada según factores negativos",
                "confidence": "medium"
            },
            "poor": {
                "action": "REVISAR",
                "conditions": "Requiere análisis adicional o garantías",
                "confidence": "low"
            },
            "very_poor": {
                "action": "RECHAZAR_O_GARANTIA",
                "conditions": "Solo con garantía colateral significativa",
                "confidence": "low"
            }
        }
        
        rec = recommendations.get(bucket, recommendations["fair"])
        
        # Añadir contexto de los factores
        if positives:
            rec["main_strengths"] = [p.explanation for p in positives[:2]]
        if negatives:
            rec["main_concerns"] = [n.explanation for n in negatives[:2]]
        
        return rec
    
    def _suggest_improvements(self, negatives: List[ReasonCode]) -> List[str]:
        """Genera sugerencias de mejora basadas en factores negativos"""
        
        suggestions = []
        seen_categories = set()
        
        improvement_map = {
            "credit_score": "Mejorar historial crediticio: pagar a tiempo, reducir utilización de crédito",
            "debt_to_income": "Reducir nivel de deuda existente antes de nueva solicitud",
            "employment_months": "Esperar mayor antigüedad laboral (mínimo 12 meses recomendado)",
            "income": "Documentar ingresos adicionales o buscar co-solicitante",
            "previous_defaults": "Regularizar situación de deudas previas, esperar rehabilitación",
            "payment_history": "Mantener pagos al día por al menos 6 meses consecutivos",
            "account_age": "Mantener cuentas activas para construir antigüedad",
            "age": "Considerar co-solicitante con perfil complementario"
        }
        
        for neg in negatives:
            if neg.factor in improvement_map and neg.factor not in seen_categories:
                suggestions.append(improvement_map[neg.factor])
                seen_categories.add(neg.factor)
            
            if len(suggestions) >= 3:
                break
        
        return suggestions
    
    def _calculate_confidence(self, factors: Dict[str, Any], reason_codes: List[ReasonCode]) -> Dict[str, Any]:
        """Calcula nivel de confianza de la explicación"""
        
        required_factors = ["credit_score", "income", "debt_to_income"]
        present = sum(1 for f in required_factors if f in factors)
        completeness = present / len(required_factors)
        
        total_weight = sum(r.weight for r in reason_codes)
        
        return {
            "level": "high" if completeness >= 0.8 else "medium" if completeness >= 0.5 else "low",
            "completeness_score": round(completeness, 2),
            "factors_coverage": f"{len(factors)}/{len(self.config.factor_weights)}",
            "total_weight_evaluated": round(total_weight, 2)
        }
    
    def _generate_audit_trail(
        self, 
        score: float, 
        factors: Dict[str, Any], 
        reason_codes: List[ReasonCode]
    ) -> Dict[str, Any]:
        """Genera audit trail para compliance"""
        
        # Hash de los inputs para verificación
        input_hash = hashlib.sha256(
            f"{score}{sorted(factors.items())}".encode()
        ).hexdigest()[:16]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "model_version": self.VERSION,
            "input_hash": input_hash,
            "score_evaluated": score,
            "factors_count": len(factors),
            "reason_codes_generated": len(reason_codes),
            "config_hash": hashlib.sha256(
                str(self.config.factor_weights).encode()
            ).hexdigest()[:8],
            "compliance_note": "Decisión generada algorítmicamente con explicabilidad completa"
        }
    
    def _reason_to_dict(self, reason: ReasonCode) -> Dict[str, Any]:
        """Convierte ReasonCode a diccionario"""
        return {
            "code": reason.code,
            "factor": reason.factor,
            "value": reason.value,
            "impact": reason.impact,
            "direction": reason.direction.value,
            "weight": reason.weight,
            "explanation": reason.explanation,
            "category": reason.category
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def apply_reason_codes(
    result: Dict[str, Any],
    config: Optional[ReasonCodesConfig] = None
) -> Dict[str, Any]:
    """
    Función helper para aplicar Reason Codes Layer.
    Uso: result = apply_reason_codes(agent_result)
    """
    layer = ReasonCodesLayer(config)
    return layer.apply(result)


def create_reason_codes_config(**kwargs) -> ReasonCodesConfig:
    """
    Crea configuración personalizada.
    Uso: config = create_reason_codes_config(require_audit_trail=True)
    """
    return ReasonCodesConfig(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# MIXIN PARA AGENTES
# ═══════════════════════════════════════════════════════════════════════════════

class ReasonCodesMixin:
    """
    Mixin para agregar Reason Codes a cualquier agente de riesgo.
    Uso: class LeadScoringIA(BaseAgent, ReasonCodesMixin): ...
    """
    
    reason_codes_config: Optional[ReasonCodesConfig] = None
    
    def post_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Hook de post-procesamiento que aplica Reason Codes"""
        return apply_reason_codes(result, self.reason_codes_config)
