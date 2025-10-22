"""
Ecosistema Inteligencia
Generado automáticamente
"""

# Imports automáticos
from .profitmaximizer import Profitmaximizer, create_agent as create_profitmaximizer
from .cashfloworacle import Cashfloworacle, create_agent as create_cashfloworacle
from .pricinggenius import Pricinggenius, create_agent as create_pricinggenius
from .roimaster import Roimaster, create_agent as create_roimaster

AGENTS_REGISTRY = {
    'Profitmaximizer': create_profitmaximizer,
    'Cashfloworacle': create_cashfloworacle,
    'Pricinggenius': create_pricinggenius,
    'Roimaster': create_roimaster,
}

__all__ = [
    'Profitmaximizer',
    'Cashfloworacle',
    'Pricinggenius',
    'Roimaster',
    "AGENTS_REGISTRY"
]