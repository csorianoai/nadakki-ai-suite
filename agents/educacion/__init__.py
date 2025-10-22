"""
Ecosistema Educacion
Generado automáticamente
"""

# Imports automáticos
from .curriculumadaptativo import Curriculumadaptativo, create_agent as create_curriculumadaptativo
from .evaluacionia import Evaluacionia, create_agent as create_evaluacionia
from .contenidopersonalizado import Contenidopersonalizado, create_agent as create_contenidopersonalizado
from .progresionestudiante import Progresionestudiante, create_agent as create_progresionestudiante

AGENTS_REGISTRY = {
    'Curriculumadaptativo': create_curriculumadaptativo,
    'Evaluacionia': create_evaluacionia,
    'Contenidopersonalizado': create_contenidopersonalizado,
    'Progresionestudiante': create_progresionestudiante,
}

__all__ = [
    'Curriculumadaptativo',
    'Evaluacionia',
    'Contenidopersonalizado',
    'Progresionestudiante',
    "AGENTS_REGISTRY"
]