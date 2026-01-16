"""
NADAKKI AI SUITE - TEST COMPLETO DEL SISTEMA AUTÓNOMO
Prueba todos los componentes del sistema de agentes autónomos.
"""

import asyncio
import sys
sys.path.insert(0, '.')

async def test_imports():
    """Test de imports"""
    print("\n" + "="*70)
    print("  TEST 1: IMPORTS")
    print("="*70)
    
    tests = []
    
    try:
        from hyper_agents import HyperMarketingBridge, MARKETING_AGENTS
        print(f"  ✅ Marketing Bridge ({len(MARKETING_AGENTS)} agentes)")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Marketing Bridge: {e}")
        tests.append(False)
    
    try:
        from hyper_agents import EventBus, EventType, EventTriggerAgent
        print(f"  ✅ Triggers (EventBus, Watchdog)")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Triggers: {e}")
        tests.append(False)
    
    try:
        from hyper_agents import Scheduler, ScheduleFrequency
        print(f"  ✅ Scheduler")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Scheduler: {e}")
        tests.append(False)
    
    try:
        from hyper_agents import AutonomousOrchestrator, WorkflowDefinition
        print(f"  ✅ Orchestrator")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Orchestrator: {e}")
        tests.append(False)
    
    try:
        from hyper_agents import AutonomyDashboard
        print(f"  ✅ Dashboard")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Dashboard: {e}")
        tests.append(False)
    
    try:
        from hyper_agents import BaseExecutor, MockExecutor, MetaExecutor
        print(f"  ✅ Executors (Mock, Meta)")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Executors: {e}")
        tests.append(False)
    
    try:
        from hyper_agents import AutonomousMarketingSystem, create_autonomous_marketing_system
        print(f"  ✅ AutonomousMarketingSystem")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ AutonomousMarketingSystem: {e}")
        tests.append(False)
    
    return all(tests)


async def test_event_bus():
    """Test del EventBus"""
    print("\n" + "="*70)
    print("  TEST 2: EVENT BUS")
    print("="*70)
    
    from hyper_agents import EventBus, Event, EventType
    
    bus = EventBus(tenant_id="test")
    
    # Suscriptor de prueba
    received_events = []
    
    async def test_handler(event):
        received_events.append(event)
    
    bus.subscribe(
        subscriber_id="test_subscriber",
        event_types=[EventType.LEAD_CREATED],
        callback=test_handler
    )
    
    # Publicar evento
    await bus.start_processing()
    
    event_id = await bus.publish_simple(
        EventType.LEAD_CREATED,
        {"lead_id": "test_123"},
        "test"
    )
    
    await asyncio.sleep(0.5)  # Esperar procesamiento
    await bus.stop_processing()
    
    print(f"  Event ID: {event_id}")
    print(f"  Eventos publicados: {bus.stats['events_published']}")
    print(f"  Eventos procesados: {bus.stats['events_processed']}")
    
    return bus.stats['events_published'] > 0


async def test_scheduler():
    """Test del Scheduler"""
    print("\n" + "="*70)
    print("  TEST 3: SCHEDULER")
    print("="*70)
    
    from hyper_agents import Scheduler, ScheduleFrequency
    from datetime import datetime, timedelta
    
    executed = []
    
    async def mock_executor(agent_id, input_data):
        executed.append(agent_id)
        class Result:
            success = True
            def to_dict(self): return {"success": True}
        return Result()
    
    scheduler = Scheduler(tenant_id="test", agent_executor=mock_executor, check_interval_seconds=1)
    
    # Programar tarea para ejecutarse inmediatamente
    task_id = scheduler.schedule_task(
        name="Test Task",
        agent_id="test_agent",
        input_data={"test": True},
        frequency=ScheduleFrequency.ONCE,
        first_run=datetime.utcnow() + timedelta(seconds=1)
    )
    
    print(f"  Task ID: {task_id}")
    print(f"  Tareas programadas: {len(scheduler.tasks)}")
    
    # No iniciar el scheduler en test para evitar delays
    
    return task_id is not None


