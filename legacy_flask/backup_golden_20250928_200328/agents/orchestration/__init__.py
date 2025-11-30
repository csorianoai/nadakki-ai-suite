"""
Ecosistema Orchestration
Generado automáticamente
"""

# Imports automáticos
from .orchestrationmaster import Orchestrationmaster, create_agent as create_orchestrationmaster
from .loadbalancer import Loadbalancer, create_agent as create_loadbalancer
from .resourcemanager import Resourcemanager, create_agent as create_resourcemanager
from .healthchecker import Healthchecker, create_agent as create_healthchecker

AGENTS_REGISTRY = {
    'Orchestrationmaster': create_orchestrationmaster,
    'Loadbalancer': create_loadbalancer,
    'Resourcemanager': create_resourcemanager,
    'Healthchecker': create_healthchecker,
}

__all__ = [
    'Orchestrationmaster',
    'Loadbalancer',
    'Resourcemanager',
    'Healthchecker',
    "AGENTS_REGISTRY"
]