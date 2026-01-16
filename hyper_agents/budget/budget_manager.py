"""
NADAKKI AI SUITE - BUDGET MANAGER
Gestión inteligente de presupuesto y costos de API.
Selección automática de modelos según presupuesto disponible.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


# ============================================================================
# ENUMS Y CONFIGURACIÓN
# ============================================================================

class ModelTier(Enum):
    """Niveles de modelos por costo/capacidad"""
    PREMIUM = "premium"      # GPT-4, Claude-3 Opus
    STANDARD = "standard"    # GPT-4o-mini, Claude-3 Sonnet
    ECONOMY = "economy"      # GPT-3.5, DeepSeek
    FREE = "free"            # Modelos gratuitos/mock


class BudgetAlert(Enum):
    """Tipos de alertas de presupuesto"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"


# Costos aproximados por 1K tokens (input, output)
MODEL_COSTS = {
    # Premium
    "gpt-4": (0.03, 0.06),
    "gpt-4-turbo": (0.01, 0.03),
    "claude-3-opus": (0.015, 0.075),
    
    # Standard
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "claude-3-sonnet": (0.003, 0.015),
    "claude-3-haiku": (0.00025, 0.00125),
    
    # Economy
    "gpt-3.5-turbo": (0.0005, 0.0015),
    "deepseek-chat": (0.00014, 0.00028),
    "deepseek-coder": (0.00014, 0.00028),
    
    # Free/Mock
    "mock-model": (0.0, 0.0),
    "local-model": (0.0, 0.0)
}

MODEL_TIERS = {
    ModelTier.PREMIUM: ["gpt-4", "gpt-4-turbo", "claude-3-opus"],
    ModelTier.STANDARD: ["gpt-4o", "gpt-4o-mini", "claude-3-sonnet", "claude-3-haiku"],
    ModelTier.ECONOMY: ["gpt-3.5-turbo", "deepseek-chat", "deepseek-coder"],
    ModelTier.FREE: ["mock-model", "local-model"]
}


# ============================================================================
# USAGE RECORD
# ============================================================================

@dataclass
class UsageRecord:
    """Registro de uso individual"""
    timestamp: str
    agent_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    context: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": round(self.cost_usd, 8),
            "context": self.context
        }


# ============================================================================
# BUDGET MANAGER
# ============================================================================

