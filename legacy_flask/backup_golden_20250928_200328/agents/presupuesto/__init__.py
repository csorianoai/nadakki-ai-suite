"""
Ecosistema Presupuesto
Generado automáticamente
"""

# Imports automáticos
from .presupuestomaestro import Presupuestomaestro, create_agent as create_presupuestomaestro
from .varianzaanalisis import Varianzaanalisis, create_agent as create_varianzaanalisis
from .forecastingia import Forecastingia, create_agent as create_forecastingia
from .costocentros import Costocentros, create_agent as create_costocentros
from .roipredictor import Roipredictor, create_agent as create_roipredictor
from .budgetoptimizer import Budgetoptimizer, create_agent as create_budgetoptimizer

AGENTS_REGISTRY = {
    'Presupuestomaestro': create_presupuestomaestro,
    'Varianzaanalisis': create_varianzaanalisis,
    'Forecastingia': create_forecastingia,
    'Costocentros': create_costocentros,
    'Roipredictor': create_roipredictor,
    'Budgetoptimizer': create_budgetoptimizer,
}

__all__ = [
    'Presupuestomaestro',
    'Varianzaanalisis',
    'Forecastingia',
    'Costocentros',
    'Roipredictor',
    'Budgetoptimizer',
    "AGENTS_REGISTRY"
]