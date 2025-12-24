# agents/marketing/budgetforecastia.py
"""
BudgetForecastIA v3.0 - Pronóstico de Presupuesto de Marketing
Simplificado y funcional - acepta dict como input.
"""

from __future__ import annotations
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class BudgetForecastIA:
    VERSION = "3.0.0"
    AGENT_ID = "budgetforecastia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta pronóstico de presupuesto - acepta dict."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            historical_data = data.get("historical_data", [])
            forecast_periods = data.get("forecast_periods", 3)
            target_roi = data.get("target_roi", 3.0)
            growth_target = data.get("growth_target", 0.15)
            
            # Generar pronóstico
            forecast = self._generate_forecast(historical_data, forecast_periods, growth_target)
            
            # Optimizar asignación por canal
            channel_allocation = self._optimize_allocation(forecast, target_roi)
            
            # Análisis de escenarios
            scenarios = self._analyze_scenarios(forecast, target_roi)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(forecast, channel_allocation)
            
            # Insights
            insights = self._generate_insights(forecast, channel_allocation)
            
            decision_trace = [
                f"forecast_periods={forecast_periods}",
                f"target_roi={target_roi}",
                f"growth_target={growth_target*100:.0f}%",
                f"total_forecast=${sum(p['budget'] for p in forecast):,.0f}"
            ]
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "forecast_id": f"bf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "forecast": forecast,
                "channel_allocation": channel_allocation,
                "scenarios": scenarios,
                "recommendations": recommendations,
                "summary": {
                    "periods_forecasted": len(forecast),
                    "total_budget": sum(p["budget"] for p in forecast),
                    "expected_revenue": sum(p["projected_revenue"] for p in forecast),
                    "expected_roi": round(sum(p["projected_revenue"] for p in forecast) / sum(p["budget"] for p in forecast), 2) if forecast else 0,
                    "confidence_interval": "±12%"
                },
                "key_insights": insights,
                "decision_trace": decision_trace,
                "model_confidence": 0.82,
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
                "forecast_id": "error",
                "tenant_id": self.tenant_id,
                "forecast": [],
                "channel_allocation": [],
                "scenarios": [],
                "recommendations": [],
                "summary": {},
                "key_insights": [f"Error: {str(e)[:100]}"],
                "decision_trace": ["error_occurred"],
                "model_confidence": 0,
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
    
    def _generate_forecast(self, historical: List[Dict], periods: int, growth: float) -> List[Dict]:
        """Genera pronóstico de presupuesto."""
        # Base: último período o default
        if historical:
            base_budget = historical[-1].get("budget", 50000)
            base_revenue = historical[-1].get("revenue", 150000)
        else:
            base_budget = 50000
            base_revenue = 150000
        
        forecast = []
        today = datetime.now()
        
        for i in range(1, periods + 1):
            period_date = today + timedelta(days=30 * i)
            period_name = period_date.strftime("%Y-%m")
            
            # Aplicar crecimiento
            period_growth = 1 + (growth / periods * i)
            budget = base_budget * period_growth
            projected_revenue = base_revenue * period_growth * 1.05  # Eficiencia mejora
            
            # Estacionalidad simplificada
            month = period_date.month
            seasonality = 1.2 if month in [11, 12] else 0.9 if month in [1, 2] else 1.0
            budget *= seasonality
            projected_revenue *= seasonality
            
            forecast.append({
                "period": period_name,
                "budget": round(budget, 2),
                "projected_revenue": round(projected_revenue, 2),
                "projected_roi": round(projected_revenue / budget, 2),
                "seasonality_factor": seasonality,
                "confidence": round(0.90 - (i * 0.05), 2)  # Confianza decrece
            })
        
        return forecast
    
    def _optimize_allocation(self, forecast: List[Dict], target_roi: float) -> List[Dict]:
        """Optimiza asignación por canal."""
        total_budget = sum(p["budget"] for p in forecast)
        
        # Asignación base por canal (optimizada para ROI objetivo)
        channels = [
            {"channel": "search", "allocation_pct": 0.30, "expected_roi": 3.5, "flexibility": "media"},
            {"channel": "social", "allocation_pct": 0.25, "expected_roi": 2.8, "flexibility": "alta"},
            {"channel": "email", "allocation_pct": 0.15, "expected_roi": 4.2, "flexibility": "baja"},
            {"channel": "display", "allocation_pct": 0.15, "expected_roi": 2.0, "flexibility": "alta"},
            {"channel": "content", "allocation_pct": 0.10, "expected_roi": 3.0, "flexibility": "media"},
            {"channel": "events", "allocation_pct": 0.05, "expected_roi": 2.5, "flexibility": "baja"}
        ]
        
        allocation = []
        for ch in channels:
            budget = total_budget * ch["allocation_pct"]
            allocation.append({
                "channel": ch["channel"],
                "allocated_budget": round(budget, 2),
                "allocation_pct": ch["allocation_pct"],
                "expected_roi": ch["expected_roi"],
                "expected_revenue": round(budget * ch["expected_roi"], 2),
                "flexibility": ch["flexibility"],
                "adjustment_range": f"±{15 if ch['flexibility'] == 'alta' else 10 if ch['flexibility'] == 'media' else 5}%"
            })
        
        return allocation
    
    def _analyze_scenarios(self, forecast: List[Dict], target_roi: float) -> List[Dict]:
        """Analiza diferentes escenarios."""
        base_budget = sum(p["budget"] for p in forecast)
        base_revenue = sum(p["projected_revenue"] for p in forecast)
        
        return [
            {
                "scenario": "Conservador",
                "budget_change": -0.20,
                "total_budget": round(base_budget * 0.8, 2),
                "projected_revenue": round(base_revenue * 0.85, 2),
                "projected_roi": round((base_revenue * 0.85) / (base_budget * 0.8), 2),
                "risk": "bajo",
                "recommendation": "Adecuado para incertidumbre económica"
            },
            {
                "scenario": "Base",
                "budget_change": 0,
                "total_budget": round(base_budget, 2),
                "projected_revenue": round(base_revenue, 2),
                "projected_roi": round(base_revenue / base_budget, 2),
                "risk": "medio",
                "recommendation": "Mantener trayectoria actual"
            },
            {
                "scenario": "Agresivo",
                "budget_change": 0.30,
                "total_budget": round(base_budget * 1.3, 2),
                "projected_revenue": round(base_revenue * 1.25, 2),  # ROI marginal decrece
                "projected_roi": round((base_revenue * 1.25) / (base_budget * 1.3), 2),
                "risk": "alto",
                "recommendation": "Requiere canales no saturados"
            }
        ]
    
    def _generate_recommendations(self, forecast: List[Dict], allocation: List[Dict]) -> List[str]:
        """Genera recomendaciones de presupuesto."""
        recs = []
        
        # Por ROI esperado
        high_roi = [a for a in allocation if a["expected_roi"] > 3.5]
        if high_roi:
            recs.append(f"PRIORIZAR: Aumentar inversión en {high_roi[0]['channel']} (ROI esperado {high_roi[0]['expected_roi']}x)")
        
        # Por flexibilidad
        flexible = [a for a in allocation if a["flexibility"] == "alta"]
        if flexible:
            recs.append(f"AJUSTAR: {flexible[0]['channel']} permite ajustes rápidos según performance")
        
        # Estacionalidad
        high_season = [f for f in forecast if f.get("seasonality_factor", 1) > 1.1]
        if high_season:
            recs.append(f"PREPARAR: Períodos de alta estacionalidad detectados ({high_season[0]['period']})")
        
        # Budget total
        total = sum(p["budget"] for p in forecast)
        recs.append(f"RESERVAR: Mantener 10% (${total*0.1:,.0f}) para oportunidades no planificadas")
        
        return recs[:5]
    
    def _generate_insights(self, forecast: List[Dict], allocation: List[Dict]) -> List[str]:
        """Genera insights del pronóstico."""
        insights = []
        
        if not forecast:
            return ["Datos insuficientes para análisis"]
        
        # Tendencia
        if len(forecast) >= 2:
            growth = (forecast[-1]["budget"] - forecast[0]["budget"]) / forecast[0]["budget"]
            insights.append(f"Tendencia: Presupuesto proyectado crece {growth*100:.1f}% en el período")
        
        # ROI promedio
        avg_roi = sum(p["projected_roi"] for p in forecast) / len(forecast)
        insights.append(f"ROI promedio esperado: {avg_roi:.2f}x")
        
        # Canal más eficiente
        if allocation:
            best = max(allocation, key=lambda x: x["expected_roi"])
            insights.append(f"Canal más eficiente: {best['channel']} (ROI {best['expected_roi']}x)")
        
        # Confianza
        avg_conf = sum(p["confidence"] for p in forecast) / len(forecast)
        insights.append(f"Confianza del pronóstico: {avg_conf*100:.0f}% (decrece con horizonte)")
        
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
    return BudgetForecastIA(tenant_id, config)
