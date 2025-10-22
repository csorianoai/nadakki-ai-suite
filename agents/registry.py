# agents/registry.py - VERSIÓN CORREGIDA v4.3
"""
Registry de agentes multi-tenant para Nadakki AI Suite
Carga automática de todos los agentes sin errores de importación
"""

import os
import importlib
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AgentRegistry:
    def __init__(self):
        self.agents = {}
        self.ecosystems = [
            'originacion', 'decision', 'vigilancia', 'recuperacion', 
            'compliance', 'operacional', 'experiencia', 'inteligencia',
            'fortaleza', 'orchestration', 'legal', 'marketing',
            'contabilidad', 'presupuesto', 'rrhh', 'ventascrm',
            'logistica', 'investigacion', 'educacion', 'regtech'
        ]
        self._load_all_agents()
    
    def _load_all_agents(self):
        """Carga automática de todos los agentes por ecosistema"""
        base_path = Path(__file__).parent
        
        for ecosystem in self.ecosystems:
            self.agents[ecosystem] = []
            ecosystem_path = base_path / ecosystem
            
            if not ecosystem_path.exists():
                logger.warning(f"Ecosistema {ecosystem} no encontrado en {ecosystem_path}")
                continue
                
            # Buscar todos los archivos .py excepto __init__ y coordinators
            for py_file in ecosystem_path.glob("*.py"):
                if py_file.name.startswith(('__init__', 'coordinator')):
                    continue
                    
                agent_name = py_file.stem
                try:
                    # Importación dinámica
                    module_path = f"agents.{ecosystem}.{agent_name}"
                    module = importlib.import_module(module_path)
                    
                    # Buscar la clase del agente
                    agent_class = self._find_agent_class(module, agent_name)
                    
                    if agent_class:
                        agent_info = {
                            'name': agent_name,
                            'class': agent_class,
                            'module': module_path,
                            'ecosystem': ecosystem,
                            'description': getattr(agent_class, '__doc__', f'Agente {agent_name}'),
                            'status': 'active'
                        }
                        self.agents[ecosystem].append(agent_info)
                        logger.debug(f"✅ Cargado: {ecosystem}.{agent_name}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error cargando {ecosystem}.{agent_name}: {e}")
                    continue
    
    def _find_agent_class(self, module, agent_name: str):
        """Encuentra la clase principal del agente en el módulo"""
        # Buscar clase con nombre similar al archivo
        possible_names = [
            agent_name.title().replace('_', ''),  # sentinelbot -> Sentinelbot
            ''.join(word.capitalize() for word in agent_name.split('_')),  # sentinel_bot -> SentinelBot
            agent_name.upper(),  # sentinelbot -> SENTINELBOT
            agent_name.capitalize()  # sentinelbot -> Sentinelbot
        ]
        
        for class_name in possible_names:
            if hasattr(module, class_name):
                return getattr(module, class_name)
        
        # Backup: buscar cualquier clase que no sea built-in
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr.__module__ == module.__name__):
                return attr
        
        return None
    
    def list_agents(self, ecosystem: str = None) -> Dict[str, List]:
        """Lista agentes por ecosistema o todos"""
        if ecosystem:
            return {ecosystem: self.agents.get(ecosystem, [])}
        return self.agents
    
    def get_agent(self, ecosystem: str, agent_name: str) -> Optional[Dict]:
        """Obtiene información específica de un agente"""
        for agent in self.agents.get(ecosystem, []):
            if agent['name'] == agent_name:
                return agent
        return None
    
    def create_agent_instance(self, ecosystem: str, agent_name: str, **kwargs):
        """Crea instancia de agente"""
        agent_info = self.get_agent(ecosystem, agent_name)
        if not agent_info:
            raise ValueError(f"Agente {ecosystem}.{agent_name} no encontrado")
        
        agent_class = agent_info['class']
        return agent_class(**kwargs)
    
    def get_ecosystem_stats(self) -> Dict[str, int]:
        """Estadísticas de agentes por ecosistema"""
        stats = {}
        total_agents = 0
        
        for ecosystem, agents in self.agents.items():
            stats[ecosystem] = len(agents)
            total_agents += len(agents)
        
        stats['total'] = total_agents
        return stats
    
    def validate_registry(self) -> Dict[str, Any]:
        """Valida el estado del registry"""
        healthy_ecosystems = []
        unhealthy_ecosystems = []
        
        for ecosystem in self.ecosystems:
            agent_count = len(self.agents.get(ecosystem, []))
            
            if agent_count > 0:
                healthy_ecosystems.append({
                    'name': ecosystem,
                    'agents': agent_count
                })
            else:
                unhealthy_ecosystems.append({
                    'name': ecosystem,
                    'agents': 0,
                    'issue': 'No agents loaded'
                })
        
        total_agents = sum(len(agents) for agents in self.agents.values())
        
        return {
            'status': 'healthy' if not unhealthy_ecosystems else 'partial',
            'total_agents': total_agents,
            'healthy_ecosystems': healthy_ecosystems,
            'unhealthy_ecosystems': unhealthy_ecosystems
        }

# Instancia global del registry
registry = AgentRegistry()

# Funciones helper
def list_all_agents():
    """Lista todos los agentes disponibles"""
    return registry.list_agents()

def get_agent_instance(ecosystem: str, agent_name: str, **kwargs):
    """Crea instancia de agente específico"""
    return registry.create_agent_instance(ecosystem, agent_name, **kwargs)

def validate_registry():
    """Valida el estado del registry"""
    return registry.validate_registry()

if __name__ == "__main__":
    print("🔍 Testing Nadakki AI Suite Registry...")
    health = validate_registry()
    print(f"✅ Status: {health['status']}")
    print(f"📊 Total agentes: {health['total_agents']}")
    
    stats = registry.get_ecosystem_stats()
    for eco, count in stats.items():
        if eco != 'total' and count > 0:
            print(f"   - {eco}: {count} agentes")