"""
Nadakki Universal Agent Loader v4.1 - Enterprise Grade
Sistema de scoring inteligente para detección de clases principales
"""

import os
import sys
import importlib
import inspect
import logging
from typing import Dict, List, Any, Optional
from dataclasses import is_dataclass

logger = logging.getLogger("AgentLoader")

# Configuración de cores
CORES_CONFIG = {
    "marketing": {"name": "Marketing Core", "color": "#f97316", "icon": "target"},
    "legal": {"name": "Legal Core", "color": "#eab308", "icon": "scale"},
    "logistica": {"name": "Logistics Core", "color": "#22c55e", "icon": "truck"},
    "contabilidad": {"name": "Accounting Core", "color": "#3b82f6", "icon": "calculator"},
    "presupuesto": {"name": "Budget Core", "color": "#8b5cf6", "icon": "chart-bar"},
    "rrhh": {"name": "HR Core", "color": "#ec4899", "icon": "users"},
    "originacion": {"name": "Origination Core", "color": "#14b8a6", "icon": "file-plus"},
    "educacion": {"name": "Education Core", "color": "#f43f5e", "icon": "academic-cap"},
    "investigacion": {"name": "Research Core", "color": "#6366f1", "icon": "search"},
    "ventascrm": {"name": "Sales CRM Core", "color": "#10b981", "icon": "currency-dollar"},
    "regtech": {"name": "RegTech Core", "color": "#f59e0b", "icon": "shield-check"},
    "compliance": {"name": "Compliance Core", "color": "#ef4444", "icon": "clipboard-check"},
    "decision": {"name": "Decision Core", "color": "#8b5cf6", "icon": "light-bulb"},
    "experiencia": {"name": "Experience Core", "color": "#06b6d4", "icon": "heart"},
    "fortaleza": {"name": "Strength Core", "color": "#84cc16", "icon": "shield"},
    "inteligencia": {"name": "Intelligence Core", "color": "#a855f7", "icon": "brain"},
    "operacional": {"name": "Operations Core", "color": "#f97316", "icon": "cog"},
    "orchestration": {"name": "Orchestration Core", "color": "#0ea5e9", "icon": "server"},
    "recuperacion": {"name": "Recovery Core", "color": "#22c55e", "icon": "refresh"},
    "vigilancia": {"name": "Surveillance Core", "color": "#dc2626", "icon": "eye"},
}


