import asyncio
from hyper_agents.marketing import HyperMarketingBridge

async def test():
    bridge = HyperMarketingBridge(tenant_id="credicefi")
    agents = bridge.get_available_agents()
    
    print(f"\n=== 36 AGENTES DE MARKETING ===")
    categories = {}
    for a in agents:
        cat = a["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print(f"\nProbando orchestrator...")
    result = await bridge.execute("campaignstrategyorchestrator", {"campaign": "test"})
    print(f"  Success: {result.success}")
    if result.parallel_thoughts:
        print(f"  Consenso: {result.parallel_thoughts.get('consensus_level', 0):.2f}")

asyncio.run(test())
