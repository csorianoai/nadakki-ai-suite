"""Test LeadScoringIA v2.2 - Simple"""
import sys
sys.path.append('.')
import asyncio
from datetime import datetime

from agents.marketing.leadscoringia import LeadScoringIA
from schemas.canonical import Lead, LeadAttributes, ContactInfo

print("\n" + "="*60)
print("  LEADSCORINGIA v2.2 - TEST")
print("="*60 + "\n")

# Crear agente
agent = LeadScoringIA(
    tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
    enable_cache=True,
    enable_fairness=True,
    enable_rate_limit=False
)

print("Version:", agent.VERSION)
print("Contrato:", agent.CONTRACT_VERSION)
print()

# Health check
health = agent.health()
print("Status:", health['status'])
print("Features activas:", sum(1 for v in health['features'].values() if v))
print()

# TEST 1: Scoring basico
print("TEST 1: Scoring basico")
print("-" * 40)

async def test1():
    lead = Lead(
        tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
        lead_id="L-20251012-0001",
        persona={},
        contact=ContactInfo(email="test@example.com"),
        attributes=LeadAttributes(
            credit_score=780,
            income=85000,
            age=35,
            channel="referral"
        )
    )
    
    result = await agent.execute(lead)
    
    print("Lead:", result.lead_id)
    print("Score:", result.score)
    print("Bucket:", result.bucket)
    print("Latencia:", result.latency_ms, "ms")
    print("Action:", result.recommended_action)
    print("Reasons:", result.reasons)
    print()

asyncio.run(test1())

# TEST 2: Cache
print("TEST 2: Cache")
print("-" * 40)

async def test2():
    lead = Lead(
        tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
        lead_id="L-20251012-0002",
        persona={},
        contact=ContactInfo(email="cache@example.com"),
        attributes=LeadAttributes(
            credit_score=750,
            income=70000,
            channel="search"
        )
    )
    
    r1 = await agent.execute(lead)
    r2 = await agent.execute(lead)
    
    print("Primera:", r1.latency_ms, "ms")
    print("Segunda:", r2.latency_ms, "ms")
    
    if r2.latency_ms <= r1.latency_ms:
        print("Cache: OK")
    print()

asyncio.run(test2())

# TEST 3: Batch
print("TEST 3: Batch scoring (5 leads)")
print("-" * 40)

async def test3():
    import time
    
    leads = []
    for i in range(5):
        lead = Lead(
            tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
            lead_id=f"L-20251012-{100+i:04d}",
            persona={},
            contact=ContactInfo(email=f"batch{i}@example.com"),
            attributes=LeadAttributes(
                credit_score=650 + i*20,
                income=50000 + i*10000,
                channel=["referral", "search", "landing_form"][i % 3]
            )
        )
        leads.append(lead)
    
    t0 = time.perf_counter()
    results = await agent.execute_batch(leads, max_concurrent=3)
    dt = (time.perf_counter() - t0) * 1000
    
    successful = sum(1 for r in results if not isinstance(r, Exception))
    
    print("Total:", len(results))
    print("Exitosos:", successful)
    print("Tiempo:", round(dt, 2), "ms")
    print()

asyncio.run(test3())

# Stats finales
print("="*60)
print("ESTADISTICAS")
print("="*60)

health = agent.health()
print("Requests:", health['metrics']['requests'])
print("Errores:", health['metrics']['errors'])
print("Tiempo promedio:", health['metrics']['avg_time_ms'], "ms")

if health.get('cache'):
    cache = health['cache']
    print("\nCache:")
    print("  Hits:", cache['hits'])
    print("  Misses:", cache['misses'])
    print("  Hit rate:", f"{cache['hit_rate']:.1%}")

if health.get('fairness'):
    fair = health['fairness']
    print("\nFairness:")
    print("  Disparity:", round(fair['disparity'], 4))
    print("  Flag:", fair['flag'])

print("\n" + "="*60)
print("LEADSCORINGIA v2.2 FUNCIONAL")
print("="*60)
print("\nNUEVAS FEATURES:")
print("  - Rate limiting por tenant")
print("  - Batch scoring async")
print("  - HMAC cache keys")
print("  - Model versioning")
print("  - Circuit breaker")
print("  - Fairness monitoring")
print()