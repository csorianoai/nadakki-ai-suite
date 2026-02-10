"""
═══════════════════════════════════════════════════════════════════════════════════════════════════
OPERATIVE WRAPPER - NADAKKI AI SUITE
═══════════════════════════════════════════════════════════════════════════════════════════════════

Este wrapper convierte CUALQUIER agente analista en un agente OPERATIVO.
Permite ejecutar acciones reales manteniendo la lógica de análisis existente.

Características:
  • Multi-tenant por diseño (tenant_id en todas las operaciones)
  • 3 niveles de autonomía: manual, semi, full_auto
  • Safety filter integrado
  • Audit trail con SHA-256
  • Circuit breaker para tolerancia a fallos

Uso:
    from agents.marketing.wrappers.operative_wrapper import OperativeWrapper
    
    wrapper = OperativeWrapper(
        base_agent=ContentGeneratorIA(),
        executor=MetaExecutor(),
        tenant_id="banco_abc"
    )
    
    result = await wrapper.execute_operative(input_data)

═══════════════════════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
import json
import os

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS Y TIPOS
# ═══════════════════════════════════════════════════════════════════════════════

class AutonomyLevel(Enum):
    """Niveles de autonomía del agente"""
    MANUAL = "manual"           # Siempre requiere aprobación humana
    SEMI = "semi"               # Auto-ejecuta si confidence > threshold
    FULL_AUTO = "full_auto"     # Ejecuta sin aprobación (con safety filters)


class ActionType(Enum):
    """Tipos de acciones que puede ejecutar un agente operativo"""
    PUBLISH_CONTENT = "publish_content"
    SEND_EMAIL = "send_email"
    POST_SOCIAL = "post_social"
    REPLY_COMMENT = "reply_comment"
    UPDATE_CAMPAIGN = "update_campaign"
    PERSONALIZE = "personalize"
    ORCHESTRATE = "orchestrate"
    ANALYZE = "analyze"  # Mantiene compatibilidad con agentes analistas


class ExecutionStatus(Enum):
    """Estados de ejecución"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING_APPROVAL = "pending_approval"
    BLOCKED_SAFETY = "blocked_safety"
    BLOCKED_CIRCUIT = "blocked_circuit"


# ═══════════════════════════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OperativeResult:
    """Resultado de una ejecución operativa"""
    status: ExecutionStatus
    action_type: ActionType
    analysis: Dict[str, Any]
    execution_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence: float = 0.0
    risk_level: str = "unknown"
    requires_approval: bool = False
    audit_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tenant_id: str = ""
    execution_time_ms: float = 0.0


@dataclass
class TenantConfig:
    """Configuración por tenant"""
    tenant_id: str
    autonomy_level: AutonomyLevel = AutonomyLevel.SEMI
    confidence_threshold: float = 0.75
    max_daily_actions: int = 100
    allowed_actions: List[ActionType] = field(default_factory=list)
    blocked_actions: List[ActionType] = field(default_factory=list)
    notification_email: str = ""
    notification_slack: str = ""
    custom_rules: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# SAFETY FILTER
# ═══════════════════════════════════════════════════════════════════════════════

