"""
Ecosistema Vigilancia
Generado automáticamente
"""

# Imports automáticos
from .earlywarning import Earlywarning, create_agent as create_earlywarning
from .portfoliosentinel import Portfoliosentinel, create_agent as create_portfoliosentinel
from .stresstester import Stresstester, create_agent as create_stresstester
from .marketradar import Marketradar, create_agent as create_marketradar

AGENTS_REGISTRY = {
    'Earlywarning': create_earlywarning,
    'Portfoliosentinel': create_portfoliosentinel,
    'Stresstester': create_stresstester,
    'Marketradar': create_marketradar,
}

__all__ = [
    'Earlywarning',
    'Portfoliosentinel',
    'Stresstester',
    'Marketradar',
    "AGENTS_REGISTRY"
]