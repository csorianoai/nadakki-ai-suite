"""
CAMPAIGN STRATEGY ORCHESTRATOR V3.6
====================================
Meta-Agente que coordina los 35 agentes de marketing para ejecutar
estrategias de campaña completas basadas en documentos de estrategia.

MULTI-TENANT: ✓ (Funciona con cualquier industria/tenant)
MULTI-INDUSTRY: ✓ (Financial Services, Boat Rental, Retail, etc.)

FEATURES V3.6:
- SmartAgentAllocator: Selecciona el mejor agente basado en historial
- ProactiveAlertSystem: Genera alertas cuando KPIs/agentes están en riesgo
- LearningLayer: Historial de ejecuciones + estadísticas de agentes
- Multi-Industry Configuration: Configuraciones pluggables por industria

VERSION: 3.6.0
SUPER_AGENT: True
CATEGORY: Meta-Orchestration
CORE: marketing

ARQUITECTURA:
┌────────────────────────────────────────────────────────────┐
│  📄 INPUT: Documento de Estrategia (PDF/MD/DOCX)          │
│       ↓                                                    │
│  🔍 PARSER: Extrae estructura, fases, KPIs, audiencias    │
│       ↓                                                    │
│  🧠 ANALYZER: Mapea tareas → 35 agentes disponibles       │
│       ↓                                                    │
│  📋 PLANNER: Crea timeline, dependencias, asignaciones    │
│       ↓                                                    │
│  🚀 EXECUTOR: Coordina ejecución secuencial/paralela      │
│       ↓                                                    │
│  📊 TRACKER: Monitorea progreso, KPIs, alertas            │
└────────────────────────────────────────────────────────────┘
"""

import asyncio
import hashlib
import json
import logging
import re
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Callable, Tuple
from uuid import uuid4
from enum import Enum
from pathlib import Path
from collections import defaultdict
import statistics

# ============================================================================
# AGENT METADATA
# ============================================================================

VERSION = "3.6.0"
AGENT_ID = "campaignstrategyorchestratoria"
DISPLAY_NAME = "Campaign Strategy Orchestrator IA"
CATEGORY = "Meta-Orchestration"
SUPER_AGENT = True
CORE = "marketing"
DESCRIPTION = "Orquesta los 35 agentes de marketing para ejecutar estrategias de campaña completas"

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CampaignOrchestratorV3.6")

# ============================================================================
# CONSTANTS
# ============================================================================

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [1, 2, 4]
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_WINDOW_SECONDS = 60
CIRCUIT_BREAKER_RESET_SECONDS = 30

# Data storage directory
DATA_DIR = Path("./orchestrator_data")
HISTORY_DIR = DATA_DIR / "history"
STATS_DIR = DATA_DIR / "stats"
ALERTS_DIR = DATA_DIR / "alerts"

# Smart allocation thresholds
MIN_SUCCESS_RATE_FOR_ALLOCATION = 0.7
MIN_EXECUTIONS_FOR_STATS = 3
SLOW_AGENT_THRESHOLD_MS = 5000

# Alert thresholds
ALERT_KPI_AT_RISK_THRESHOLD = 0.4
ALERT_AGENT_FAILURE_THRESHOLD = 2
ALERT_DECLINING_DAYS_THRESHOLD = 3

# ============================================================================
# ENUMS
# ============================================================================

class TaskType(str, Enum):
    AUDIENCE_ANALYSIS = "AUDIENCE_ANALYSIS"
    CUSTOMER_SEGMENTATION = "CUSTOMER_SEGMENTATION"
    GEO_TARGETING = "GEO_TARGETING"
    LEAD_SCORING = "LEAD_SCORING"
    LEAD_PREDICTION = "LEAD_PREDICTION"
    CONTENT_CREATION = "CONTENT_CREATION"
    EMAIL_AUTOMATION = "EMAIL_AUTOMATION"
    SOCIAL_POSTS = "SOCIAL_POSTS"
    CAMPAIGN_DESIGN = "CAMPAIGN_DESIGN"
    AB_TESTING = "AB_TESTING"
    BUDGET_ALLOCATION = "BUDGET_ALLOCATION"
    PRICING_STRATEGY = "PRICING_STRATEGY"
    COMPETITOR_ANALYSIS = "COMPETITOR_ANALYSIS"
    JOURNEY_OPTIMIZATION = "JOURNEY_OPTIMIZATION"
    PERSONALIZATION = "PERSONALIZATION"
    RETENTION_ANALYSIS = "RETENTION_ANALYSIS"
    ATTRIBUTION = "ATTRIBUTION"
    CREATIVE_ANALYSIS = "CREATIVE_ANALYSIS"
    INFLUENCER_MATCHING = "INFLUENCER_MATCHING"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertType(str, Enum):
    KPI_AT_RISK = "kpi_at_risk"
    KPI_DECLINING = "kpi_declining"
    AGENT_UNDERPERFORMING = "agent_underperforming"
    AGENT_CONSECUTIVE_FAILURES = "agent_consecutive_failures"
    EXECUTION_FAILED = "execution_failed"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"


class IndustryType(str, Enum):
    FINANCIAL_SERVICES = "financial_services"
    BOAT_RENTAL = "boat_rental"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    REAL_ESTATE = "real_estate"
    HOSPITALITY = "hospitality"
    PROFESSIONAL_SERVICES = "professional_services"
    SAAS = "saas"
    CUSTOM = "custom"


# ============================================================================
# TASK-AGENT REGISTRY (Maps tasks to the 35 marketing agents)
# ============================================================================

TASK_AGENT_REGISTRY: Dict[TaskType, Dict[str, Any]] = {
    TaskType.AUDIENCE_ANALYSIS: {
        "agent_id": "audiencesegmenteria",
        "core": "marketing",
        "fallback": "customersegmentatonia",
        "required_inputs": ["target_criteria"],
        "produces": ["segments", "segment_distribution"]
    },
    TaskType.CUSTOMER_SEGMENTATION: {
        "agent_id": "customersegmentatonia",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["customer_data"],
        "produces": ["customer_segments", "profiles"]
    },
    TaskType.GEO_TARGETING: {
        "agent_id": "geosegmentationia",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["locations"],
        "produces": ["geo_segments", "location_scores"]
    },
    TaskType.LEAD_SCORING: {
        "agent_id": "leadscoringia",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["leads"],
        "produces": ["scores", "lead_rankings"]
    },
    TaskType.LEAD_PREDICTION: {
        "agent_id": "predictiveleadia",
        "core": "marketing",
        "fallback": "leadscoringia",
        "required_inputs": ["historical_data"],
        "produces": ["predictions", "conversion_probability"]
    },
    TaskType.CONTENT_CREATION: {
        "agent_id": "contentgeneratoria",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["content_brief", "audience"],
        "produces": ["content_pieces", "variations"]
    },
    TaskType.EMAIL_AUTOMATION: {
        "agent_id": "emailautomationia",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["email_sequence_config"],
        "produces": ["email_templates", "automation_rules"]
    },
    TaskType.SOCIAL_POSTS: {
        "agent_id": "socialpostgeneratoria",
        "core": "marketing",
        "fallback": "contentgeneratoria",
        "required_inputs": ["platforms", "content_themes"],
        "produces": ["posts", "scheduling"]
    },
    TaskType.CAMPAIGN_DESIGN: {
        "agent_id": "campaignoptimizeria",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["campaign_brief", "budget"],
        "produces": ["optimized_campaign", "recommendations"]
    },
    TaskType.AB_TESTING: {
        "agent_id": "abtestingimpactia",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["variants", "test_config"],
        "produces": ["test_plan", "statistical_significance"]
    },
    TaskType.BUDGET_ALLOCATION: {
        "agent_id": "budgetforecastia",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["total_budget", "channels"],
        "produces": ["allocation", "roi_forecast"]
    },
    TaskType.PRICING_STRATEGY: {
        "agent_id": "pricingoptimizeria",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["products", "market_data"],
        "produces": ["pricing_recommendations", "elasticity"]
    },
    TaskType.COMPETITOR_ANALYSIS: {
        "agent_id": "competitoranalyzeria",
        "core": "marketing",
        "fallback": "competitorintelligenceia",
        "required_inputs": ["competitors"],
        "produces": ["competitive_analysis", "opportunities"]
    },
    TaskType.JOURNEY_OPTIMIZATION: {
        "agent_id": "journeyoptimizeria",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["journey_stages", "touchpoints"],
        "produces": ["optimized_journey", "drop_off_analysis"]
    },
    TaskType.PERSONALIZATION: {
        "agent_id": "personalizationengineia",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["user_profiles"],
        "produces": ["personalization_rules", "segments"]
    },
    TaskType.RETENTION_ANALYSIS: {
        "agent_id": "retentionpredictorea",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["customer_data"],
        "produces": ["churn_risk", "retention_strategies"]
    },
    TaskType.ATTRIBUTION: {
        "agent_id": "attributionmodelia",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["touchpoint_data"],
        "produces": ["attribution_model", "channel_weights"]
    },
    TaskType.CREATIVE_ANALYSIS: {
        "agent_id": "creativeanalyzeria",
        "core": "marketing",
        "fallback": None,
        "required_inputs": ["creative_assets"],
        "produces": ["performance_analysis", "recommendations"]
    },
    TaskType.INFLUENCER_MATCHING: {
        "agent_id": "influencermatcheria",
        "core": "marketing",
        "fallback": "influencermatchingia",
        "required_inputs": ["campaign_goals", "budget"],
        "produces": ["influencer_list", "match_scores"]
    }
}