class SafetyFilter:
    """
    Filtro de seguridad para bloquear acciones peligrosas.
    Implementa múltiples capas de validación.
    """
    
    BLOCKED_KEYWORDS = [
        "delete_all", "drop_database", "rm -rf", "format",
        "offensive", "inappropriate", "spam", "phishing"
    ]
    
    MAX_CONTENT_LENGTH = 10000
    MAX_EMAIL_RECIPIENTS = 1000
    
    def __init__(self, tenant_config: TenantConfig):
        self.config = tenant_config
        self.logger = logging.getLogger(f"SafetyFilter.{tenant_config.tenant_id}")
    
    def check(self, action_type: ActionType, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Verifica si una acción es segura para ejecutar.
        
        Returns:
            tuple[bool, str]: (es_seguro, razón_si_bloqueado)
        """
        # 1. Verificar si la acción está bloqueada para este tenant
        if action_type in self.config.blocked_actions:
            return False, f"Action {action_type.value} is blocked for this tenant"
        
        # 2. Verificar keywords bloqueadas
        data_str = json.dumps(data).lower()
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in data_str:
                return False, f"Blocked keyword detected: {keyword}"
        
        # 3. Verificar límites de contenido
        content = data.get("content", "") or data.get("message", "")
        if len(content) > self.MAX_CONTENT_LENGTH:
            return False, f"Content too long: {len(content)} > {self.MAX_CONTENT_LENGTH}"
        
        # 4. Verificar límites de email
        if action_type == ActionType.SEND_EMAIL:
            recipients = data.get("recipients", [])
            if len(recipients) > self.MAX_EMAIL_RECIPIENTS:
                return False, f"Too many recipients: {len(recipients)} > {self.MAX_EMAIL_RECIPIENTS}"
        
        return True, ""


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT TRAIL
# ═══════════════════════════════════════════════════════════════════════════════

class AuditTrail:
    """
    Sistema de auditoría inmutable con hashing SHA-256.
    Registra todas las acciones para compliance y debugging.
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.logger = logging.getLogger(f"AuditTrail.{tenant_id}")
    
    def create_entry(
        self,
        action_type: ActionType,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        status: ExecutionStatus,
        agent_name: str
    ) -> str:
        """
        Crea una entrada de auditoría con hash inmutable.
        
        Returns:
            str: Hash SHA-256 de la entrada
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": self.tenant_id,
            "agent_name": agent_name,
            "action_type": action_type.value,
            "status": status.value,
            "input_hash": self._hash_data(input_data),
            "output_hash": self._hash_data(output_data)
        }
        
        entry_hash = self._hash_data(entry)
        entry["entry_hash"] = entry_hash
        
        # Log para persistencia (en producción, guardar en DB)
        self.logger.info(f"AUDIT: {json.dumps(entry)}")
        
        return entry_hash
    
    def _hash_data(self, data: Any) -> str:
        """Genera hash SHA-256 de cualquier dato serializable"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER
# ═══════════════════════════════════════════════════════════════════════════════

class CircuitBreaker:
    """
    Implementación del patrón Circuit Breaker para tolerancia a fallos.
    Detiene operaciones si hay demasiados errores consecutivos.
    """
    
    def __init__(
        self,
        max_failures: int = 5,
        reset_timeout_seconds: int = 60,
        tenant_id: str = ""
    ):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout_seconds
        self.tenant_id = tenant_id
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False
        self.logger = logging.getLogger(f"CircuitBreaker.{tenant_id}")
    
    def can_execute(self) -> tuple[bool, str]:
        """Verifica si el circuito permite ejecución"""
        if not self.is_open:
            return True, ""
        
        # Verificar si pasó el timeout para reset
        if self.last_failure_time:
            elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
            if elapsed > self.reset_timeout:
                self.reset()
                return True, ""
        
        return False, f"Circuit breaker OPEN: {self.failure_count} failures"
    
    def record_success(self):
        """Registra una ejecución exitosa"""
        self.failure_count = 0
        self.is_open = False
    
    def record_failure(self):
        """Registra un fallo"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.max_failures:
            self.is_open = True
            self.logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")
    
    def reset(self):
        """Resetea el circuit breaker"""
        self.failure_count = 0
        self.is_open = False
        self.logger.info("Circuit breaker RESET")


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTOR INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class BaseExecutor(ABC):
    """
    Interfaz base para ejecutores de acciones.
    Cada tipo de acción (Meta, Email, etc.) implementa esta interfaz.
    """
    
    @abstractmethod
    async def execute(
        self,
        action_type: ActionType,
        data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Ejecuta una acción real.
        
        Args:
            action_type: Tipo de acción a ejecutar
            data: Datos necesarios para la acción
            tenant_id: ID del tenant
        
        Returns:
            Dict con resultado de la ejecución
        """
        pass
    
    @abstractmethod
    def get_supported_actions(self) -> List[ActionType]:
        """Retorna lista de acciones soportadas por este executor"""
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# OPERATIVE WRAPPER (EL CORE)
# ═══════════════════════════════════════════════════════════════════════════════

class OperativeWrapper:
    """
    Wrapper universal que convierte agentes analistas en operativos.
    
    Este es el componente central del sistema. Envuelve cualquier agente
    existente y le añade capacidad de ejecutar acciones reales.
    """
    
    def __init__(
        self,
        base_agent: Any,
        executor: BaseExecutor,
        tenant_id: str,
        config: Optional[TenantConfig] = None
    ):
        self.agent = base_agent
        self.executor = executor
        self.tenant_id = tenant_id
        
        # Configuración del tenant
        self.config = config or TenantConfig(
            tenant_id=tenant_id,
            autonomy_level=AutonomyLevel.SEMI,
            confidence_threshold=0.75
        )
        
        # Componentes enterprise
        self.safety_filter = SafetyFilter(self.config)
        self.audit_trail = AuditTrail(tenant_id)
        self.circuit_breaker = CircuitBreaker(tenant_id=tenant_id)
        
        # Logger
        self.logger = logging.getLogger(f"OperativeWrapper.{tenant_id}.{self._get_agent_name()}")
    
    def _get_agent_name(self) -> str:
        """Obtiene el nombre del agente base"""
        return getattr(self.agent, 'name', self.agent.__class__.__name__)
    
    async def execute_operative(
        self,
        input_data: Dict[str, Any],
        action_type: ActionType = ActionType.ANALYZE,
        force_execute: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> OperativeResult:
        """
        Ejecuta el agente en modo operativo.
        
        Flujo:
        1. Análisis del agente base
        2. Verificación de seguridad
        3. Verificación de circuit breaker
        4. Decisión de ejecución (basado en autonomía)
        5. Ejecución real si procede
        6. Registro en audit trail
        
        Args:
            input_data: Datos de entrada para el agente
            action_type: Tipo de acción a ejecutar
            force_execute: Si True, salta verificación de autonomía
            context: Contexto adicional (opcional)
        
        Returns:
            OperativeResult con todos los detalles de la ejecución
        """
        import time
        start_time = time.time()
        
        # Añadir tenant_id al contexto
        ctx = context or {}
        ctx["tenant_id"] = self.tenant_id
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 1: ANÁLISIS DEL AGENTE BASE
        # ═══════════════════════════════════════════════════════════════════
        
        try:
            # Intentar diferentes métodos de ejecución del agente base
            if hasattr(self.agent, 'execute'):
                analysis = self.agent.execute(input_data, ctx)
            elif hasattr(self.agent, 'run'):
                analysis = self.agent.run(input_data, ctx)
            elif hasattr(self.agent, 'process'):
                analysis = self.agent.process(input_data, ctx)
            elif callable(self.agent):
                analysis = self.agent(input_data, ctx)
            else:
                analysis = {"raw_input": input_data, "warning": "No execute method found"}
        except Exception as e:
            self.logger.error(f"Agent analysis failed: {e}")
            analysis = {"error": str(e), "raw_input": input_data}
        
        # Extraer métricas del análisis
        confidence = float(analysis.get("confidence", 0.5))
        risk_level = analysis.get("risk_level", "medium")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 2: VERIFICACIÓN DE CIRCUIT BREAKER
        # ═══════════════════════════════════════════════════════════════════
        
        can_execute, circuit_reason = self.circuit_breaker.can_execute()
        if not can_execute:
            return OperativeResult(
                status=ExecutionStatus.BLOCKED_CIRCUIT,
                action_type=action_type,
                analysis=analysis,
                error=circuit_reason,
                confidence=confidence,
                risk_level=risk_level,
                tenant_id=self.tenant_id,
                execution_time_ms=(time.time() - start_time) * 1000
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 3: VERIFICACIÓN DE SEGURIDAD
        # ═══════════════════════════════════════════════════════════════════
        
        is_safe, safety_reason = self.safety_filter.check(action_type, input_data)
        if not is_safe:
            audit_hash = self.audit_trail.create_entry(
                action_type=action_type,
                input_data=input_data,
                output_data={"blocked": True, "reason": safety_reason},
                status=ExecutionStatus.BLOCKED_SAFETY,
                agent_name=self._get_agent_name()
            )
            
            return OperativeResult(
                status=ExecutionStatus.BLOCKED_SAFETY,
                action_type=action_type,
                analysis=analysis,
                error=safety_reason,
                confidence=confidence,
                risk_level=risk_level,
                audit_hash=audit_hash,
                tenant_id=self.tenant_id,
                execution_time_ms=(time.time() - start_time) * 1000
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 4: DECISIÓN DE EJECUCIÓN
        # ═══════════════════════════════════════════════════════════════════
        
        should_execute = force_execute or self._should_auto_execute(
            confidence=confidence,
            risk_level=risk_level,
            action_type=action_type
        )
        
        if not should_execute:
            audit_hash = self.audit_trail.create_entry(
                action_type=action_type,
                input_data=input_data,
                output_data={"pending_approval": True},
                status=ExecutionStatus.PENDING_APPROVAL,
                agent_name=self._get_agent_name()
            )
            
            return OperativeResult(
                status=ExecutionStatus.PENDING_APPROVAL,
                action_type=action_type,
                analysis=analysis,
                confidence=confidence,
                risk_level=risk_level,
                requires_approval=True,
                audit_hash=audit_hash,
                tenant_id=self.tenant_id,
                execution_time_ms=(time.time() - start_time) * 1000
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 5: EJECUCIÓN REAL
        # ═══════════════════════════════════════════════════════════════════
        
        try:
            # Preparar datos para el executor
            execution_data = self._prepare_execution_data(analysis, input_data, action_type)
            
            # Ejecutar acción real
            execution_result = await self.executor.execute(
                action_type=action_type,
                data=execution_data,
                tenant_id=self.tenant_id
            )
            
            # Registrar éxito
            self.circuit_breaker.record_success()
            
            audit_hash = self.audit_trail.create_entry(
                action_type=action_type,
                input_data=input_data,
                output_data=execution_result,
                status=ExecutionStatus.SUCCESS,
                agent_name=self._get_agent_name()
            )
            
            return OperativeResult(
                status=ExecutionStatus.SUCCESS,
                action_type=action_type,
                analysis=analysis,
                execution_result=execution_result,
                confidence=confidence,
                risk_level=risk_level,
                audit_hash=audit_hash,
                tenant_id=self.tenant_id,
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            # Registrar fallo
            self.circuit_breaker.record_failure()
            self.logger.error(f"Execution failed: {e}")
            
            audit_hash = self.audit_trail.create_entry(
                action_type=action_type,
                input_data=input_data,
                output_data={"error": str(e)},
                status=ExecutionStatus.FAILED,
                agent_name=self._get_agent_name()
            )
            
            return OperativeResult(
                status=ExecutionStatus.FAILED,
                action_type=action_type,
                analysis=analysis,
                error=str(e),
                confidence=confidence,
                risk_level=risk_level,
                audit_hash=audit_hash,
                tenant_id=self.tenant_id,
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def _should_auto_execute(
        self,
        confidence: float,
        risk_level: str,
        action_type: ActionType
    ) -> bool:
        """
        Decide si ejecutar automáticamente basado en autonomía y métricas.
        """
        # MANUAL: nunca auto-ejecutar
        if self.config.autonomy_level == AutonomyLevel.MANUAL:
            return False
        
        # FULL_AUTO: siempre ejecutar (ya pasó safety filter)
        if self.config.autonomy_level == AutonomyLevel.FULL_AUTO:
            return True
        
        # SEMI: ejecutar si cumple criterios
        if self.config.autonomy_level == AutonomyLevel.SEMI:
            # Verificar threshold de confianza
            if confidence < self.config.confidence_threshold:
                return False
            
            # Verificar nivel de riesgo
            if risk_level in ["high", "critical"]:
                return False
            
            return True
        
        return False
    
    def _prepare_execution_data(
        self,
        analysis: Dict[str, Any],
        input_data: Dict[str, Any],
        action_type: ActionType
    ) -> Dict[str, Any]:
        """
        Prepara los datos para el executor combinando análisis e input.
        """
        # Extraer contenido generado del análisis
        content = (
            analysis.get("generated_content") or
            analysis.get("content") or
            analysis.get("recommendation") or
            analysis.get("output") or
            input_data.get("content", "")
        )
        
        return {
            "content": content,
            "analysis": analysis,
            "original_input": input_data,
            "action_type": action_type.value,
            "metadata": {
                "agent_name": self._get_agent_name(),
                "tenant_id": self.tenant_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD
# ═══════════════════════════════════════════════════════════════════════════════

def load_tenant_config(tenant_id: str) -> TenantConfig:
    """
    Carga configuración del tenant desde archivo JSON.
    Si no existe, retorna configuración por defecto.
    """
    config_path = f"config/tenants/{tenant_id}.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            data = json.load(f)
            return TenantConfig(
                tenant_id=tenant_id,
                autonomy_level=AutonomyLevel(data.get("autonomy_level", "semi")),
                confidence_threshold=data.get("confidence_threshold", 0.75),
                max_daily_actions=data.get("max_daily_actions", 100),
                allowed_actions=[ActionType(a) for a in data.get("allowed_actions", [])],
                blocked_actions=[ActionType(a) for a in data.get("blocked_actions", [])],
                notification_email=data.get("notification_email", ""),
                notification_slack=data.get("notification_slack", ""),
                custom_rules=data.get("custom_rules", {})
            )
    
    # Configuración por defecto
    return TenantConfig(
        tenant_id=tenant_id,
        autonomy_level=AutonomyLevel.SEMI,
        confidence_threshold=0.75
    )


def create_operative_agent(
    base_agent: Any,
    executor: BaseExecutor,
    tenant_id: str
) -> OperativeWrapper:
    """
    Factory function para crear agentes operativos.
    
    Uso:
        agent = create_operative_agent(
            ContentGeneratorIA(),
            MetaExecutor(),
            "banco_abc"
        )
    """
    config = load_tenant_config(tenant_id)
    return OperativeWrapper(
        base_agent=base_agent,
        executor=executor,
        tenant_id=tenant_id,
        config=config
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'OperativeWrapper',
    'OperativeResult',
    'BaseExecutor',
    'ActionType',
    'AutonomyLevel',
    'ExecutionStatus',
    'TenantConfig',
    'SafetyFilter',
    'AuditTrail',
    'CircuitBreaker',
    'create_operative_agent',
    'load_tenant_config'
]
