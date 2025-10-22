"""
TEST SIMPLE de verificación - LeadScoringIA
"""

import asyncio
from agents.marketing.leadscoringia import LeadScoringIA

async def simple_test():
    print("🧪 TEST SIMPLE DE VERIFICACIÓN")
    print("=" * 40)
    
    # Crear agente
    agent = LeadScoringIA(tenant_id="simple_test")
    
    # Health check
    health = agent.health()
    print(f"✓ Agent: {health['agent']}")
    print(f"✓ Version: {health['version']}")
    print(f"✓ Status: {health['status']}")
    
    # Test con datos simples
    test_data = {
        "lead_id": "simple_test_001",
        "tenant_id": "simple_test",
        "attributes": {
            "credit_score": 700,
            "income": 50000
        }
    }
    
    try:
        result = await agent.execute(test_data)
        if result.success:
            print(f"✓ Score calculado: {result.result['score']}")
            print(f"✓ Bucket: {result.result['bucket']}")
            print(f"✓ Tiempo: {result.execution_time_ms}ms")
            print("🎉 ¡AGENTE FUNCIONANDO CORRECTAMENTE!")
            return True
        else:
            print(f"✗ Error: {result.result}")
            return False
    except Exception as e:
        print(f"✗ Excepción: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_test())
    exit(0 if success else 1)
