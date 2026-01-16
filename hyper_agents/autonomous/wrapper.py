"""
NADAKKI AI SUITE - AUTONOMOUS AGENT WRAPPER
Convierte cualquier agente en autónomo con ejecución real de acciones.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from hyper_agents.core import HyperCortex, ActionType, ActionDef
from hyper_agents.memory import QuantumMemory, MemoryType
from hyper_agents.learning import RLLearningEngine
from hyper_agents.budget import BudgetManager
from hyper_agents.safety import SafetyFilter

from hyper_agents.executors.base_executor import (
    BaseExecutor, ActionRequest, ExecutionResult, ActionRisk,
    MockExecutor, get_executor
)


class AutonomyLevel(Enum):
    """Niveles de autonomía del agente"""
    MANUAL = 0          # Solo análisis, humano ejecuta
    ASSISTED = 1        # Sugiere acciones, humano aprueba
    SUPERVISED = 2      # Ejecuta automático, humano revisa después
    AUTONOMOUS = 3      # Ejecuta sin intervención, reporta resultados
    PROACTIVE = 4       # Inicia acciones por sí mismo basado en triggers


@dataclass
class AutonomousConfig:
    """Configuración de autonomía para un agente"""
    level: AutonomyLevel = AutonomyLevel.SUPERVISED
    
    # Umbrales de auto-aprobación
    auto_approve_confidence: float = 0.85  # Ejecutar sin aprobación si > este valor
    queue_review_confidence: float = 0.60  # Poner en cola si entre este y auto_approve
    
    # Límites
    max_actions_per_hour: int = 50
    max_cost_per_day_usd: float = 10.0
    
    # Acciones permitidas
    allowed_actions: List[str] = field(default_factory=list)  # Vacío = todas
    blocked_actions: List[str] = field(default_factory=list)
    
    # Notificaciones
    notify_on_execution: bool = True
    notify_on_failure: bool = True
    notification_webhook: Optional[str] = None


@dataclass
class AutonomousExecutionResult:
    """Resultado de ejecución autónoma completa"""
    success: bool
    agent_id: str
    tenant_id: str
    autonomy_level: AutonomyLevel
    
    # Fases del ciclo
    analysis_result: Dict[str, Any] = field(default_factory=dict)
    decision: Dict[str, Any] = field(default_factory=dict)
    actions_generated: List[Dict] = field(default_factory=list)
    actions_executed: List[Dict] = field(default_factory=list)
    actions_queued: List[Dict] = field(default_factory=list)
    
    # Aprendizaje
    reflection: str = ""
    rl_updates: List[Dict] = field(default_factory=list)
    memory_stored: bool = False
    
    # Métricas
    total_execution_time_ms: float = 0.0
    total_cost_usd: float = 0.0
    
    # Meta
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "autonomy_level": self.autonomy_level.name,
            "analysis": self.analysis_result,
            "decision": self.decision,
            "actions": {
                "generated": len(self.actions_generated),
                "executed": len(self.actions_executed),
                "queued": len(self.actions_queued),
                "details": self.actions_executed
            },
            "learning": {
                "reflection": self.reflection[:200] if self.reflection else "",
                "rl_updates": len(self.rl_updates),
                "memory_stored": self.memory_stored
            },
            "metrics": {
                "execution_time_ms": self.total_execution_time_ms,
                "cost_usd": round(self.total_cost_usd, 6)
            },
            "timestamp": self.timestamp,
            "errors": self.errors,
            "warnings": self.warnings
        }


class ApprovalQueue:
    """Cola de acciones pendientes de aprobación"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._queue: List[Dict] = []
    
    def add(self, action: ActionRequest, reason: str):
        """Agregar acción a la cola"""
        self._queue.append({
            "action": action,
            "reason": reason,
            "added_at": datetime.utcnow().isoformat(),
            "status": "pending"
        })
    
    def get_pending(self) -> List[Dict]:
        """Obtener acciones pendientes"""
        return [item for item in self._queue if item["status"] == "pending"]
    
    def approve(self, request_id: str, approved_by: str) -> Optional[ActionRequest]:
        """Aprobar una acción"""
        for item in self._queue:
            if item["action"].request_id == request_id:
                item["status"] = "approved"
                item["approved_by"] = approved_by
                item["approved_at"] = datetime.utcnow().isoformat()
                item["action"].approved_by = approved_by
                return item["action"]
        return None
    
    def reject(self, request_id: str, rejected_by: str, reason: str):
        """Rechazar una acción"""
        for item in self._queue:
            if item["action"].request_id == request_id:
                item["status"] = "rejected"
                item["rejected_by"] = rejected_by
                item["rejection_reason"] = reason
                item["rejected_at"] = datetime.utcnow().isoformat()
                break


