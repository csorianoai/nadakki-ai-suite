# src/Core/agent_factory.py
import json
import importlib
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory avanzado para cargar y gestionar agentes de Nadakki AI Suite"""
    
    def __init__(self):
        self.agents = {}
        self.registry_file = "agent_registry.json"
        self.loaded_modules = {}
    
    def safe_import(self, module_path: str) -> Any:
        """Importación segura que evita circular imports"""
        if module_path in self.loaded_modules:
            return self.loaded_modules[module_path]
        
        try:
            module = importlib.import_module(module_path)
            self.loaded_modules[module_path] = module
            return module
        except ImportError as e:
            logger.warning(f"No se pudo importar {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado importando {module_path}: {e}")
            return None
    
    def find_agent_class(self, module, agent_name: str) -> Any:
        """Busca clases de agente con múltiples patrones"""
        class_patterns = [
            'Agent', 'IA', 'Model', 'Engine', 'Optimizer', 
            'Predictor', 'Analyzer', 'Generator', 'Coordinator'
        ]
        
        for attr_name in dir(module):
            if attr_name.startswith('_'):  # Ignorar atributos privados
                continue
                
            attr = getattr(module, attr_name)
            if isinstance(attr, type):  # Es una clase
                # Verificar si coincide con algún patrón
                if any(pattern in attr.__name__ for pattern in class_patterns):
                    return attr
                
                # Verificar si el nombre coincide con el archivo
                if attr_name.lower().replace('_', '') == agent_name.lower().replace('_', ''):
                    return attr
        
        return None
    
    def load_registry(self) -> Dict[str, Any]:
        """Carga y valida el registry de agentes"""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Validar estructura básica
            valid_registry = {}
            for agent_name, agent_data in registry.items():
                if (isinstance(agent_data, dict) and 
                    'file_path' in agent_data and 
                    'ecosystem' in agent_data):
                    valid_registry[agent_name] = agent_data
            
            logger.info(f"Registry cargado: {len(valid_registry)} agentes válidos")
            return valid_registry
            
        except FileNotFoundError:
            logger.error("Registry no encontrado")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando registry: {e}")
            return {}
    
    def discover_agents(self) -> Dict[str, Any]:
        """Descubre y carga agentes con manejo robusto de errores"""
        registry = self.load_registry()
        loaded_agents = {}
        
        # Ordenar por ecosistema para mejor agrupación
        ecosystems = {}
        for agent_name, agent_data in registry.items():
            ecosystem = agent_data.get('ecosystem', 'unknown')
            if ecosystem not in ecosystems:
                ecosystems[ecosystem] = []
            ecosystems[ecosystem].append((agent_name, agent_data))
        
        # Procesar por ecosistemas
        for ecosystem, agents_list in ecosystems.items():
            logger.info(f"Procesando ecosistema: {ecosystem} ({len(agents_list)} agentes)")
            
            for agent_name, agent_data in agents_list:
                if agent_data.get('status') != 'active':
                    continue
                    
                try:
                    file_path = agent_data['file_path']
                    
                    # Convertir ruta a módulo Python
                    if file_path.startswith('agents/'):
                        module_path = file_path.replace('/', '.').replace('.py', '')
                    else:
                        # Asumir estructura agents\ecosistema\agente.py
                        parts = Path(file_path).parts
                        if len(parts) >= 3 and parts[0] == 'agents':
                            module_path = '.'.join(parts).replace('.py', '')
                        else:
                            module_path = file_path.replace('\\', '.').replace('.py', '')
                    
                    # Importación segura
                    module = self.safe_import(module_path)
                    if not module:
                        continue
                    
                    # Buscar clase de agente
                    agent_class = self.find_agent_class(module, agent_name)
                    
                    if agent_class:
                        loaded_agents[agent_name] = {
                            'class': agent_class,
                            'instance': agent_class(),  # Crear instancia
                            'ecosystem': ecosystem,
                            'module': module_path,
                            'file_path': file_path,
                            'metadata': agent_data
                        }
                        logger.info(f"✅ {agent_name} cargado desde {module_path}")
                    else:
                        logger.warning(f"⚠️  No se encontró clase adecuada en: {agent_name}")
                        
                except Exception as e:
                    logger.error(f"❌ Error cargando {agent_name}: {str(e)}")
        
        self.agents = loaded_agents
        return loaded_agents
    
    def get_agent(self, agent_name: str) -> Any:
        """Obtiene una instancia de agente por nombre"""
        agent_info = self.agents.get(agent_name)
        return agent_info.get('instance') if agent_info else None
    
    def get_ecosystem_agents(self, ecosystem: str) -> Dict[str, Any]:
        """Obtiene todos los agentes de un ecosistema"""
        return {name: data for name, data in self.agents.items() 
                if data.get('ecosystem') == ecosystem}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Obtiene el estado de todos los agentes"""
        status = {
            'total_registry': len(self.load_registry()),
            'loaded_agents': len(self.agents),
            'success_rate': f"{(len(self.agents) / len(self.load_registry()) * 100):.1f}%" if self.load_registry() else '0%',
            'by_ecosystem': {}
        }
        
        for agent_name, agent_data in self.agents.items():
            ecosystem = agent_data['ecosystem']
            if ecosystem not in status['by_ecosystem']:
                status['by_ecosystem'][ecosystem] = 0
            status['by_ecosystem'][ecosystem] += 1
        
        return status

# Singleton global
_factory_instance = None

def get_agent_factory() -> AgentFactory:
    """Obtiene la instancia singleton del AgentFactory"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AgentFactory()
        _factory_instance.discover_agents()
    return _factory_instance

if __name__ == "__main__":
    # Prueba de funcionamiento
    print("🎯 INICIALIZANDO AGENT FACTORY AVANZADO...")
    factory = get_agent_factory()
    status = factory.get_agent_status()
    
    print(f"\n📊 ESTADO DEL SISTEMA:")
    print(f"   • Agentes en registry: {status['total_registry']}")
    print(f"   • Agentes cargados: {status['loaded_agents']}")
    print(f"   • Tasa de éxito: {status['success_rate']}")
    
    print(f"\n🏭 DISTRIBUCIÓN POR ECOSISTEMA:")
    for eco, count in sorted(status['by_ecosystem'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {eco}: {count} agentes")
    
    # Probar agentes de marketing
    marketing_agents = factory.get_ecosystem_agents('marketing')
    print(f"\n🎪 AGENTES DE MARKETING CARGADOS: {len(marketing_agents)}")
    for agent_name in marketing_agents.keys():
        print(f"   ✅ {agent_name}")
