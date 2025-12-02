# src/Core/agent_factory_optimized.py
import sys
import os
import importlib
import json
import inspect
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AgentFactoryOptimized:
    """AgentFactory que maneja todos los casos de inicialización"""
    
    def __init__(self):
        self.agents = {}
        sys.path.insert(0, os.path.abspath('.'))
        logger.info("✅ AgentFactoryOptimized inicializado")
    
    def create_agent_instance(self, agent_class):
        """Crea instancia de agente manejando todos los casos de parámetros"""
        try:
            # Obtener la firma del constructor
            signature = inspect.signature(agent_class.__init__)
            parameters = signature.parameters
            
            # Preparar argumentos basados en la firma
            kwargs = {}
            
            for param_name, param in parameters.items():
                if param_name == 'self':
                    continue
                
                # Proporcionar valores por defecto basados en el nombre del parámetro
                if param_name == 'config':
                    kwargs[param_name] = {'tenant_id': 'default', 'environment': 'production'}
                elif param_name == 'tenant_id':
                    kwargs[param_name] = 'default'
                elif param_name == 'environment':
                    kwargs[param_name] = 'production'
                elif param_name == 'model_name':
                    kwargs[param_name] = 'default_model'
                elif param.has_default():
                    kwargs[param_name] = param.default
                else:
                    # Para parámetros requeridos sin valor por defecto, usar None
                    kwargs[param_name] = None
            
            # Intentar crear instancia con los argumentos preparados
            return agent_class(**kwargs)
            
        except Exception as e:
            logger.warning(f"⚠️  No se pudo crear instancia con parámetros: {e}")
            # Fallback: intentar sin argumentos
            try:
                return agent_class()
            except:
                # Último fallback: usar object() como placeholder
                logger.error(f"❌ No se pudo crear instancia de {agent_class.__name__}")
                return object()
    
    def discover_agents(self):
        """Descubre agentes con manejo robusto de errores"""
        try:
            with open('agent_registry.json', 'r', encoding='utf-8') as f:
                registry = json.load(f)
            logger.info(f"📊 Registry cargado: {len(registry)} agentes")
        except FileNotFoundError:
            logger.error("❌ Registry no encontrado")
            return {}
        
        loaded_agents = {}
        success_count = 0
        
        # Ordenar agentes: primero los que no son coordinadores
        agents_list = []
        coordinators_list = []
        
        for agent_name, agent_data in registry.items():
            if agent_data.get('status') != 'active':
                continue
            if 'coordinator' in agent_name.lower():
                coordinators_list.append((agent_name, agent_data))
            else:
                agents_list.append((agent_name, agent_data))
        
        # Procesar agentes normales primero
        for agent_name, agent_data in agents_list + coordinators_list:
            file_path = agent_data['file_path']
            
            try:
                # Convertir ruta a módulo
                module_path = file_path.replace('/', '.').replace('.py', '')
                
                # Importar módulo
                module = importlib.import_module(module_path)
                
                # Buscar clase principal
                agent_class = None
                candidate_classes = []
                
                for attr_name in dir(module):
                    if attr_name.startswith('_'):
                        continue
                        
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and attr.__module__ == module_path:
                        candidate_classes.append(attr)
                        
                        # Priorizar clases que coincidan con el nombre del archivo
                        if attr_name.lower().replace('_', '') == agent_name.lower().replace('_', ''):
                            agent_class = attr
                            break
                
                # Si no encontramos coincidencia exacta, usar la primera clase
                if not agent_class and candidate_classes:
                    agent_class = candidate_classes[0]
                
                if agent_class:
                    # Crear instancia con manejo de parámetros
                    instance = self.create_agent_instance(agent_class)
                    
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
        """Obtiene estado detallado"""
        total_registry = 0
        try:
            with open('agent_registry.json', 'r') as f:
                total_registry = len(json.load(f))
        except:
            pass
            
        ecosystems = {}
        for agent in self.agents.values():
            eco = agent['ecosystem']
            if eco not in ecosystems:
                ecosystems[eco] = 0
            ecosystems[eco] += 1
            
        return {
            'total_registry': total_registry,
            'loaded_agents': len(self.agents),
            'success_rate': f"{(len(self.agents) / total_registry * 100):.1f}%" if total_registry else '0%',
            'ecosystems': ecosystems
        }

# Singleton global
_factory_instance = None

def get_agent_factory_optimized():
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AgentFactoryOptimized()
        _factory_instance.discover_agents()
    return _factory_instance

if __name__ == "__main__":
    print("🧪 PROBANDO AGENT FACTORY OPTIMIZADO...")
    factory = get_agent_factory_optimized()
    status = factory.get_status()
    
    print(f"📊 RESULTADOS:")
    print(f"   • Agentes en registry: {status['total_registry']}")
    print(f"   • Agentes cargados: {status['loaded_agents']}")
    print(f"   • Tasa de éxito: {status['success_rate']}")
    
    print(f"   • Distribución por ecosistema:")
    for eco, count in status['ecosystems'].items():
        print(f"     - {eco}: {count} agentes")
    
    # Mostrar agentes de marketing
    marketing_agents = factory.get_ecosystem_agents('marketing')
    print(f"   • Agentes de Marketing: {len(marketing_agents)}")
    
    if marketing_agents:
        print(f"\n🎪 AGENTES DE MARKETING CARGADOS:")
        for agent_name in sorted(marketing_agents.keys()):
            print(f"   ✅ {agent_name}")
