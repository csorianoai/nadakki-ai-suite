import asyncio
from hyper_agents.marketing import HyperMarketingBridge

async def test():
    bridge = HyperMarketingBridge(tenant_id="credicefi")
    
    print("Probando socialpostgeneratoria (agente REAL)...")
    result = await bridge.execute(
        "socialpostgeneratoria",
        {
            "topic": "Promocion de prestamos personales",
            "platform": "facebook",
            "tone": "profesional",
            "tenant_id": "credicefi"
        }
    )
    
    print(f"Success: {result.success}")
    print(f"Agent: {result.agent_name}")
    if result.parallel_thoughts:
        print(f"Consenso: {result.parallel_thoughts.get('consensus_level', 0):.2f}")
    if result.original_result:
        print(f"Status: {result.original_result.get('status', 'N/A')}")
        if result.original_result.get("result"):
            print("Contenido generado: SI")
            print(f"Keys: {list(result.original_result.get('result', {}).keys())}")

asyncio.run(test())
