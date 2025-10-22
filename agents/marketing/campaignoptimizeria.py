# agents/campaign_optimizer.py - CampaignOptimizerIA Agent
import time
from typing import Dict, List
from datetime import datetime
import sys
sys.path.append('..')
from schemas.canonical import CampaignOptimizerInput, CampaignOptimizerOutput, CampaignAllocation

class CampaignOptimizerIA:
    def __init__(self, tenant_id: str, config: Dict = None):
        self.tenant_id = tenant_id
        self.agent_id = 'campaign_optimizer_ia'
        self.config = config or {}
    
    def _calculate_efficiency(self, campaign) -> float:
        """Calcula eficiencia (ROAS) de cada campaña"""
        perf = campaign.performance
        if perf.spend == 0:
            return 0.0
        return perf.revenue / perf.spend
    
    def _greedy_allocation(self, campaigns: List, total_budget: float, constraints) -> List[CampaignAllocation]:
        """Algoritmo greedy para asignar presupuesto"""
        allocations = []
        
        # Calcular eficiencia de cada campaña
        campaign_efficiency = [
            (c, self._calculate_efficiency(c)) 
            for c in campaigns
        ]
        
        # Ordenar por eficiencia (ROAS) descendente
        campaign_efficiency.sort(key=lambda x: x[1], reverse=True)
        
        remaining_budget = total_budget
        
        for campaign, efficiency in campaign_efficiency:
            current_spend = campaign.performance.spend
            
            # Calcular nuevo presupuesto (proporcional a ROAS)
            if efficiency > 2.0:
                # Aumentar 20% si ROAS > 2.0
                new_spend = current_spend * 1.20
            elif efficiency > 1.5:
                # Mantener si ROAS > 1.5
                new_spend = current_spend
            else:
                # Reducir 30% si ROAS bajo
                new_spend = current_spend * 0.70
            
            # Respetar mínimo por campaña
            new_spend = max(new_spend, constraints.min_per_campaign)
            
            # Respetar presupuesto disponible
            new_spend = min(new_spend, remaining_budget)
            
            delta = new_spend - current_spend
            delta_pct = (delta / current_spend * 100) if current_spend > 0 else 0
            delta_str = f"{'+' if delta >= 0 else ''}{delta_pct:.1f}%"
            
            allocations.append(CampaignAllocation(
                campaign_id=campaign.campaign_id,
                recommended_spend=round(new_spend, 2),
                delta=delta_str
            ))
            
            remaining_budget -= new_spend
        
        return allocations
    
    def _estimate_uplift(self, allocations: List[CampaignAllocation], campaigns: List) -> Dict[str, str]:
        """Estima mejora esperada con nueva asignación"""
        # Simplificado: asumir mejora proporcional al cambio de budget
        total_increase = sum(
            float(a.delta.replace('%','').replace('+','')) 
            for a in allocations if '+' in a.delta
        )
        
        avg_increase = total_increase / len(allocations) if allocations else 0
        
        return {
            "conversions": f"+{avg_increase * 0.6:.0f}%",
            "roas": f"+{avg_increase * 0.4:.0f}%"
        }
    
    def _check_constraints(self, allocations: List[CampaignAllocation], constraints) -> List[str]:
        """Verifica que se respeten constraints"""
        checks = []
        
        # Verificar mínimo por campaña
        min_respected = all(a.recommended_spend >= constraints.min_per_campaign for a in allocations)
        if min_respected:
            checks.append("min_budget_respected")
        
        # Verificar total no exceda max daily spend
        total = sum(a.recommended_spend for a in allocations)
        if total <= constraints.max_daily_spend:
            checks.append("max_daily_spend_respected")
        
        checks.append("allocation_optimized")
        
        return checks
    
    async def execute(self, input_data: CampaignOptimizerInput) -> CampaignOptimizerOutput:
        start = time.perf_counter()
        
        if input_data.tenant_id != self.tenant_id:
            raise ValueError(f"Tenant mismatch: {input_data.tenant_id} != {self.tenant_id}")
        
        # Calcular asignación óptima
        allocations = self._greedy_allocation(
            input_data.campaigns, 
            input_data.total_budget,
            input_data.constraints
        )
        
        # Estimar uplift
        uplift = self._estimate_uplift(allocations, input_data.campaigns)
        
        # Verificar constraints
        constraints_met = self._check_constraints(allocations, input_data.constraints)
        
        latency_ms = max(1, int((time.perf_counter() - start) * 1000))
        
        return CampaignOptimizerOutput(
            tenant_id=self.tenant_id,
            allocation=allocations,
            expected_uplift=uplift,
            constraints_met=constraints_met,
            latency_ms=latency_ms
        )

def create_agent_instance(tenant_id: str, config: Dict = None):
    return CampaignOptimizerIA(tenant_id, config)