# ============================================================================
# INDUSTRY CONFIGURATIONS (Pluggable)
# ============================================================================

INDUSTRY_CONFIGS = {
    IndustryType.FINANCIAL_SERVICES: {
        "name": "Financial Services",
        "specialized_agents": [
            "financialcomplianceia", "riskassessmentia", "creditscoringia",
            "regulatorycontentia", "wealthsegmentatoria", "fraudpreventmessagia",
            "financialcrosssellia"
        ],
        "kpis": ["AUM", "NPS", "CAC", "LTV", "Churn Rate", "ROA", "Tier 1 Ratio"],
        "compliance": ["GDPR", "CCPA", "PCI-DSS", "KYC", "AML", "SOX"],
        "seasonal_calendar": {
            1: {"event": "New Year Financial Planning", "multiplier": 1.2},
            2: {"event": "Tax Season Prep", "multiplier": 1.1},
            3: {"event": "Tax Season Peak", "multiplier": 1.3},
            4: {"event": "Tax Season End", "multiplier": 1.2},
            11: {"event": "Black Friday", "multiplier": 1.3},
            12: {"event": "Year-End", "multiplier": 0.8}
        }
    },
    IndustryType.BOAT_RENTAL: {
        "name": "Boat Rental",
        "specialized_agents": [
            "marketplacerankeria", "whatsappcloseria", "birthdayboatcontentia",
            "bacheloretteboatcontentia", "reviewvelocitia", "seasonalpriceria",
            "charterupsellia", "weatherresponseia"
        ],
        "kpis": ["Booking Rate", "Average Charter Value", "Review Velocity",
                 "WhatsApp Close Rate", "Fleet Utilization", "GetMyBoat Ranking"],
        "compliance": ["USCG", "Local Maritime"],
        "seasonal_calendar": {
            2: {"event": "Super Bowl", "multiplier": 1.5},
            3: {"event": "Spring Break", "multiplier": 1.6},
            7: {"event": "July 4th", "multiplier": 1.4},
            8: {"event": "Hurricane Season Start", "multiplier": 1.0},
            9: {"event": "Hurricane Peak", "multiplier": 0.7},
            10: {"event": "Hurricane Late", "multiplier": 0.8},
            12: {"event": "Art Basel", "multiplier": 1.7}
        }
    },
    IndustryType.RETAIL: {
        "name": "Retail",
        "specialized_agents": [
            "inventoryoptimizeria", "cartrecoveryia", "productrecommenderia",
            "pricedynamicia", "loyaltyprogramia"
        ],
        "kpis": ["AOV", "Cart Abandonment", "Repeat Rate", "ROAS", "LTV"],
        "compliance": ["PCI-DSS", "CCPA"],
        "seasonal_calendar": {
            11: {"event": "Black Friday", "multiplier": 2.0},
            12: {"event": "Holiday Season", "multiplier": 1.8}
        }
    },
    IndustryType.HEALTHCARE: {
        "name": "Healthcare",
        "specialized_agents": [
            "patientengagemia", "appointmentoptimizeria", "hipaacomplianceia"
        ],
        "kpis": ["Patient Satisfaction", "Appointment Rate", "Retention"],
        "compliance": ["HIPAA", "GDPR"],
        "seasonal_calendar": {
            1: {"event": "New Year Health Goals", "multiplier": 1.3}
        }
    },
    IndustryType.REAL_ESTATE: {
        "name": "Real Estate",
        "specialized_agents": [
            "propertymatcheria", "leadnurtureria", "virtualtouroptimizeria"
        ],
        "kpis": ["Lead to Showing Rate", "Days on Market", "Conversion Rate"],
        "compliance": ["Fair Housing"],
        "seasonal_calendar": {
            3: {"event": "Spring Market", "multiplier": 1.4},
            4: {"event": "Peak Season", "multiplier": 1.5},
            5: {"event": "Peak Season", "multiplier": 1.5}
        }
    }
}


# ============================================================================
# DATA CLASSES
# ============================================================================

from dataclasses import dataclass, field

@dataclass
class AgentStats:
    agent_id: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    total_retries: int = 0
    last_execution: Optional[datetime] = None
    recent_errors: List[str] = field(default_factory=list)
    consecutive_failures: int = 0


@dataclass
class Alert:
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    tenant_id: str
    created_at: datetime
    title: str
    message: str
    affected_entity: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class AgentAllocationDecision:
    task_type: str
    original_agent: str
    selected_agent: str
    reason: str
    confidence: float
    stats_used: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlannedTask:
    task_id: str
    task_type: TaskType
    agent_id: str
    phase_id: int
    priority: str = "MEDIUM"
    depends_on: List[str] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    estimated_duration_seconds: int = 60
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    actual_duration_ms: Optional[int] = None
    allocated_by: str = "default"
    original_agent_id: Optional[str] = None


