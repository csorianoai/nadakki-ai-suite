"""
Ecosistema Contabilidad
Generado automáticamente
"""

# Imports automáticos
from .dgiiautoreporter import Dgiiautoreporter, create_agent as create_dgiiautoreporter
from .facturacionelectronica import Facturacionelectronica, create_agent as create_facturacionelectronica
from .conciliacionbancaria import Conciliacionbancaria, create_agent as create_conciliacionbancaria
from .controlgastos import Controlgastos, create_agent as create_controlgastos
from .previsionfiscal import Previsionfiscal, create_agent as create_previsionfiscal
from .auditoriainterna import Auditoriainterna, create_agent as create_auditoriainterna
from .flujocajaia import Flujocajaia, create_agent as create_flujocajaia
from .activosfijos import Activosfijos, create_agent as create_activosfijos
from .cierrecontable import Cierrecontable, create_agent as create_cierrecontable
from .reportingfinanciero import Reportingfinanciero, create_agent as create_reportingfinanciero

AGENTS_REGISTRY = {
    'Dgiiautoreporter': create_dgiiautoreporter,
    'Facturacionelectronica': create_facturacionelectronica,
    'Conciliacionbancaria': create_conciliacionbancaria,
    'Controlgastos': create_controlgastos,
    'Previsionfiscal': create_previsionfiscal,
    'Auditoriainterna': create_auditoriainterna,
    'Flujocajaia': create_flujocajaia,
    'Activosfijos': create_activosfijos,
    'Cierrecontable': create_cierrecontable,
    'Reportingfinanciero': create_reportingfinanciero,
}

__all__ = [
    'Dgiiautoreporter',
    'Facturacionelectronica',
    'Conciliacionbancaria',
    'Controlgastos',
    'Previsionfiscal',
    'Auditoriainterna',
    'Flujocajaia',
    'Activosfijos',
    'Cierrecontable',
    'Reportingfinanciero',
    "AGENTS_REGISTRY"
]