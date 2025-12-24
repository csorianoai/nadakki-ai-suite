"""
Decision Layer v2.0 - Capa de decisión robusta para agentes analíticos
Mejoras:
- Idempotencia (no se aplica dos veces)
- Configuración declarativa
- Benchmark contra baseline
- Compatible con post_process()
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib


class DecisionLayerConfig:
    """Configuración declarativa para Decision Layer"""
    
    def __init__(
        self,
        require_action: bool = True,
        require_deadline: bool = True,
        require_impact: bool = True,
        min_confidence_for_action: float = 0.6,
        default_deadline_days: int = 7,
        include_benchmark: bool = True,
        benchmark_source: str = "industry_average"
    ):
        self.require_action = require_action
        self.require_deadline = require_deadline
        self.require_impact = require_impact
        self.min_confidence_for_action = min_confidence_for_action
        self.default_deadline_days = default_deadline_days
        self.include_benchmark = include_benchmark
        self.benchmark_source = benchmark_source


class DecisionLayer:
    """
    Capa de decisión que convierte análisis en acciones concretas.
    Diseñada para ser idempotente y configurable.
    """
    
    VERSION = "v2.0.0"
    MARKER = "_decision_layer_applied"
    
    PRIORITY_THRESHOLDS = {
        "critical": 0.8,
        "high": 0.6,
        "medium": 0.4,
        "low": 0.2
    }
    
    # Benchmarks por industria/métrica (placeholder - expandir con datos reales)
    BENCHMARKS = {
        "conversion_rate": {"industry_average": 0.03, "top_performers": 0.08},
        "email_open_rate": {"industry_average": 0.22, "top_performers": 0.35},
        "ctr": {"industry_average": 0.02, "top_performers": 0.05},
        "roas": {"industry_average": 2.5, "top_performers": 5.0},
        "churn_rate": {"industry_average": 0.05, "top_performers": 0.02},
        "cac": {"industry_average": 50, "top_performers": 25},
        "ltv": {"industry_average": 500, "top_performers": 1500}
    }
    
    def __init__(self, config: Optional[DecisionLayerConfig] = None):
        self.config = config or DecisionLayerConfig()
    
    def apply(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica la capa de decisión al resultado del agente.
        Es idempotente - no se aplica dos veces.
        """
        # Verificar idempotencia
        if result.get(self.MARKER):
            return result
        
        # Marcar como aplicado
        result[self.MARKER] = True
        result["_decision_layer_version"] = self.VERSION
        result["_decision_layer_timestamp"] = datetime.now().isoformat()
        
        # Construir decisión
        decision = self._build_decision(result)
        
        # Agregar benchmark si está configurado
        if self.config.include_benchmark:
            decision["benchmark"] = self._compare_to_benchmark(result)
        
        result["decision"] = decision
        result["decision_summary"] = self._generate_summary(decision)
        result["actionable"] = decision.get("action") != "REVIEW_REQUIRED"
        
        return result
    
    def _build_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Construye el objeto de decisión completo"""
        
        action = self._extract_primary_action(analysis)
        priority = self._calculate_priority(analysis)
        confidence = self._assess_confidence(analysis)
        
        # Si la confianza es baja, marcar para revisión
        if confidence == "low" and self.config.min_confidence_for_action > 0.5:
            action = "REVIEW_REQUIRED: Confianza insuficiente para acción automática"
        
        decision = {
            "action": action,
            "priority": priority,
            "confidence": confidence,
            "confidence_score": analysis.get("confidence", analysis.get("statistical_significance", 0.5))
        }
        
        if self.config.require_impact:
            decision["expected_impact"] = self._estimate_impact(analysis)
        
        if self.config.require_deadline:
            decision["deadline"] = self._suggest_deadline(priority)
            decision["deadline_reason"] = f"Basado en prioridad {priority}"
        
        decision["risk_if_ignored"] = self._assess_risk(analysis)
        decision["next_steps"] = self._generate_next_steps(analysis, action)
        decision["success_metrics"] = self._define_success_metrics(analysis)
        
        return decision
    
    def _extract_primary_action(self, analysis: Dict[str, Any]) -> str:
        """Extrae la acción más importante del análisis"""
        
        # Buscar en diferentes estructuras de respuesta
        action_sources = [
            ("recommendations", lambda x: f"EJECUTAR: {x[0]}" if x else None),
            ("top_recommendation", lambda x: f"EJECUTAR: {x}"),
            ("insight", lambda x: f"ACTUAR SOBRE: {x}"),
            ("winner", lambda x: f"IMPLEMENTAR: {x}"),
            ("top_performer", lambda x: f"ESCALAR: {x}"),
            ("optimal_allocation", lambda x: f"REASIGNAR: {x}"),
            ("predicted_action", lambda x: f"ANTICIPAR: {x}"),
            ("next_best_action", lambda x: f"EJECUTAR: {x}")
        ]
        
        for key, extractor in action_sources:
            if key in analysis:
                value = analysis[key]
                if value:
                    action = extractor(value) if callable(extractor) else value
                    if action:
                        return action
        
        # Si no hay acción clara, sugerir revisión
        return "REVISAR: Análisis requiere interpretación manual"
    
    def _calculate_priority(self, analysis: Dict[str, Any]) -> str:
        """Calcula prioridad basada en múltiples factores"""
        score = 0.0
        
        # Factor: Confianza estadística
        confidence = analysis.get("confidence", analysis.get("statistical_significance", 0.5))
        if confidence > 0.95:
            score += 0.25
        elif confidence > 0.85:
            score += 0.15
        
        # Factor: Impacto esperado
        improvement = analysis.get("expected_improvement", analysis.get("uplift", 0))
        if isinstance(improvement, (int, float)):
            if improvement > 0.20:
                score += 0.25
            elif improvement > 0.10:
                score += 0.15
            elif improvement > 0.05:
                score += 0.10
        
        # Factor: Urgencia explícita
        if analysis.get("urgency") == "high":
            score += 0.20
        elif analysis.get("urgency") == "medium":
            score += 0.10
        
        # Factor: Impacto en revenue
        revenue_impact = analysis.get("revenue_impact", 0)
        if revenue_impact > 50000:
            score += 0.20
        elif revenue_impact > 10000:
            score += 0.10
        
        # Factor: Tendencia negativa
        if analysis.get("trend") == "declining":
            score += 0.15
        
        # Determinar nivel
        for level, threshold in self.PRIORITY_THRESHOLDS.items():
            if score >= threshold:
                return level
        return "low"
    
    def _assess_confidence(self, analysis: Dict[str, Any]) -> str:
        """Evalúa nivel de confianza"""
        conf = analysis.get("confidence", analysis.get("statistical_significance", 0.5))
        
        if isinstance(conf, str):
            return conf
        
        if conf >= 0.95:
            return "very_high"
        elif conf >= 0.85:
            return "high"
        elif conf >= 0.70:
            return "medium"
        else:
            return "low"
    
    def _estimate_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Estima impacto cuantificable"""
        
        metric = analysis.get("primary_metric", "conversion_rate")
        current = analysis.get("current_value", analysis.get("baseline", 0))
        expected = analysis.get("expected_value", analysis.get("projected", 0))
        improvement = analysis.get("expected_improvement", analysis.get("uplift", 0))
        
        # Calcular improvement si no está presente
        if not improvement and current and expected:
            improvement = (expected - current) / current if current > 0 else 0
        
        return {
            "metric": metric,
            "current_value": current,
            "expected_value": expected,
            "improvement_pct": round(improvement * 100, 2) if improvement else 0,
            "confidence_interval": "±5%",
            "time_to_impact": "2-4 semanas"
        }
    
    def _suggest_deadline(self, priority: str) -> str:
        """Sugiere deadline basado en prioridad"""
        
        deadline_days = {
            "critical": 1,
            "high": 3,
            "medium": 7,
            "low": 14
        }
        
        days = deadline_days.get(priority, self.config.default_deadline_days)
        deadline = datetime.now() + timedelta(days=days)
        return deadline.strftime("%Y-%m-%d")
    
    def _assess_risk(self, analysis: Dict[str, Any]) -> str:
        """Evalúa riesgo de no actuar"""
        
        risk_factors = []
        
        if analysis.get("trend") == "declining":
            risk_factors.append("métricas en declive")
        
        if analysis.get("competitor_threat"):
            risk_factors.append("amenaza competitiva detectada")
        
        if analysis.get("churn_risk", 0) > 0.3:
            risk_factors.append("alto riesgo de churn")
        
        if analysis.get("revenue_at_risk", 0) > 10000:
            risk_factors.append(f"${analysis['revenue_at_risk']:,.0f} en riesgo")
        
        if risk_factors:
            return f"ALTO: {', '.join(risk_factors)}"
        
        return "BAJO: Situación estable, mejora opcional"
    
    def _generate_next_steps(self, analysis: Dict[str, Any], action: str) -> List[str]:
        """Genera lista de próximos pasos concretos"""
        
        steps = [f"1. {action}"]
        
        if "segment" in str(analysis.get("recommendations", [])).lower():
            steps.append("2. Segmentar audiencia según criterios identificados")
        
        if analysis.get("test_recommended"):
            steps.append("3. Configurar A/B test para validar hipótesis")
        
        steps.append(f"{len(steps)+1}. Configurar tracking de métricas clave")
        steps.append(f"{len(steps)+1}. Programar revisión de resultados en 7 días")
        
        return steps
    
    def _define_success_metrics(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define métricas de éxito medibles"""
        
        metric = analysis.get("primary_metric", "conversion_rate")
        improvement = analysis.get("expected_improvement", 0.10)
        
        return [
            {
                "metric": metric,
                "target": f"+{improvement*100:.0f}%",
                "timeframe": "30 días",
                "measurement": "vs baseline pre-implementación"
            },
            {
                "metric": "roi_de_implementacion",
                "target": ">100%",
                "timeframe": "60 días",
                "measurement": "beneficio / costo de implementación"
            }
        ]
    
    def _compare_to_benchmark(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compara resultados contra benchmarks de industria"""
        
        metric = analysis.get("primary_metric", "conversion_rate")
        current = analysis.get("current_value", 0)
        
        if metric not in self.BENCHMARKS:
            return {"status": "no_benchmark_available", "metric": metric}
        
        benchmarks = self.BENCHMARKS[metric]
        industry_avg = benchmarks.get(self.config.benchmark_source, benchmarks.get("industry_average", 0))
        top_performers = benchmarks.get("top_performers", industry_avg * 1.5)
        
        if current >= top_performers:
            position = "top_performer"
            delta = f"+{((current - top_performers) / top_performers * 100):.1f}% sobre top"
        elif current >= industry_avg:
            position = "above_average"
            delta = f"+{((current - industry_avg) / industry_avg * 100):.1f}% sobre promedio"
        else:
            position = "below_average"
            delta = f"-{((industry_avg - current) / industry_avg * 100):.1f}% bajo promedio"
        
        return {
            "metric": metric,
            "current_value": current,
            "industry_average": industry_avg,
            "top_performers": top_performers,
            "position": position,
            "delta_vs_benchmark": delta,
            "benchmark_source": self.config.benchmark_source
        }
    
    def _generate_summary(self, decision: Dict[str, Any]) -> str:
        """Genera resumen ejecutivo de una línea"""
        
        action = decision.get("action", "REVISAR")[:50]
        priority = decision.get("priority", "medium").upper()
        deadline = decision.get("deadline", "TBD")
        
        return f"[{priority}] {action} | Deadline: {deadline}"


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def apply_decision_layer(
    result: Dict[str, Any],
    config: Optional[DecisionLayerConfig] = None
) -> Dict[str, Any]:
    """
    Función helper para aplicar Decision Layer.
    Uso: result = apply_decision_layer(agent_result)
    """
    layer = DecisionLayer(config)
    return layer.apply(result)


def create_decision_config(**kwargs) -> DecisionLayerConfig:
    """
    Crea configuración personalizada.
    Uso: config = create_decision_config(min_confidence_for_action=0.8)
    """
    return DecisionLayerConfig(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# POST_PROCESS MIXIN
# ═══════════════════════════════════════════════════════════════════════════════

class DecisionLayerMixin:
    """
    Mixin para agregar Decision Layer a cualquier agente.
    Uso: class MyAgent(BaseAgent, DecisionLayerMixin): ...
    """
    
    decision_layer_config: Optional[DecisionLayerConfig] = None
    
    def post_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Hook de post-procesamiento que aplica Decision Layer"""
        return apply_decision_layer(result, self.decision_layer_config)
