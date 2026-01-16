"""
NADAKKI AI SUITE - AUTONOMY DASHBOARD
Dashboard de monitoreo del sistema de agentes autónomos.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class AgentMetrics:
    """Métricas de un agente"""
    agent_id: str
    executions_total: int = 0
    executions_successful: int = 0
    executions_failed: int = 0
    avg_confidence: float = 0.0
    avg_execution_time_ms: float = 0.0
    last_execution: Optional[str] = None
    last_decision: Optional[str] = None
    confidence_history: List[float] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.executions_total == 0:
            return 0.0
        return self.executions_successful / self.executions_total
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "executions": {
                "total": self.executions_total,
                "successful": self.executions_successful,
                "failed": self.executions_failed,
                "success_rate": round(self.success_rate * 100, 1)
            },
            "performance": {
                "avg_confidence": round(self.avg_confidence, 3),
                "avg_execution_time_ms": round(self.avg_execution_time_ms, 1)
            },
            "last_execution": self.last_execution,
            "last_decision": self.last_decision
        }


@dataclass
class SystemHealth:
    """Estado de salud del sistema"""
    overall_status: str = "healthy"
    uptime_seconds: float = 0.0
    agents_active: int = 0
    agents_total: int = 36
    events_per_minute: float = 0.0
    executions_per_minute: float = 0.0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    last_error: Optional[str] = None
    last_check: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AutonomyDashboard:
    """Dashboard centralizado para monitorear el sistema de agentes autónomos."""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.started_at = datetime.utcnow()
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.decision_history: List[Dict] = []
        self._max_decision_history = 500
        self.recent_events: List[Dict] = []
        self._max_recent_events = 100
        self.active_alerts: List[Dict] = []
        self._event_times: List[datetime] = []
        self._execution_times: List[datetime] = []
        self.alert_thresholds = {
            "success_rate_min": 0.7,
            "avg_confidence_min": 0.6,
            "error_rate_max": 0.3,
            "latency_max_ms": 5000
        }
        print(f"📊 AutonomyDashboard inicializado para tenant: {tenant_id}")
    
    def record_execution(self, agent_id: str, success: bool, confidence: float, 
                         decision: str, execution_time_ms: float, details: Dict = None):
        """Registrar una ejecución de agente"""
        now = datetime.utcnow()
        
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics(agent_id=agent_id)
        
        metrics = self.agent_metrics[agent_id]
        metrics.executions_total += 1
        if success:
            metrics.executions_successful += 1
        else:
            metrics.executions_failed += 1
        
        metrics.confidence_history.append(confidence)
        if len(metrics.confidence_history) > 100:
            metrics.confidence_history = metrics.confidence_history[-100:]
        
        metrics.avg_confidence = sum(metrics.confidence_history) / len(metrics.confidence_history)
        
        alpha = 0.1
        if metrics.avg_execution_time_ms == 0:
            metrics.avg_execution_time_ms = execution_time_ms
        else:
            metrics.avg_execution_time_ms = alpha * execution_time_ms + (1 - alpha) * metrics.avg_execution_time_ms
        
        metrics.last_execution = now.isoformat()
        metrics.last_decision = decision
        
        self._execution_times.append(now)
        self._cleanup_rate_times()
        
        self.decision_history.append({
            "agent_id": agent_id,
            "decision": decision,
            "confidence": confidence,
            "success": success,
            "execution_time_ms": execution_time_ms,
            "timestamp": now.isoformat()
        })
        if len(self.decision_history) > self._max_decision_history:
            self.decision_history = self.decision_history[-self._max_decision_history:]
        
        self._check_alerts(agent_id, metrics)
    
    def record_event(self, event_type: str, data: Dict):
        """Registrar un evento del sistema"""
        now = datetime.utcnow()
        self.recent_events.append({
            "event_type": event_type,
            "data": data,
            "timestamp": now.isoformat()
        })
        if len(self.recent_events) > self._max_recent_events:
            self.recent_events = self.recent_events[-self._max_recent_events:]
        self._event_times.append(now)
        self._cleanup_rate_times()
    
    def _cleanup_rate_times(self):
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        self._event_times = [t for t in self._event_times if t > cutoff]
        self._execution_times = [t for t in self._execution_times if t > cutoff]
    
    def _check_alerts(self, agent_id: str, metrics: AgentMetrics):
        """Verificar y generar alertas si es necesario"""
        if metrics.executions_total >= 10:
            if metrics.success_rate < self.alert_thresholds["success_rate_min"]:
                self._add_alert("low_success_rate", agent_id, metrics.success_rate, 
                               self.alert_thresholds["success_rate_min"], "warning")
        
        if metrics.avg_confidence < self.alert_thresholds["avg_confidence_min"]:
            self._add_alert("low_confidence", agent_id, metrics.avg_confidence,
                           self.alert_thresholds["avg_confidence_min"], "info")
        
        if metrics.avg_execution_time_ms > self.alert_thresholds["latency_max_ms"]:
            self._add_alert("high_latency", agent_id, metrics.avg_execution_time_ms,
                           self.alert_thresholds["latency_max_ms"], "warning")
    
    def _add_alert(self, alert_type: str, agent_id: str, value: float, threshold: float, severity: str):
        existing = [a for a in self.active_alerts if a["type"] == alert_type and a["agent_id"] == agent_id]
        if not existing:
            self.active_alerts.append({
                "type": alert_type,
                "agent_id": agent_id,
                "value": value,
                "threshold": threshold,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def get_system_health(self) -> SystemHealth:
        """Obtener estado de salud del sistema"""
        now = datetime.utcnow()
        events_per_minute = len(self._event_times) / 5.0
        executions_per_minute = len(self._execution_times) / 5.0
        
        total_executions = sum(m.executions_total for m in self.agent_metrics.values())
        total_failures = sum(m.executions_failed for m in self.agent_metrics.values())
        error_rate = total_failures / max(total_executions, 1)
        
        latencies = [m.avg_execution_time_ms for m in self.agent_metrics.values() if m.avg_execution_time_ms > 0]
        avg_latency = sum(latencies) / max(len(latencies), 1)
        
        if error_rate > 0.5 or avg_latency > 10000:
            overall_status = "critical"
        elif error_rate > 0.2 or avg_latency > 5000:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return SystemHealth(
            overall_status=overall_status,
            uptime_seconds=(now - self.started_at).total_seconds(),
            agents_active=len([m for m in self.agent_metrics.values() if m.executions_total > 0]),
            agents_total=36,
            events_per_minute=events_per_minute,
            executions_per_minute=executions_per_minute,
            error_rate=error_rate,
            avg_latency_ms=avg_latency,
            last_check=now.isoformat()
        )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtener todos los datos del dashboard"""
        health = self.get_system_health()
        
        sorted_agents = sorted(self.agent_metrics.values(), key=lambda m: m.success_rate, reverse=True)
        top_performers = [m.to_dict() for m in sorted_agents[:5] if m.executions_total >= 3]
        
        needs_attention = [
            m.to_dict() for m in self.agent_metrics.values()
            if m.executions_total >= 5 and (m.success_rate < 0.7 or m.avg_confidence < 0.6)
        ]
        
        autonomy_distribution = {
            "executing": len([m for m in self.agent_metrics.values() if m.last_decision == "EXECUTE_NOW"]),
            "reviewing": len([m for m in self.agent_metrics.values() if m.last_decision == "REQUEST_REVIEW"]),
            "monitoring": len([m for m in self.agent_metrics.values() if m.last_decision == "EXECUTE_WITH_MONITORING"]),
            "inactive": 36 - len(self.agent_metrics)
        }
        
        recent_confidence = [d["confidence"] for d in self.decision_history[-100:]]
        confidence_trend = {
            "current": recent_confidence[-1] if recent_confidence else 0,
            "avg_last_100": sum(recent_confidence) / max(len(recent_confidence), 1),
            "min": min(recent_confidence) if recent_confidence else 0,
            "max": max(recent_confidence) if recent_confidence else 0
        }
        
        return {
            "tenant_id": self.tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": {
                "overall_status": health.overall_status,
                "uptime_hours": round(health.uptime_seconds / 3600, 2),
                "agents_active": health.agents_active,
                "agents_total": health.agents_total,
                "events_per_minute": round(health.events_per_minute, 2),
                "executions_per_minute": round(health.executions_per_minute, 2),
                "error_rate": round(health.error_rate * 100, 1),
                "avg_latency_ms": round(health.avg_latency_ms, 1)
            },
            "autonomy_distribution": autonomy_distribution,
            "confidence_trend": confidence_trend,
            "top_performers": top_performers,
            "needs_attention": needs_attention,
            "active_alerts": self.active_alerts,
            "recent_decisions": self.decision_history[-10:],
            "recent_events": self.recent_events[-10:]
        }
    
    def get_summary_report(self) -> str:
        """Generar reporte de resumen textual"""
        health = self.get_system_health()
        data = self.get_dashboard_data()
        
        report = f"""
══════════════════════════════════════════════════════════════════
          NADAKKI AI SUITE - AUTONOMY DASHBOARD REPORT            
══════════════════════════════════════════════════════════════════
  Tenant: {self.tenant_id}
  Status: {health.overall_status.upper()}
  Uptime: {health.uptime_seconds/3600:.1f} horas
══════════════════════════════════════════════════════════════════
  MÉTRICAS DEL SISTEMA                                            
══════════════════════════════════════════════════════════════════
  Agentes activos:     {health.agents_active}/{health.agents_total}
  Ejecuciones/min:     {health.executions_per_minute:.1f}
  Tasa de error:       {health.error_rate*100:.1f}%
  Latencia promedio:   {health.avg_latency_ms:.0f}ms
══════════════════════════════════════════════════════════════════
  DISTRIBUCIÓN DE AUTONOMÍA                                       
══════════════════════════════════════════════════════════════════
  Ejecutando:          {data['autonomy_distribution']['executing']}
  En revisión:         {data['autonomy_distribution']['reviewing']}
  Monitoreando:        {data['autonomy_distribution']['monitoring']}
  Inactivos:           {data['autonomy_distribution']['inactive']}
══════════════════════════════════════════════════════════════════
  ALERTAS ACTIVAS: {len(self.active_alerts)}
══════════════════════════════════════════════════════════════════
"""
        return report
