"""
Ecosistema Operacional
Generado automáticamente
"""

# Imports automáticos
from .processgenius import Processgenius, create_agent as create_processgenius
from .costoptimizer import Costoptimizer, create_agent as create_costoptimizer
from .qualitycontroller import Qualitycontroller, create_agent as create_qualitycontroller
from .workflowmaster import Workflowmaster, create_agent as create_workflowmaster

AGENTS_REGISTRY = {
    'Processgenius': create_processgenius,
    'Costoptimizer': create_costoptimizer,
    'Qualitycontroller': create_qualitycontroller,
    'Workflowmaster': create_workflowmaster,
}

__all__ = [
    'Processgenius',
    'Costoptimizer',
    'Qualitycontroller',
    'Workflowmaster',
    "AGENTS_REGISTRY"
]