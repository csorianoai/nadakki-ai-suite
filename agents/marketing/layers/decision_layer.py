"""
Decision Layer - Capa obligatoria para agentes analíticos
Convierte análisis en decisiones accionables
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta

class DecisionLayer:
    """Envuelve respuestas analíticas con decisiones concretas"""
    
    PRIORITY_THRESHOLDS = {
        "critical": 0.8,
        "high": 0.6,
        "medium": 0.4,
        "low": 0.2
    }
    
    def wrap_response(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega capa de decisión a cualquier análisis"""
        
        decision = {
            "action": self._extract_primary_action(analysis),
            "priority": self._calculate_priority(analysis),
            "expected_impact": self._estimate_impact(analysis),
            "confidence": self._assess_confidence(analysis),
            "deadline": self._suggest_deadline(analysis),
            "risk_if_ignored": self._assess_risk(analysis),
            "next_steps": self._generate_next_steps(analysis),
            "success_metrics": self._define_success_metrics(analysis)
        }
        
        return {
            **analysis,
            "decision": decision,
            "decision_summary": self._generate_summary(decision),
            "actionable": True
        }
    
    def _extract_primary_action(self, analysis: Dict) -> str:
        """Extrae la acción más importante del análisis"""
        # Buscar recomendaciones, insights, o conclusiones
        if "recommendations" in analysis:
            recs = analysis["recommendations"]
            if isinstance(recs, list) and len(recs) > 0:
                return f"EJECUTAR: {recs[0]}"
        
        if "insight" in analysis:
            return f"ACTUAR SOBRE: {analysis['insight']}"
        
        if "top_performer" in analysis:
            return f"ESCALAR: {analysis['top_performer']}"
        
        return "REVISAR: Análisis requiere interpretación manual"
    
    def _calculate_priority(self, analysis: Dict) -> str:
        """Calcula prioridad basada en métricas del análisis"""
        score = 0
        
        # Factores que aumentan prioridad
        if analysis.get("confidence", 0) > 0.8:
            score += 0.3
        if analysis.get("expected_improvement", 0) > 0.15:
            score += 0.3
        if analysis.get("urgency", "") == "high":
            score += 0.2
        if analysis.get("revenue_impact", 0) > 10000:
            score += 0.2
        
        for level, threshold in self.PRIORITY_THRESHOLDS.items():
            if score >= threshold:
                return level
        return "low"
    
    def _estimate_impact(self, analysis: Dict) -> Dict[str, Any]:
        """Estima impacto cuantificable"""
        return {
            "metric": analysis.get("primary_metric", "conversion_rate"),
            "current_value": analysis.get("current_value", 0),
            "expected_value": analysis.get("expected_value", 0),
            "improvement_pct": analysis.get("expected_improvement", 0) * 100,
            "confidence_interval": "±5%"
        }
    
    def _assess_confidence(self, analysis: Dict) -> str:
        """Evalúa nivel de confianza"""
        conf = analysis.get("confidence", analysis.get("statistical_significance", 0.5))
        if conf >= 0.95:
            return "very_high"
        elif conf >= 0.85:
            return "high"
        elif conf >= 0.70:
            return "medium"
        else:
            return "low"
    
    def _suggest_deadline(self, analysis: Dict) -> str:
        """Sugiere deadline basado en urgencia"""
        priority = self._calculate_priority(analysis)
        
        deadlines = {
            "critical": datetime.now() + timedelta(hours=24),
            "high": datetime.now() + timedelta(days=3),
            "medium": datetime.now() + timedelta(days=7),
            "low": datetime.now() + timedelta(days=14)
        }
        
        return deadlines.get(priority, datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    def _assess_risk(self, analysis: Dict) -> str:
        """Evalúa riesgo de no actuar"""
        if analysis.get("trend", "") == "declining":
            return "Alto: Métricas en declive, acción urgente requerida"
        if analysis.get("competitor_threat", False):
            return "Medio: Competencia ganando terreno"
        return "Bajo: Situación estable, mejora opcional"
    
    def _generate_next_steps(self, analysis: Dict) -> List[str]:
        """Genera lista de próximos pasos"""
        steps = []
        
        action = self._extract_primary_action(analysis)
        steps.append(f"1. {action}")
        steps.append("2. Configurar tracking de métricas")
        steps.append("3. Definir criterios de éxito")
        steps.append("4. Programar revisión en 7 días")
        
        return steps
    
    def _define_success_metrics(self, analysis: Dict) -> List[Dict]:
        """Define métricas de éxito"""
        return [
            {"metric": "primary_kpi", "target": "+10%", "timeframe": "30 días"},
            {"metric": "secondary_kpi", "target": "+5%", "timeframe": "30 días"}
        ]
    
    def _generate_summary(self, decision: Dict) -> str:
        """Genera resumen ejecutivo de la decisión"""
        return f"ACCIÓN: {decision['action']} | PRIORIDAD: {decision['priority'].upper()} | DEADLINE: {decision['deadline']}"


# Función helper para aplicar a cualquier agente
def apply_decision_layer(agent_response: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica Decision Layer a respuesta de agente"""
    layer = DecisionLayer()
    return layer.wrap_response(agent_response)