class BudgetManager:
    """
    Gestor de presupuesto inteligente.
    
    Características:
    - Límites diarios, semanales y mensuales
    - Selección automática de modelo según presupuesto
    - Alertas configurables
    - Historial de uso detallado
    - Multi-tenant
    """
    
    def __init__(
        self,
        tenant_id: str = "default",
        monthly_budget_usd: float = 100.0,
        daily_limit_usd: Optional[float] = None,
        alert_thresholds: Dict[str, float] = None
    ):
        self.tenant_id = tenant_id
        self.monthly_budget = monthly_budget_usd
        self.daily_limit = daily_limit_usd or (monthly_budget_usd / 30)
        
        # Umbrales de alerta (% del presupuesto)
        self.alert_thresholds = alert_thresholds or {
            "info": 0.5,      # 50%
            "warning": 0.75,   # 75%
            "critical": 0.9,   # 90%
            "exceeded": 1.0    # 100%
        }
        
        # Uso por período
        self.usage_records: List[UsageRecord] = []
        
        # Caché de totales
        self._daily_total = 0.0
        self._monthly_total = 0.0
        self._last_daily_reset = datetime.utcnow().date()
        self._last_monthly_reset = datetime.utcnow().replace(day=1).date()
        
        # Uso por agente
        self.agent_usage: Dict[str, float] = defaultdict(float)
        
        # Alertas activas
        self.active_alerts: List[Dict] = []
    
    def record_usage(
        self,
        agent_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        context: str = ""
    ) -> UsageRecord:
        """
        Registra uso de API.
        
        Args:
            agent_id: ID del agente
            model: Modelo utilizado
            input_tokens: Tokens de entrada
            output_tokens: Tokens de salida
            context: Contexto adicional
        
        Returns:
            UsageRecord creado
        """
        # Resetear contadores si es necesario
        self._check_reset_periods()
        
        # Calcular costo
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        # Crear registro
        record = UsageRecord(
            timestamp=datetime.utcnow().isoformat(),
            agent_id=agent_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            context=context
        )
        
        # Actualizar totales
        self.usage_records.append(record)
        self._daily_total += cost
        self._monthly_total += cost
        self.agent_usage[agent_id] += cost
        
        # Verificar alertas
        self._check_alerts()
        
        # Limpiar registros antiguos
        self._cleanup_old_records()
        
        return record
    
    def _calculate_cost(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """Calcula costo en USD"""
        costs = MODEL_COSTS.get(model, (0.001, 0.002))
        input_cost = (input_tokens / 1000) * costs[0]
        output_cost = (output_tokens / 1000) * costs[1]
        return input_cost + output_cost
    
    def select_model(
        self,
        preferred_model: str,
        task_complexity: float = 0.5,
        estimated_tokens: int = 1000
    ) -> str:
        """
        Selecciona el mejor modelo según presupuesto y tarea.
        
        Args:
            preferred_model: Modelo preferido
            task_complexity: Complejidad de la tarea (0.0-1.0)
            estimated_tokens: Tokens estimados
        
        Returns:
            Modelo seleccionado
        """
        # Calcular presupuesto disponible
        daily_remaining = self.daily_limit - self._daily_total
        monthly_remaining = self.monthly_budget - self._monthly_total
        
        # Si hay suficiente presupuesto, usar preferido
        estimated_cost = self._calculate_cost(
            preferred_model, 
            estimated_tokens, 
            estimated_tokens
        )
        
        if estimated_cost < min(daily_remaining, monthly_remaining):
            return preferred_model
        
        # Buscar alternativa más económica
        for tier in [ModelTier.STANDARD, ModelTier.ECONOMY, ModelTier.FREE]:
            for model in MODEL_TIERS[tier]:
                est_cost = self._calculate_cost(
                    model, 
                    estimated_tokens, 
                    estimated_tokens
                )
                if est_cost < min(daily_remaining, monthly_remaining):
                    return model
        
        # Fallback a mock si no hay presupuesto
        return "mock-model"
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Retorna estado actual del presupuesto"""
        self._check_reset_periods()
        
        daily_pct = (self._daily_total / self.daily_limit) * 100
        monthly_pct = (self._monthly_total / self.monthly_budget) * 100
        
        # Determinar nivel de alerta
        alert_level = BudgetAlert.INFO
        for level_name, threshold in sorted(
            self.alert_thresholds.items(), 
            key=lambda x: x[1],
            reverse=True
        ):
            if monthly_pct / 100 >= threshold:
                alert_level = BudgetAlert[level_name.upper()]
                break
        
        return {
            "tenant_id": self.tenant_id,
            "daily": {
                "limit": self.daily_limit,
                "used": round(self._daily_total, 6),
                "remaining": round(self.daily_limit - self._daily_total, 6),
                "percentage": round(daily_pct, 2)
            },
            "monthly": {
                "budget": self.monthly_budget,
                "used": round(self._monthly_total, 6),
                "remaining": round(self.monthly_budget - self._monthly_total, 6),
                "percentage": round(monthly_pct, 2)
            },
            "alert_level": alert_level.value,
            "active_alerts": len(self.active_alerts),
            "top_agents": self._get_top_agents(5),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_usage_report(
        self,
        period: str = "day",
        agent_id: str = None
    ) -> Dict[str, Any]:
        """
        Genera reporte de uso.
        
        Args:
            period: "day", "week", or "month"
            agent_id: Filtrar por agente específico
        
        Returns:
            Reporte detallado
        """
        now = datetime.utcnow()
        
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        else:
            start_date = now - timedelta(days=30)
        
        # Filtrar registros
        filtered = [
            r for r in self.usage_records
            if datetime.fromisoformat(r.timestamp) >= start_date
            and (agent_id is None or r.agent_id == agent_id)
        ]
        
        # Calcular estadísticas
        total_cost = sum(r.cost_usd for r in filtered)
        total_input = sum(r.input_tokens for r in filtered)
        total_output = sum(r.output_tokens for r in filtered)
        
        # Uso por modelo
        by_model = defaultdict(lambda: {"cost": 0.0, "calls": 0})
        for r in filtered:
            by_model[r.model]["cost"] += r.cost_usd
            by_model[r.model]["calls"] += 1
        
        # Uso por agente
        by_agent = defaultdict(lambda: {"cost": 0.0, "calls": 0})
        for r in filtered:
            by_agent[r.agent_id]["cost"] += r.cost_usd
            by_agent[r.agent_id]["calls"] += 1
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "summary": {
                "total_cost_usd": round(total_cost, 6),
                "total_calls": len(filtered),
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "avg_cost_per_call": round(total_cost / max(len(filtered), 1), 8)
            },
            "by_model": {
                model: {
                    "cost": round(data["cost"], 6),
                    "calls": data["calls"]
                }
                for model, data in sorted(
                    by_model.items(), 
                    key=lambda x: x[1]["cost"], 
                    reverse=True
                )
            },
            "by_agent": {
                agent: {
                    "cost": round(data["cost"], 6),
                    "calls": data["calls"]
                }
                for agent, data in sorted(
                    by_agent.items(), 
                    key=lambda x: x[1]["cost"], 
                    reverse=True
                )[:10]
            }
        }
    
    def can_execute(
        self, 
        estimated_cost: float = 0.01
    ) -> Tuple[bool, str]:
        """
        Verifica si hay presupuesto para ejecutar.
        
        Returns:
            Tuple (puede_ejecutar, razón)
        """
        self._check_reset_periods()
        
        if self._daily_total + estimated_cost > self.daily_limit:
            return False, f"Daily limit exceeded: ${self._daily_total:.4f}/${self.daily_limit:.4f}"
        
        if self._monthly_total + estimated_cost > self.monthly_budget:
            return False, f"Monthly budget exceeded: ${self._monthly_total:.4f}/${self.monthly_budget:.4f}"
        
        return True, "Budget available"
    
    def _check_reset_periods(self):
        """Resetea contadores si es nuevo día/mes"""
        today = datetime.utcnow().date()
        first_of_month = today.replace(day=1)
        
        if today > self._last_daily_reset:
            self._daily_total = 0.0
            self._last_daily_reset = today
        
        if first_of_month > self._last_monthly_reset:
            self._monthly_total = 0.0
            self._last_monthly_reset = first_of_month
            self.agent_usage.clear()
    
    def _check_alerts(self):
        """Verifica y genera alertas si es necesario"""
        monthly_pct = self._monthly_total / self.monthly_budget
        
        for level_name, threshold in self.alert_thresholds.items():
            if monthly_pct >= threshold:
                alert = {
                    "level": level_name,
                    "threshold": threshold,
                    "current_usage": monthly_pct,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": f"Budget usage at {monthly_pct*100:.1f}% (threshold: {threshold*100:.0f}%)"
                }
                
                # Evitar alertas duplicadas
                if not any(
                    a["level"] == level_name 
                    for a in self.active_alerts
                ):
                    self.active_alerts.append(alert)
    
    def _get_top_agents(self, n: int = 5) -> List[Dict]:
        """Retorna top agentes por uso"""
        sorted_agents = sorted(
            self.agent_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"agent_id": agent, "cost_usd": round(cost, 6)}
            for agent, cost in sorted_agents[:n]
        ]
    
    def _cleanup_old_records(self, max_records: int = 10000):
        """Limpia registros antiguos"""
        if len(self.usage_records) > max_records:
            self.usage_records = self.usage_records[-max_records//2:]
    
    def export_data(self) -> Dict[str, Any]:
        """Exporta datos para persistencia"""
        return {
            "tenant_id": self.tenant_id,
            "monthly_budget": self.monthly_budget,
            "daily_limit": self.daily_limit,
            "alert_thresholds": self.alert_thresholds,
            "daily_total": self._daily_total,
            "monthly_total": self._monthly_total,
            "agent_usage": dict(self.agent_usage),
            "usage_records": [r.to_dict() for r in self.usage_records[-1000:]],
            "exported_at": datetime.utcnow().isoformat()
        }
    
    def import_data(self, data: Dict[str, Any]):
        """Importa datos desde export"""
        self.monthly_budget = data.get("monthly_budget", 100.0)
        self.daily_limit = data.get("daily_limit", self.monthly_budget / 30)
        self.alert_thresholds = data.get("alert_thresholds", self.alert_thresholds)
        self._daily_total = data.get("daily_total", 0.0)
        self._monthly_total = data.get("monthly_total", 0.0)
        self.agent_usage = defaultdict(float, data.get("agent_usage", {}))
        
        # Restaurar registros
        for record_dict in data.get("usage_records", []):
            self.usage_records.append(UsageRecord(
                timestamp=record_dict["timestamp"],
                agent_id=record_dict["agent_id"],
                model=record_dict["model"],
                input_tokens=record_dict["input_tokens"],
                output_tokens=record_dict["output_tokens"],
                cost_usd=record_dict["cost_usd"],
                context=record_dict.get("context", "")
            ))
