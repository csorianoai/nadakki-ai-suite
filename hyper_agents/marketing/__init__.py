"""
NADAKKI AI SUITE - HYPER MARKETING MODULE
Integración de los 35 agentes de marketing con capacidades hyper.
"""

from .hyper_marketing_bridge import (
    HyperMarketingBridge,
    HyperExecutionResult,
    MARKETING_AGENTS,
    execute_marketing_workflow
)

__all__ = [
    "HyperMarketingBridge",
    "HyperExecutionResult",
    "MARKETING_AGENTS",
    "execute_marketing_workflow"
]
