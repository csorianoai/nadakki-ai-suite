"""
Registry Central de Agentes - Nadakki AI Suite
Auto-generado
"""

from typing import Dict, Any
from . import *

class AgentRegistry:
    def __init__(self):
        self.ecosystems = {
            'originacion': originacion,
            'decision': decision,
            'vigilancia': vigilancia,
            'recuperacion': recuperacion,
            'compliance': compliance,
            'operacional': operacional,
            'experiencia': experiencia,
            'inteligencia': inteligencia,
            'fortaleza': fortaleza,
            'orchestration': orchestration,
            'legal': legal,
            'marketing': marketing,
            'contabilidad': contabilidad,
            'presupuesto': presupuesto,
            'rrhh': rrhh,
            'ventascrm': ventascrm,
            'logistica': logistica,
            'investigacion': investigacion,
            'educacion': educacion,
            'regtech': regtech,
        }

    def get_agent(self, ecosystem: str, agent_name: str, tenant_id: str):
        eco = self.ecosystems.get(ecosystem)
        if eco and hasattr(eco, "AGENTS_REGISTRY") and agent_name in eco.AGENTS_REGISTRY:
            return eco.AGENTS_REGISTRY[agent_name](tenant_id)
        return None

    def list_agents(self) -> Dict[str, Any]:
        return {eco: list(mod.AGENTS_REGISTRY.keys()) for eco, mod in self.ecosystems.items()}

registry = AgentRegistry()

__all__ = ["registry", "AgentRegistry"]