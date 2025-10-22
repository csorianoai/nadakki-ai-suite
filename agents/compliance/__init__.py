"""
Ecosistema Compliance
Generado automáticamente
"""

# Imports automáticos
from .compliancewatchdog import Compliancewatchdog, create_agent as create_compliancewatchdog
from .auditmaster import Auditmaster, create_agent as create_auditmaster
from .docguardian import Docguardian, create_agent as create_docguardian
from .regulatoryradar import Regulatoryradar, create_agent as create_regulatoryradar

AGENTS_REGISTRY = {
    'Compliancewatchdog': create_compliancewatchdog,
    'Auditmaster': create_auditmaster,
    'Docguardian': create_docguardian,
    'Regulatoryradar': create_regulatoryradar,
}

__all__ = [
    'Compliancewatchdog',
    'Auditmaster',
    'Docguardian',
    'Regulatoryradar',
    "AGENTS_REGISTRY"
]