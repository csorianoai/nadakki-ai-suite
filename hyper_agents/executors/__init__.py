"""
NADAKKI AI SUITE - EXECUTORS MODULE
Conectores para ejecutar acciones reales en plataformas externas.
"""

from .base_executor import (
    BaseExecutor,
    MockExecutor,
    ActionRequest,
    ExecutionResult,
    ExecutionStatus,
    ActionRisk,
    get_executor,
    register_executor,
    EXECUTOR_REGISTRY
)

from .meta_executor import MetaExecutor

__all__ = [
    "BaseExecutor",
    "MockExecutor",
    "MetaExecutor",
    "ActionRequest",
    "ExecutionResult",
    "ExecutionStatus",
    "ActionRisk",
    "get_executor",
    "register_executor",
    "EXECUTOR_REGISTRY"
]
