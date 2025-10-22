"""
Ecosistema Decision
Generado automáticamente
"""

# Imports automáticos
from .quantumdecision import Quantumdecision, create_agent as create_quantumdecision
from .riskoracle import Riskoracle, create_agent as create_riskoracle
from .policyguardian import Policyguardian, create_agent as create_policyguardian
from .turboapprover import Turboapprover, create_agent as create_turboapprover

AGENTS_REGISTRY = {
    'Quantumdecision': create_quantumdecision,
    'Riskoracle': create_riskoracle,
    'Policyguardian': create_policyguardian,
    'Turboapprover': create_turboapprover,
}

__all__ = [
    'Quantumdecision',
    'Riskoracle',
    'Policyguardian',
    'Turboapprover',
    "AGENTS_REGISTRY"
]