"""
NADAKKI AI SUITE - HYPER AGENTS MODULE
Sistema de agentes inteligentes nivel 0.1% - AUTONOMÍA COMPLETA

CARACTERÍSTICAS:
- Completamente independiente (sin dependencias externas)
- Multi-tenant nativo
- Pensamiento paralelo
- Memoria semántica vectorial
- Aprendizaje por refuerzo (UCB, Thompson Sampling)
- Gestión de presupuesto inteligente
- Filtros de seguridad multi-capa
- Compatible con múltiples LLMs
- Sistema de eventos y triggers
- Workflows multi-agente
- Tareas programadas
- Monitoreo en tiempo real

USO BÁSICO:
    from hyper_agents import HyperMarketingBridge
    
    bridge = HyperMarketingBridge(tenant_id="mi_banco")
    result = await bridge.execute("socialpostgeneratoria", {"topic": "..."})

USO AVANZADO (Sistema Autónomo Completo):
    from hyper_agents import create_autonomous_marketing_system
    
    system = await create_autonomous_marketing_system(tenant_id="mi_banco")
    await system.run_workflow("lead_nurturing", {"lead_id": "123"})
"""

__version__ = "3.3.0"
__author__ = "Nadakki AI"

# Core exports
from .core import (
    # Types
    ActionType,
    ActionDef,
    AutonomyLevel,
    SafetyLevel,
    MemoryType,
    HyperAgentProfile,
    HyperAgentOutput,
    EthicalAssessment,
    SafetyResult,
    TenantConfig,
    get_default_tenant_config,
    create_financial_tenant_config,
    
    # Adapters
    BaseLLM,
    MockLLM,
    OpenAILLM,
    DeepSeekLLM,
    LLMFactory,
    get_llm,
    get_adapter,
    
    # Cortex
    HyperCortex,
    
    # Base Agent
    BaseHyperAgent
)

# Memory
from .memory import QuantumMemory, MemoryEntry, MemoryType

# Learning
from .learning import RLLearningEngine, ActionStats

# Budget
from .budget import BudgetManager, ModelTier, BudgetAlert

# Safety
from .safety import SafetyFilter

# Agents
from .agents.hyper_content_generator import HyperContentGenerator, hyper_generate_content

# Marketing Bridge (36 agentes)
from .marketing import (
    HyperMarketingBridge,
    HyperExecutionResult,
    MARKETING_AGENTS,
    execute_marketing_workflow
)

# Executors
from .executors import (
    BaseExecutor,
    MockExecutor,
    MetaExecutor,
    ActionRequest,
    ExecutionResult,
    ExecutionStatus,
    ActionRisk,
    get_executor,
    register_executor
)

# Autonomous
from .autonomous import (
    AutonomousAgentWrapper,
    AutonomousConfig,
    AutonomousExecutionResult,
    AutonomyLevel,
    ApprovalQueue,
    make_autonomous
)

# Triggers
from .triggers import (
    EventBus,
    Event,
    EventType,
    EventTriggerAgent,
    TriggerRule,
    Scheduler,
    ScheduleFrequency,
    DEFAULT_SCHEDULED_TASKS
)

# Orchestration
from .orchestration import (
    AutonomousOrchestrator,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowExecution,
    WorkflowStatus
)

# Monitoring
from .monitoring import (
    AutonomyDashboard,
    AgentMetrics,
    SystemHealth
)

# Complete System
from .autonomous_marketing_system import (
    AutonomousMarketingSystem,
    create_autonomous_marketing_system
)


__all__ = [
    # Version
    "__version__",
    
    # Types
    "ActionType",
    "ActionDef",
    "AutonomyLevel",
    "SafetyLevel",
    "MemoryType",
    "HyperAgentProfile",
    "HyperAgentOutput",
    "EthicalAssessment",
    "SafetyResult",
    "TenantConfig",
    "get_default_tenant_config",
    "create_financial_tenant_config",
    
    # Adapters
    "BaseLLM",
    "MockLLM",
    "OpenAILLM",
    "DeepSeekLLM",
    "LLMFactory",
    "get_llm",
    "get_adapter",
    
    # Cortex
    "HyperCortex",
    
    # Base Agent
    "BaseHyperAgent",
    
    # Memory
    "QuantumMemory",
    "MemoryEntry",
    
    # Learning
    "RLLearningEngine",
    "ActionStats",
    
    # Budget
    "BudgetManager",
    "ModelTier",
    "BudgetAlert",
    
    # Safety
    "SafetyFilter",
    
    # Agents
    "HyperContentGenerator",
    "hyper_generate_content",
    
    # Marketing Bridge
    "HyperMarketingBridge",
    "HyperExecutionResult",
    "MARKETING_AGENTS",
    "execute_marketing_workflow",
    
    # Executors
    "BaseExecutor",
    "MockExecutor",
    "MetaExecutor",
    "ActionRequest",
    "ExecutionResult",
    "ExecutionStatus",
    "ActionRisk",
    "get_executor",
    "register_executor",
    
    # Autonomous
    "AutonomousAgentWrapper",
    "AutonomousConfig",
    "AutonomousExecutionResult",
    "ApprovalQueue",
    "make_autonomous",
    
    # Triggers
    "EventBus",
    "Event",
    "EventType",
    "EventTriggerAgent",
    "TriggerRule",
    "Scheduler",
    "ScheduleFrequency",
    "DEFAULT_SCHEDULED_TASKS",
    
    # Orchestration
    "AutonomousOrchestrator",
    "WorkflowDefinition",
    "WorkflowStep",
    "WorkflowExecution",
    "WorkflowStatus",
    
    # Monitoring
    "AutonomyDashboard",
    "AgentMetrics",
    "SystemHealth",
    
    # Complete System
    "AutonomousMarketingSystem",
    "create_autonomous_marketing_system"
]
