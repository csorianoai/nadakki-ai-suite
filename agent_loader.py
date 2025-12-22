"""
Nadakki Universal Agent Loader v4.0
Carga dinámica de todos los agentes del sistema
"""

import importlib
import inspect
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AgentLoader")

# Definición de CORES
CORES_CONFIG = {
    "marketing": {"name": "Marketing Core", "color": "#f97316", "icon": "target"},
    "legal": {"name": "Legal Core", "color": "#eab308", "icon": "scale"},
    "logistica": {"name": "Logistics Core", "color": "#22c55e", "icon": "truck"},
    "contabilidad": {"name": "Accounting Core", "color": "#3b82f6", "icon": "calculator"},
    "rrhh": {"name": "HR Core", "color": "#8b5cf6", "icon": "users"},
    "ventascrm": {"name": "Sales CRM Core", "color": "#ec4899", "icon": "shopping-cart"},
    "educacion": {"name": "Education Core", "color": "#14b8a6", "icon": "graduation-cap"},
    "presupuesto": {"name": "Budget Core", "color": "#f59e0b", "icon": "wallet"},
    "compliance": {"name": "Compliance Core", "color": "#10b981", "icon": "shield-check"},
    "regtech": {"name": "RegTech Core", "color": "#6366f1", "icon": "file-text"},
    "investigacion": {"name": "Research Core", "color": "#0ea5e9", "icon": "search"},
    "originacion": {"name": "Origination Core", "color": "#84cc16", "icon": "file-plus"},
    "decision": {"name": "Decision Core", "color": "#a855f7", "icon": "brain"},
    "experiencia": {"name": "Experience Core", "color": "#f43f5e", "icon": "heart"},
    "fortaleza": {"name": "Strength Core", "color": "#64748b", "icon": "shield"},
    "inteligencia": {"name": "Intelligence Core", "color": "#0891b2", "icon": "lightbulb"},
    "operacional": {"name": "Operations Core", "color": "#65a30d", "icon": "cog"},
    "orchestration": {"name": "Orchestration Core", "color": "#7c3aed", "icon": "layers"},
    "recuperacion": {"name": "Recovery Core", "color": "#dc2626", "icon": "refresh"},
    "vigilancia": {"name": "Surveillance Core", "color": "#475569", "icon": "eye"}
}

class AgentRegistry:
    """Registro universal de agentes"""
    
    def __init__(self, base_path: str = "agents"):
        self.base_path = Path(base_path)
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.cores: Dict[str, List[str]] = {}
        self.total = 0
        self._discover_agents()
    
    def _discover_agents(self):
        """Descubrir todos los agentes automáticamente"""
        logger.info(f"Discovering agents from {self.base_path}")
        
        for core_dir in self.base_path.iterdir():
            if not core_dir.is_dir() or core_dir.name.startswith("_"):
                continue
            
            core_name = core_dir.name
            self.cores[core_name] = []
            
            for agent_file in core_dir.glob("*.py"):
                if agent_file.name in ["__init__.py", "canonical.py"]:
                    continue
                
                agent_id = agent_file.stem
                agent_key = f"{core_name}.{agent_id}"
                
                # Registrar metadata (sin importar aún)
                self.agents[agent_key] = {
                    "id": agent_id,
                    "key": agent_key,
                    "name": self._format_name(agent_id),
                    "core": core_name,
                    "core_config": CORES_CONFIG.get(core_name, {"name": core_name.title(), "color": "#666", "icon": "box"}),
                    "file": str(agent_file),
                    "module": f"agents.{core_name}.{agent_id}",
                    "status": "registered",
                    "class": None,
                    "error": None
                }
                self.cores[core_name].append(agent_id)
                self.total += 1
        
        logger.info(f"✓ Discovered {self.total} agents in {len(self.cores)} cores")
    
    def _format_name(self, agent_id: str) -> str:
        """Convertir ID a nombre legible"""
        name = agent_id.replace("ia", "").replace("_", " ").replace("-", " ")
        return " ".join(word.capitalize() for word in name.split())
    
    def load_agent(self, agent_key: str) -> Optional[Any]:
        """Cargar un agente específico bajo demanda"""
        if agent_key not in self.agents:
            return None
        
        agent = self.agents[agent_key]
        
        # Si ya está cargado, retornarlo
        if agent["class"] is not None:
            return agent["class"]
        
        try:
            module = importlib.import_module(agent["module"])
            
            # Buscar la clase principal
            agent_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module.__name__:
                    agent_class = obj
                    break
            
            if agent_class:
                agent["class"] = agent_class
                agent["status"] = "loaded"
                return agent_class
            else:
                agent["status"] = "no_class"
                agent["error"] = "No class found in module"
                return None
                
        except Exception as e:
            agent["status"] = "error"
            agent["error"] = str(e)[:100]
            logger.warning(f"Could not load {agent_key}: {e}")
            return None
    
    def get_agent(self, core: str, agent_id: str) -> Optional[Dict]:
        """Obtener info de un agente"""
        return self.agents.get(f"{core}.{agent_id}")
    
    def get_agents_by_core(self, core: str) -> List[Dict]:
        """Obtener todos los agentes de un core"""
        agent_ids = self.cores.get(core, [])
        return [self.agents[f"{core}.{aid}"] for aid in agent_ids]
    
    def get_all_agents(self) -> List[Dict]:
        """Obtener todos los agentes"""
        return list(self.agents.values())
    
    def get_core_summary(self) -> Dict[str, int]:
        """Resumen de agentes por core"""
        return {core: len(agents) for core, agents in self.cores.items()}
    
    def get_cores(self) -> List[Dict]:
        """Obtener info de todos los cores"""
        cores_info = []
        for core_id, agent_ids in self.cores.items():
            config = CORES_CONFIG.get(core_id, {"name": core_id.title(), "color": "#666", "icon": "box"})
            cores_info.append({
                "id": core_id,
                "name": config["name"],
                "color": config["color"],
                "icon": config["icon"],
                "agents_count": len(agent_ids),
                "status": "active" if len(agent_ids) > 0 else "empty"
            })
        return sorted(cores_info, key=lambda x: -x["agents_count"])


# Instancia global
registry = AgentRegistry()
