# agents/conversion_cohort.py - ConversionCohortIA Agent
import time
from typing import Dict, List
from datetime import datetime
import sys
sys.path.append('..')
from schemas.canonical import ConversionCohortInput, ConversionCohortOutput, Cohort

class ConversionCohortIA:
    def __init__(self, tenant_id: str, config: Dict = None):
        self.tenant_id = tenant_id
        self.agent_id = 'conversion_cohort_ia'
        self.config = config or {}
    
    def _calculate_cohort_metrics(self, campaign) -> Cohort:
        """Calcula métricas de cohort para una campaña"""
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
        """Genera insights basados en cohorts"""
        insights = []
        
        if not cohorts:
            return ["No cohort data available"]
        
        # Mejor ROAS
        best_roas = max(cohorts, key=lambda c: c.roas)
        if best_roas.roas > 3.0:
            insights.append(f"Cohort {best_roas.key} exceeds target ROAS with {best_roas.roas}x")
        
        # Peor CAC
        worst_cac = max(cohorts, key=lambda c: c.cac)
        if worst_cac.cac > 50:
            insights.append(f"Cohort {worst_cac.key} has high CAC: ${worst_cac.cac}")
        
        # Mejor conversion rate
        best_conv = max(cohorts, key=lambda c: c.conv_rate or 0)
        if best_conv.conv_rate and best_conv.conv_rate > 0.05:
            insights.append(f"Cohort {best_conv.key} has strong conversion rate: {best_conv.conv_rate*100:.1f}%")
        
        return insights or ["All cohorts within normal parameters"]
    
    def _generate_recommendations(self, cohorts: List[Cohort]) -> List[str]:
        """Genera recomendaciones de optimización"""
        recommendations = []
        
        if not cohorts:
            return ["Insufficient data for recommendations"]
        
        # Recomendar aumentar budget en cohorts con mejor ROAS
        high_roas = [c for c in cohorts if c.roas > 3.0]
        for cohort in high_roas[:2]:
            recommendations.append(f"increase_budget:{cohort.key}:20%")
        
        # Recomendar reducir en cohorts con mal ROAS
        low_roas = [c for c in cohorts if c.roas < 1.5]
        for cohort in low_roas[:2]:
            recommendations.append(f"reduce_budget:{cohort.key}:30%")
        
        # Recomendar optimizar conversion en cohorts con bajo CR
        low_conv = [c for c in cohorts if c.conv_rate and c.conv_rate < 0.02]
        for cohort in low_conv[:1]:
            recommendations.append(f"optimize_landing_page:{cohort.key}")
        
        return recommendations or ["Maintain current allocation"]
    
    async def execute(self, input_data: ConversionCohortInput) -> ConversionCohortOutput:
        start = time.perf_counter()
        
        if input_data.tenant_id != self.tenant_id:
            raise ValueError(f"Tenant mismatch: {input_data.tenant_id} != {self.tenant_id}")
        
        # Calcular cohorts
        cohorts = [self._calculate_cohort_metrics(c) for c in input_data.campaigns]
        
        # Generar insights
        insights = self._generate_insights(cohorts)
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(cohorts)
        
        latency_ms = max(1, int((time.perf_counter() - start) * 1000))
        
        return ConversionCohortOutput(
            tenant_id=self.tenant_id,
            cohorts=cohorts,
            insights=insights,
            recommendations=recommendations,
            latency_ms=latency_ms
        )

def create_agent_instance(tenant_id: str, config: Dict = None):
    return ConversionCohortIA(tenant_id, config)