"""
NADAKKI AI SUITE - AUTONOMOUS MARKETING SYSTEM
Sistema integrado que combina todos los componentes de autonomía.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

# Marketing Bridge
from hyper_agents.marketing import HyperMarketingBridge, MARKETING_AGENTS

# Triggers
from hyper_agents.triggers import (
    EventBus, Event, EventType,
    EventTriggerAgent, TriggerRule,
    Scheduler, ScheduleFrequency, DEFAULT_SCHEDULED_TASKS
)

# Orchestration
from hyper_agents.orchestration import (
    AutonomousOrchestrator,
    WorkflowDefinition,
    WorkflowStatus
)

# Monitoring
from hyper_agents.monitoring import AutonomyDashboard

# Autonomous
from hyper_agents.autonomous import (
    AutonomousAgentWrapper,
    AutonomousConfig,
    AutonomyLevel
)


class AutonomousMarketingSystem:
    """
    Sistema completo de marketing autónomo.
    
    COMPONENTES:
    1. HyperMarketingBridge - 36 agentes de marketing
    2. EventBus - Sistema de eventos
    3. EventTriggerAgent - Watchdog para triggers automáticos
    4. Scheduler - Tareas programadas
    5. AutonomousOrchestrator - Coordinación de workflows
    6. AutonomyDashboard - Monitoreo en tiempo real
    
    CAPACIDADES:
    - Ejecución autónoma de agentes
    - Triggers basados en eventos
    - Workflows multi-agente
    - Tareas programadas
    - Monitoreo y alertas
    - Aprendizaje continuo (RL)
    """
    
    def __init__(self, tenant_id: str, config: Dict[str, Any] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.started_at = None
        self._running = False
        
        print(f"\n{'='*70}")
        print(f"  NADAKKI AI SUITE - AUTONOMOUS MARKETING SYSTEM")
        print(f"  Tenant: {tenant_id}")
        print(f"{'='*70}\n")
        
        # 1. Marketing Bridge (36 agentes)
        print("🔧 Inicializando componentes...")
        self.bridge = HyperMarketingBridge(tenant_id=tenant_id)
        
        # 2. Event Bus
        self.event_bus = EventBus(tenant_id=tenant_id)
        
        # 3. Dashboard
        self.dashboard = AutonomyDashboard(tenant_id=tenant_id)
        
        # 4. Orchestrator
        self.orchestrator = AutonomousOrchestrator(
            tenant_id=tenant_id,
            agent_executor=self._execute_agent
        )
        
        # 5. Trigger Agent (Watchdog)
        self.trigger_agent = EventTriggerAgent(
            tenant_id=tenant_id,
            event_bus=self.event_bus,
            agent_executor=self._execute_agent
        )
        
        # 6. Scheduler
        self.scheduler = Scheduler(
            tenant_id=tenant_id,
            agent_executor=self._execute_agent
        )
        
        print(f"\n✅ Sistema inicializado:")
        print(f"   • {len(MARKETING_AGENTS)} agentes de marketing")
        print(f"   • {len(self.trigger_agent.rules)} reglas de trigger")
        print(f"   • {len(self.orchestrator.workflows)} workflows")
        print(f"   • Dashboard de monitoreo activo")
    
    async def _execute_agent(self, agent_id: str, input_data: Dict[str, Any]):
        """Ejecutor interno de agentes con registro en dashboard"""
        start_time = datetime.utcnow()
        
        # Ejecutar via bridge
        result = await self.bridge.execute(agent_id, input_data)
        
        # Registrar en dashboard
        self.dashboard.record_execution(
            agent_id=agent_id,
            success=result.success,
            confidence=result.parallel_thoughts.get("consensus_level", 0.5) if result.parallel_thoughts else 0.5,
            decision=result.original_result.get("decision", {}).get("action", "UNKNOWN"),
            execution_time_ms=result.execution_time_ms
        )
        
        return result
    
    async def start(self):
        """Iniciar el sistema autónomo"""
        if self._running:
            print("⚠️ Sistema ya está en ejecución")
            return
        
        self._running = True
        self.started_at = datetime.utcnow()
        
        print(f"\n🚀 Iniciando sistema autónomo...")
        
        # Iniciar EventBus
        await self.event_bus.start_processing()
        
        # Iniciar Trigger Agent
        await self.trigger_agent.start()
        
        # Iniciar Scheduler
        await self.scheduler.start()
        
        print(f"\n{'='*70}")
        print(f"  ✅ SISTEMA AUTÓNOMO ACTIVO")
        print(f"{'='*70}")
        print(f"  • EventBus: Procesando eventos")
        print(f"  • Watchdog: Monitoreando {len(self.trigger_agent.rules)} triggers")
        print(f"  • Scheduler: {len(self.scheduler.tasks)} tareas programadas")
        print(f"  • Dashboard: Recopilando métricas")
        print(f"{'='*70}\n")
    
    async def stop(self):
        """Detener el sistema"""
        if not self._running:
            return
        
        print("\n🛑 Deteniendo sistema autónomo...")
        
        await self.scheduler.stop()
        await self.trigger_agent.stop()
        await self.event_bus.stop_processing()
        
        self._running = False
        print("   Sistema detenido")
    
    # =========================================================================
    # EJECUCIÓN DE AGENTES
    # =========================================================================
    
    async def execute_agent(self, agent_id: str, input_data: Dict[str, Any]) -> Dict:
        """Ejecutar un agente específico"""
        result = await self._execute_agent(agent_id, input_data)
        return result.to_dict() if hasattr(result, 'to_dict') else {"result": result}
    
    async def execute_all_agents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar todos los agentes (para testing)"""
        results = {}
        for agent in MARKETING_AGENTS:
            agent_id = agent["id"]
            try:
                result = await self._execute_agent(agent_id, input_data)
                results[agent_id] = {
                    "success": result.success,
                    "decision": result.original_result.get("decision", {}).get("action", "N/A")
                }
            except Exception as e:
                results[agent_id] = {"success": False, "error": str(e)}
        return results
    
    # =========================================================================
    # WORKFLOWS
    # =========================================================================
    
    async def run_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict:
        """Ejecutar un workflow"""
        execution = await self.orchestrator.execute_workflow(workflow_id, input_data)
        return execution.to_dict()
    
    def list_workflows(self) -> List[Dict]:
        """Listar workflows disponibles"""
        return self.orchestrator.list_workflows()
    
    # =========================================================================
    # EVENTOS
    # =========================================================================
    
    async def publish_event(self, event_type: EventType, data: Dict[str, Any]) -> str:
        """Publicar un evento al sistema"""
        event_id = await self.event_bus.publish_simple(
            event_type=event_type,
            data=data,
            source="manual"
        )
        
        # Registrar en dashboard
        self.dashboard.record_event(event_type.value, data)
        
        return event_id
    
    # =========================================================================
    # TAREAS PROGRAMADAS
    # =========================================================================
    
    def schedule_task(
        self,
        name: str,
        agent_id: str,
        frequency: ScheduleFrequency,
        input_data: Dict[str, Any] = None,
        **kwargs
    ) -> str:
        """Programar una tarea"""
        return self.scheduler.schedule_task(
            name=name,
            agent_id=agent_id,
            input_data=input_data or {},
            frequency=frequency,
            **kwargs
        )
    
    def load_default_scheduled_tasks(self):
        """Cargar tareas programadas por defecto"""
        for task_config in DEFAULT_SCHEDULED_TASKS:
            self.scheduler.schedule_task(**task_config)
        print(f"   📅 {len(DEFAULT_SCHEDULED_TASKS)} tareas programadas cargadas")
    
    # =========================================================================
    # MONITOREO
    # =========================================================================
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Obtener datos del dashboard"""
        return self.dashboard.get_dashboard_data()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado general del sistema"""
        health = self.dashboard.get_system_health()
        
        return {
            "tenant_id": self.tenant_id,
            "running": self._running,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "system_health": {
                "status": health.overall_status,
                "uptime_hours": round(health.uptime_seconds / 3600, 2),
                "error_rate": round(health.error_rate * 100, 1)
            },
            "components": {
                "agents": len(MARKETING_AGENTS),
                "triggers": len(self.trigger_agent.rules),
                "workflows": len(self.orchestrator.workflows),
                "scheduled_tasks": len(self.scheduler.tasks)
            },
            "stats": {
                "bridge": self.bridge.get_stats(),
                "triggers": self.trigger_agent.get_stats(),
                "scheduler": self.scheduler.get_stats(),
                "orchestrator": self.orchestrator.get_stats()
            }
        }
    
    def print_status(self):
        """Imprimir estado del sistema"""
        print(self.dashboard.get_summary_report())


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

