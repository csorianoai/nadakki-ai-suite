"""
NADAKKI AI SUITE - EVENT BUS
Sistema de eventos para comunicación entre agentes y triggers automáticos.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json


class EventType(Enum):
    """Tipos de eventos del sistema"""
    # Lead Events
    LEAD_CREATED = "lead.created"
    LEAD_SCORED = "lead.scored"
    LEAD_QUALIFIED = "lead.qualified"
    LEAD_CONVERTED = "lead.converted"
    
    # Campaign Events
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_PAUSED = "campaign.paused"
    CAMPAIGN_ENDED = "campaign.ended"
    CAMPAIGN_BUDGET_LOW = "campaign.budget_low"
    CAMPAIGN_PERFORMANCE_DROP = "campaign.performance_drop"
    
    # Content Events
    CONTENT_CREATED = "content.created"
    CONTENT_APPROVED = "content.approved"
    CONTENT_PUBLISHED = "content.published"
    CONTENT_VIRAL = "content.viral"
    
    # Social Events
    SOCIAL_COMMENT_RECEIVED = "social.comment_received"
    SOCIAL_MENTION_DETECTED = "social.mention_detected"
    SOCIAL_SENTIMENT_NEGATIVE = "social.sentiment_negative"
    SOCIAL_ENGAGEMENT_SPIKE = "social.engagement_spike"
    
    # Analytics Events
    ANALYTICS_ANOMALY_DETECTED = "analytics.anomaly_detected"
    ANALYTICS_GOAL_REACHED = "analytics.goal_reached"
    ANALYTICS_THRESHOLD_BREACH = "analytics.threshold_breach"
    
    # Email Events
    EMAIL_SENT = "email.sent"
    EMAIL_OPENED = "email.opened"
    EMAIL_CLICKED = "email.clicked"
    EMAIL_BOUNCED = "email.bounced"
    EMAIL_UNSUBSCRIBED = "email.unsubscribed"
    
    # System Events
    AGENT_EXECUTED = "agent.executed"
    AGENT_FAILED = "agent.failed"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    SCHEDULE_TRIGGERED = "schedule.triggered"
    
    # Custom
    CUSTOM = "custom"


@dataclass
class Event:
    """Representa un evento en el sistema"""
    event_type: EventType
    data: Dict[str, Any]
    tenant_id: str
    source: str  # Quién generó el evento (agent_id, "system", "webhook", etc.)
    
    # Metadata
    event_id: str = field(default_factory=lambda: f"evt_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}")
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    priority: int = 5  # 1-10, 10 = máxima
    
    # Tracking
    processed: bool = False
    processed_by: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "data": self.data,
            "tenant_id": self.tenant_id,
            "source": self.source,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "processed": self.processed,
            "processed_by": self.processed_by
        }


@dataclass
class EventSubscription:
    """Suscripción a eventos"""
    subscriber_id: str
    event_types: List[EventType]
    callback: Callable
    filter_fn: Optional[Callable] = None  # Filtro adicional
    priority: int = 5
    active: bool = True


class EventBus:
    """
    Bus de eventos centralizado para el sistema de agentes autónomos.
    
    Funcionalidades:
    - Publicar eventos
    - Suscribirse a eventos
    - Filtrar eventos por tenant/tipo
    - Cola de eventos con prioridad
    - Historial de eventos
    """
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        
        # Suscriptores por tipo de evento
        self._subscriptions: Dict[EventType, List[EventSubscription]] = defaultdict(list)
        
        # Cola de eventos pendientes
        self._event_queue: asyncio.Queue = asyncio.Queue()
        
        # Historial de eventos (últimos 1000)
        self._event_history: List[Event] = []
        self._max_history = 1000
        
        # Estado
        self._running = False
        self._processor_task = None
        
        # Estadísticas
        self.stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_by_type": defaultdict(int),
            "subscribers_count": 0
        }
        
        print(f"📡 EventBus inicializado para tenant: {tenant_id}")
    
    def subscribe(
        self,
        subscriber_id: str,
        event_types: List[EventType],
        callback: Callable,
        filter_fn: Callable = None,
        priority: int = 5
    ) -> str:
        """
        Suscribirse a uno o más tipos de eventos.
        
        Args:
            subscriber_id: ID del suscriptor (agent_id, etc.)
            event_types: Lista de tipos de eventos
            callback: Función async a llamar cuando ocurra el evento
            filter_fn: Función opcional para filtrar eventos
            priority: Prioridad del suscriptor (mayor = procesa primero)
        
        Returns:
            subscription_id
        """
        subscription = EventSubscription(
            subscriber_id=subscriber_id,
            event_types=event_types,
            callback=callback,
            filter_fn=filter_fn,
            priority=priority
        )
        
        for event_type in event_types:
            self._subscriptions[event_type].append(subscription)
            # Ordenar por prioridad (mayor primero)
            self._subscriptions[event_type].sort(key=lambda s: s.priority, reverse=True)
        
        self.stats["subscribers_count"] += 1
        
        subscription_id = f"sub_{subscriber_id}_{datetime.utcnow().strftime('%H%M%S')}"
        print(f"   📌 {subscriber_id} suscrito a {len(event_types)} tipos de eventos")
        
        return subscription_id
    
    def unsubscribe(self, subscriber_id: str, event_types: List[EventType] = None):
        """Cancelar suscripción"""
        types_to_check = event_types or list(self._subscriptions.keys())
        
        for event_type in types_to_check:
            self._subscriptions[event_type] = [
                s for s in self._subscriptions[event_type]
                if s.subscriber_id != subscriber_id
            ]
    
    async def publish(self, event: Event) -> str:
        """
        Publicar un evento al bus.
        
        Args:
            event: Evento a publicar
        
        Returns:
            event_id
        """
        # Validar tenant
        if event.tenant_id != self.tenant_id and self.tenant_id != "default":
            print(f"   ⚠️ Evento ignorado: tenant {event.tenant_id} != {self.tenant_id}")
            return event.event_id
        
        # Agregar a la cola
        await self._event_queue.put(event)
        
        # Agregar al historial
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        # Actualizar stats
        self.stats["events_published"] += 1
        self.stats["events_by_type"][event.event_type.value] += 1
        
        return event.event_id
    
    async def publish_simple(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str,
        priority: int = 5
    ) -> str:
        """Publicar evento de forma simplificada"""
        event = Event(
            event_type=event_type,
            data=data,
            tenant_id=self.tenant_id,
            source=source,
            priority=priority
        )
        return await self.publish(event)
    
    async def start_processing(self):
        """Iniciar procesamiento de eventos en background"""
        if self._running:
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        print(f"   🚀 EventBus procesando eventos...")
    
    async def stop_processing(self):
        """Detener procesamiento"""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
    
    async def _process_events(self):
        """Loop principal de procesamiento de eventos"""
        while self._running:
            try:
                # Obtener evento de la cola (con timeout para poder cancelar)
                try:
                    event = await asyncio.wait_for(
                        self._event_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Procesar evento
                await self._dispatch_event(event)
                
                self.stats["events_processed"] += 1
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"   ❌ Error procesando evento: {e}")
    
    async def _dispatch_event(self, event: Event):
        """Despachar evento a todos los suscriptores"""
        subscribers = self._subscriptions.get(event.event_type, [])
        
        for subscription in subscribers:
            if not subscription.active:
                continue
            
            # Aplicar filtro si existe
            if subscription.filter_fn:
                try:
                    if not subscription.filter_fn(event):
                        continue
                except Exception:
                    continue
            
            # Llamar callback
            try:
                if asyncio.iscoroutinefunction(subscription.callback):
                    await subscription.callback(event)
                else:
                    subscription.callback(event)
                
                event.processed_by.append(subscription.subscriber_id)
                
            except Exception as e:
                print(f"   ❌ Error en suscriptor {subscription.subscriber_id}: {e}")
        
        event.processed = True
    
    async def process_immediate(self, event: Event):
        """Procesar evento inmediatamente (sin cola)"""
        await self._dispatch_event(event)
        
        # Agregar al historial
        self._event_history.append(event)
        self.stats["events_published"] += 1
        self.stats["events_processed"] += 1
        self.stats["events_by_type"][event.event_type.value] += 1
        
        return event
    
    def get_history(
        self,
        event_type: EventType = None,
        limit: int = 100,
        since: datetime = None
    ) -> List[Event]:
        """Obtener historial de eventos"""
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if since:
            events = [e for e in events if datetime.fromisoformat(e.timestamp) >= since]
        
        return events[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del bus"""
        return {
            "tenant_id": self.tenant_id,
            "running": self._running,
            "queue_size": self._event_queue.qsize(),
            "history_size": len(self._event_history),
            "stats": dict(self.stats),
            "subscriptions": {
                et.value: len(subs) 
                for et, subs in self._subscriptions.items()
            }
        }