async def test_orchestrator():
    """Test del Orchestrator"""
    print("\n" + "="*70)
    print("  TEST 4: ORCHESTRATOR")
    print("="*70)
    
    from hyper_agents import AutonomousOrchestrator
    
    async def mock_executor(agent_id, input_data):
        class Result:
            success = True
            def to_dict(self): return {"agent": agent_id, "success": True}
        return Result()
    
    orchestrator = AutonomousOrchestrator(tenant_id="test", agent_executor=mock_executor)
    
    workflows = orchestrator.list_workflows()
    print(f"  Workflows disponibles: {len(workflows)}")
    
    for w in workflows[:3]:
        print(f"    - {w['name']} ({w['steps_count']} pasos)")
    
    # Ejecutar workflow
    result = await orchestrator.execute_workflow(
        "lead_nurturing",
        {"lead_id": "test_123"}
    )
    
    print(f"\n  Workflow ejecutado: {result.status.value}")
    print(f"  Pasos completados: {result.final_output.get('steps_completed', 0) if result.final_output else 0}")
    
    return result.status.value == "completed"


async def test_dashboard():
    """Test del Dashboard"""
    print("\n" + "="*70)
    print("  TEST 5: DASHBOARD")
    print("="*70)
    
    from hyper_agents import AutonomyDashboard
    
    dashboard = AutonomyDashboard(tenant_id="test")
    
    # Registrar ejecuciones de prueba
    for i in range(5):
        dashboard.record_execution(
            agent_id=f"agent_{i}",
            success=i % 2 == 0,
            confidence=0.7 + (i * 0.05),
            decision="EXECUTE_NOW" if i % 2 == 0 else "REQUEST_REVIEW",
            execution_time_ms=100 + (i * 20)
        )
    
    # Obtener datos
    data = dashboard.get_dashboard_data()
    health = dashboard.get_system_health()
    
    print(f"  Status: {health.overall_status}")
    print(f"  Agentes activos: {data['system_health']['agents_active']}")
    print(f"  Distribución:")
    for k, v in data['autonomy_distribution'].items():
        print(f"    - {k}: {v}")
    
    return health.overall_status == "healthy"


async def test_marketing_bridge():
    """Test del Marketing Bridge con agentes reales"""
    print("\n" + "="*70)
    print("  TEST 6: MARKETING BRIDGE (36 AGENTES)")
    print("="*70)
    
    from hyper_agents import HyperMarketingBridge, MARKETING_AGENTS
    
    bridge = HyperMarketingBridge(tenant_id="credicefi")
    
    # Categorías
    categories = {}
    for a in MARKETING_AGENTS:
        cat = a["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"  Total agentes: {len(MARKETING_AGENTS)}")
    print(f"  Categorías: {len(categories)}")
    
    # Ejecutar algunos agentes
    test_agents = ["socialpostgeneratoria", "leadscoria", "campaignoptimizeria"]
    results = {"success": 0, "failed": 0}
    
    for agent_id in test_agents:
        result = await bridge.execute(
            agent_id,
            {"topic": "Test", "platform": "facebook"},
            {"skip_parallel": True}
        )
        if result.success:
            results["success"] += 1
        else:
            results["failed"] += 1
    
    print(f"\n  Resultados prueba:")
    print(f"    Exitosos: {results['success']}/{len(test_agents)}")
    
    return results["success"] > 0


async def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("  NADAKKI AI SUITE - TEST COMPLETO SISTEMA AUTÓNOMO v3.3.0")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("EventBus", test_event_bus),
        ("Scheduler", test_scheduler),
        ("Orchestrator", test_orchestrator),
        ("Dashboard", test_dashboard),
        ("Marketing Bridge", test_marketing_bridge)
    ]
    
    results = []
    for name, test_fn in tests:
        try:
            success = await test_fn()
            results.append((name, success))
        except Exception as e:
            print(f"\n  ❌ Error en {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Resumen
    print("\n" + "="*70)
    print("  RESUMEN DE TESTS")
    print("="*70)
    
    all_passed = True
    for name, success in results:
        icon = "✅" if success else "❌"
        print(f"  {icon} {name}")
        if not success:
            all_passed = False
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\n  Resultado: {passed}/{total} tests pasaron")
    
    print("\n" + "="*70)
    if all_passed:
        print("  🎉 SISTEMA AUTÓNOMO v3.3.0 FUNCIONANDO CORRECTAMENTE")
    else:
        print("  ⚠️ ALGUNOS TESTS FALLARON - REVISAR ERRORES")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
