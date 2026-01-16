import asyncio
from hyper_agents import create_autonomous_marketing_system, EventType

async def test():
    print("="*60)
    print("  SISTEMA AUTONOMO COMPLETO - TEST FINAL")
    print("="*60)
    
    system = await create_autonomous_marketing_system("credicefi", auto_start=True, load_defaults=False)
    
    print("\nEjecutando workflow lead_nurturing...")
    result = await system.run_workflow("lead_nurturing", {"lead_id": "001"})
    print(f"Status: {result['status']}")
    
    print("\nPublicando evento...")
    await system.publish_event(EventType.LEAD_CREATED, {"lead_id": "002"})
    
    print("\nDashboard:")
    d = system.get_dashboard()
    print(f"  Agentes activos: {d['system_health']['agents_active']}")
    
    await system.stop()
    print("\n" + "="*60)
    print("  SISTEMA AUTONOMO v3.3.0 OPERATIVO")
    print("="*60)

asyncio.run(test())
