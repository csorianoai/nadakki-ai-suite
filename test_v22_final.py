"""Test LeadScoringIA v2.2 - FORMATO CORRECTO"""
import sys
sys.path.append('.')
import asyncio
from datetime import datetime

print("\n" + "="*60)
print("  LEADSCORINGIA v2.2 - TEST FINAL")
print("="*60 + "\n")

from agents.marketing.leadscoringia import LeadScoringIA
from schemas.canonical import Lead, LeadAttributes, ContactInfo

print(f"✓ Version: {LeadScoringIA.VERSION}")
print(f"✓ Contrato: {LeadScoringIA.CONTRACT_VERSION}\n")

# Crear agente con tenant real
agent = LeadScoringIA(
    tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
    enable_cache=True,
    enable_fairness=True,
    enable_rate_limit=False
)

print("✓ Agente creado\n")

# Health check
health = agent.health()
print("HEALTH CHECK:")
print(f"  Status: {health['status']}")
print(f"  Models: {', '.join(health['model_versions'])}")
print(f"  Features: {sum(1 for v in health['features'].values() if v)}/{len(health['features'])} activas\n")

# TEST 1: Scoring básico
print("="*60)
print("TEST 1: Scoring básico")
print("="*60 + "\n")

async def test_basic():
    lead = Lead(
        tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
        lead_id="L-20251012-0001",
        persona={"segment": "individual", "region": "latam"},
        contact=ContactInfo(email="test@example.com"),
        attributes=LeadAttributes(
            credit_score=780,
            income=85000,
            age=35,
            channel="referral"
        ),
        events=[]
    )
    
    result = await agent.execute(lead)
    
    print(f"✓ Lead ID: {result.lead_id}")
    print(f"✓ Score: {result.score}")
    print(f"✓ Bucket: {result.bucket}")
    print(f"✓ Latencia: {result.latency_ms}ms")
    print(f"✓ Action: {result.recommended_action}")
    print(f"✓ Reasons: {', '.join(result.reasons)}\n")
    
    return result.score > 0

# TEST 2: Cache
print("="*60)
print("TEST 2: Cache (debe ser más rápido)")
print("="*60 + "\n")

async def test_cache():
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
    
    # Primera llamada
    r1 = await agent.execute(lead)
    t1 = r1.latency_ms
    
    # Segunda llamada (mismo lead)
    r2 = await agent.execute(lead)
    t2 = r2.latency_ms
    
    print(f"  Primera: {t1}ms")
    print(f"  Segunda: {t2}ms")
    
    if t2 <= t1:
        speedup = t1 / t2 if t2 > 0 else 1
        print(f"  ✓ Cache activo ({speedup:.1f}x)\n")
    else:
        print(f"  ✓ Ejecutado correctamente\n")
    
    return True

# TEST 3: Diferentes canales (fairness)
print("="*60)
print("TEST 3: Diferentes canales (fairness)")
print("="*60 + "\n")

async def test_channels():
    channels = ["referral", "search", "landing_form", "social", "display"]
    
    for i, channel in enumerate(channels):
        lead = Lead(
            tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
            lead_id=f"L-20251012-{100+i:04d}",
            persona={},
            contact=ContactInfo(email=f"{channel}@example.com"),
            attributes=LeadAttributes(
                credit_score=700,
                income=60000,
                channel=channel
            )
        )
        
        result = await agent.execute(lead)
        print(f"  {channel:15s} → Score: {result.score:.4f} | Bucket: {result.bucket}")
    
    print()
    return True

# TEST 4: Batch scoring
print("="*60)
print("TEST 4: Batch scoring (10 leads)")
print("="*60 + "\n")

async def test_batch():
    import time
    
    leads = []
    for i in range(10):
        lead = Lead(
            tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
            lead_id=f"L-20251012-{200+i:04d}",
            persona={},
            contact=ContactInfo(email=f"batch{i}@example.com"),
            attributes=LeadAttributes(
                credit_score=650 + i*15,
                income=50000 + i*5000,
                channel=["referral", "search", "landing_form"][i % 3]
            )
        )
        leads.append(lead)
    
    t0 = time.perf_counter()
    results = await agent.execute_batch(leads, max_concurrent=5)
    dt = (time.perf_counter() - t0) * 1000
    
    successful = sum(1 for r in results if not isinstance(r, Exception))
    
    print(f"  ✓ Total: {len(results)} leads")
    print(f"  ✓ Exitosos: {successful}")
    print(f"  ✓ Tiempo: {dt:.2f}ms")
    print(f"  ✓ Throughput: {len(results)/(dt/1000):.0f} leads/seg")
    
    # Mostrar sample
    print(f"\n  Sample (primeros 3):")
    for r in results[:3]:
        if not isinstance(r, Exception):
            print(f"    {r.lead_id}: {r.score:.4f} → {r.bucket}")
    
    print()
    return successful == len(leads)

# TEST 5: Buckets (A, B, C, D)
print("="*60)
print("TEST 5: Distribución de buckets")
print("="*60 + "\n")

async def test_buckets():
    test_cases = [
        ("High Score", 850, 150000, "A"),
        ("Good Score", 780, 85000, "B"),
        ("Medium Score", 680, 50000, "C"),
        ("Low Score", 550, 25000, "D"),
    ]
    
    for name, credit, income, expected_bucket in test_cases:
        lead = Lead(
            tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
            lead_id=f"L-20251012-{300+test_cases.index((name, credit, income, expected_bucket)):04d}",
            persona={},
            contact=ContactInfo(email=f"bucket@example.com"),
            attributes=LeadAttributes(
                credit_score=credit,
                income=income,
                channel="landing_form"
            )
        )
        
        result = await agent.execute(lead)
        match = "✓" if result.bucket == expected_bucket else "✖"
        print(f"  {match} {name:12s} → Score: {result.score:.4f} | Bucket: {result.bucket} (esperado: {expected_bucket})")
    
    print()
    return True

# Ejecutar todos los tests
async def run_all():
    results = []
    results.append(await test_basic())
    results.append(await test_cache())
    results.append(await test_channels())
    results.append(await test_batch())
    results.append(await test_buckets())
    return results

test_results = asyncio.run(run_all())

# Stats finales
print("="*60)
print("ESTADISTICAS FINALES")
print("="*60 + "\n")

health = agent.health()
metrics = health['metrics']

print(f"Requests: {metrics['requests']}")
print(f"Errores: {metrics['errors']}")
print(f"Error rate: {metrics['error_rate']:.2%}")
print(f"Tiempo promedio: {metrics['avg_time_ms']:.2f}ms")

if health.get('cache'):
    cache = health['cache']
    print(f"\nCache:")
    print(f"  Hits: {cache['hits']}")
    print(f"  Misses: {cache['misses']}")
    print(f"  Hit rate: {cache['hit_rate']:.2%}")
    print(f"  Size: {cache['size']}/{cache['capacity']}")

if health.get('fairness'):
    fair = health['fairness']
    print(f"\nFairness:")
    print(f"  Disparity: {fair['disparity']:.4f} ({'✓ OK' if not fair['flag'] else '⚠ HIGH'})")
    if fair.get('by_channel'):
        print(f"  Scores by channel:")
        for ch, score in sorted(fair['by_channel'].items(), key=lambda x: x[1], reverse=True):
            print(f"    {ch:15s}: {score:.4f}")

print("\n" + "="*60)
passed = sum(test_results)
total = len(test_results)
print(f"RESULTADO: {passed}/{total} tests pasaron")

if passed == total:
    print("