class AgentRegistry:
    """Registro universal de agentes con carga dinámica y scoring inteligente"""
    
    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = agents_dir
        self.agents: Dict[str, Dict] = {}
        self.cores: Dict[str, List[str]] = {}
        self.total = 0
        self._discover_agents()
    
    def _discover_agents(self):
        """Descubrir todos los agentes en el directorio"""
        if not os.path.exists(self.agents_dir):
            logger.warning(f"Agents directory not found: {self.agents_dir}")
            return
        
        # Asegurar que el directorio está en el path
        if self.agents_dir not in sys.path:
            sys.path.insert(0, os.path.dirname(os.path.abspath(self.agents_dir)))
        
        logger.info(f"AgentLoader: Discovering agents from {self.agents_dir}")
        
        for core_name in os.listdir(self.agents_dir):
            core_path = os.path.join(self.agents_dir, core_name)
            
            if not os.path.isdir(core_path) or core_name.startswith('_'):
                continue
            
            self.cores[core_name] = []
            
            for filename in os.listdir(core_path):
                if not filename.endswith('.py') or filename.startswith('_'):
                    continue
                
                agent_id = filename[:-3]  # Remover .py
                agent_key = f"{core_name}.{agent_id}"
                module_path = f"agents.{core_name}.{agent_id}"
                
                self.agents[agent_key] = {
                    "id": agent_id,
                    "name": agent_id.replace('_', ' ').title(),
                    "core": core_name,
                    "module": module_path,
                    "file": os.path.join(core_path, filename),
                    "class": None,
                    "status": "discovered",
                    "error": None
                }
                
                self.cores[core_name].append(agent_id)
                self.total += 1
        
        logger.info(f"AgentLoader: ✓ Discovered {self.total} agents in {len(self.cores)} cores")
    
    def _score_class(self, cls, agent_id: str) -> int:
        """
        Sistema de scoring para identificar la clase principal del agente.
        Mayor score = más probable que sea la clase principal.
        """
        score = 0
        name = cls.__name__
        name_lower = name.lower()
        agent_id_clean = agent_id.lower().replace('_', '').replace('-', '')
        
        # +20: Nombre termina en 'IA' (patrón principal de nuestros agentes)
        if name.endswith('IA') or name.endswith('Ia'):
            score += 20
        
        # +15: Nombre contiene el ID del agente
        if agent_id_clean in name_lower or name_lower.replace('ia', '') in agent_id_clean:
            score += 15
        
        # +10: Tiene método 'execute'
        if hasattr(cls, 'execute') and callable(getattr(cls, 'execute', None)):
            score += 10
        
        # +5: Tiene otros métodos de ejecución
        for method in ['run', 'process', 'analyze', 'score', 'predict', 'generate', 'personalize']:
            if hasattr(cls, method) and callable(getattr(cls, method, None)):
                score += 5
                break
        
        # +3 por cada método propio (no heredado de object)
        own_methods = [m for m in dir(cls) if not m.startswith('_') and callable(getattr(cls, m, None))]
        score += min(len(own_methods) * 2, 20)  # Max 20 puntos por métodos
        
        # -50: Es un dataclass (helper, no agente)
        if is_dataclass(cls):
            score -= 50
        
        # -30: Nombres de helpers comunes
        helper_patterns = ['input', 'output', 'config', 'result', 'response', 'request',
                          'bucket', 'cache', 'flags', 'params', 'settings', 'strategy',
                          'anomaly', 'audit', 'trace', 'utm', 'feature']
        if any(pattern in name_lower for pattern in helper_patterns):
            score -= 30
        
        # +8: Nombre termina en Coordinator, Orchestrator, Engine, Analyzer
        if any(name.endswith(suffix) for suffix in ['Coordinator', 'Orchestrator', 'Engine', 'Analyzer', 'Optimizer']):
            score += 8
        
        return score
    
    def load_agent(self, agent_key: str) -> Optional[Any]:
        """Cargar un agente específico usando sistema de scoring"""
        if agent_key not in self.agents:
            return None
        
        agent = self.agents[agent_key]
        
        if agent["class"] is not None:
            return agent["class"]
        
        try:
            module = importlib.import_module(agent["module"])
            
            # Recolectar todas las clases del módulo con sus scores
            candidates = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module.__name__:
                    score = self._score_class(obj, agent["id"])
                    candidates.append((score, name, obj))
            
            # Ordenar por score descendente y tomar la mejor
            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                best_score, best_name, best_class = candidates[0]
                
                if best_score > 0:  # Solo aceptar si tiene score positivo
                    agent["class"] = best_class
                    agent["status"] = "loaded"
                    agent["class_name"] = best_name
                    agent["class_score"] = best_score
                    return best_class
                else:
                    agent["status"] = "no_valid_class"
                    agent["error"] = f"Best candidate '{best_name}' has score {best_score}"
                    return None
            else:
                agent["status"] = "no_class"
                agent["error"] = "No classes found in module"
                return None
                
        except Exception as e:
            agent["status"] = "error"
            agent["error"] = str(e)[:200]
            logger.warning(f"Could not load {agent_key}: {e}")
            return None
    
    def _get_constructor_params(self, agent_class) -> list:
        """Obtener parámetros del constructor"""
        try:
            sig = inspect.signature(agent_class.__init__)
            params = list(sig.parameters.keys())
            return [p for p in params if p != 'self']
        except:
            return []
    
    def create_instance(self, agent_key: str, tenant_id: str = "default"):
        """Crear instancia del agente probando múltiples patrones de constructor"""
        agent = self.agents.get(agent_key)
        if not agent or not agent.get("class"):
            self.load_agent(agent_key)
            agent = self.agents.get(agent_key)
        
        if not agent or not agent.get("class"):
            return None
        
        agent_class = agent["class"]
        
        # Lista ordenada de estrategias de instanciación
        strategies = [
            lambda: agent_class(tenant_id, None),
            lambda: agent_class(tenant_id=tenant_id, config=None),
            lambda: agent_class(tenant_id, {}),
            lambda: agent_class(tenant_id),
            lambda: agent_class({"tenant_id": tenant_id}),
            lambda: agent_class(config={"tenant_id": tenant_id}),
            lambda: agent_class(tenant_config={"tenant_id": tenant_id}),
            lambda: agent_class(initial=None),
            lambda: agent_class(initial={}),
            lambda: agent_class(None),
            lambda: agent_class({}),
            lambda: agent_class(),
            lambda: agent_class(rate=100, capacity=1000),
            lambda: agent_class(max_memory_size=1000),
        ]
        
        last_error = None
        for strategy in strategies:
            try:
                instance = strategy()
                if not hasattr(instance, 'tenant_id'):
                    instance.tenant_id = tenant_id
                elif not instance.tenant_id:
                    instance.tenant_id = tenant_id
                return instance
            except (TypeError, AttributeError) as e:
                last_error = e
                continue
        
        logger.error(f"Error creating instance of {agent_key}: {last_error}")
        return None
    
    def get_agent(self, core: str, agent_id: str) -> Optional[Dict]:
        """Obtener información de un agente"""
        return self.agents.get(f"{core}.{agent_id}")
    
    def get_agents_by_core(self, core: str) -> List[Dict]:
        """Obtener todos los agentes de un core"""
        return [
            self.agents[f"{core}.{aid}"]
            for aid in self.cores.get(core, [])
        ]
    
    def get_all_agents(self) -> List[Dict]:
        """Obtener todos los agentes"""
        return list(self.agents.values())
    
    def get_core_summary(self) -> Dict[str, int]:
        """Resumen de agentes por core"""
        return {core: len(agents) for core, agents in self.cores.items()}


# Instancia global del registry

    def get_cores(self) -> List[Dict[str, Any]]:
        """Retorna lista de cores con información detallada"""
        cores_list = []
        for core_id, agent_ids in self.cores.items():
            cores_list.append({
                "id": core_id,
                "name": core_id.replace("_", " ").title(),
                "agents_count": len(agent_ids),
                "agents": agent_ids,
                "status": "active"
            })
        return cores_list


registry = AgentRegistry()
