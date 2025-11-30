"""
Ecosistema Regtech
Generado automáticamente
"""

# Imports automáticos
from .kycautomatico import Kycautomatico, create_agent as create_kycautomatico
from .amldetector import Amldetector, create_agent as create_amldetector
from .sancioneschecker import Sancioneschecker, create_agent as create_sancioneschecker
from .reportingregulatorio import Reportingregulatorio, create_agent as create_reportingregulatorio

AGENTS_REGISTRY = {
    'Kycautomatico': create_kycautomatico,
    'Amldetector': create_amldetector,
    'Sancioneschecker': create_sancioneschecker,
    'Reportingregulatorio': create_reportingregulatorio,
}

__all__ = [
    'Kycautomatico',
    'Amldetector',
    'Sancioneschecker',
    'Reportingregulatorio',
    "AGENTS_REGISTRY"
]