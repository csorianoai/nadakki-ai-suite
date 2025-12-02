# src/Core/agent_factory_fixed.py
import sys
import os
import importlib
import json
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AgentFactoryFixed:
    """AgentFactory corregido que maneja imports correctamente"""
    
    def __init__(self):
        self.agents = {}
        # Agregar directorio raíz al PYTHONPATH para imports absolutos
        sys.path.insert(0, os.path.abspath('.'))
        logger.info("✅ AgentFactoryFixed inicializado")
    
    def discover_agents(self):
        """Descubre y carga agentes usando imports absolutos"""
        try:
            with open('agent_registry.json', 'r', encoding='utf-8') as f:
                registry = json.load(f)
            logger.info(f"📊 Registry cargado: {len(registry)} agentes")
        except FileNotFoundError:
            logger.error("❌ Registry no encontrado")
            return {}
        
        loaded_agents = {}
        success_count = 0
        
        for agent_name, agent_data in registry.items():
            if agent_data.get('status') != 'active':
                continue
                
            file_path = agent_data['file_path']
            
            try:
                # Convertir ruta de archivo a módulo Python
                # Ej: 'agents/marketing/abtestingia.py' -> 'agents.marketing.abtestingia'
                module_path = file_path.replace('/', '.').replace('.py', '')
                
                # Importar módulo
                module = importlib.import_module(module_path)
                
                # Buscar cualquier clase en el módulo (no solo las que contienen 'Agent')
                agent_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        not attr_name.startswith('_') and 
                        attr.__module__ == module_path):
                        agent_class = attr
                        break
                
                if agent_class:
                    # Intentar crear instancia
                    try:
                        instance = agent_class()
                    except TypeError as e:
                        # Si requiere argumentos, intentar con config vacío
                        if 'missing' in str(e) and 'required' in str(e):
                            instance = agent_class(config={})
                        else:
                            raise e
                    
                    loaded_agents[agent_name] = {
                        'instance': instance,
                        'class': agent_class,
                        'ecosystem': agent_data.get('ecosystem', 'unknown'),
                        'module': module_path,
                        'file_path': file_path
                    }
                    success_count += 1
                    logger.info(f"✅ {agent_name} cargado desde {module_path}")
                else:
                    logger.warning(f"⚠️  No se encontró clase en: {agent_name}")
                    
            except Exception as e:
                logger.error(f"❌ Error cargando {agent_name}: {str(e)}")
        
        self.agents = loaded_agents
        logger.info(f"🎯 Carga completada: {success_count}/{len(registry)} agentes cargados")
        return loaded_agents
    
    def get_agent(self, agent_name: str):
        """Obtiene instancia de agente por nombre"""
        agent_info = self.agents.get(agent_name)
        return agent_info.get('instance') if agent_info else None
    
    def get_ecosystem_agents(self, ecosystem: str):
        """Obtiene todos los agentes de un ecosistema"""
        return {name: data for name, data in self.agents.items() 
                if data.get('ecosystem') == ecosystem}
    
    def get_status(self):
        """Obtiene estado detallado del factory"""
        total_registry = 0
        try:
            with open('agent_registry.json', 'r') as f:
                total_registry = len(json.load(f))
        except:
            pass
            
        return {
            'total_registry': total_registry,
            'loaded_agents': len(self.agents),
            'success_rate': f"{(len(self.agents) / total_registry * 100):.1f}%" if total_registry else '0%',
            'ecosystems': len(set(agent['ecosystem'] for agent in self.agents.values()))
        }

# Singleton global
_factory_instance = None

def get_agent_factory_fixed():
    """Obtiene instancia singleton del AgentFactory corregido"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AgentFactoryFixed()
        _factory_instance.discover_agents()
    return _factory_instance

if __name__ == "__main__":
    # Prueba de funcionamiento
    print("🧪 PROBANDO AGENT FACTORY CORREGIDO...")
    factory = get_agent_factory_fixed()
    status = factory.get_status()
    
    print(f"📊 RESULTADOS:")
    print(f"   • Agentes en registry: {status['total_registry']}")
    print(f"   • Agentes cargados: {status['loaded_agents']}")
    print(f"   • Tasa de éxito: {status['success_rate']}")
    print(f"   • Ecosistemas: {status['ecosystems']}")
    
    # Mostrar algunos agentes cargados
    if factory.agents:
        print(f"\n🎪 EJEMPLOS DE AGENTES CARGADOS:")
        for agent_name in list(factory.agents.keys())[:10]:
            print(f"   ✅ {agent_name}")
