"""
NADAKKI AI SUITE - SCHEDULER
Sistema de tareas programadas para agentes autónomos.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json


class ScheduleFrequency(Enum):
    """Frecuencias de programación"""
    ONCE = "once"
    MINUTELY = "minutely"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # Expresión cron-like


@dataclass
class ScheduledTask:
    """Tarea programada"""
    task_id: str
    name: str
    agent_id: str
    input_data: Dict[str, Any]
    
    # Programación
    frequency: ScheduleFrequency
    next_run: datetime
    
    # Para frecuencias específicas
    run_at_hour: int = 9  # Para daily
    run_at_minute: int = 0
    run_on_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Lun-Vie
    run_on_day_of_month: int = 1  # Para monthly
    
    # Control
    max_runs: Optional[int] = None
    run_count: int = 0
    active: bool = True
    
    # Metadata
    tenant_id: str = "default"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_run: Optional[str] = None
    last_result: Optional[Dict] = None


@dataclass 
class TaskExecution:
    """Registro de ejecución de tarea"""
    task_id: str
    agent_id: str
    started_at: str
    completed_at: Optional[str] = None
    success: bool = False
    result: Optional[Dict] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class Scheduler:
    """
    Sistema de programación de tareas para agentes autónomos.
    
    FUNCIONALIDADES:
    1. Programar ejecuciones periódicas de agentes
    2. Soporte para múltiples frecuencias
    3. Gestión de timezone
    4. Historial de ejecuciones
    5. Retry automático en fallos
    """
    
    def __init__(
        self,
        tenant_id: str,
        agent_executor: Callable,
        check_interval_seconds: int = 30
    ):
        self.tenant_id = tenant_id
        self.agent_executor = agent_executor
        self.check_interval = check_interval_seconds
        
        # Tareas programadas
        self.tasks: Dict[str, ScheduledTask] = {}
        
        # Historial de ejecuciones
        self.execution_history: List[TaskExecution] = []
        self._max_history = 500
        
        # Estado
        self._running = False
        self._scheduler_task = None
        
        # Stats
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "tasks_created": 0
        }
        
        print(f"⏰ Scheduler inicializado para tenant: {tenant_id}")
    
    def schedule_task(
        self,
        name: str,
        agent_id: str,
        input_data: Dict[str, Any],
        frequency: ScheduleFrequency,
        first_run: datetime = None,
        **kwargs
    ) -> str:
        """
        Programar una nueva tarea.
        
        Args:
            name: Nombre descriptivo
            agent_id: ID del agente a ejecutar
            input_data: Datos de entrada para el agente
            frequency: Frecuencia de ejecución
            first_run: Primera ejecución (default: ahora)
            **kwargs: Configuración adicional (run_at_hour, run_on_days, etc.)
        
        Returns:
            task_id
        """
        task_id = f"task_{agent_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Calcular primera ejecución
        if first_run is None:
            first_run = self._calculate_next_run(frequency, datetime.utcnow(), **kwargs)
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            agent_id=agent_id,
            input_data=input_data,
            frequency=frequency,
            next_run=first_run,
            tenant_id=self.tenant_id,
            **{k: v for k, v in kwargs.items() if k in ScheduledTask.__dataclass_fields__}
        )
        
        self.tasks[task_id] = task
        self.stats["tasks_created"] += 1
        
        print(f"   📅 Tarea programada: '{name}'")
        print(f"      Agente: {agent_id}")
        print(f"      Frecuencia: {frequency.value}")
        print(f"      Próxima ejecución: {first_run.isoformat()}")
        
        return task_id
    
    def _calculate_next_run(
        self,
        frequency: ScheduleFrequency,
        from_time: datetime,
        **kwargs
    ) -> datetime:
        """Calcular próxima ejecución basada en frecuencia"""
        
        if frequency == ScheduleFrequency.ONCE:
            return from_time
        
        elif frequency == ScheduleFrequency.MINUTELY:
            return from_time + timedelta(minutes=1)
        
        elif frequency == ScheduleFrequency.HOURLY:
            next_hour = from_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return next_hour
        
        elif frequency == ScheduleFrequency.DAILY:
            run_at_hour = kwargs.get("run_at_hour", 9)
            run_at_minute = kwargs.get("run_at_minute", 0)
            
            next_run = from_time.replace(
                hour=run_at_hour,
                minute=run_at_minute,
                second=0,
                microsecond=0
            )
            
            if next_run <= from_time:
                next_run += timedelta(days=1)
            
            return next_run
        
        elif frequency == ScheduleFrequency.WEEKLY:
            run_on_days = kwargs.get("run_on_days", [0])  # Default: Lunes
            run_at_hour = kwargs.get("run_at_hour", 9)
            
            next_run = from_time.replace(
                hour=run_at_hour,
                minute=0,
                second=0,
                microsecond=0
            )
            
            # Buscar próximo día válido
            for i in range(8):
                check_day = (next_run + timedelta(days=i)).weekday()
                if check_day in run_on_days:
                    next_run = next_run + timedelta(days=i)
                    if next_run > from_time:
                        break
            
            return next_run
        
        elif frequency == ScheduleFrequency.MONTHLY:
            run_on_day = kwargs.get("run_on_day_of_month", 1)
            run_at_hour = kwargs.get("run_at_hour", 9)
            
            next_run = from_time.replace(
                day=min(run_on_day, 28),  # Evitar problemas con meses cortos
                hour=run_at_hour,
                minute=0,
                second=0,
                microsecond=0
            )
            
            if next_run <= from_time:
                # Siguiente mes
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
            
            return next_run
        
        else:
            # Default: 1 hora
            return from_time + timedelta(hours=1)
    
    async def start(self):
        """Iniciar el scheduler"""
        if self._running:
            return
        
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        print(f"   🟢 Scheduler activo, verificando cada {self.check_interval}s")
        print(f"      {len(self.tasks)} tareas programadas")
    
    async def stop(self):
        """Detener el scheduler"""
        self._running = False
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        print(f"   🔴 Scheduler detenido")
    
    async def _scheduler_loop(self):
        """Loop principal del scheduler"""
        while self._running:
            try:
                now = datetime.utcnow()
                
                # Buscar tareas que deban ejecutarse
                for task in list(self.tasks.values()):
                    if not task.active:
                        continue
                    
                    if task.next_run <= now:
                        # Ejecutar tarea
                        await self._execute_task(task)
                
                # Esperar hasta próxima verificación
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"   ❌ Error en scheduler loop: {e}")
                await asyncio.sleep(5)
    
    async def _execute_task(self, task: ScheduledTask):
        """Ejecutar una tarea programada"""
        start_time = datetime.utcnow()
        
        execution = TaskExecution(
            task_id=task.task_id,
            agent_id=task.agent_id,
            started_at=start_time.isoformat()
        )
        
        print(f"   ▶️ Ejecutando tarea: '{task.name}'")
        
        try:
            # Preparar input con metadata del scheduler
            enriched_input = {
                **task.input_data,
                "scheduled_task_id": task.task_id,
                "scheduled_run": task.next_run.isoformat(),
                "run_count": task.run_count + 1,
                "tenant_id": self.tenant_id
            }
            
            # Ejecutar agente
            result = await self.agent_executor(task.agent_id, enriched_input)
            
            execution.success = result.success if hasattr(result, 'success') else True
            execution.result = result.to_dict() if hasattr(result, 'to_dict') else {"result": str(result)}
            
            self.stats["successful_executions"] += 1
            
        except Exception as e:
            execution.success = False
            execution.error = str(e)
            self.stats["failed_executions"] += 1
            print(f"      ❌ Error: {e}")
        
        # Completar ejecución
        execution.completed_at = datetime.utcnow().isoformat()
        execution.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Actualizar tarea
        task.run_count += 1
        task.last_run = execution.completed_at
        task.last_result = execution.result
        
        # Calcular próxima ejecución
        if task.frequency == ScheduleFrequency.ONCE:
            task.active = False
        elif task.max_runs and task.run_count >= task.max_runs:
            task.active = False
        else:
            task.next_run = self._calculate_next_run(
                task.frequency,
                datetime.utcnow(),
                run_at_hour=task.run_at_hour,
                run_at_minute=task.run_at_minute,
                run_on_days=task.run_on_days,
                run_on_day_of_month=task.run_on_day_of_month
            )
        
        # Guardar en historial
        self.execution_history.append(execution)
        if len(self.execution_history) > self._max_history:
            self.execution_history = self.execution_history[-self._max_history:]
        
        self.stats["total_executions"] += 1
        
        # Log resultado
        status = "✅" if execution.success else "❌"
        print(f"      {status} Completado en {execution.duration_ms:.0f}ms")
        
        if task.active:
            print(f"      📅 Próxima ejecución: {task.next_run.isoformat()}")
    
    def cancel_task(self, task_id: str):
        """Cancelar tarea"""
        if task_id in self.tasks:
            self.tasks[task_id].active = False
            print(f"   ❎ Tarea cancelada: {task_id}")
    
    def resume_task(self, task_id: str):
        """Reactivar tarea"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.active = True
            task.next_run = self._calculate_next_run(
                task.frequency,
                datetime.utcnow(),
                run_at_hour=task.run_at_hour,
                run_at_minute=task.run_at_minute,
                run_on_days=task.run_on_days
            )
            print(f"   ▶️ Tarea reactivada: {task_id}")
    
    def delete_task(self, task_id: str):
        """Eliminar tarea"""
        if task_id in self.tasks:
            del self.tasks[task_id]
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Obtener tarea por ID"""
        return self.tasks.get(task_id)
    
    def get_pending_tasks(self) -> List[Dict]:
        """Obtener tareas pendientes"""
        now = datetime.utcnow()
        pending = [
            {
                "task_id": t.task_id,
                "name": t.name,
                "agent_id": t.agent_id,
                "next_run": t.next_run.isoformat(),
                "frequency": t.frequency.value,
                "active": t.active
            }
            for t in self.tasks.values()
            if t.active
        ]
        return sorted(pending, key=lambda x: x["next_run"])
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas"""
        return {
            "tenant_id": self.tenant_id,
            "running": self._running,
            "total_tasks": len(self.tasks),
            "active_tasks": sum(1 for t in self.tasks.values() if t.active),
            "stats": self.stats,
            "next_task": min(
                (t.next_run for t in self.tasks.values() if t.active),
                default=None
            )
        }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict]:
        """Obtener historial de ejecuciones"""
        return [
            {
                "task_id": e.task_id,
                "agent_id": e.agent_id,
                "success": e.success,
                "duration_ms": e.duration_ms,
                "started_at": e.started_at,
                "error": e.error
            }
            for e in self.execution_history[-limit:]
        ]


