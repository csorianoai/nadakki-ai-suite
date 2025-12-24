"""
Reason Codes Layer - Capa de explicabilidad para agentes de riesgo
Proporciona transparencia y trazabilidad en decisiones de scoring
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ImpactDirection(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class ReasonCode:
    factor: str
    value: Any
    impact: float
    direction: ImpactDirection
    weight: float
    explanation: str

class ReasonCodesLayer:
    """Genera explicaciones detalladas para decisiones de scoring"""
    
    FACTOR_WEIGHTS = {
        "credit_score": 0.25,
        "income": 0.20,
        "debt_to_income": 0.15,
        "employment_months": 0.10,
        "age": 0.05,
        "previous_defaults": 0.15,
        "account_age": 0.05,
        "payment_history": 0.05
    }
    
    BUCKETS = {
        (90, 100): "excellent",
        (80, 89): "very_good",
        (70, 79): "good",
        (60, 69): "fair",
        (50, 59): "poor",
        (0, 49): "very_poor"
    }
    
    def explain_score(self, score: float, factors: Dict[str, Any]) -> Dict[str, Any]:
        """Genera explicación completa del score"""
        
        reason_codes = self._calculate_reason_codes(factors)
        bucket = self._get_bucket(score)
        
        # Separar positivos y negativos
        positives = [r for r in reason_codes if r.direction == ImpactDirection.POSITIVE]
        negatives = [r for r in reason_codes if r.direction == ImpactDirection.NEGATIVE]
        
        # Ordenar por impacto absoluto
        positives.sort(key=lambda x: abs(x.impact), reverse=True)
        negatives.sort(key=lambda x: abs(x.impact), reverse=True)
        
        return {
            "score": round(score, 2),
            "bucket": bucket,
            "bucket_description": self._get_bucket_description(bucket),
            "reason_codes": [self._reason_to_dict(r) for r in reason_codes],
            "top_positive_factors": [self._reason_to_dict(r) for r in positives[:3]],
            "top_negative_factors": [self._reason_to_dict(r) for r in negatives[:3]],
            "recommendation": self._generate_recommendation(score, bucket, positives, negatives),
            "improvement_suggestions": self._suggest_improvements(negatives),
            "confidence": self._calculate_confidence(factors),
            "audit_trail": {
                "factors_evaluated": len(factors),
                "model_version": "v2.0.0",
                "explanation_version": "v1.0.0"
            }
        }
    
    def _calculate_reason_codes(self, factors: Dict[str, Any]) -> List[ReasonCode]:
        """Calcula reason codes para cada factor"""
        codes = []
        
        for factor, value in factors.items():
            if factor not in self.FACTOR_WEIGHTS:
                continue
            
            weight = self.FACTOR_WEIGHTS[factor]
            impact, direction, explanation = self._evaluate_factor(factor, value)
            
            codes.append(ReasonCode(
                factor=factor,
                value=value,
                impact=impact * weight,
                direction=direction,
                weight=weight,
                explanation=explanation
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
            "payment_history": self._eval_payment_history
        }
        
        if factor in evaluators:
            return evaluators[factor](value)
        
        return (0, ImpactDirection.NEUTRAL, "Factor no evaluado")
    
    def _eval_credit_score(self, value: float) -> Tuple[float, ImpactDirection, str]:
        if value >= 750:
            return (15, ImpactDirection.POSITIVE, "Excelente historial crediticio")
        elif value >= 700:
            return (10, ImpactDirection.POSITIVE, "Buen historial crediticio")
        elif value >= 650:
            return (0, ImpactDirection.NEUTRAL, "Historial crediticio aceptable")
        elif value >= 600:
            return (-10, ImpactDirection.NEGATIVE, "Historial crediticio limitado")
        else:
            return (-20, ImpactDirection.NEGATIVE, "Historial crediticio deficiente")
    
    def _eval_income(self, value: float) -> Tuple[float, ImpactDirection, str]:
        if value >= 80000:
            return (12, ImpactDirection.POSITIVE, "Ingresos altos y estables")
        elif value >= 50000:
            return (8, ImpactDirection.POSITIVE, "Ingresos moderados")
        elif value >= 30000:
            return (0, ImpactDirection.NEUTRAL, "Ingresos básicos")
        else:
            return (-8, ImpactDirection.NEGATIVE, "Ingresos por debajo del umbral")
    
    def _eval_dti(self, value: float) -> Tuple[float, ImpactDirection, str]:
        if value <= 0.20:
            return (10, ImpactDirection.POSITIVE, "Bajo nivel de endeudamiento")
        elif value <= 0.35:
            return (5, ImpactDirection.POSITIVE, "Endeudamiento manejable")
        elif value <= 0.45:
            return (-5, ImpactDirection.NEGATIVE, "Endeudamiento elevado")
        else:
            return (-15, ImpactDirection.NEGATIVE, "Sobreendeudamiento")
    
    def _eval_employment(self, value: int) -> Tuple[float, ImpactDirection, str]:
        if value >= 60:
            return (8, ImpactDirection.POSITIVE, "Empleo estable a largo plazo")
        elif value >= 24:
            return (5, ImpactDirection.POSITIVE, "Empleo estable")
        elif value >= 12:
            return (0, ImpactDirection.NEUTRAL, "Empleo reciente")
        else:
            return (-8, ImpactDirection.NEGATIVE, "Empleo muy reciente")
    
    def _eval_age(self, value: int) -> Tuple[float, ImpactDirection, str]:
        if 30 <= value <= 55:
            return (3, ImpactDirection.POSITIVE, "Edad óptima de ingresos")
        elif 25 <= value < 30 or 55 < value <= 65:
            return (0, ImpactDirection.NEUTRAL, "Edad aceptable")
        else:
            return (-3, ImpactDirection.NEGATIVE, "Fuera del rango óptimo de edad")
    
    def _eval_defaults(self, value: int) -> Tuple[float, ImpactDirection, str]:
        if value == 0:
            return (10, ImpactDirection.POSITIVE, "Sin incumplimientos previos")
        elif value == 1:
            return (-10, ImpactDirection.NEGATIVE, "Un incumplimiento previo")
        else:
            return (-25, ImpactDirection.NEGATIVE, f"{value} incumplimientos previos")
    
    def _eval_payment_history(self, value: str) -> Tuple[float, ImpactDirection, str]:
        if value == "excellent":
            return (8, ImpactDirection.POSITIVE, "Historial de pagos excelente")
        elif value == "good":
            return (4, ImpactDirection.POSITIVE, "Buen historial de pagos")
        elif value == "fair":
            return (-4, ImpactDirection.NEGATIVE, "Historial de pagos irregular")
        else:
            return (-12, ImpactDirection.NEGATIVE, "Historial de pagos deficiente")
    
    def _get_bucket(self, score: float) -> str:
        for (low, high), bucket in self.BUCKETS.items():
            if low <= score <= high:
                return bucket
        return "unknown"
    
    def _get_bucket_description(self, bucket: str) -> str:
        descriptions = {
            "excellent": "Cliente premium, máxima confianza",
            "very_good": "Cliente preferente, alta confianza",
            "good": "Cliente estándar, confianza moderada",
            "fair": "Cliente con observaciones, revisar condiciones",
            "poor": "Cliente de alto riesgo, condiciones restrictivas",
            "very_poor": "No recomendado, requiere garantías adicionales"
        }
        return descriptions.get(bucket, "Sin clasificación")
    
    def _generate_recommendation(self, score: float, bucket: str, positives: List, negatives: List) -> str:
        if bucket in ["excellent", "very_good"]:
            return "APROBAR: Cliente calificado para mejores condiciones"
        elif bucket == "good":
            return "APROBAR: Cliente calificado con condiciones estándar"
        elif bucket == "fair":
            if len(negatives) <= 2:
                return "APROBAR CON CONDICIONES: Límite reducido o tasa ajustada"
            return "REVISAR: Requiere análisis adicional"
        else:
            return "RECHAZAR o GARANTÍA: Riesgo elevado, requiere colateral"
    
    def _suggest_improvements(self, negatives: List[ReasonCode]) -> List[str]:
        suggestions = []
        for neg in negatives[:3]:
            if neg.factor == "credit_score":
                suggestions.append("Mejorar historial crediticio pagando a tiempo")
            elif neg.factor == "debt_to_income":
                suggestions.append("Reducir deudas existentes antes de nueva solicitud")
            elif neg.factor == "employment_months":
                suggestions.append("Esperar mayor antigüedad laboral")
            elif neg.factor == "income":
                suggestions.append("Demostrar ingresos adicionales o colateral")
        return suggestions
    
    def _calculate_confidence(self, factors: Dict) -> float:
        """Calcula confianza basada en completitud de datos"""
        required = ["credit_score", "income", "debt_to_income"]
        present = sum(1 for f in required if f in factors)
        return round(present / len(required), 2)
    
    def _reason_to_dict(self, reason: ReasonCode) -> Dict:
        return {
            "factor": reason.factor,
            "value": reason.value,
            "impact": round(reason.impact, 2),
            "direction": reason.direction.value,
            "weight": reason.weight,
            "explanation": reason.explanation
        }


# Función helper
def apply_reason_codes(score: float, factors: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica Reason Codes Layer a un score"""
    layer = ReasonCodesLayer()
    return layer.explain_score(score, factors)
