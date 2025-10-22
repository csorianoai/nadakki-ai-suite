"""
Ecosistema Originacion
Generado automáticamente
"""

# Imports automáticos
from .sentinelbot import Sentinelbot, create_agent as create_sentinelbot
from .dnaprofiler import Dnaprofiler, create_agent as create_dnaprofiler
from .incomeoracle import Incomeoracle, create_agent as create_incomeoracle
from .behaviorminer import Behaviorminer, create_agent as create_behaviorminer

AGENTS_REGISTRY = {
    'Sentinelbot': create_sentinelbot,
    'Dnaprofiler': create_dnaprofiler,
    'Incomeoracle': create_incomeoracle,
    'Behaviorminer': create_behaviorminer,
}

__all__ = [
    'Sentinelbot',
    'Dnaprofiler',
    'Incomeoracle',
    'Behaviorminer',
    "AGENTS_REGISTRY"
]