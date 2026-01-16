"""
NADAKKI AI SUITE - TIPOS Y DEFINICIONES BASE
Módulo completamente independiente - Sin dependencias externas.
Reutilizable para múltiples instituciones financieras.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


# ============================================================================
# TIPOS DE ACCIONES
# ============================================================================

class ActionType(Enum):
    """Tipos de acciones que puede ejecutar un agente"""
    # Marketing Actions
    PUBLISH_SOCIAL = "publish_social"
    SEND_EMAIL = "send_email"
    CAPTURE_LEAD = "capture_lead"
    
    # Financial Actions
    CREDIT_EVALUATION = "credit_evaluation"
    RISK_ASSESSMENT = "risk_assessment"
    FRAUD_DETECTION = "fraud_detection"
    COLLECTION_ACTION = "collection_action"
    
    # System Actions
    LOG_EVENT = "log_event"
    TRIGGER_AGENT = "trigger_agent"
    NOTIFY_HUMAN = "notify_human"
    ADJUST_BUDGET = "adjust_budget"
    UPDATE_MEMORY = "update_memory"
    
    # Compliance Actions
    COMPLIANCE_CHECK = "compliance_check"
    AUDIT_LOG = "audit_log"
    REGULATORY_REPORT = "regulatory_report"


class AutonomyLevel(Enum):
    """Niveles de autonomía del agente"""
    MANUAL = "manual"           # Requiere aprobación humana para todo
    SEMI = "semi"               # Aprobación para acciones de alto impacto
    FULL_AUTO = "full"          # Completamente autónomo
    LEARNING = "learning"       # En modo aprendizaje, requiere supervisión


class SafetyLevel(Enum):
    """Niveles de seguridad para contenido/acciones"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


class MemoryType(Enum):
    """Tipos de memoria para el sistema"""
    SHORT_TERM = "short_term"     # Sesión actual
    LONG_TERM = "long_term"       # Persistente
    EPISODIC = "episodic"         # Eventos específicos
    SEMANTIC = "semantic"         # Conocimiento general
    PROCEDURAL = "procedural"     # Cómo hacer cosas


# ============================================================================
# DATACLASSES PRINCIPALES
# ============================================================================

@dataclass
class ActionDef:
    """Definición de una acción a ejecutar"""
    action: ActionType
    params: Dict[str, Any]
    confidence: float = 0.9
    priority: int = 5
    requires_approval: bool = False
    agent_id: str = ""
    tenant_id: str = ""
    reasoning: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "params": self.params,
            "confidence": self.confidence,
            "priority": self.priority,
            "requires_approval": self.requires_approval,
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "reasoning": self.reasoning,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionDef":
        return cls(
            action=ActionType(data["action"]),
            params=data.get("params", {}),
            confidence=data.get("confidence", 0.9),
            priority=data.get("priority", 5),
            requires_approval=data.get("requires_approval", False),
            agent_id=data.get("agent_id", ""),
            tenant_id=data.get("tenant_id", ""),
            reasoning=data.get("reasoning", ""),
            created_at=data.get("created_at", datetime.utcnow().isoformat())
        )


@dataclass
class HyperAgentProfile:
    """Perfil completo del agente - Configurable por institución"""
    agent_id: str
    agent_name: str
    description: str
    category: str
    version: str = "3.0.0"
    autonomy_level: AutonomyLevel = AutonomyLevel.SEMI
    default_model: str = "gpt-4o-mini"
    fallback_model: str = "deepseek-chat"
    max_tokens: int = 2000
    temperature: float = 0.7
    tenant_id: str = "default"
    can_trigger_agents: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    # Configuración específica por institución
    institution_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "autonomy_level": self.autonomy_level.value,
            "default_model": self.default_model,
            "fallback_model": self.fallback_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "tenant_id": self.tenant_id,
            "can_trigger_agents": self.can_trigger_agents,
            "personality_traits": self.personality_traits,
            "institution_config": self.institution_config
        }