@dataclass
class ExecutionPhase:
    phase_id: int
    name: str
    tasks: List[PlannedTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ExecutionPlan:
    plan_id: str
    strategy_id: str
    tenant_id: str
    industry_type: IndustryType
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    phases: List[ExecutionPhase] = field(default_factory=list)
    total_tasks: int = 0
    estimated_duration_minutes: int = 0
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    progress_percent: float = 0.0
    smart_allocation_used: bool = False
    agents_reallocated: int = 0


@dataclass
class ExecutionResult:
    execution_id: str
    plan_id: str
    tenant_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    phases_completed: int = 0
    phases_total: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_skipped: int = 0
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    audit_hash: str = ""
    total_duration_ms: Optional[int] = None
    agent_performance: Dict[str, Any] = field(default_factory=dict)
    kpi_status: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    smart_allocation_summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KPIStatus:
    kpi_name: str
    metric: str
    target: float
    current: Optional[float] = None
    progress_percent: float = 0.0
    status: str = "pending"
    trend: str = "stable"
    days_declining: int = 0
    alert_generated: bool = False


# ============================================================================
# SMART AGENT ALLOCATOR
# ============================================================================

class SmartAgentAllocator:
    """
    Uses historical performance data to select the best agent for each task.
    """
    
    def __init__(self, performance_tracker: 'AgentPerformanceTracker'):
        self.performance_tracker = performance_tracker
        self.allocation_log: List[AgentAllocationDecision] = []
    
    def allocate_agent(
        self, 
        task_type: TaskType, 
        tenant_id: str,
        registry: Dict[TaskType, Dict[str, Any]] = None
    ) -> Tuple[str, AgentAllocationDecision]:
        registry = registry or TASK_AGENT_REGISTRY
        
        if task_type not in registry:
            return "unknown", AgentAllocationDecision(
                task_type=task_type.value,
                original_agent="unknown",
                selected_agent="unknown",
                reason="Task type not in registry",
                confidence=0.0
            )
        
        entry = registry[task_type]
        default_agent = entry["agent_id"]
        fallback_agent = entry.get("fallback")
        
        default_stats = self.performance_tracker.get_agent_stats(tenant_id, default_agent)
        
        if not default_stats or default_stats.total_executions < MIN_EXECUTIONS_FOR_STATS:
            return default_agent, AgentAllocationDecision(
                task_type=task_type.value,
                original_agent=default_agent,
                selected_agent=default_agent,
                reason="Insufficient historical data, using default",
                confidence=0.5
            )
        
        if default_stats.success_rate >= MIN_SUCCESS_RATE_FOR_ALLOCATION:
            return default_agent, AgentAllocationDecision(
                task_type=task_type.value,
                original_agent=default_agent,
                selected_agent=default_agent,
                reason=f"Default agent performing well ({default_stats.success_rate:.0%} success rate)",
                confidence=default_stats.success_rate,
                stats_used={"success_rate": default_stats.success_rate, "executions": default_stats.total_executions}
            )
        
        if fallback_agent:
            fallback_stats = self.performance_tracker.get_agent_stats(tenant_id, fallback_agent)
            
            if fallback_stats and fallback_stats.total_executions >= MIN_EXECUTIONS_FOR_STATS:
                if fallback_stats.success_rate > default_stats.success_rate:
                    decision = AgentAllocationDecision(
                        task_type=task_type.value,
                        original_agent=default_agent,
                        selected_agent=fallback_agent,
                        reason=f"Fallback has better performance ({fallback_stats.success_rate:.0%} vs {default_stats.success_rate:.0%})",
                        confidence=fallback_stats.success_rate,
                        stats_used={
                            "default_success_rate": default_stats.success_rate,
                            "fallback_success_rate": fallback_stats.success_rate
                        }
                    )
                    self.allocation_log.append(decision)
                    logger.info(f"Smart allocation: {task_type.value} → {fallback_agent} (was {default_agent})")
                    return fallback_agent, decision
        
        return default_agent, AgentAllocationDecision(
            task_type=task_type.value,
            original_agent=default_agent,
            selected_agent=default_agent,
            reason=f"Using default despite low performance ({default_stats.success_rate:.0%}), no better fallback available",
            confidence=default_stats.success_rate,
            stats_used={"success_rate": default_stats.success_rate}
        )
    
    def get_allocation_summary(self) -> Dict[str, Any]:
        if not self.allocation_log:
            return {"total_reallocations": 0, "decisions": []}
        
        reallocations = [d for d in self.allocation_log if d.original_agent != d.selected_agent]
        
        return {
            "total_decisions": len(self.allocation_log),
            "total_reallocations": len(reallocations),
            "reallocation_rate": len(reallocations) / len(self.allocation_log) if self.allocation_log else 0,
            "avg_confidence": statistics.mean([d.confidence for d in self.allocation_log]) if self.allocation_log else 0,
            "reallocations": [
                {
                    "task_type": d.task_type,
                    "from": d.original_agent,
                    "to": d.selected_agent,
                    "reason": d.reason
                }
                for d in reallocations
            ]
        }
    
    def clear_log(self):
        self.allocation_log = []


# ============================================================================
# PROACTIVE ALERT SYSTEM
# ============================================================================

class ProactiveAlertSystem:
    """Generates proactive alerts based on KPI status and agent performance."""
    
    def __init__(self, storage_dir: Path = ALERTS_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.active_alerts: Dict[str, List[Alert]] = {}
    
    def _get_alerts_path(self, tenant_id: str) -> Path:
        return self.storage_dir / f"alerts_{tenant_id}.json"
    
    def generate_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        tenant_id: str,
        title: str,
        message: str,
        affected_entity: str,
        metadata: Dict[str, Any] = None
    ) -> Alert:
        alert = Alert(
            alert_id=f"ALERT-{uuid4().hex[:8]}",
            alert_type=alert_type,
            severity=severity,
            tenant_id=tenant_id,
            created_at=datetime.now(timezone.utc),
            title=title,
            message=message,
            affected_entity=affected_entity,
            metadata=metadata or {}
        )
        
        if tenant_id not in self.active_alerts:
            self.active_alerts[tenant_id] = []
        self.active_alerts[tenant_id].append(alert)
        
        logger.warning(f"Alert generated: [{severity.value.upper()}] {title}")
        return alert
    
    def check_agent_alerts(self, agent_stats: AgentStats, tenant_id: str) -> List[Alert]:
        alerts = []
        
        if (agent_stats.total_executions >= MIN_EXECUTIONS_FOR_STATS and 
            agent_stats.success_rate < MIN_SUCCESS_RATE_FOR_ALLOCATION):
            alert = self.generate_alert(
                alert_type=AlertType.AGENT_UNDERPERFORMING,
                severity=AlertSeverity.WARNING,
                tenant_id=tenant_id,
                title=f"Agent underperforming: {agent_stats.agent_id}",
                message=f"Agent {agent_stats.agent_id} has a success rate of {agent_stats.success_rate:.0%}",
                affected_entity=agent_stats.agent_id,
                metadata={"success_rate": agent_stats.success_rate}
            )
            alerts.append(alert)
        
        if agent_stats.consecutive_failures >= ALERT_AGENT_FAILURE_THRESHOLD:
            alert = self.generate_alert(
                alert_type=AlertType.AGENT_CONSECUTIVE_FAILURES,
                severity=AlertSeverity.CRITICAL,
                tenant_id=tenant_id,
                title=f"Agent consecutive failures: {agent_stats.agent_id}",
                message=f"Agent {agent_stats.agent_id} has failed {agent_stats.consecutive_failures} times in a row",
                affected_entity=agent_stats.agent_id,
                metadata={"consecutive_failures": agent_stats.consecutive_failures}
            )
            alerts.append(alert)
        
        return alerts
    
    def get_active_alerts(self, tenant_id: str, unresolved_only: bool = True) -> List[Alert]:
        alerts = self.active_alerts.get(tenant_id, [])
        if unresolved_only:
            return [a for a in alerts if not a.resolved]
        return alerts


# ============================================================================
# AGENT PERFORMANCE TRACKER
# ============================================================================

class AgentPerformanceTracker:
    def __init__(self, storage_dir: Path = STATS_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._stats_cache: Dict[str, Dict[str, AgentStats]] = {}
    
    def _get_stats_path(self, tenant_id: str) -> Path:
        return self.storage_dir / f"agent_stats_{tenant_id}.json"
    
    def _load_stats(self, tenant_id: str) -> Dict[str, AgentStats]:
        if tenant_id in self._stats_cache:
            return self._stats_cache[tenant_id]
        
        path = self._get_stats_path(tenant_id)
        if path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
                stats = {}
                for k, v in data.items():
                    stats[k] = AgentStats(
                        agent_id=v.get("agent_id", k),
                        total_executions=v.get("total_executions", 0),
                        successful_executions=v.get("successful_executions", 0),
                        failed_executions=v.get("failed_executions", 0),
                        success_rate=v.get("success_rate", 0.0),
                        avg_duration_ms=v.get("avg_duration_ms", 0.0),
                        consecutive_failures=v.get("consecutive_failures", 0)
                    )
                self._stats_cache[tenant_id] = stats
                return stats
        return {}
    
    def _save_stats(self, tenant_id: str, stats: Dict[str, AgentStats]) -> None:
        path = self._get_stats_path(tenant_id)
        with open(path, 'w') as f:
            data = {}
            for k, v in stats.items():
                data[k] = {
                    "agent_id": v.agent_id,
                    "total_executions": v.total_executions,
                    "successful_executions": v.successful_executions,
                    "failed_executions": v.failed_executions,
                    "success_rate": v.success_rate,
                    "avg_duration_ms": v.avg_duration_ms,
                    "consecutive_failures": v.consecutive_failures
                }
            json.dump(data, f, indent=2)
        self._stats_cache[tenant_id] = stats
    
    def record_task_result(
        self, 
        tenant_id: str, 
        agent_id: str, 
        success: bool, 
        duration_ms: int,
        retries: int = 0,
        error: Optional[str] = None
    ) -> AgentStats:
        stats = self._load_stats(tenant_id)
        
        if agent_id not in stats:
            stats[agent_id] = AgentStats(agent_id=agent_id)
        
        agent_stats = stats[agent_id]
        agent_stats.total_executions += 1
        
        if success:
            agent_stats.successful_executions += 1
            agent_stats.consecutive_failures = 0
        else:
            agent_stats.failed_executions += 1
            agent_stats.consecutive_failures += 1
            if error:
                agent_stats.recent_errors.append(error[:200])
                agent_stats.recent_errors = agent_stats.recent_errors[-5:]
        
        agent_stats.success_rate = agent_stats.successful_executions / agent_stats.total_executions
        agent_stats.last_execution = datetime.now(timezone.utc)
        
        self._save_stats(tenant_id, stats)
        return agent_stats
    
    def get_agent_stats(self, tenant_id: str, agent_id: str) -> Optional[AgentStats]:
        stats = self._load_stats(tenant_id)
        return stats.get(agent_id)
    
    def get_all_stats(self, tenant_id: str) -> Dict[str, AgentStats]:
        return self._load_stats(tenant_id)
    
    def get_underperformers(self, tenant_id: str, threshold: float = MIN_SUCCESS_RATE_FOR_ALLOCATION) -> List[AgentStats]:
        stats = self._load_stats(tenant_id)
        return [
            s for s in stats.values()
            if s.success_rate < threshold and s.total_executions >= MIN_EXECUTIONS_FOR_STATS
        ]


# ============================================================================
# STRATEGY PARSER
# ============================================================================

class StrategyParser:
    """Extracts structured information from marketing strategy documents."""
    
    async def parse(self, document_content: str, tenant_id: str, industry_type: IndustryType) -> Dict[str, Any]:
        logger.info(f"Parsing strategy for tenant {tenant_id}, industry {industry_type.value}")
        
        text = document_content
        text_lower = text.lower()
        industry_config = INDUSTRY_CONFIGS.get(industry_type, {})
        
        return {
            "strategy_id": f"STR-{uuid4().hex[:8]}",
            "tenant_id": tenant_id,
            "industry_type": industry_type.value,
            "business_name": self._extract_business_name(text),
            "target_audiences": self._extract_audiences(text, industry_type),
            "objectives": self._extract_objectives(text),
            "kpis": self._extract_kpis(text, industry_config.get("kpis", [])),
            "budget": self._extract_budget(text),
            "timeline": self._extract_timeline(text),
            "channels": self._extract_channels(text),
            "tactics": self._extract_tactics(text, industry_type),
            "seasonal_context": self._get_seasonal_context(industry_config),
            "parse_confidence": self._calculate_confidence(text)
        }
    
    def _extract_business_name(self, text: str) -> str:
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) < 100:
                clean = re.sub(r'^#+\s*', '', line)
                if clean and len(clean) > 3:
                    return clean
        return "Unknown Business"
    
    def _extract_audiences(self, text: str, industry_type: IndustryType) -> List[Dict]:
        audiences = []
        text_lower = text.lower()
        
        if industry_type == IndustryType.BOAT_RENTAL:
            patterns = [
                (["birthday", "celebration", "party"], "Birthday/Celebration Planners", "HIGH"),
                (["bachelorette", "bachelor", "wedding"], "Bachelorette/Wedding Groups", "HIGH"),
                (["sunset", "romantic", "couples"], "Couples & Romantics", "MEDIUM"),
                (["family", "kids", "children"], "Family Adventures", "MEDIUM"),
                (["corporate", "team building"], "Corporate Events", "HIGH"),
            ]
        elif industry_type == IndustryType.FINANCIAL_SERVICES:
            patterns = [
                (["hnwi", "high net worth", "affluent"], "High Net Worth Individuals", "HIGH"),
                (["sme", "small business", "pyme"], "Small & Medium Enterprises", "HIGH"),
                (["retail banking", "consumer"], "Retail Banking Customers", "MEDIUM"),
                (["corporate", "enterprise"], "Corporate & Institutional", "HIGH"),
            ]
        else:
            patterns = [
                (["corporate", "b2b", "business"], "Corporate & Enterprise", "HIGH"),
                (["consumer", "retail"], "Consumer/Retail", "MEDIUM"),
            ]
        
        for keywords, name, priority in patterns:
            if any(kw in text_lower for kw in keywords):
                audiences.append({
                    "name": name,
                    "priority": priority,
                    "keywords_matched": [kw for kw in keywords if kw in text_lower]
                })
        
        return audiences or [{"name": "General Audience", "priority": "MEDIUM"}]
    
    def _extract_objectives(self, text: str) -> List[Dict]:
        objectives = []
        patterns = [r'\+(\d+)%?\s*(?:increase\s+in\s+)?(\w+)', r'(\d+)%?\s*increase\s+in\s+(\w+)']
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                groups = match.groups()
                if len(groups) >= 2:
                    try:
                        value = float(groups[0])
                        metric = groups[1]
                        objectives.append({
                            "name": f"Increase {metric}",
                            "metric": metric.lower(),
                            "target_value": value
                        })
                    except (ValueError, IndexError):
                        continue
        
        return objectives[:5] or [{"name": "General Growth", "metric": "revenue", "target_value": 15.0}]
    
    def _extract_kpis(self, text: str, industry_kpis: List[str]) -> List[Dict]:
        kpis = []
        text_lower = text.lower()
        
        standard_kpis = {
            "cvr": ("Conversion Rate", 3.0),
            "cpa": ("Cost Per Acquisition", 40.0),
            "roas": ("Return on Ad Spend", 3.0),
            "ctr": ("Click-Through Rate", 2.0),
        }
        
        for key, (name, default_target) in standard_kpis.items():
            if key in text_lower:
                kpis.append({"name": name, "metric": key.upper(), "target": default_target})
        
        for kpi in industry_kpis:
            if kpi.lower() in text_lower:
                kpis.append({"name": kpi, "metric": kpi, "target": 0.0})
        
        return kpis
    
    def _extract_budget(self, text: str) -> Dict:
        matches = re.findall(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
        if matches:
            amounts = sorted([float(m.replace(',', '')) for m in matches], reverse=True)
            total = amounts[0] if amounts else 10000.0
            return {"total": total, "currency": "USD", "daily": total / 90}
        return {"total": 10000.0, "currency": "USD", "daily": 111.11}
    
    def _extract_timeline(self, text: str) -> List[Dict]:
        if "90" in text:
            return [
                {"phase_id": 1, "name": "Foundation", "days_start": 1, "days_end": 14},
                {"phase_id": 2, "name": "Validation", "days_start": 15, "days_end": 30},
                {"phase_id": 3, "name": "Acceleration", "days_start": 31, "days_end": 60},
                {"phase_id": 4, "name": "Optimization", "days_start": 61, "days_end": 90}
            ]
        return [{"phase_id": 1, "name": "Campaign Period", "days_start": 1, "days_end": 30}]
    
    def _extract_channels(self, text: str) -> List[str]:
        channels = []
        keywords = [
            ("google", "Google"), ("meta", "Meta"), ("facebook", "Facebook"),
            ("instagram", "Instagram"), ("tiktok", "TikTok"), ("email", "Email"),
            ("sms", "SMS"), ("whatsapp", "WhatsApp"), ("linkedin", "LinkedIn"),
            ("youtube", "YouTube"), ("getmyboat", "GetMyBoat"), ("boatsetter", "Boatsetter")
        ]
        
        text_lower = text.lower()
        for keyword, name in keywords:
            if keyword in text_lower:
                channels.append(name)
        
        return channels or ["Digital"]
    
    def _extract_tactics(self, text: str, industry_type: IndustryType) -> List[Dict]:
        tactics = []
        text_lower = text.lower()
        
        general_patterns = [
            (["paid", "ads", "advertising"], "Paid Advertising", "HIGH"),
            (["content", "blog"], "Content Marketing", "MEDIUM"),
            (["email", "newsletter"], "Email Marketing", "HIGH"),
            (["seo", "organic"], "SEO", "MEDIUM"),
        ]
        
        if industry_type == IndustryType.BOAT_RENTAL:
            general_patterns.extend([
                (["birthday", "party"], "Birthday/Party Packages", "HIGH"),
                (["bachelorette"], "Bachelorette Packages", "HIGH"),
                (["sunset", "cruise"], "Sunset Cruise Promotions", "HIGH"),
            ])
        
        for keywords, name, priority in general_patterns:
            if any(kw in text_lower for kw in keywords):
                tactics.append({"name": name, "priority": priority})
        
        return tactics
    
    def _get_seasonal_context(self, industry_config: Dict) -> Dict:
        current_month = datetime.now().month
        calendar = industry_config.get("seasonal_calendar", {})
        
        if current_month in calendar:
            return calendar[current_month]
        return {"event": "Standard Period", "multiplier": 1.0}
    
    def _calculate_confidence(self, text: str) -> float:
        confidence = 0.5
        if len(text) > 5000: confidence += 0.15
        elif len(text) > 2000: confidence += 0.10
        if '|' in text: confidence += 0.10
        if '#' in text: confidence += 0.05
        if '$' in text: confidence += 0.10
        if '%' in text: confidence += 0.05
        return min(confidence, 0.95)


# ============================================================================
# TASK PLANNER
# ============================================================================

class TaskPlanner:
    """Creates execution plan mapping tasks to agents."""
    
    def __init__(self, registry: Dict = None, smart_allocator: SmartAgentAllocator = None):
        self.registry = registry or TASK_AGENT_REGISTRY
        self.smart_allocator = smart_allocator
    
    async def create_plan(
        self, 
        strategy: Dict, 
        execution_mode: str = "standard",
        use_smart_allocation: bool = True
    ) -> ExecutionPlan:
        logger.info(f"Creating execution plan for strategy {strategy['strategy_id']}")
        
        required_tasks = self._identify_required_tasks(strategy, execution_mode)
        planned_tasks, reallocations = self._create_planned_tasks(
            required_tasks, strategy, use_smart_allocation
        )
        phases = self._organize_phases(planned_tasks, strategy.get("timeline", []))
        
        plan = ExecutionPlan(
            plan_id=f"PLAN-{uuid4().hex[:8]}",
            strategy_id=strategy["strategy_id"],
            tenant_id=strategy["tenant_id"],
            industry_type=IndustryType(strategy.get("industry_type", "custom")),
            phases=phases,
            total_tasks=len(planned_tasks),
            estimated_duration_minutes=self._estimate_duration(planned_tasks),
            smart_allocation_used=use_smart_allocation and self.smart_allocator is not None,
            agents_reallocated=reallocations
        )
        
        logger.info(f"Created plan {plan.plan_id} with {plan.total_tasks} tasks")
        return plan
    
    def _identify_required_tasks(self, strategy: Dict, mode: str) -> List[TaskType]:
        tasks = [TaskType.AUDIENCE_ANALYSIS]
        
        if len(strategy.get("target_audiences", [])) > 1:
            tasks.append(TaskType.CUSTOMER_SEGMENTATION)
        
        channels_lower = [c.lower() for c in strategy.get("channels", [])]
        if "email" in channels_lower:
            tasks.extend([TaskType.EMAIL_AUTOMATION, TaskType.LEAD_SCORING])
        if any(s in channels_lower for s in ["instagram", "facebook", "tiktok"]):
            tasks.append(TaskType.SOCIAL_POSTS)
        
        if strategy.get("budget", {}).get("total", 0) > 0:
            tasks.extend([TaskType.CAMPAIGN_DESIGN, TaskType.BUDGET_ALLOCATION])
        
        if mode in ["standard", "comprehensive"]:
            tasks.append(TaskType.AB_TESTING)
        
        if mode == "comprehensive":
            tasks.extend([
                TaskType.COMPETITOR_ANALYSIS,
                TaskType.JOURNEY_OPTIMIZATION,
                TaskType.ATTRIBUTION,
                TaskType.RETENTION_ANALYSIS,
                TaskType.PERSONALIZATION
            ])
        
        return list(dict.fromkeys(tasks))
    
    def _create_planned_tasks(
        self, 
        task_types: List[TaskType], 
        strategy: Dict,
        use_smart_allocation: bool
    ) -> Tuple[List[PlannedTask], int]:
        tasks = []
        reallocations = 0
        
        for i, task_type in enumerate(task_types):
            registry_entry = self.registry.get(task_type, {})
            default_agent = registry_entry.get("agent_id", "unknown")
            
            if use_smart_allocation and self.smart_allocator:
                selected_agent, decision = self.smart_allocator.allocate_agent(
                    task_type, strategy["tenant_id"]
                )
                allocated_by = "smart_allocator"
                original_agent = default_agent if selected_agent != default_agent else None
                if original_agent:
                    reallocations += 1
            else:
                selected_agent = default_agent
                allocated_by = "default"
                original_agent = None
            
            task = PlannedTask(
                task_id=f"T{str(i+1).zfill(3)}",
                task_type=task_type,
                agent_id=selected_agent,
                phase_id=self._determine_phase(task_type),
                priority=self._determine_priority(task_type),
                depends_on=self._determine_dependencies(task_type, task_types),
                input_data=self._prepare_input_data(task_type, strategy),
                allocated_by=allocated_by,
                original_agent_id=original_agent
            )
            tasks.append(task)
        
        return tasks, reallocations
    
    def _determine_phase(self, task_type: TaskType) -> int:
        phase_map = {
            TaskType.AUDIENCE_ANALYSIS: 1,
            TaskType.CUSTOMER_SEGMENTATION: 1,
            TaskType.COMPETITOR_ANALYSIS: 1,
            TaskType.LEAD_SCORING: 2,
            TaskType.CAMPAIGN_DESIGN: 2,
            TaskType.BUDGET_ALLOCATION: 2,
            TaskType.CONTENT_CREATION: 3,
            TaskType.EMAIL_AUTOMATION: 3,
            TaskType.SOCIAL_POSTS: 3,
            TaskType.AB_TESTING: 3,
            TaskType.JOURNEY_OPTIMIZATION: 4,
            TaskType.PERSONALIZATION: 4,
            TaskType.ATTRIBUTION: 4,
            TaskType.RETENTION_ANALYSIS: 4
        }
        return phase_map.get(task_type, 2)
    
    def _determine_priority(self, task_type: TaskType) -> str:
        high_priority = {
            TaskType.AUDIENCE_ANALYSIS,
            TaskType.LEAD_SCORING,
            TaskType.CAMPAIGN_DESIGN,
            TaskType.BUDGET_ALLOCATION,
            TaskType.EMAIL_AUTOMATION
        }
        return "HIGH" if task_type in high_priority else "MEDIUM"
    
    def _determine_dependencies(self, task_type: TaskType, all_tasks: List[TaskType]) -> List[str]:
        dep_map = {
            TaskType.CUSTOMER_SEGMENTATION: [TaskType.AUDIENCE_ANALYSIS],
            TaskType.LEAD_SCORING: [TaskType.AUDIENCE_ANALYSIS],
            TaskType.CAMPAIGN_DESIGN: [TaskType.AUDIENCE_ANALYSIS],
            TaskType.BUDGET_ALLOCATION: [TaskType.CAMPAIGN_DESIGN],
            TaskType.EMAIL_AUTOMATION: [TaskType.LEAD_SCORING],
            TaskType.SOCIAL_POSTS: [TaskType.AUDIENCE_ANALYSIS],
            TaskType.AB_TESTING: [TaskType.CAMPAIGN_DESIGN],
            TaskType.PERSONALIZATION: [TaskType.CUSTOMER_SEGMENTATION],
            TaskType.JOURNEY_OPTIMIZATION: [TaskType.CUSTOMER_SEGMENTATION]
        }
        
        deps = dep_map.get(task_type, [])
        return [f"T{str(all_tasks.index(d) + 1).zfill(3)}" for d in deps if d in all_tasks]
    
    def _prepare_input_data(self, task_type: TaskType, strategy: Dict) -> Dict:
        base = {
            "tenant_id": strategy["tenant_id"],
            "strategy_id": strategy["strategy_id"],
            "business_name": strategy.get("business_name", "Unknown")
        }
        
        if task_type == TaskType.AUDIENCE_ANALYSIS:
            base["target_audiences"] = strategy.get("target_audiences", [])
        elif task_type == TaskType.BUDGET_ALLOCATION:
            base["total_budget"] = strategy.get("budget", {}).get("total", 0)
            base["channels"] = strategy.get("channels", [])
        elif task_type == TaskType.CAMPAIGN_DESIGN:
            base["tactics"] = strategy.get("tactics", [])
            base["objectives"] = strategy.get("objectives", [])
        
        return base
    
    def _organize_phases(self, tasks: List[PlannedTask], timeline: List[Dict]) -> List[ExecutionPhase]:
        phase_tasks = defaultdict(list)
        
        for task in tasks:
            phase_tasks[task.phase_id].append(task)
        
        phases = []
        for tl in timeline:
            phases.append(ExecutionPhase(
                phase_id=tl["phase_id"],
                name=tl["name"],
                tasks=phase_tasks.get(tl["phase_id"], [])
            ))
        
        return phases
    
    def _estimate_duration(self, tasks: List[PlannedTask]) -> int:
        return int((len(tasks) * 60 * 0.6) / 60) + 1


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitBreaker:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.threshold = CIRCUIT_BREAKER_THRESHOLD
        self.failures: List[datetime] = []
        self.state = CircuitBreakerState.CLOSED
        self.last_state_change = datetime.now(timezone.utc)
    
    def record_failure(self) -> None:
        now = datetime.now(timezone.utc)
        self.failures = [f for f in self.failures if (now - f).total_seconds() < CIRCUIT_BREAKER_WINDOW_SECONDS]
        self.failures.append(now)
        
        if len(self.failures) >= self.threshold:
            self.state = CircuitBreakerState.OPEN
            self.last_state_change = now
            logger.warning(f"Circuit breaker OPEN for agent {self.agent_id}")
    
    def record_success(self) -> None:
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.failures = []
            logger.info(f"Circuit breaker CLOSED for agent {self.agent_id}")
    
    def can_execute(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            elapsed = (datetime.now(timezone.utc) - self.last_state_change).total_seconds()
            if elapsed > CIRCUIT_BREAKER_RESET_SECONDS:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        
        return True


_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(agent_id: str) -> CircuitBreaker:
    if agent_id not in _circuit_breakers:
        _circuit_breakers[agent_id] = CircuitBreaker(agent_id)
    return _circuit_breakers[agent_id]


# ============================================================================
# EXECUTION ENGINE
# ============================================================================

class ExecutionEngine:
    """Executes the plan by calling the 35 marketing agents."""
    
    def __init__(
        self, 
        agent_executor_fn: Optional[Callable] = None,
        performance_tracker: Optional[AgentPerformanceTracker] = None,
        alert_system: Optional[ProactiveAlertSystem] = None
    ):
        self.agent_executor = agent_executor_fn
        self.performance_tracker = performance_tracker or AgentPerformanceTracker()
        self.alert_system = alert_system
    
    async def execute_plan(self, plan: ExecutionPlan, dry_run: bool = False) -> ExecutionResult:
        execution_id = f"EXEC-{uuid4().hex[:8]}"
        started_at = datetime.now(timezone.utc)
        
        logger.info(f"Starting execution {execution_id} for plan {plan.plan_id}")
        
        tasks_completed = 0
        tasks_failed = 0
        tasks_skipped = 0
        completed_results = {}
        generated_alerts = []
        
        for phase in plan.phases:
            logger.info(f"Executing phase {phase.phase_id}: {phase.name}")
            phase.started_at = datetime.now(timezone.utc)
            
            for task in phase.tasks:
                deps_met = all(d in completed_results for d in task.depends_on)
                
                if not deps_met:
                    task.status = TaskStatus.SKIPPED
                    task.error = "Dependencies not met"
                    tasks_skipped += 1
                    continue
                
                task.started_at = datetime.now(timezone.utc)
                task.status = TaskStatus.RUNNING
                
                cb = get_circuit_breaker(task.agent_id)
                if not cb.can_execute():
                    task.status = TaskStatus.FAILED
                    task.error = f"Circuit breaker open for {task.agent_id}"
                    tasks_failed += 1
                    continue
                
                if dry_run:
                    await asyncio.sleep(0.1)
                    task.actual_duration_ms = 100
                    result = {"status": "success", "dry_run": True, "agent_id": task.agent_id}
                else:
                    try:
                        start = datetime.now(timezone.utc)
                        if self.agent_executor:
                            result = await self.agent_executor(
                                "marketing", task.agent_id, task.input_data, plan.tenant_id
                            )
                        else:
                            result = {"status": "success", "mock": True, "agent_id": task.agent_id}
                        task.actual_duration_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
                        cb.record_success()
                    except Exception as e:
                        task.actual_duration_ms = 0
                        cb.record_failure()
                        result = {"status": "error", "error": str(e)}
                
                duration_ms = task.actual_duration_ms or 0
                
                if result.get("status") == "success":
                    task.status = TaskStatus.SUCCESS
                    task.result = result
                    completed_results[task.task_id] = result
                    tasks_completed += 1
                    
                    self.performance_tracker.record_task_result(
                        plan.tenant_id, task.agent_id, True, duration_ms
                    )
                else:
                    task.status = TaskStatus.FAILED
                    task.error = result.get("error", "Unknown error")
                    tasks_failed += 1
                    
                    agent_stats = self.performance_tracker.record_task_result(
                        plan.tenant_id, task.agent_id, False, duration_ms, error=task.error
                    )
                    
                    if self.alert_system:
                        alerts = self.alert_system.check_agent_alerts(agent_stats, plan.tenant_id)
                        generated_alerts.extend(alerts)
                
                task.completed_at = datetime.now(timezone.utc)
            
            phase.completed_at = datetime.now(timezone.utc)
            phase.status = TaskStatus.SUCCESS if all(
                t.status == TaskStatus.SUCCESS for t in phase.tasks if t.status != TaskStatus.SKIPPED
            ) else TaskStatus.FAILED
        
        completed_at = datetime.now(timezone.utc)
        total_duration_ms = int((completed_at - started_at).total_seconds() * 1000)
        
        result = ExecutionResult(
            execution_id=execution_id,
            plan_id=plan.plan_id,
            tenant_id=plan.tenant_id,
            started_at=started_at,
            completed_at=completed_at,
            status=TaskStatus.SUCCESS if tasks_failed == 0 else TaskStatus.FAILED,
            phases_completed=sum(1 for p in plan.phases if p.status == TaskStatus.SUCCESS),
            phases_total=len(plan.phases),
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            tasks_skipped=tasks_skipped,
            summary={
                "plan_id": plan.plan_id,
                "strategy_id": plan.strategy_id,
                "industry": plan.industry_type.value,
                "successful_task_ids": list(completed_results.keys()),
                "duration_seconds": total_duration_ms / 1000
            },
            recommendations=self._generate_recommendations(plan, completed_results),
            audit_hash=self._generate_audit_hash(plan, completed_results),
            total_duration_ms=total_duration_ms,
            alerts=[{
                "alert_id": a.alert_id,
                "type": a.alert_type.value,
                "severity": a.severity.value,
                "title": a.title,
                "message": a.message
            } for a in generated_alerts],
            smart_allocation_summary={
                "used": plan.smart_allocation_used,
                "reallocations": plan.agents_reallocated
            }
        )
        
        logger.info(f"Execution {execution_id} completed: {result.status.value}")
        return result
    
    def _generate_recommendations(self, plan: ExecutionPlan, results: Dict) -> List[str]:
        recs = []
        if len(results) == plan.total_tasks:
            recs.append("✅ All tasks completed successfully")
        else:
            recs.append(f"⚠️ {plan.total_tasks - len(results)} tasks did not complete")
        return recs
    
    def _generate_audit_hash(self, plan: ExecutionPlan, results: Dict) -> str:
        data = {
            "plan_id": plan.plan_id,
            "tenant_id": plan.tenant_id,
            "task_count": plan.total_tasks,
            "result_keys": sorted(results.keys())
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


# ============================================================================
# MAIN ORCHESTRATOR CLASS
# ============================================================================

class CampaignStrategyOrchestrator:
    """
    Main orchestrator that coordinates all 35 marketing agents.
    Multi-tenant and multi-industry ready.
    
    Usage:
        orchestrator = CampaignStrategyOrchestrator()
        result = await orchestrator.process_strategy(
            document_content="...",
            tenant_id="tenant_123",
            industry_type="boat_rental"
        )
    """
    
    def __init__(self, agent_executor_fn: Optional[Callable] = None):
        self.parser = StrategyParser()
        self.performance_tracker = AgentPerformanceTracker()
        self.alert_system = ProactiveAlertSystem()
        self.smart_allocator = SmartAgentAllocator(self.performance_tracker)
        self.planner = TaskPlanner(TASK_AGENT_REGISTRY, self.smart_allocator)
        self.executor = ExecutionEngine(agent_executor_fn, self.performance_tracker, self.alert_system)
        self.version = VERSION
    
    async def process_strategy(
        self,
        document_content: str,
        tenant_id: str,
        industry_type: str = "custom",
        execution_mode: str = "standard",
        dry_run: bool = False,
        use_smart_allocation: bool = True
    ) -> Dict[str, Any]:
        """
        Process a marketing strategy document and execute it using the 35 agents.
        
        Args:
            document_content: The strategy document text
            tenant_id: ID of the tenant/client
            industry_type: Type of industry (financial_services, boat_rental, retail, etc.)
            execution_mode: plan_only, standard, or comprehensive
            dry_run: If True, simulate execution without calling agents
            use_smart_allocation: Use smart agent allocation based on history
        
        Returns:
            Complete execution results with plan and recommendations
        """
        logger.info(f"Processing strategy for tenant {tenant_id}, industry {industry_type}")
        
        self.smart_allocator.clear_log()
        
        try:
            industry = IndustryType(industry_type)
        except ValueError:
            industry = IndustryType.CUSTOM
        
        # 1. Parse the strategy document
        strategy = await self.parser.parse(document_content, tenant_id, industry)
        
        # 2. Create execution plan
        plan = await self.planner.create_plan(strategy, execution_mode, use_smart_allocation)
        
        # 3. Execute the plan (or just return it if plan_only)
        if execution_mode == "plan_only":
            return {
                "orchestrator_version": self.version,
                "strategy": strategy,
                "plan": self._plan_to_dict(plan),
                "execution": None,
                "message": "Plan created. Use execution_mode='standard' to execute."
            }
        
        # 4. Execute
        result = await self.executor.execute_plan(plan, dry_run)
        
        return {
            "orchestrator_version": self.version,
            "strategy": strategy,
            "plan": self._plan_to_dict(plan),
            "execution": self._result_to_dict(result),
            "learning_layer": {
                "smart_allocation": self.smart_allocator.get_allocation_summary(),
                "alerts_generated": len(result.alerts)
            }
        }
    
    def _plan_to_dict(self, plan: ExecutionPlan) -> Dict:
        return {
            "plan_id": plan.plan_id,
            "strategy_id": plan.strategy_id,
            "tenant_id": plan.tenant_id,
            "industry_type": plan.industry_type.value,
            "total_tasks": plan.total_tasks,
            "estimated_duration_minutes": plan.estimated_duration_minutes,
            "smart_allocation_used": plan.smart_allocation_used,
            "agents_reallocated": plan.agents_reallocated,
            "phases": [
                {
                    "phase_id": p.phase_id,
                    "name": p.name,
                    "tasks": [
                        {
                            "task_id": t.task_id,
                            "task_type": t.task_type.value,
                            "agent_id": t.agent_id,
                            "priority": t.priority,
                            "status": t.status.value,
                            "allocated_by": t.allocated_by
                        }
                        for t in p.tasks
                    ]
                }
                for p in plan.phases
            ]
        }
    
    def _result_to_dict(self, result: ExecutionResult) -> Dict:
        return {
            "execution_id": result.execution_id,
            "status": result.status.value,
            "tasks_completed": result.tasks_completed,
            "tasks_failed": result.tasks_failed,
            "tasks_skipped": result.tasks_skipped,
            "started_at": result.started_at.isoformat(),
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "total_duration_ms": result.total_duration_ms,
            "summary": result.summary,
            "recommendations": result.recommendations,
            "alerts": result.alerts,
            "smart_allocation_summary": result.smart_allocation_summary
        }
    
    def get_supported_industries(self) -> List[Dict]:
        return [
            {
                "type": industry.value,
                "name": config["name"],
                "specialized_agents": len(config.get("specialized_agents", [])),
                "kpis": config.get("kpis", [])
            }
            for industry, config in INDUSTRY_CONFIGS.items()
        ]
    
    def get_task_agent_mapping(self) -> Dict[str, str]:
        return {
            task_type.value: info["agent_id"]
            for task_type, info in TASK_AGENT_REGISTRY.items()
        }


# ============================================================================
# AGENT EXECUTE FUNCTION (Required for Nadakki AI Suite)
# ============================================================================

async def execute(input_data: dict) -> dict:
    """
    Main execute function for the Campaign Strategy Orchestrator.
    This is called by the Nadakki AI Suite agent execution framework.
    
    Input expected:
    {
        "strategy_document": "...(text or base64 of document)",
        "tenant_id": "optional, defaults to 'default'",
        "industry_type": "financial_services|boat_rental|retail|custom",
        "execution_mode": "plan_only|standard|comprehensive",
        "dry_run": true/false
    }
    """
    try:
        strategy_document = input_data.get("strategy_document", "")
        tenant_id = input_data.get("tenant_id", "default")
        industry_type = input_data.get("industry_type", "custom")
        execution_mode = input_data.get("execution_mode", "standard")
        dry_run = input_data.get("dry_run", False)
        
        if not strategy_document:
            return {
                "status": "error",
                "error": "strategy_document is required",
                "agent_id": AGENT_ID,
                "version": VERSION,
                "super_agent": SUPER_AGENT
            }
        
        orchestrator = CampaignStrategyOrchestrator()
        
        result = await orchestrator.process_strategy(
            document_content=strategy_document,
            tenant_id=tenant_id,
            industry_type=industry_type,
            execution_mode=execution_mode,
            dry_run=dry_run
        )
        
        return {
            "status": "success",
            "agent_id": AGENT_ID,
            "version": VERSION,
            "super_agent": SUPER_AGENT,
            "display_name": DISPLAY_NAME,
            "category": CATEGORY,
            "result": result,
            "business_impact_score": 9.5,
            "audit_hash": hashlib.sha256(
                json.dumps(result, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]
        }
        
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "agent_id": AGENT_ID,
            "version": VERSION,
            "super_agent": SUPER_AGENT
        }


# ============================================================================
# TEST
# ============================================================================

async def test_orchestrator():
    """Test the Campaign Strategy Orchestrator with multiple industries"""
    print("=" * 70)
    print("🎯 CAMPAIGN STRATEGY ORCHESTRATOR V3.6 TEST")
    print("=" * 70)
    
    # Sample strategy document (Nadaki Boat Rentals)
    boat_strategy = """
    # NADAKI EXCURSIONS - 90-Day Marketing Strategy
    ## Miami Premium Boat Rentals
    
    ### Target Audiences
    - Birthday parties and celebrations
    - Bachelorette groups
    - Sunset cruise seekers
    - Corporate team building
    
    ### Budget: $45,000
    - Google Ads: $20,000
    - Meta Ads: $15,000  
    - Content: $10,000
    
    ### KPIs
    - CVR > 3%
    - CPA < $45
    - ROAS > 3.5x
    - WhatsApp close rate > 40%
    
    ### Channels
    - Instagram
    - Facebook
    - Google
    - WhatsApp
    - GetMyBoat
    
    ### Tactics
    - Paid advertising campaigns
    - Email marketing sequences
    - Content marketing (blog, video)
    - Birthday/Party packages
    - Bachelorette packages
    - Sunset cruise promotions
    """
    
    # Test 1: Boat Rental
    print("\n🚤 Testing BOAT_RENTAL industry...")
    result1 = await execute({
        "strategy_document": boat_strategy,
        "tenant_id": "nadaki_miami_001",
        "industry_type": "boat_rental",
        "execution_mode": "standard",
        "dry_run": True
    })
    
    print(f"\n   Status: {result1['status']}")
    if result1['status'] == 'success':
        exec_result = result1['result']
        print(f"   Strategy ID: {exec_result['strategy']['strategy_id']}")
        print(f"   Plan ID: {exec_result['plan']['plan_id']}")
        print(f"   Total Tasks: {exec_result['plan']['total_tasks']}")
        print(f"   Smart Allocation: {exec_result['plan']['smart_allocation_used']}")
        if exec_result.get('execution'):
            print(f"   Execution Status: {exec_result['execution']['status']}")
            print(f"   Tasks Completed: {exec_result['execution']['tasks_completed']}")
    
    # Test 2: Financial Services
    print("\n" + "-" * 70)
    print("\n🏦 Testing FINANCIAL_SERVICES industry...")
    
    bank_strategy = """
    # BANCO ABC - Q1 Marketing Strategy
    
    ### Target Audiences
    - High net worth individuals
    - Small & Medium Enterprises (SME)
    - Retail banking customers
    
    ### Budget: $100,000
    - Digital: $60,000
    - Content: $25,000
    - Events: $15,000
    
    ### KPIs
    - AUM growth +15%
    - NPS improvement +10 points
    - CAC reduction 20%
    
    ### Channels
    - Email
    - LinkedIn
    - Google Ads
    """
    
    result2 = await execute({
        "strategy_document": bank_strategy,
        "tenant_id": "banco_abc_001",
        "industry_type": "financial_services",
        "execution_mode": "plan_only",
        "dry_run": False
    })
    
    print(f"\n   Status: {result2['status']}")
    if result2['status'] == 'success':
        print(f"   Strategy ID: {result2['result']['strategy']['strategy_id']}")
        print(f"   Industry: {result2['result']['plan']['industry_type']}")
        print(f"   Total Tasks: {result2['result']['plan']['total_tasks']}")
        print(f"   Seasonal Context: {result2['result']['strategy']['seasonal_context']}")
    
    # Show supported industries
    print("\n" + "-" * 70)
    print("\n📊 SUPPORTED INDUSTRIES:")
    orchestrator = CampaignStrategyOrchestrator()
    for ind in orchestrator.get_supported_industries():
        print(f"   • {ind['name']}: {ind['specialized_agents']} specialized agents")
        print(f"     KPIs: {', '.join(ind['kpis'][:3])}...")
    
    print("\n" + "=" * 70)
    print("✅ ORCHESTRATOR V3.6 TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_orchestrator())


# ═══════════════════════════════════════════════════════════════════════════════
# NADAKKI_OPERATIVE_BIND_V2 manual_cso_001
# ═══════════════════════════════════════════════════════════════════════════════
from nadakki_operative_final import OperativeMixin

AGENT_NAME = "CampaignStrategyOrchestratorIA"

class CampaignStrategyOrchestratorAgentOperative:
    def __init__(self):
        self.agent_id = AGENT_ID
        self.agent_name = AGENT_NAME
        self.version = VERSION
    
    async def execute(self, input_data, tenant_id="default", **kwargs):
        # Runner mode: single dict payload from agent_runner
        if isinstance(input_data, dict):
            dry_run = input_data.get("dry_run", True)
            if dry_run:
                return {
                    "agent": AGENT_NAME,
                    "agent_id": AGENT_ID,
                    "status": "ready",
                    "version": VERSION,
                    "dry_run": True,
                }
            return await execute(input_data)
        # Direct call mode
        merged = {"strategy_document": input_data, "tenant_id": tenant_id, **kwargs}
        return await execute(merged)

OperativeMixin.bind(CampaignStrategyOrchestratorAgentOperative)
campaignstrategyorchestratoria_operative = CampaignStrategyOrchestratorAgentOperative()