# ============================================================================
# EVENT MAPPINGS - Qué agentes se activan con cada evento
# ============================================================================

EVENT_TO_AGENTS_MAP: Dict[EventType, List[str]] = {
    # Lead Events
    EventType.LEAD_CREATED: [
        "leadscoria",
        "leadscoringia", 
        "predictiveleadia"
    ],
    EventType.LEAD_QUALIFIED: [
        "emailautomationia",
        "personalizationengineia",
        "journeyoptimizeria"
    ],
    
    # Campaign Events
    EventType.CAMPAIGN_STARTED: [
        "campaignoptimizeria",
        "budgetforecastia",
        "contentgeneratoria"
    ],
    EventType.CAMPAIGN_PERFORMANCE_DROP: [
        "campaignoptimizeria",
        "abtestingia",
        "contentperformanceia"
    ],
    
    # Content Events
    EventType.CONTENT_APPROVED: [
        "socialpostgeneratoria"
    ],
    EventType.CONTENT_PUBLISHED: [
        "sentimentanalyzeria",
        "sociallisteningia",
        "contentperformanceia"
    ],
    
    # Social Events
    EventType.SOCIAL_COMMENT_RECEIVED: [
        "sentimentanalyzeria",
        "sociallisteningia"
    ],
    EventType.SOCIAL_SENTIMENT_NEGATIVE: [
        "socialpostgeneratoria",  # Para responder
        "sentimentanalyzeria"
    ],
    EventType.SOCIAL_ENGAGEMENT_SPIKE: [
        "contentperformanceia",
        "abtestingimpactia"
    ],
    
    # Analytics Events
    EventType.ANALYTICS_ANOMALY_DETECTED: [
        "campaignoptimizeria",
        "budgetforecastia"
    ],
    
    # Email Events
    EventType.EMAIL_BOUNCED: [
        "contactqualityia"
    ],
    EventType.EMAIL_UNSUBSCRIBED: [
        "retentionpredictoria",
        "journeyoptimizeria"
    ]
}


def get_agents_for_event(event_type: EventType) -> List[str]:
    """Obtener lista de agentes que deben activarse para un evento"""
    return EVENT_TO_AGENTS_MAP.get(event_type, [])
