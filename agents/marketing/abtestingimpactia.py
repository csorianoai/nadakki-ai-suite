# agents/marketing/abtestingimpactia.py
"""
ABTestingImpactIA v3.0 - Análisis de Impacto de Tests A/B
Simplificado y funcional - acepta dict como input.
"""

from __future__ import annotations
import time
import logging
import math
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class ABTestingImpactIA:
    VERSION = "3.0.0"
    AGENT_ID = "abtestingimpactia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta análisis de impacto A/B - acepta dict."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            test_id = data.get("test_id", "test_001")
            variants = data.get("variants", [])
            confidence_level = data.get("confidence_level", 0.95)
            primary_metric = data.get("primary_metric", "conversion_rate")
            
            # Analizar variantes
            analysis = self._analyze_variants(variants, primary_metric)
            
            # Calcular significancia estadística
            stats = self._calculate_statistics(analysis, confidence_level)
            
            # Determinar ganador
            winner = self._determine_winner(analysis, stats)
            
            # Calcular impacto proyectado
            impact = self._calculate_impact(analysis, winner)
            
            # Generar recomendación
            recommendation = self._generate_recommendation(winner, stats, impact)
            
            # Insights
            insights = self._generate_insights(analysis, stats, winner)
            
            decision_trace = [
                f"test_id={test_id}",
                f"variants_analyzed={len(analysis)}",
                f"primary_metric={primary_metric}",
                f"statistical_significance={stats.get('is_significant', False)}"
            ]
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "analysis_id": f"ab_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "test_id": test_id,
                "variants_analysis": analysis,
                "statistical_analysis": stats,
                "winner": winner,
                "projected_impact": impact,
                "recommendation": recommendation,
                "summary": {
                    "is_conclusive": stats.get("is_significant", False),
                    "confidence_level": confidence_level,
                    "winning_variant": winner.get("variant", "none") if winner else "inconclusive",
                    "improvement": winner.get("improvement_pct", 0) if winner else 0,
                    "sample_size_adequate": stats.get("sample_adequate", True)
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
                "analysis_id": "error",
                "tenant_id": self.tenant_id,
                "test_id": "error",
                "variants_analysis": [],
                "statistical_analysis": {},
                "winner": None,
                "projected_impact": {},
                "recommendation": f"Error: {str(e)[:100]}",
                "summary": {},
                "key_insights": [f"Error: {str(e)[:100]}"],
                "decision_trace": ["error_occurred"],
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
    
    def _analyze_variants(self, variants: List[Dict], metric: str) -> List[Dict]:
        """Analiza cada variante del test."""
        if not variants:
            # Datos de ejemplo
            return [
                {
                    "variant": "control",
                    "visitors": 15000,
                    "conversions": 450,
                    "conversion_rate": 0.030,
                    "revenue": 67500,
                    "avg_order_value": 150
                },
                {
                    "variant": "variant_a",
                    "visitors": 15000,
                    "conversions": 525,
                    "conversion_rate": 0.035,
                    "revenue": 81375,
                    "avg_order_value": 155
                },
                {
                    "variant": "variant_b",
                    "visitors": 15000,
                    "conversions": 480,
                    "conversion_rate": 0.032,
                    "revenue": 72000,
                    "avg_order_value": 150
                }
            ]
        
        analysis = []
        for v in variants:
            visitors = v.get("visitors", 0)
            conversions = v.get("conversions", 0)
            revenue = v.get("revenue", 0)
            
            analysis.append({
                "variant": v.get("variant", "unknown"),
                "visitors": visitors,
                "conversions": conversions,
                "conversion_rate": round(conversions / visitors, 4) if visitors > 0 else 0,
                "revenue": revenue,
                "avg_order_value": round(revenue / conversions, 2) if conversions > 0 else 0
            })
        
        return analysis
    
    def _calculate_statistics(self, analysis: List[Dict], confidence: float) -> Dict[str, Any]:
        """Calcula significancia estadística."""
        if len(analysis) < 2:
            return {"is_significant": False, "p_value": 1.0, "sample_adequate": False}
        
        control = next((a for a in analysis if a["variant"] == "control"), analysis[0])
        treatment = next((a for a in analysis if a["variant"] != "control"), analysis[1])
        
        # Z-test simplificado para proporciones
        n1, n2 = control["visitors"], treatment["visitors"]
        p1, p2 = control["conversion_rate"], treatment["conversion_rate"]
        
        if n1 == 0 or n2 == 0:
            return {"is_significant": False, "p_value": 1.0, "sample_adequate": False}
        
        # Pooled proportion
        p_pooled = (control["conversions"] + treatment["conversions"]) / (n1 + n2)
        
        # Standard error
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2)) if p_pooled > 0 else 0.001
        
        # Z-score
        z = abs(p2 - p1) / se if se > 0 else 0
        
        # P-value aproximado (two-tailed)
        p_value = 2 * (1 - min(0.9999, 0.5 + 0.5 * math.erf(z / math.sqrt(2))))
        
        # Determinar significancia
        alpha = 1 - confidence
        is_significant = p_value < alpha
        
        # Sample size adequacy
        min_sample = 1000  # Mínimo recomendado
        sample_adequate = min(n1, n2) >= min_sample
        
        return {
            "is_significant": is_significant,
            "p_value": round(p_value, 4),
            "z_score": round(z, 3),
            "confidence_level": confidence,
            "sample_adequate": sample_adequate,
            "minimum_detectable_effect": round(se * 2, 4),
            "observed_effect": round(abs(p2 - p1), 4)
        }
    
    def _determine_winner(self, analysis: List[Dict], stats: Dict) -> Optional[Dict]:
        """Determina el ganador del test."""
        if not stats.get("is_significant", False):
            return None
        
        control = next((a for a in analysis if a["variant"] == "control"), None)
        best = max(analysis, key=lambda x: x["conversion_rate"])
        
        if control and best["variant"] != "control":
            improvement = (best["conversion_rate"] - control["conversion_rate"]) / control["conversion_rate"]
            return {
                "variant": best["variant"],
                "conversion_rate": best["conversion_rate"],
                "improvement_pct": round(improvement * 100, 2),
                "confidence": stats.get("confidence_level", 0.95)
            }
        
        return None
    
    def _calculate_impact(self, analysis: List[Dict], winner: Optional[Dict]) -> Dict[str, Any]:
        """Calcula impacto proyectado del ganador."""
        if not winner:
            return {"monthly_impact": 0, "annual_impact": 0, "roi": 0}
        
        control = next((a for a in analysis if a["variant"] == "control"), None)
        winning = next((a for a in analysis if a["variant"] == winner["variant"]), None)
        
        if not control or not winning:
            return {"monthly_impact": 0, "annual_impact": 0, "roi": 0}
        
        # Proyectar impacto
        monthly_visitors = control["visitors"] * 2  # Estimado mensual
        incremental_conversions = monthly_visitors * (winning["conversion_rate"] - control["conversion_rate"])
        incremental_revenue = incremental_conversions * winning["avg_order_value"]
        
        return {
            "incremental_conversions_monthly": round(incremental_conversions),
            "incremental_revenue_monthly": round(incremental_revenue, 2),
            "incremental_revenue_annual": round(incremental_revenue * 12, 2),
            "conversion_lift": winner["improvement_pct"],
            "confidence": winner["confidence"]
        }
    
    def _generate_recommendation(self, winner: Optional[Dict], stats: Dict, impact: Dict) -> str:
        """Genera recomendación del test."""
        if not stats.get("is_significant"):
            if not stats.get("sample_adequate"):
                return "CONTINUAR: Muestra insuficiente. Continuar recolectando datos."
            return "CONTINUAR: Sin diferencia significativa. Considerar nuevo test con variantes mas distintas."
        
        if winner:
            annual_impact = impact.get('incremental_revenue_annual', 0)
            return f"IMPLEMENTAR: {winner['variant']} es ganador con +{winner['improvement_pct']:.1f}% mejora. Impacto anual estimado: ${annual_impact:,.0f}"
        
        return "MANTENER: Control sigue siendo la mejor opcion."
    
    def _generate_insights(self, analysis: List[Dict], stats: Dict, winner: Optional[Dict]) -> List[str]:
        """Genera insights del test."""
        insights = []
        
        if not analysis:
            return ["Datos insuficientes para analisis"]
        
        # Resultado principal
        if winner:
            insights.append(f"Test CONCLUSIVO: {winner['variant']} supera al control en {winner['improvement_pct']:.1f}%")
        elif stats.get("is_significant"):
            insights.append("Diferencia significativa pero sin ganador claro")
        else:
            insights.append("Test AUN NO CONCLUSIVO: Diferencias dentro del margen de error")
        
        # Sample size
        if not stats.get("sample_adequate"):
            min_needed = 1000
            current = min(a["visitors"] for a in analysis)
            insights.append(f"Muestra insuficiente: {current:,} vs {min_needed:,} minimo recomendado")
        
        # P-value
        p = stats.get("p_value", 1)
        sig_text = "significativo" if p < 0.05 else "no significativo"
        insights.append(f"P-value: {p:.4f} ({sig_text} al 95%)")
        
        # Mejores performers
        if len(analysis) > 1:
            sorted_variants = sorted(analysis, key=lambda x: x["conversion_rate"], reverse=True)
            ranking_parts = []
            for v in sorted_variants[:3]:
                ranking_parts.append(f"{v['variant']} ({v['conversion_rate']*100:.2f}%)")
            ranking_str = " > ".join(ranking_parts)
            insights.append(f"Ranking: {ranking_str}")
        
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
    return ABTestingImpactIA(tenant_id, config)