async def create_autonomous_marketing_system(
    tenant_id: str,
    auto_start: bool = True,
    load_defaults: bool = True
) -> AutonomousMarketingSystem:
    """
    Factory para crear y configurar el sistema autónomo.
    
    Args:
        tenant_id: ID del tenant
        auto_start: Si True, inicia el sistema automáticamente
        load_defaults: Si True, carga tareas programadas por defecto
    
    Returns:
        AutonomousMarketingSystem configurado y listo
    """
    system = AutonomousMarketingSystem(tenant_id=tenant_id)
    
    if load_defaults:
        system.load_default_scheduled_tasks()
    
    if auto_start:
        await system.start()
    
    return system


# ============================================================================
# TEST
# ============================================================================

async def test_autonomous_system():
    """Test del sistema autónomo completo"""
    print("\n" + "="*70)
    print("  TEST: AUTONOMOUS MARKETING SYSTEM")
    print("="*70 + "\n")
    
    # Crear sistema
    system = await create_autonomous_marketing_system(
        tenant_id="credicefi",
        auto_start=True,
        load_defaults=False  # No cargar tareas para test rápido
    )
    
    # Test 1: Ejecutar un agente
    print("\n📋 TEST 1: Ejecutar agente")
    result = await system.execute_agent(
        "socialpostgeneratoria",
        {"topic": "Test autonomia", "platform": "facebook"}
    )
    print(f"   Resultado: {result.get('success', False)}")
    
    # Test 2: Publicar evento
    print("\n📋 TEST 2: Publicar evento")
    event_id = await system.publish_event(
        EventType.LEAD_CREATED,
        {"lead_id": "test_123", "email": "test@example.com"}
    )
    print(f"   Event ID: {event_id}")
    
    # Test 3: Ejecutar workflow
    print("\n📋 TEST 3: Ejecutar workflow")
    workflow_result = await system.run_workflow(
        "lead_nurturing",
        {"lead_id": "test_123"}
    )
    print(f"   Status: {workflow_result.get('status')}")
    
    # Test 4: Dashboard
    print("\n📋 TEST 4: Dashboard")
    dashboard_data = system.get_dashboard()
    print(f"   Agentes activos: {dashboard_data['system_health']['agents_active']}")
    
    # Imprimir reporte
    system.print_status()
    
    # Detener
    await system.stop()
    
    print("\n" + "="*70)
    print("  ✅ TODOS LOS TESTS COMPLETADOS")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_autonomous_system())
