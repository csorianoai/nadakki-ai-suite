"""
Ecosistema Investigacion
Generado automáticamente
"""

# Imports automáticos
from .patentesanalyzer import Patentesanalyzer, create_agent as create_patentesanalyzer
from .tendenciasia import Tendenciasia, create_agent as create_tendenciasia
from .prototipogenerator import Prototipogenerator, create_agent as create_prototipogenerator
from .innovaciontracker import Innovaciontracker, create_agent as create_innovaciontracker

AGENTS_REGISTRY = {
    'Patentesanalyzer': create_patentesanalyzer,
    'Tendenciasia': create_tendenciasia,
    'Prototipogenerator': create_prototipogenerator,
    'Innovaciontracker': create_innovaciontracker,
}

__all__ = [
    'Patentesanalyzer',
    'Tendenciasia',
    'Prototipogenerator',
    'Innovaciontracker',
    "AGENTS_REGISTRY"
]