# ================================================================
# AGENT_REGISTRY.PY
# Registro centralizado de agentes consolidados
# ================================================================
# Generado automÃ¡ticamente: 09/04/2025 21:44:03
# ================================================================

from typing import Dict, List, Any
import importlib
import os

class AgentRegistry:
    def __init__(self):
        self.agents = {}
        self.load_agents()
    
    def load_agents(self):
        """Carga automÃ¡tica de todos los agentes consolidados"""
        
        # Ecosystem: recuperacion
        self.register_agent('collection_master.py', 'recuperacion.collection_master.py')
        self.register_agent('recovery_optimizer.py', 'recuperacion.recovery_optimizer.py')
        self.register_agent('negotiation_bot.py', 'recuperacion.negotiation_bot.py')
        self.register_agent('legal_pathway.py', 'recuperacion.legal_pathway.py')

        # Ecosystem: compliance
        self.register_agent('compliance_watchdog.py', 'compliance.compliance_watchdog.py')
        self.register_agent('audit_master.py', 'compliance.audit_master.py')
        self.register_agent('doc_guardian.py', 'compliance.doc_guardian.py')
        self.register_agent('regulatory_radar.py', 'compliance.regulatory_radar.py')

        # Ecosystem: decision
        self.register_agent('quantum_decision.py', 'decision.quantum_decision.py')
        self.register_agent('risk_oracle.py', 'decision.risk_oracle.py')
        self.register_agent('policy_guardian.py', 'decision.policy_guardian.py')
        self.register_agent('turbo_approver.py', 'decision.turbo_approver.py')

        # Ecosystem: originacion
        self.register_agent('sentinel_bot.py', 'originacion.sentinel_bot.py')
        self.register_agent('dna_profiler.py', 'originacion.dna_profiler.py')
        self.register_agent('income_oracle.py', 'originacion.income_oracle.py')
        self.register_agent('behavior_miner.py', 'originacion.behavior_miner.py')

        # Ecosystem: vigilancia
        self.register_agent('early_warning.py', 'vigilancia.early_warning.py')
        self.register_agent('portfolio_sentinel.py', 'vigilancia.portfolio_sentinel.py')
        self.register_agent('market_radar.py', 'vigilancia.market_radar.py')
        self.register_agent('stress_tester.py', 'vigilancia.stress_tester.py')

        # Ecosystem: operacional
        self.register_agent('process_genius.py', 'operacional.process_genius.py')
        self.register_agent('cost_optimizer.py', 'operacional.cost_optimizer.py')
        self.register_agent('quality_controller.py', 'operacional.quality_controller.py')
        self.register_agent('workflow_master.py', 'operacional.workflow_master.py')

    def register_agent(self, name: str, module_path: str):
        """Registra un agente en el registry"""
        try:
            module = importlib.import_module(f'agents.{module_path}')
            self.agents[name] = {
                'module': module,
                'path': module_path,
                'status': 'loaded'
            }
        except Exception as e:
            self.agents[name] = {
                'module': None,
                'path': module_path,
                'status': f'error: {str(e)}'
            }
    
    def get_agent(self, name: str):
        """Obtiene un agente por nombre"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """Lista todos los agentes registrados"""
        return list(self.agents.keys())
    
    def get_agent_status(self, name: str) -> str:
        """Obtiene el status de un agente"""
        agent = self.agents.get(name)
        return agent['status'] if agent else 'not_found'
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica la salud de todos los agentes"""
        healthy = []
        errors = []
        
        for name, agent in self.agents.items():
            if agent['status'] == 'loaded':
                healthy.append(name)
            else:
                errors.append({'name': name, 'error': agent['status']})
        
        return {
            'total_agents': len(self.agents),
            'healthy_agents': len(healthy),
            'error_agents': len(errors),
            'healthy_list': healthy,
            'error_list': errors
        }

# Instancia global del registry
registry = AgentRegistry()

# Funciones de conveniencia
def get_agent(name: str):
    return registry.get_agent(name)

def list_agents():
    return registry.list_agents()

def health_check():
    return registry.health_check()
