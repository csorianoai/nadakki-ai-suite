"""
NADAKKI AI SUITE - BASE EXECUTOR
Clase base para todos los Action Executors.
"""

import asyncio
import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ExecutionStatus(Enum):
    """Estados de ejecución"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    APPROVAL_REQUIRED = "approval_required"


class ActionRisk(Enum):
    """Niveles de riesgo de acciones"""
    LOW = "low"           # Publicar post, log evento
    MEDIUM = "medium"     # Enviar email, crear lead
    HIGH = "high"         # Cambiar presupuesto, pausar campaña
    CRITICAL = "critical" # Eliminar, acciones irreversibles


@dataclass
class ExecutionResult:
    """Resultado de una ejecución"""
    success: bool
    status: ExecutionStatus
    action_type: str
    executor: str
    
    # Resultado
    result_data: Dict[str, Any] = field(default_factory=dict)
    external_id: Optional[str] = None  # ID en plataforma externa (post_id, email_id, etc.)
    
    # Métricas
    execution_time_ms: float = 0.0
    retry_count: int = 0
    cost_usd: float = 0.0
    
    # Auditoría
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Trazabilidad
    request_hash: str = ""
    tenant_id: str = ""
    agent_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "status": self.status.value,
            "action_type": self.action_type,
            "executor": self.executor,
            "external_id": self.external_id,
            "result_data": self.result_data,
            "metrics": {
                "execution_time_ms": self.execution_time_ms,
                "retry_count": self.retry_count,
                "cost_usd": self.cost_usd
            },
            "timestamp": self.timestamp,
            "error": self.error,
            "warnings": self.warnings,
            "audit": {
                "request_hash": self.request_hash,
                "tenant_id": self.tenant_id,
                "agent_id": self.agent_id
            }
        }


@dataclass
class ActionRequest:
    """Solicitud de acción a ejecutar"""
    action_type: str
    params: Dict[str, Any]
    tenant_id: str
    agent_id: str
    
    # Control
    priority: int = 5  # 1-10, 10 = máxima
    confidence: float = 0.8
    risk_level: ActionRisk = ActionRisk.LOW
    
    # Aprobación
    requires_approval: bool = False
    approved_by: Optional[str] = None
    approval_timestamp: Optional[str] = None
    
    # Retry
    max_retries: int = 3
    retry_delay_seconds: int = 5
    
    # Meta
    request_id: str = field(default_factory=lambda: f"req_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}")
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def get_hash(self) -> str:
        """Genera hash único del request"""
        content = f"{self.action_type}:{json.dumps(self.params, sort_keys=True)}:{self.tenant_id}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class BaseExecutor(ABC):
    """
    Clase base abstracta para todos los Action Executors.
    
    Cada executor implementa la conexión con una plataforma específica
    (Facebook, Twitter, Email, etc.) y ejecuta acciones reales.
    """
    
    # Configuración de la subclase
    EXECUTOR_NAME: str = "base"
    SUPPORTED_ACTIONS: List[str] = []
    DEFAULT_RISK_LEVELS: Dict[str, ActionRisk] = {}
    
    def __init__(self, tenant_id: str, config: Dict[str, Any] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.is_connected = False
        
        # Estadísticas
        self.stats = {
            "total_executions": 0,
            "successes": 0,
            "failures": 0,
            "total_cost": 0.0,
            "by_action": {}
        }
        
        # Rate limiting
        self._last_execution = None
        self._execution_count = 0
        self._rate_limit_window = 60  # segundos
        self._rate_limit_max = 100  # ejecuciones por ventana
    
    @abstractmethod
    async def connect(self) -> bool:
        """Conectar con la plataforma externa"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Desconectar de la plataforma"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verificar estado de la conexión"""
        pass
    
    @abstractmethod
    async def _execute_action(self, request: ActionRequest) -> ExecutionResult:
        """Implementación específica de ejecución"""
        pass
    
    def supports_action(self, action_type: str) -> bool:
        """Verifica si el executor soporta una acción"""
        return action_type in self.SUPPORTED_ACTIONS
    
    def get_risk_level(self, action_type: str) -> ActionRisk:
        """Obtiene el nivel de riesgo de una acción"""
        return self.DEFAULT_RISK_LEVELS.get(action_type, ActionRisk.MEDIUM)
    
    async def execute(self, request: ActionRequest) -> ExecutionResult:
        """
        Ejecuta una acción con manejo de errores, reintentos y logging.
        """
        start_time = datetime.utcnow()
        
        # Validar acción soportada
        if not self.supports_action(request.action_type):
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error=f"Acción no soportada: {request.action_type}",
                tenant_id=request.tenant_id,
                agent_id=request.agent_id
            )
        
        # Verificar conexión
        if not self.is_connected:
            connected = await self.connect()
            if not connected:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    action_type=request.action_type,
                    executor=self.EXECUTOR_NAME,
                    error="No se pudo conectar con la plataforma",
                    tenant_id=request.tenant_id,
                    agent_id=request.agent_id
                )
        
        # Verificar rate limit
        if not self._check_rate_limit():
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error="Rate limit excedido",
                tenant_id=request.tenant_id,
                agent_id=request.agent_id
            )
        
        # Verificar aprobación si es necesario
        if request.requires_approval and not request.approved_by:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.APPROVAL_REQUIRED,
                action_type=request.action_type,
                executor=self.EXECUTOR_NAME,
                error="Requiere aprobación antes de ejecutar",
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                request_hash=request.get_hash()
            )
        
        # Ejecutar con reintentos
        result = None
        retry_count = 0
        
        while retry_count <= request.max_retries:
            try:
                result = await self._execute_action(request)
                
                if result.success:
                    break
                
                # Si falla, reintentar
                retry_count += 1
                if retry_count <= request.max_retries:
                    result.status = ExecutionStatus.RETRYING
                    await asyncio.sleep(request.retry_delay_seconds * retry_count)
                    
            except Exception as e:
                result = ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    action_type=request.action_type,
                    executor=self.EXECUTOR_NAME,
                    error=str(e),
                    tenant_id=request.tenant_id,
                    agent_id=request.agent_id
                )
                retry_count += 1
                if retry_count <= request.max_retries:
                    await asyncio.sleep(request.retry_delay_seconds * retry_count)
        
        # Completar resultado
        result.retry_count = retry_count
        result.execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.request_hash = request.get_hash()
        result.tenant_id = request.tenant_id
        result.agent_id = request.agent_id
        
        # Actualizar estadísticas
        self._update_stats(request.action_type, result)
        
        return result
    
    def _check_rate_limit(self) -> bool:
        """Verifica si se puede ejecutar según rate limit"""
        now = datetime.utcnow()
        
        if self._last_execution is None:
            self._last_execution = now
            self._execution_count = 1
            return True
        
        # Resetear ventana si pasó el tiempo
        elapsed = (now - self._last_execution).total_seconds()
        if elapsed > self._rate_limit_window:
            self._last_execution = now
            self._execution_count = 1
            return True
        
        # Verificar límite
        if self._execution_count >= self._rate_limit_max:
            return False
        
        self._execution_count += 1
        return True
    
    def _update_stats(self, action_type: str, result: ExecutionResult):
        """Actualiza estadísticas internas"""
        self.stats["total_executions"] += 1
        
        if result.success:
            self.stats["successes"] += 1
        else:
            self.stats["failures"] += 1
        
        self.stats["total_cost"] += result.cost_usd
        
        if action_type not in self.stats["by_action"]:
            self.stats["by_action"][action_type] = {"executions": 0, "successes": 0}
        
        self.stats["by_action"][action_type]["executions"] += 1
        if result.success:
            self.stats["by_action"][action_type]["successes"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del executor"""
        return {
            "executor": self.EXECUTOR_NAME,
            "tenant_id": self.tenant_id,
            "is_connected": self.is_connected,
            "supported_actions": self.SUPPORTED_ACTIONS,
            "stats": self.stats
        }


