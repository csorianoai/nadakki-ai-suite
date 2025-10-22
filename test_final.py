"""
TEST COMPLETO para LeadScoringIA v2.2.1
"""

import asyncio
import time
from agents.marketing.leadscoringia import LeadScoringIA, Lead, LeadAttributes

async def test_basic():
    """Test básico de funcionamiento"""
    print("=" * 50)
    print("TEST 1: Scoring básico")
    print("=" * 50)
    
    agent = LeadScoringIA(tenant_id="test_tenant_001")
    
    # Health check
    health = agent.health()
    print(f"✓ Status: {health['status']}")
    print(f"✓ Version: {health['version']}")
    print(f"✓ Features: {sum(health['features'].values())} activas")
    
    # Create test lead
    lead = Lead(
        lead_id="L-20251012-0001",
        tenant_id="test_tenant_001",
        channel="referral",
        attributes=LeadAttributes(
            credit_score=750,
            income=65000,
            age=35,
            employment_years=5
        ),
        events=[
            {"type": "form_submit", "timestamp": "2024-01-01T10:00:00Z"},
            {"type": "click", "timestamp": "2024-01-01T10:01:00Z"}
        ]
    )
    
    try:
        result = await agent.execute(lead)
        print(f"✓ Lead: {result.result['lead_id']}")
        print(f"✓ Score: {result.result['score']}")
        print(f"✓ Bucket: {result.result['bucket']}")
        print(f"✓ Action: {result.result['recommended_action']}")
        print(f"✓ Reasons: {result.result['reasons']}")
        print(f"✓ Latencia: {result.execution_time_ms}ms")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_cache():
    """Test de cache performance"""
    print("\n" + "=" * 50)
    print("TEST 2: Cache performance")
    print("=" * 50)
    
    agent = LeadScoringIA(tenant_id="cache_test")
    
    lead = Lead(
        lead_id="cache_test_001",
        tenant_id="cache_test",
        attributes=LeadAttributes(credit_score=680, income=55000)
    )
    
    # First execution
    t0 = time.time()
    result1 = await agent.execute(lead)
    time1 = time.time() - t0
    
    # Second execution (should be faster due to cache)
    t0 = time.time()
    result2 = await agent.execute(lead)
    time2 = time.time() - t0
    
    print(f"✓ Primera ejecución: {time1*1000:.2f}ms")
    print(f"✓ Segunda ejecución: {time2*1000:.2f}ms")
    print(f"✓ Speedup: {time1/time2:.1f}x")
    
    # Verify same results
    same_score = result1.result['score'] == result2.result['score']
    print(f"✓ Scores consistentes: {same_score}")
    
    return time2 < time1 and same_score

async def test_batch():
    """Test de batch processing"""
    print("\n" + "=" * 50)
    print("TEST 3: Batch scoring")
    print("=" * 50)
    
    agent = LeadScoringIA(tenant_id="batch_test")
    
    # Create multiple leads
    leads = []
    for i in range(5):
        leads.append(Lead(
            lead_id=f"batch_lead_{i:03d}",
            tenant_id="batch_test",
            attributes=LeadAttributes(
                credit_score=600 + i * 30,
                income=30000 + i * 8000
            )
        ))
    
    try:
        results = await agent.execute_batch(leads)
        success_count = sum(1 for r in results if r.success)
        
        print(f"✓ Procesados: {len(leads)} leads")
        print(f"✓ Exitosos: {success_count}/{len(leads)}")
        
        # Show first 3 results
        for i, result in enumerate(results[:3]):
            if result.success:
                print(f"  Lead {i}: score={result.result['score']}, bucket={result.result['bucket']}")
        
        return success_count == len(leads)
    except Exception as e:
        print(f"✗ Error en batch: {e}")
        return False

async def run_all_tests():
    """Ejecutar todos los tests"""
    print("🚀 LEADSCORINGIA v2.2.1 - TEST COMPLETO")
    print("=" * 60)
    
    # Run tests
    test1_ok = await test_basic()
    test2_ok = await test_cache()
    test3_ok = await test_batch()
    
    # Summary
    print("\n" + "=" * 60)
    print("RESUMEN FINAL:")
    print(f"  Test básico: {'✓ PASÓ' if test1_ok else '✗ FALLÓ'}")
    print(f"  Test cache:  {'✓ PASÓ' if test2_ok else '✗ FALLÓ'}")
    print(f"  Test batch:  {'✓ PASÓ' if test3_ok else '✗ FALLÓ'}")
    
    all_passed = test1_ok and test2_ok and test3_ok
    print(f"  RESULTADO: {'🎉 TODOS LOS TESTS PASARON' if all_passed else '💥 ALGUNOS TESTS FALLARON'}")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
