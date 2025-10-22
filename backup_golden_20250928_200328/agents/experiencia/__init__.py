"""
Ecosistema Experiencia
Generado automáticamente
"""

# Imports automáticos
from .customergenius import Customergenius, create_agent as create_customergenius
from .personalizationengine import Personalizationengine, create_agent as create_personalizationengine
from .chatbotsupreme import Chatbotsupreme, create_agent as create_chatbotsupreme
from .onboardingwizard import Onboardingwizard, create_agent as create_onboardingwizard

AGENTS_REGISTRY = {
    'Customergenius': create_customergenius,
    'Personalizationengine': create_personalizationengine,
    'Chatbotsupreme': create_chatbotsupreme,
    'Onboardingwizard': create_onboardingwizard,
}

__all__ = [
    'Customergenius',
    'Personalizationengine',
    'Chatbotsupreme',
    'Onboardingwizard',
    "AGENTS_REGISTRY"
]