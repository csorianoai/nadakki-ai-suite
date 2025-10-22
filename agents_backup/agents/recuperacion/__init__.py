"""
Ecosistema Recuperacion
Generado automáticamente
"""

# Imports automáticos
from .collectionmaster import Collectionmaster, create_agent as create_collectionmaster
from .negotiationbot import Negotiationbot, create_agent as create_negotiationbot
from .recoveryoptimizer import Recoveryoptimizer, create_agent as create_recoveryoptimizer
from .legalpathway import Legalpathway, create_agent as create_legalpathway

AGENTS_REGISTRY = {
    'Collectionmaster': create_collectionmaster,
    'Negotiationbot': create_negotiationbot,
    'Recoveryoptimizer': create_recoveryoptimizer,
    'Legalpathway': create_legalpathway,
}

__all__ = [
    'Collectionmaster',
    'Negotiationbot',
    'Recoveryoptimizer',
    'Legalpathway',
    "AGENTS_REGISTRY"
]