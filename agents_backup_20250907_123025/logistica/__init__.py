"""
Ecosistema Logistica
Generado automáticamente
"""

# Imports automáticos
from .optimizadorrutasia import Optimizadorrutasia, create_agent as create_optimizadorrutasia
from .previsioninventarioia import Previsioninventarioia, create_agent as create_previsioninventarioia
from .controlpedidosia import Controlpedidosia, create_agent as create_controlpedidosia
from .evaluadorproveedoresia import Evaluadorproveedoresia, create_agent as create_evaluadorproveedoresia
from .alertasinventario import Alertasinventario, create_agent as create_alertasinventario
from .logisticareversa import Logisticareversa, create_agent as create_logisticareversa
from .controlcalidad import Controlcalidad, create_agent as create_controlcalidad
from .trazabilidadia import Trazabilidadia, create_agent as create_trazabilidadia
from .predicciondemanda import Predicciondemanda, create_agent as create_predicciondemanda
from .optimizacionalmacen import Optimizacionalmacen, create_agent as create_optimizacionalmacen
from .transportepredictivo import Transportepredictivo, create_agent as create_transportepredictivo
from .costoslogisticos import Costoslogisticos, create_agent as create_costoslogisticos
from .seguridadcarga import Seguridadcarga, create_agent as create_seguridadcarga

AGENTS_REGISTRY = {
    'Optimizadorrutasia': create_optimizadorrutasia,
    'Previsioninventarioia': create_previsioninventarioia,
    'Controlpedidosia': create_controlpedidosia,
    'Evaluadorproveedoresia': create_evaluadorproveedoresia,
    'Alertasinventario': create_alertasinventario,
    'Logisticareversa': create_logisticareversa,
    'Controlcalidad': create_controlcalidad,
    'Trazabilidadia': create_trazabilidadia,
    'Predicciondemanda': create_predicciondemanda,
    'Optimizacionalmacen': create_optimizacionalmacen,
    'Transportepredictivo': create_transportepredictivo,
    'Costoslogisticos': create_costoslogisticos,
    'Seguridadcarga': create_seguridadcarga,
}

__all__ = [
    'Optimizadorrutasia',
    'Previsioninventarioia',
    'Controlpedidosia',
    'Evaluadorproveedoresia',
    'Alertasinventario',
    'Logisticareversa',
    'Controlcalidad',
    'Trazabilidadia',
    'Predicciondemanda',
    'Optimizacionalmacen',
    'Transportepredictivo',
    'Costoslogisticos',
    'Seguridadcarga',
    "AGENTS_REGISTRY"
]