@dataclass
class HyperAgentOutput:
    """Output completo del ciclo de ejecución"""
    success: bool
    agent_id: str
    actions: List[ActionDef] = field(default_factory=list)
    content: Optional[str] = None
    plan: Optional[Dict[str, Any]] = None
    parallel_thoughts: Optional[Dict[str, Any]] = None
    ethical_assessment: Optional[Dict[str, Any]] = None
    safety_check: Optional[Dict[str, Any]] = None
    reflection: Optional[str] = None
    self_score: float = 0.0
    learnings: List[str] = field(default_factory=list)
    cost_usd: float = 0.0
    tokens_used: int = 0
    execution_time_ms: float = 0.0
    budget_status: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    # Metadatos de institución
    tenant_id: str = "default"
    institution_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "agent_id": self.agent_id,
            "actions": [a.to_dict() for a in self.actions],
            "content": self.content,
            "plan": self.plan,
            "parallel_thoughts": self.parallel_thoughts,
            "ethical_assessment": self.ethical_assessment,
            "safety_check": self.safety_check,
            "reflection": self.reflection,
            "self_score": self.self_score,
            "learnings": self.learnings,
            "cost_usd": self.cost_usd,
            "tokens_used": self.tokens_used,
            "execution_time_ms": self.execution_time_ms,
            "budget_status": self.budget_status,
            "error": self.error,
            "warnings": self.warnings,
            "timestamp": self.timestamp,
            "tenant_id": self.tenant_id,
            "institution_metadata": self.institution_metadata
        }


@dataclass
class EthicalAssessment:
    """Resultado de evaluación ética"""
    overall_score: float
    recommendation: str  # APPROVE, REVIEW, REJECT
    concerns: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyResult:
    """Resultado de verificación de seguridad"""
    is_safe: bool
    safety_level: SafetyLevel
    score: float
    issues: List[str] = field(default_factory=list)
    modified_content: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# CONFIGURACIÓN MULTI-TENANT
# ============================================================================

@dataclass
class TenantConfig:
    """Configuración por tenant/institución"""
    tenant_id: str
    institution_name: str
    institution_type: str  # bank, credit_union, fintech, etc.
    country: str = "US"
    currency: str = "USD"
    timezone: str = "UTC"
    
    # Límites y presupuestos
    monthly_budget_usd: float = 100.0
    daily_limit_requests: int = 1000
    max_concurrent_agents: int = 10
    
    # Configuración de modelos
    preferred_models: List[str] = field(default_factory=lambda: ["gpt-4o-mini", "deepseek-chat"])
    fallback_models: List[str] = field(default_factory=lambda: ["gpt-3.5-turbo"])
    
    # Compliance
    regulatory_framework: List[str] = field(default_factory=lambda: ["GDPR", "SOC2"])
    data_retention_days: int = 90
    audit_required: bool = True
    
    # Features habilitados
    enabled_features: Dict[str, bool] = field(default_factory=lambda: {
        "parallel_thinking": True,
        "ethical_assessment": True,
        "safety_filter": True,
        "rl_learning": True,
        "memory_system": True
    })
    
    # Personalización
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "institution_name": self.institution_name,
            "institution_type": self.institution_type,
            "country": self.country,
            "currency": self.currency,
            "timezone": self.timezone,
            "monthly_budget_usd": self.monthly_budget_usd,
            "daily_limit_requests": self.daily_limit_requests,
            "max_concurrent_agents": self.max_concurrent_agents,
            "preferred_models": self.preferred_models,
            "fallback_models": self.fallback_models,
            "regulatory_framework": self.regulatory_framework,
            "data_retention_days": self.data_retention_days,
            "audit_required": self.audit_required,
            "enabled_features": self.enabled_features,
            "custom_config": self.custom_config
        }


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def get_default_tenant_config(tenant_id: str = "default") -> TenantConfig:
    """Retorna configuración por defecto para un tenant"""
    return TenantConfig(
        tenant_id=tenant_id,
        institution_name="Default Institution",
        institution_type="generic"
    )


def create_financial_tenant_config(
    tenant_id: str,
    institution_name: str,
    institution_type: str = "bank",
    country: str = "US"
) -> TenantConfig:
    """Crea configuración específica para instituciones financieras"""
    return TenantConfig(
        tenant_id=tenant_id,
        institution_name=institution_name,
        institution_type=institution_type,
        country=country,
        regulatory_framework=["GDPR", "SOC2", "PCI-DSS", "AML/KYC"],
        audit_required=True,
        enabled_features={
            "parallel_thinking": True,
            "ethical_assessment": True,
            "safety_filter": True,
            "rl_learning": True,
            "memory_system": True,
            "fraud_detection": True,
            "compliance_check": True
        }
    )
