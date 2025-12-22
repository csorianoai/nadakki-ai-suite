"""
Ecosistema Rrhh
Generado automáticamente
"""

# Imports automáticos
from .cvanalyzeria import Cvanalyzeria, create_agent as create_cvanalyzeria
from .nominaautomatica import Nominaautomatica, create_agent as create_nominaautomatica
from .talentopredictor import Talentopredictor, create_agent as create_talentopredictor
from .performancetracker import Performancetracker, create_agent as create_performancetracker
from .capacitacionia import Capacitacionia, create_agent as create_capacitacionia

AGENTS_REGISTRY = {
    'Cvanalyzeria': create_cvanalyzeria,
    'Nominaautomatica': create_nominaautomatica,
    'Talentopredictor': create_talentopredictor,
    'Performancetracker': create_performancetracker,
    'Capacitacionia': create_capacitacionia,
}

__all__ = [
    'Cvanalyzeria',
    'Nominaautomatica',
    'Talentopredictor',
    'Performancetracker',
    'Capacitacionia',
    "AGENTS_REGISTRY"
]