import asyncio
from hyper_agents.marketing import HyperMarketingBridge, MARKETING_AGENTS

async def test_all_agents():
    bridge = HyperMarketingBridge(tenant_id="credicefi")
    
    print("=" * 70)
    print("  TEST DE LOS 36 AGENTES DE MARKETING")
    print("=" * 70)
    
    results = {"success": [], "failed": [], "analysis_only": [], "can_execute": []}
    
    for agent in MARKETING_AGENTS:
        agent_id = agent["id"]
        result = await bridge.execute(
            agent_id,
            {"topic": "Test autonomia", "platform": "facebook", "tenant_id": "credicefi"},
            {"skip_parallel": True, "skip_ethics": True}  # Rapido
        )
        
        status = "?"
        if result.success and result.original_result.get("status") == "success":
            decision = result.original_result.get("decision", {})
            action = decision.get("action", "UNKNOWN")
            
            if action == "EXECUTE_NOW":
                results["can_execute"].append(agent_id)
                status = "EXEC"
            else:
                results["analysis_only"].append(agent_id)
                status = "ANAL"
            results["success"].append(agent_id)
        else:
            results["failed"].append(agent_id)
            status = "FAIL"
        
        print(f"  [{status}] {agent_id}")
    
    print("\n" + "=" * 70)
    print("  RESUMEN")
    print("=" * 70)
    print(f"  Total agentes: {len(MARKETING_AGENTS)}")
    print(f"  Exitosos: {len(results['success'])}")
    print(f"  Fallidos: {len(results['failed'])}")
    print(f"  Listos para EJECUTAR: {len(results['can_execute'])}")
    print(f"  Solo ANALISIS: {len(results['analysis_only'])}")
    
    if results["failed"]:
        print(f"\n  Fallidos: {results['failed']}")
    
    print("\n" + "=" * 70)
    return results

asyncio.run(test_all_agents())
