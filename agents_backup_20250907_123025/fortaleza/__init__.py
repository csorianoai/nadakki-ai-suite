"""
Ecosistema Fortaleza
Generado automáticamente
"""

# Imports automáticos
from .cybersentinel import Cybersentinel, create_agent as create_cybersentinel
from .datavault import Datavault, create_agent as create_datavault
from .systemhealthmonitor import Systemhealthmonitor, create_agent as create_systemhealthmonitor
from .backupguardian import Backupguardian, create_agent as create_backupguardian

AGENTS_REGISTRY = {
    'Cybersentinel': create_cybersentinel,
    'Datavault': create_datavault,
    'Systemhealthmonitor': create_systemhealthmonitor,
    'Backupguardian': create_backupguardian,
}

__all__ = [
    'Cybersentinel',
    'Datavault',
    'Systemhealthmonitor',
    'Backupguardian',
    "AGENTS_REGISTRY"
]