class AutonomousAgentWrapper:
    """
    Wrapper que convierte cualquier agente en autónomo.
    
    CICLO COMPLETO:
    1. Recibir input (manual o trigger)
    2. Ejecutar agente original (análisis)
    3. Generar decisión
    4. Crear ActionDefs
    5. Evaluar aprobación
    6. Ejecutar acciones (vía Executors)
    7. Reflexionar
    8. Aprender (RL)
    9. Guardar en memoria
    """
    
    # Mapeo de tipos de acción a executors
    ACTION_TO_EXECUTOR = {
        "publish_social": "meta",
        "publish_facebook_post": "meta",
        "publish_instagram_post": "meta",
        "schedule_post": "meta",
        "send_email": "email",
        "create_lead": "crm",
        "update_campaign": "ads",
        "log_event": "mock"
    }
    
    def __init__(
        self,
        agent_execute_fn: Callable,
        agent_id: str,
        tenant_id: str,
        config: AutonomousConfig = None,
        executor_configs: Dict[str, Dict] = None
    ):
        """
        Args:
            agent_execute_fn: Función execute del agente original
            agent_id: ID del agente
            tenant_id: ID del tenant
            config: Configuración de autonomía
            executor_configs: Configuraciones por executor {"meta": {...}, "email": {...}}
        """
        self.agent_execute_fn = agent_execute_fn
        self.agent_id = agent_id
        self.tenant_id = tenant_id
        self.config = config or AutonomousConfig()
        self.executor_configs = executor_configs or {}
        
        # Componentes Hyper
        self.cortex = HyperCortex(agent_id=agent_id, tenant_id=tenant_id)
        self.memory = QuantumMemory(tenant_id=tenant_id, agent_id=agent_id)
        self.rl_engine = RLLearningEngine(agent_id=agent_id, tenant_id=tenant_id)
        self.budget_manager = BudgetManager(tenant_id=tenant_id)
        self.safety_filter = SafetyFilter(tenant_id=tenant_id)
        
        # Cola de aprobación
        self.approval_queue = ApprovalQueue(tenant_id)
        
        # Executors (cargados on-demand)
        self._executors: Dict[str, BaseExecutor] = {}
        
        # Stats
        self.stats = {
            "total_runs": 0,
            "actions_executed": 0,
            "actions_queued": 0,
            "total_cost": 0.0
        }
    
    def _get_executor(self, executor_type: str) -> BaseExecutor:
        """Obtener o crear executor"""
        if executor_type not in self._executors:
            config = self.executor_configs.get(executor_type, {})
            self._executors[executor_type] = get_executor(executor_type, self.tenant_id, config)
        return self._executors[executor_type]
    
    async def run(self, input_data: Dict[str, Any]) -> AutonomousExecutionResult:
        """
        Ejecutar ciclo autónomo completo.
        """
        start_time = datetime.utcnow()
        result = AutonomousExecutionResult(
            success=False,
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            autonomy_level=self.config.level
        )
        
        try:
            # ═══════════════════════════════════════════════════════════
            # FASE 1: ANÁLISIS - Ejecutar agente original
            # ═══════════════════════════════════════════════════════════
            context = {
                "tenant_id": self.tenant_id,
                "autonomy_level": self.config.level.name
            }
            
            # Obtener contexto de memoria
            query = json.dumps(input_data, ensure_ascii=False)[:200]
            memory_context = await self.memory.get_context(query, limit=3)
            context["memory_context"] = memory_context
            
            # Ejecutar agente
            analysis_result = self.agent_execute_fn(input_data, context)
            result.analysis_result = analysis_result
            
            # Verificar éxito del análisis
            if analysis_result.get("status") != "success":
                result.errors.append(f"Análisis falló: {analysis_result.get('error', 'Unknown')}")
                return result
            
            # ═══════════════════════════════════════════════════════════
            # FASE 2: DECISIÓN - Extraer o generar decisión
            # ═══════════════════════════════════════════════════════════
            decision = analysis_result.get("decision", {})
            
            # Si no hay decisión explícita, generarla
            if not decision:
                decision = await self._generate_decision(analysis_result, input_data)
            
            result.decision = decision
            action = decision.get("action", "REVIEW_REQUIRED")
            confidence = decision.get("confidence", decision.get("confidence_score", 0.5))
            
            # ═══════════════════════════════════════════════════════════
            # FASE 3: GENERAR ACCIONES
            # ═══════════════════════════════════════════════════════════
            actions = await self._generate_actions(analysis_result, decision, input_data)
            result.actions_generated = [a.__dict__ if hasattr(a, '__dict__') else a for a in actions]
            
            if not actions:
                result.warnings.append("No se generaron acciones")
            
            # ═══════════════════════════════════════════════════════════
            # FASE 4: EVALUAR Y EJECUTAR ACCIONES
            # ═══════════════════════════════════════════════════════════
            if self.config.level == AutonomyLevel.MANUAL:
                # Solo análisis, poner todo en cola
                for action_req in actions:
                    self.approval_queue.add(action_req, "Nivel MANUAL - requiere aprobación")
                    result.actions_queued.append(action_req.__dict__ if hasattr(action_req, '__dict__') else action_req)
            
            elif self.config.level >= AutonomyLevel.ASSISTED:
                for action_req in actions:
                    # Verificar si puede auto-ejecutar
                    can_auto, reason = self._can_auto_execute(action_req, confidence)
                    
                    if can_auto and self.config.level >= AutonomyLevel.SUPERVISED:
                        # Ejecutar
                        exec_result = await self._execute_action(action_req)
                        result.actions_executed.append(exec_result.to_dict())
                        result.total_cost_usd += exec_result.cost_usd
                        
                        # Actualizar RL basado en resultado
                        rl_update = self.rl_engine.update_policy(
                            context=f"action_{action_req.action_type}",
                            action="execute",
                            success=exec_result.success,
                            reward=0.9 if exec_result.success else 0.2,
                            cost=exec_result.cost_usd
                        )
                        result.rl_updates.append(rl_update)
                    else:
                        # Poner en cola
                        self.approval_queue.add(action_req, reason)
                        result.actions_queued.append({
                            "action": action_req.__dict__ if hasattr(action_req, '__dict__') else action_req,
                            "reason": reason
                        })
            
            # ═══════════════════════════════════════════════════════════
            # FASE 5: REFLEXIÓN
            # ═══════════════════════════════════════════════════════════
            reflection = await self._reflect(input_data, result)
            result.reflection = reflection
            
            # ═══════════════════════════════════════════════════════════
            # FASE 6: GUARDAR EN MEMORIA
            # ═══════════════════════════════════════════════════════════
            try:
                await self.memory.store(
                    key=f"{self.agent_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    content={
                        "input": str(input_data)[:200],
                        "decision": decision.get("action", "none"),
                        "actions_executed": len(result.actions_executed),
                        "success": len(result.errors) == 0
                    },
                    memory_type=MemoryType.SHORT_TERM,
                    importance=confidence,
                    tags=[self.agent_id, decision.get("action", "none")]
                )
                result.memory_stored = True
            except Exception as e:
                result.warnings.append(f"Error guardando memoria: {e}")
            
            result.success = len(result.errors) == 0
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        result.total_execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._update_stats(result)
        
        return result
    
    async def _generate_decision(self, analysis: Dict, input_data: Dict) -> Dict:
        """Generar decisión si el agente no la proporcionó"""
        # Usar el score de análisis para decidir
        score = analysis.get("analysis_score", analysis.get("score", 0.5))
        
        if score >= 0.7:
            return {
                "action": "EXECUTE_NOW",
                "confidence": score,
                "reason": f"Score alto: {score:.2f}"
            }
        elif score >= 0.4:
            return {
                "action": "REVIEW_REQUIRED",
                "confidence": score,
                "reason": f"Score medio: {score:.2f}"
            }
        else:
            return {
                "action": "REJECT",
                "confidence": score,
                "reason": f"Score bajo: {score:.2f}"
            }
    
    async def _generate_actions(
        self, 
        analysis: Dict, 
        decision: Dict, 
        input_data: Dict
    ) -> List[ActionRequest]:
        """Generar acciones basadas en análisis y decisión"""
        actions = []
        
        action_type = decision.get("action", "")
        confidence = decision.get("confidence", 0.5)
        
        if action_type == "EXECUTE_NOW":
            # Determinar tipo de acción según el agente y resultado
            result_data = analysis.get("result", {})
            
            # Si hay contenido generado, crear acción de publicación
            if "content" in result_data or "post" in result_data or "message" in result_data:
                content = result_data.get("content") or result_data.get("post") or result_data.get("message", "")
                platform = input_data.get("platform", "facebook")
                
                action_req = ActionRequest(
                    action_type=f"publish_{platform}_post",
                    params={
                        "message": content,
                        "platform": platform
                    },
                    tenant_id=self.tenant_id,
                    agent_id=self.agent_id,
                    confidence=confidence,
                    risk_level=ActionRisk.LOW
                )
                actions.append(action_req)
            
            # Si hay recomendaciones de email
            if "email" in result_data or "email_content" in result_data:
                email_data = result_data.get("email") or result_data.get("email_content", {})
                action_req = ActionRequest(
                    action_type="send_email",
                    params=email_data,
                    tenant_id=self.tenant_id,
                    agent_id=self.agent_id,
                    confidence=confidence,
                    risk_level=ActionRisk.MEDIUM
                )
                actions.append(action_req)
            
            # Acción genérica de log si no hay nada específico
            if not actions:
                actions.append(ActionRequest(
                    action_type="log_event",
                    params={
                        "event": "analysis_complete",
                        "agent": self.agent_id,
                        "score": analysis.get("analysis_score", 0)
                    },
                    tenant_id=self.tenant_id,
                    agent_id=self.agent_id,
                    confidence=confidence,
                    risk_level=ActionRisk.LOW
                ))
        
        return actions
    
    def _can_auto_execute(self, action: ActionRequest, confidence: float) -> tuple:
        """Determinar si una acción puede ejecutarse automáticamente"""
        # Verificar nivel de autonomía
        if self.config.level < AutonomyLevel.SUPERVISED:
            return False, "Nivel de autonomía insuficiente"
        
        # Verificar confianza
        if confidence < self.config.auto_approve_confidence:
            if confidence >= self.config.queue_review_confidence:
                return False, f"Confianza {confidence:.2f} < umbral {self.config.auto_approve_confidence}"
            else:
                return False, f"Confianza muy baja: {confidence:.2f}"
        
        # Verificar acción bloqueada
        if action.action_type in self.config.blocked_actions:
            return False, f"Acción bloqueada: {action.action_type}"
        
        # Verificar lista de permitidos
        if self.config.allowed_actions and action.action_type not in self.config.allowed_actions:
            return False, f"Acción no en lista permitida"
        
        # Verificar riesgo
        if action.risk_level in [ActionRisk.HIGH, ActionRisk.CRITICAL]:
            return False, f"Riesgo alto: {action.risk_level.value}"
        
        return True, "Auto-aprobado"
    
    async def _execute_action(self, action: ActionRequest) -> ExecutionResult:
        """Ejecutar una acción vía el executor apropiado"""
        # Determinar executor
        executor_type = self.ACTION_TO_EXECUTOR.get(action.action_type, "mock")
        
        try:
            executor = self._get_executor(executor_type)
            return await executor.execute(action)
        except Exception as e:
            return ExecutionResult(
                success=False,
                status="failed",
                action_type=action.action_type,
                executor=executor_type,
                error=str(e),
                tenant_id=self.tenant_id,
                agent_id=self.agent_id
            )
    
    async def _reflect(self, input_data: Dict, result: AutonomousExecutionResult) -> str:
        """Generar reflexión sobre la ejecución"""
        executed = len(result.actions_executed)
        queued = len(result.actions_queued)
        errors = len(result.errors)
        
        reflection = f"""
Ejecución autónoma de {self.agent_id}:
- Decisión: {result.decision.get('action', 'N/A')}
- Confianza: {result.decision.get('confidence', 0):.2f}
- Acciones ejecutadas: {executed}
- Acciones en cola: {queued}
- Errores: {errors}
- Nivel autonomía: {self.config.level.name}
"""
        return reflection.strip()
    
    def _update_stats(self, result: AutonomousExecutionResult):
        """Actualizar estadísticas"""
        self.stats["total_runs"] += 1
        self.stats["actions_executed"] += len(result.actions_executed)
        self.stats["actions_queued"] += len(result.actions_queued)
        self.stats["total_cost"] += result.total_cost_usd
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del wrapper"""
        return {
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "autonomy_level": self.config.level.name,
            "stats": self.stats,
            "pending_approvals": len(self.approval_queue.get_pending())
        }
    
    def get_pending_approvals(self) -> List[Dict]:
        """Obtener acciones pendientes de aprobación"""
        return self.approval_queue.get_pending()
    
    async def approve_action(self, request_id: str, approved_by: str) -> Optional[ExecutionResult]:
        """Aprobar y ejecutar una acción pendiente"""
        action = self.approval_queue.approve(request_id, approved_by)
        if action:
            return await self._execute_action(action)
        return None


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def make_autonomous(
    agent_module,
    agent_id: str,
    tenant_id: str,
    autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED,
    executor_configs: Dict = None
) -> AutonomousAgentWrapper:
    """
    Factory para convertir un módulo de agente en autónomo.
    
    Args:
        agent_module: Módulo del agente (con función execute)
        agent_id: ID del agente
        tenant_id: ID del tenant
        autonomy_level: Nivel de autonomía
        executor_configs: Configuraciones de executors
    
    Returns:
        AutonomousAgentWrapper configurado
    """
    if not hasattr(agent_module, "execute"):
        raise ValueError(f"El módulo no tiene función execute")
    
    config = AutonomousConfig(level=autonomy_level)
    
    return AutonomousAgentWrapper(
        agent_execute_fn=agent_module.execute,
        agent_id=agent_id,
        tenant_id=tenant_id,
        config=config,
        executor_configs=executor_configs
    )
