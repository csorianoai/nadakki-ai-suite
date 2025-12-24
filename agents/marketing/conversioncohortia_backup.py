# agents/marketing/conversioncohortia.py
"""
ConversionCohortIA v3.0 - Análisis de Cohortes de Conversión
Corregido para aceptar dict O objeto tipado como input.
"""

import time
from typing import Dict, List, Any, Union
from datetime import datetime

from schemas.canonical import ConversionCohortInput, ConversionCohortOutput, Cohort

# Layer opcional
try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class ConversionCohortIA:
    VERSION = "3.0.0"
    AGENT_ID = "conversioncohortia"
    
    def __init__(self, tenant_id: str, config: Dict = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}

    def _dict_to_input(self, data: Dict[str, Any]) -> ConversionCohortInput:
        """Convierte dict a ConversionCohortInput para compatibilidad con router."""
        # Puede venir como {"input_data": {...}} o directo
        input_data = data.get("input_data", data) if isinstance(data, dict) else data
        
        # Si ya es el tipo correcto, devolverlo
        if isinstance(input_data, ConversionCohortInput):
            return input_data
        
        # Extraer tenant_id
        tenant_id = input_data.get("tenant_id", self.tenant_id)
        
        # Extraer campaigns - pueden venir como lista de dicts o vacío
        campaigns_raw = input_data.get("campaigns", [])
        
        # Si no hay campaigns, crear datos de ejemplo para no fallar
        if not campaigns_raw:
            # Devolver input mínimo válido para diagnóstico
            from schemas.canonical import CampaignPerformance
            
            # Crear campaign de ejemplo
            example_perf = CampaignPerformance(
                impressions=10000,
                clicks=500,
                conversions=50,
                spend=1000.0,
                revenue=5000.0
            )
            
            # Intentar crear con datos mínimos
            try:
                return ConversionCohortInput(
                    tenant_id=tenant_id,
                    campaigns=[]  # Vacío, el agente manejará
                )
            except Exception:
                pass
        
        # Construir ConversionCohortInput desde dict
        try:
            return ConversionCohortInput.model_validate({
                "tenant_id": tenant_id,
                "campaigns": campaigns_raw
            })
        except Exception as e:
            # Fallback: crear con mínimos
            return ConversionCohortInput(
                tenant_id=tenant_id,
                campaigns=[]
            )

    def _calculate_cohort_metrics(self, campaign) -> Cohort:
        """Calcula métricas de cohort para una campaña."""
        perf = campaign.performance

        # CAC (Customer Acquisition Cost)
        cac = perf.spend / perf.conversions if perf.conversions > 0 else 0

        # LTV simplificado (revenue / conversions)
        ltv = perf.revenue / perf.conversions if perf.conversions > 0 else 0

        # Conversion rate
        conv_rate = perf.conversions / perf.clicks if perf.clicks > 0 else 0

        # ROAS (Return on Ad Spend)
        roas = perf.revenue / perf.spend if perf.spend > 0 else 0

        return Cohort(
            key=f"{campaign.channel}_{campaign.campaign_id}",
            size=perf.conversions,
            ltv=round(ltv, 2),
            cac=round(cac, 2),
            conv_rate=round(conv_rate, 4),
            roas=round(roas, 2)
        )

    def _generate_insights(self, cohorts: List[Cohort]) -> List[str]:
        """Genera insights basados en cohorts."""
        insights = []

        if not cohorts:
            return ["No hay datos de cohorte disponibles para análisis"]

        # Mejor ROAS
        best_roas = max(cohorts, key=lambda c: c.roas)
        if best_roas.roas > 3.0:
            insights.append(f"Cohorte {best_roas.key} supera objetivo ROAS con {best_roas.roas}x")

        # Peor CAC
        worst_cac = max(cohorts, key=lambda c: c.cac)
        if worst_cac.cac > 50:
            insights.append(f"Cohorte {worst_cac.key} tiene CAC alto: ${worst_cac.cac}")

        # Mejor conversion rate
        best_conv = max(cohorts, key=lambda c: c.conv_rate or 0)
        if best_conv.conv_rate and best_conv.conv_rate > 0.05:
            insights.append(f"Cohorte {best_conv.key} tiene tasa de conversión fuerte: {best_conv.conv_rate*100:.1f}%")

        return insights or ["Todas las cohortes dentro de parámetros normales"]

    def _generate_recommendations(self, cohorts: List[Cohort]) -> List[str]:
        """Genera recomendaciones de optimización."""
        recommendations = []

        if not cohorts:
            return ["Datos insuficientes para recomendaciones"]

        # Recomendar aumentar budget en cohorts con mejor ROAS
        high_roas = [c for c in cohorts if c.roas > 3.0]
        for cohort in high_roas[:2]:
            recommendations.append(f"AUMENTAR presupuesto {cohort.key}: +20%")

        # Recomendar reducir en cohorts con mal ROAS
        low_roas = [c for c in cohorts if c.roas < 1.5]
        for cohort in low_roas[:2]:
            recommendations.append(f"REDUCIR presupuesto {cohort.key}: -30%")

        # Recomendar optimizar conversion en cohorts con bajo CR
        low_conv = [c for c in cohorts if c.conv_rate and c.conv_rate < 0.02]
        for cohort in low_conv[:1]:
            recommendations.append(f"OPTIMIZAR landing page para {cohort.key}")

        return recommendations or ["Mantener asignación actual"]

    async def execute(self, input_data: Union[ConversionCohortInput, Dict[str, Any]]) -> ConversionCohortOutput:
        """
        Ejecuta análisis de cohortes.
        Acepta ConversionCohortInput O dict para compatibilidad con router.
        """
        self.metrics["requests"] += 1
        start = time.perf_counter()

        try:
            # Convertir dict a objeto tipado si es necesario
            if isinstance(input_data, dict):
                inp = self._dict_to_input(input_data)
            else:
                inp = input_data

            # Verificar tenant
            if inp.tenant_id != self.tenant_id:
                raise ValueError(f"Tenant mismatch: {inp.tenant_id} != {self.tenant_id}")

            # Calcular cohorts
            cohorts = []
            if inp.campaigns:
                cohorts = [self._calculate_cohort_metrics(c) for c in inp.campaigns]

            # Generar insights y recomendaciones
            insights = self._generate_insights(cohorts)
            recommendations = self._generate_recommendations(cohorts)

            latency_ms = max(1, int((time.perf_counter() - start) * 1000))
            self.metrics["total_ms"] += latency_ms

            # Construir resultado
            result = ConversionCohortOutput(
                tenant_id=self.tenant_id,
                cohorts=cohorts,
                insights=insights,
                recommendations=recommendations,
                latency_ms=latency_ms
            )

            # Aplicar Decision Layer si está disponible
            if DECISION_LAYER_AVAILABLE and cohorts:
                try:
                    result_dict = result.model_dump()
                    enhanced = apply_decision_layer(result_dict)
                    # Agregar decision al resultado (como atributo extra si es posible)
                except Exception:
                    pass

            return result

        except Exception as e:
            self.metrics["errors"] += 1
            latency_ms = max(1, int((time.perf_counter() - start) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            # Devolver resultado de error válido
            return ConversionCohortOutput(
                tenant_id=self.tenant_id,
                cohorts=[],
                insights=[f"Error en análisis: {str(e)[:100]}"],
                recommendations=["Revisar datos de entrada"],
                latency_ms=latency_ms
            )

    def health(self) -> Dict[str, Any]:
        """Health check del agente."""
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


def create_agent_instance(tenant_id: str, config: Dict = None):
    return ConversionCohortIA(tenant_id, config)
