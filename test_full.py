import asyncio
import json
from hyper_agents.marketing import HyperMarketingBridge

async def test():
    bridge = HyperMarketingBridge(tenant_id="credicefi")
    
    result = await bridge.execute(
        "socialpostgeneratoria",
        {
            "topic": "Promocion de prestamos personales",
            "platform": "facebook",
            "tone": "profesional"
        }
    )
    
    print("=== RESULTADO COMPLETO ===")
    print(f"Success del bridge: {result.success}")
    print(f"Error: {result.error}")
    print(f"\n=== RESULTADO DEL AGENTE REAL ===")
    print(json.dumps(result.original_result, indent=2, default=str)[:1500])

asyncio.run(test())
