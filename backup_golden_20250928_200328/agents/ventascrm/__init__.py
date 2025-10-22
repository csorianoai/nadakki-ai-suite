"""
Ecosistema Ventascrm
Generado automáticamente
"""

# Imports automáticos
from .leadscoringia import Leadscoringia, create_agent as create_leadscoringia
from .pipelineoptimizer import Pipelineoptimizer, create_agent as create_pipelineoptimizer
from .churnpredictor import Churnpredictor, create_agent as create_churnpredictor
from .upsellengine import Upsellengine, create_agent as create_upsellengine

AGENTS_REGISTRY = {
    'Leadscoringia': create_leadscoringia,
    'Pipelineoptimizer': create_pipelineoptimizer,
    'Churnpredictor': create_churnpredictor,
    'Upsellengine': create_upsellengine,
}

__all__ = [
    'Leadscoringia',
    'Pipelineoptimizer',
    'Churnpredictor',
    'Upsellengine',
    "AGENTS_REGISTRY"
]