# ============================================================================
# TAREAS PROGRAMADAS POR DEFECTO
# ============================================================================

DEFAULT_SCHEDULED_TASKS = [
    {
        "name": "Daily Content Performance Analysis",
        "agent_id": "contentperformanceia",
        "frequency": ScheduleFrequency.DAILY,
        "run_at_hour": 8,
        "input_data": {"analysis_type": "daily_summary"}
    },
    {
        "name": "Weekly Competitor Analysis",
        "agent_id": "competitoranalyzeria",
        "frequency": ScheduleFrequency.WEEKLY,
        "run_on_days": [0],  # Lunes
        "run_at_hour": 9,
        "input_data": {"analysis_type": "weekly_competitive"}
    },
    {
        "name": "Daily Lead Scoring Update",
        "agent_id": "leadscoringia",
        "frequency": ScheduleFrequency.DAILY,
        "run_at_hour": 7,
        "input_data": {"batch_mode": True}
    },
    {
        "name": "Hourly Social Listening",
        "agent_id": "sociallisteningia",
        "frequency": ScheduleFrequency.HOURLY,
        "input_data": {"monitor_all_channels": True}
    },
    {
        "name": "Monthly Budget Forecast",
        "agent_id": "budgetforecastia",
        "frequency": ScheduleFrequency.MONTHLY,
        "run_on_day_of_month": 1,
        "run_at_hour": 10,
        "input_data": {"forecast_period": "next_month"}
    }
]