class MockExecutor(BaseExecutor):
    """
    Executor de pruebas que simula ejecuciones.
    Útil para testing y desarrollo.
    """
    
    EXECUTOR_NAME = "mock"
    SUPPORTED_ACTIONS = [
        "publish_post", "send_email", "create_lead", 
        "update_campaign", "log_event", "send_notification"
    ]
    DEFAULT_RISK_LEVELS = {
        "publish_post": ActionRisk.LOW,
        "send_email": ActionRisk.MEDIUM,
        "create_lead": ActionRisk.LOW,
        "update_campaign": ActionRisk.HIGH,
        "log_event": ActionRisk.LOW,
        "send_notification": ActionRisk.LOW
    }
    
    def __init__(self, tenant_id: str, config: Dict[str, Any] = None):
        super().__init__(tenant_id, config)
        self._mock_delay = config.get("mock_delay", 0.1) if config else 0.1
        self._mock_success_rate = config.get("success_rate", 0.95) if config else 0.95
    
    async def connect(self) -> bool:
        await asyncio.sleep(0.05)
        self.is_connected = True
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self.is_connected else "disconnected",
            "executor": self.EXECUTOR_NAME,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_action(self, request: ActionRequest) -> ExecutionResult:
        """Simula ejecución"""
        await asyncio.sleep(self._mock_delay)
        
        import random
        success = random.random() < self._mock_success_rate
        
        return ExecutionResult(
            success=success,
            status=ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED,
            action_type=request.action_type,
            executor=self.EXECUTOR_NAME,
            external_id=f"mock_{request.action_type}_{datetime.utcnow().strftime('%H%M%S')}",
            result_data={
                "message": f"Mock execution of {request.action_type}",
                "params_received": request.params,
                "_mock": True
            },
            error=None if success else "Mock random failure"
        )


# Registro de executors disponibles
EXECUTOR_REGISTRY: Dict[str, type] = {
    "mock": MockExecutor
}


def get_executor(executor_type: str, tenant_id: str, config: Dict = None) -> BaseExecutor:
    """Factory para obtener un executor"""
    if executor_type not in EXECUTOR_REGISTRY:
        raise ValueError(f"Executor no registrado: {executor_type}")
    
    return EXECUTOR_REGISTRY[executor_type](tenant_id, config)


def register_executor(name: str, executor_class: type):
    """Registra un nuevo executor"""
    EXECUTOR_REGISTRY[name] = executor_class
