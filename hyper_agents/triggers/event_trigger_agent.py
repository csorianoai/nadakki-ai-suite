"""
NADAKKI AI SUITE - EVENT TRIGGER AGENT (WATCHDOG)
Agente que monitorea eventos y dispara otros agentes automáticamente.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

from .event_bus import EventBus, Event, EventType, get_agents_for_event


@dataclass
class TriggerRule:
    """Regla de trigger para activar agentes"""
    rule_id: str
    name: str
    event_types: List[EventType]
    agents_to_trigger: List[str]
    
    # Condiciones
    conditions: Dict[str, Any] = field(default_factory=dict)
    min_confidence: float = 0.6
    
    # Límites
    cooldown_seconds: int = 60  # Tiempo mínimo entre activaciones
    max_triggers_per_hour: int = 10
    
    # Estado
    active: bool = True
    last_triggered: Optional[str] = None
    trigger_count: int = 0


@dataclass
class TriggerExecution:
    """Registro de ejecución de trigger"""
    rule_id: str
    event: Event
    agents_triggered: List[str]
    results: List[Dict[str, Any]]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    success: bool = False
    duration_ms: float = 0.0


class EventTriggerAgent:
    """
    Watchdog que monitorea eventos y dispara agentes automáticamente.
    
    FUNCIONALIDADES:
    1. Suscribirse a eventos del EventBus
    2. Evaluar reglas de trigger
    3. Activar agentes correspondientes
    4. Gestionar cooldowns y límites
    5. Logging de activaciones
    """
    
    def __init__(
        self,
        tenant_id: str,
        event_bus: EventBus,
        agent_executor: Callable  # Función para ejecutar agentes
    ):
        self.tenant_id = tenant_id
        self.event_bus = event_bus
        self.agent_executor = agent_executor
        
        # Reglas de trigger
        self.rules: Dict[str, TriggerRule] = {}
        
        # Historial de ejecuciones
        self.execution_history: List[TriggerExecution] = []
        self._max_history = 500
        
        # Cooldowns activos (rule_id -> last_trigger_time)
        self._cooldowns: Dict[str, datetime] = {}
        
        # Contadores por hora
        self._hourly_counts: Dict[str, List[datetime]] = {}
        
        # Estado
        self._active = False
        
        # Stats
        self.stats = {
            "total_events_received": 0,
            "total_triggers_fired": 0,
            "total_agents_activated": 0,
            "triggers_blocked_cooldown": 0,
            "triggers_blocked_limit": 0
        }
        
        # Cargar reglas por defecto
        self._load_default_rules()
        
        print(f"🔔 EventTriggerAgent inicializado para tenant: {tenant_id}")
        print(f"   {len(self.rules)} reglas de trigger cargadas")
    
    def _load_default_rules(self):
        """Cargar reglas de trigger por defecto basadas en EVENT_TO_AGENTS_MAP"""
        default_rules = [
            # Lead Management
            TriggerRule(
                rule_id="lead_scoring_auto",
                name="Auto Lead Scoring",
                event_types=[EventType.LEAD_CREATED],
                agents_to_trigger=["leadscoria", "leadscoringia", "predictiveleadia"],
                conditions={"min_data_fields": 3},
                cooldown_seconds=5,
                max_triggers_per_hour=100
            ),
            TriggerRule(
                rule_id="lead_nurturing_auto",
                name="Auto Lead Nurturing",
                event_types=[EventType.LEAD_QUALIFIED],
                agents_to_trigger=["emailautomationia", "personalizationengineia"],
                conditions={"lead_score": {"min": 70}},
                cooldown_seconds=30,
                max_triggers_per_hour=50
            ),
            
            # Campaign Management
            TriggerRule(
                rule_id="campaign_optimization_auto",
                name="Auto Campaign Optimization",
                event_types=[EventType.CAMPAIGN_PERFORMANCE_DROP],
                agents_to_trigger=["campaignoptimizeria", "abtestingia", "budgetforecastia"],
                conditions={"performance_drop_pct": {"min": 10}},
                cooldown_seconds=300,  # 5 minutos
                max_triggers_per_hour=5
            ),
            TriggerRule(
                rule_id="campaign_launch_support",
                name="Campaign Launch Support",
                event_types=[EventType.CAMPAIGN_STARTED],
                agents_to_trigger=["contentgeneratoria", "audiencesegmenteria"],
                cooldown_seconds=60,
                max_triggers_per_hour=10
            ),
            
            # Content & Social
            TriggerRule(
                rule_id="content_auto_publish",
                name="Auto Publish Approved Content",
                event_types=[EventType.CONTENT_APPROVED],
                agents_to_trigger=["socialpostgeneratoria"],
                conditions={"auto_publish": True},
                cooldown_seconds=10,
                max_triggers_per_hour=20
            ),
            TriggerRule(
                rule_id="social_monitoring",
                name="Social Monitoring",
                event_types=[EventType.CONTENT_PUBLISHED],
                agents_to_trigger=["sentimentanalyzeria", "sociallisteningia"],
                cooldown_seconds=30,
                max_triggers_per_hour=30
            ),
            TriggerRule(
                rule_id="negative_sentiment_response",
                name="Negative Sentiment Auto Response",
                event_types=[EventType.SOCIAL_SENTIMENT_NEGATIVE],
                agents_to_trigger=["sentimentanalyzeria", "socialpostgeneratoria"],
                conditions={"sentiment_score": {"max": -0.5}},
                cooldown_seconds=120,
                max_triggers_per_hour=10
            ),
            TriggerRule(
                rule_id="engagement_analysis",
                name="Engagement Spike Analysis",
                event_types=[EventType.SOCIAL_ENGAGEMENT_SPIKE],
                agents_to_trigger=["contentperformanceia", "abtestingimpactia"],
                cooldown_seconds=60,
                max_triggers_per_hour=15
            ),
            
            # Email
            TriggerRule(
                rule_id="email_quality_check",
                name="Email Bounce Quality Check",
                event_types=[EventType.EMAIL_BOUNCED],
                agents_to_trigger=["contactqualityia"],
                cooldown_seconds=10,
                max_triggers_per_hour=50
            ),
            TriggerRule(
                rule_id="retention_alert",
                name="Unsubscribe Retention Alert",
                event_types=[EventType.EMAIL_UNSUBSCRIBED],
                agents_to_trigger=["retentionpredictoria", "journeyoptimizeria"],
                cooldown_seconds=30,
                max_triggers_per_hour=20
            ),
            
            # Analytics
            TriggerRule(
                rule_id="anomaly_investigation",
                name="Anomaly Auto Investigation",
                event_types=[EventType.ANALYTICS_ANOMALY_DETECTED],
                agents_to_trigger=["campaignoptimizeria", "competitoranalyzeria"],
                cooldown_seconds=300,
                max_triggers_per_hour=5
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
    
    async def start(self):
        """Iniciar el watchdog - suscribirse a eventos"""
        if self._active:
            return
        
        self._active = True
        
        # Recopilar todos los tipos de eventos de las reglas
        all_event_types = set()
        for rule in self.rules.values():
            all_event_types.update(rule.event_types)
        
        # Suscribirse al EventBus
        self.event_bus.subscribe(
            subscriber_id="event_trigger_agent",
            event_types=list(all_event_types),
            callback=self._handle_event,
            priority=10  # Alta prioridad
        )
        
        print(f"   🟢 Watchdog activo, monitoreando {len(all_event_types)} tipos de eventos")
    
    async def stop(self):
        """Detener el watchdog"""
        self._active = False
        self.event_bus.unsubscribe("event_trigger_agent")
        print(f"   🔴 Watchdog detenido")
    
    async def _handle_event(self, event: Event):
        """Manejar evento recibido"""
        self.stats["total_events_received"] += 1
        
        # Buscar reglas que apliquen
        applicable_rules = [
            rule for rule in self.rules.values()
            if rule.active and event.event_type in rule.event_types
        ]
        
        for rule in applicable_rules:
            # Verificar cooldown
            if not self._check_cooldown(rule):
                self.stats["triggers_blocked_cooldown"] += 1
                continue
            
            # Verificar límite por hora
            if not self._check_hourly_limit(rule):
                self.stats["triggers_blocked_limit"] += 1
                continue
            
            # Verificar condiciones
            if not self._check_conditions(rule, event):
                continue
            
            # ¡Disparar trigger!
            await self._fire_trigger(rule, event)
    
    def _check_cooldown(self, rule: TriggerRule) -> bool:
        """Verificar si el cooldown permite activar"""
        if rule.rule_id not in self._cooldowns:
            return True
        
        last_trigger = self._cooldowns[rule.rule_id]
        elapsed = (datetime.utcnow() - last_trigger).total_seconds()
        
        return elapsed >= rule.cooldown_seconds
    
    def _check_hourly_limit(self, rule: TriggerRule) -> bool:
        """Verificar límite de triggers por hora"""
        if rule.rule_id not in self._hourly_counts:
            self._hourly_counts[rule.rule_id] = []
        
        # Limpiar triggers antiguos (más de 1 hora)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        self._hourly_counts[rule.rule_id] = [
            t for t in self._hourly_counts[rule.rule_id]
            if t > one_hour_ago
        ]
        
        return len(self._hourly_counts[rule.rule_id]) < rule.max_triggers_per_hour
    
    def _check_conditions(self, rule: TriggerRule, event: Event) -> bool:
        """Verificar condiciones de la regla"""
        if not rule.conditions:
            return True
        
        for key, condition in rule.conditions.items():
            event_value = event.data.get(key)
            
            if event_value is None:
                # Si la condición requiere un campo que no existe
                if isinstance(condition, dict) and condition.get("required", False):
                    return False
                continue
            
            # Evaluar condición
            if isinstance(condition, dict):
                if "min" in condition and event_value < condition["min"]:
                    return False
                if "max" in condition and event_value > condition["max"]:
                    return False
                if "equals" in condition and event_value != condition["equals"]:
                    return False
            elif event_value != condition:
                return False
        
        return True
    
    async def _fire_trigger(self, rule: TriggerRule, event: Event):
        """Disparar el trigger y ejecutar agentes"""
        start_time = datetime.utcnow()
        
        execution = TriggerExecution(
            rule_id=rule.rule_id,
            event=event,
            agents_triggered=rule.agents_to_trigger,
            results=[]
        )
        
        print(f"   ⚡ Trigger '{rule.name}' activado por {event.event_type.value}")
        
        try:
            # Ejecutar cada agente
            for agent_id in rule.agents_to_trigger:
                try:
                    # Preparar input para el agente
                    agent_input = {
                        "trigger_rule": rule.rule_id,
                        "event_type": event.event_type.value,
                        "event_data": event.data,
                        "tenant_id": self.tenant_id,
                        "triggered_at": datetime.utcnow().isoformat()
                    }
                    
                    # Ejecutar agente
                    result = await self.agent_executor(agent_id, agent_input)
                    
                    execution.results.append({
                        "agent_id": agent_id,
                        "success": result.success if hasattr(result, 'success') else True,
                        "result": result.to_dict() if hasattr(result, 'to_dict') else str(result)
                    })
                    
                    self.stats["total_agents_activated"] += 1
                    
                except Exception as e:
                    execution.results.append({
                        "agent_id": agent_id,
                        "success": False,
                        "error": str(e)
                    })
            
            execution.success = all(r.get("success", False) for r in execution.results)
            
        except Exception as e:
            execution.success = False
            execution.results.append({"error": str(e)})
        
        # Actualizar estado
        execution.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Registrar cooldown y conteo
        self._cooldowns[rule.rule_id] = datetime.utcnow()
        if rule.rule_id not in self._hourly_counts:
            self._hourly_counts[rule.rule_id] = []
        self._hourly_counts[rule.rule_id].append(datetime.utcnow())
        
        # Actualizar regla
        rule.last_triggered = datetime.utcnow().isoformat()
        rule.trigger_count += 1
        
        # Guardar en historial
        self.execution_history.append(execution)
        if len(self.execution_history) > self._max_history:
            self.execution_history = self.execution_history[-self._max_history:]
        
        self.stats["total_triggers_fired"] += 1
        
        # Log resultado
        success_count = sum(1 for r in execution.results if r.get("success", False))
        print(f"      → {success_count}/{len(execution.results)} agentes ejecutados OK ({execution.duration_ms:.0f}ms)")
    
    def add_rule(self, rule: TriggerRule):
        """Agregar nueva regla de trigger"""
        self.rules[rule.rule_id] = rule
        
        # Si está activo, re-suscribirse para incluir nuevos eventos
        if self._active:
            for event_type in rule.event_types:
                # El EventBus ya maneja duplicados
                pass
    
    def remove_rule(self, rule_id: str):
        """Eliminar regla"""
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    def enable_rule(self, rule_id: str):
        """Activar regla"""
        if rule_id in self.rules:
            self.rules[rule_id].active = True
    
    def disable_rule(self, rule_id: str):
        """Desactivar regla"""
        if rule_id in self.rules:
            self.rules[rule_id].active = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas"""
        return {
            "tenant_id": self.tenant_id,
            "active": self._active,
            "rules_count": len(self.rules),
            "rules_active": sum(1 for r in self.rules.values() if r.active),
            "stats": self.stats,
            "recent_executions": len(self.execution_history)
        }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict]:
        """Obtener historial de ejecuciones"""
        return [
            {
                "rule_id": e.rule_id,
                "event_type": e.event.event_type.value,
                "agents_triggered": e.agents_triggered,
                "success": e.success,
                "duration_ms": e.duration_ms,
                "timestamp": e.timestamp
            }
            for e in self.execution_history[-limit:]
        ]
