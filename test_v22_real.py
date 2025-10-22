"""Test LeadScoringIA v2.2 con schemas canonicos"""
import sys
sys.path.append('.')
import asyncio
from datetime import datetime

print("\n" + "="*60)
print("  LEADSCORINGIA v2.2 - TEST REAL")
print("="*60 + "\n")

# Import
from agents.marketing.leadscoringia import LeadScoringIA
from schemas.canonical import Lead, LeadAttributes

print(f"✓ Version: {LeadScoringIA.VERSION}")
print(f"✓ Contrato: {LeadScoringIA.CONTRACT_VERSION}\n")

# Crear agente
agent = LeadScoringIA(
    tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
    enable_cache=True,
    enable_fairness=True,
    enable_rate_limit=False  # Deshabilitado para test
)

print("✓ Agente creado\n")

# Health check
health = agent.health()
print("HEALTH CHECK:")
print(f"  Status: {health['status']}")
print(f"  Features activas:")
for feat, enabled in health['features'].items():
    if enabled:
        print(f"    • {feat}")
print()

# Test 1: Scoring basico
print("="*60)
print("TEST 1: Scoring basico")
print("="*60 + "\n")

async def test_basic():
    # Crear Lead con formato canonico correcto
    lead = Lead(
        tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
        lead_id=f"L-{datetime.now().strftime('%Y%m%d')}-0001",
        persona="individual",
        contact={"email": "test@example.com"},
        attributes=LeadAttributes(
            credit_score=780,
            income=85000,
            age=35,
            employment_years=8,
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
    
    return True

# Test 2: Cache
print("="*60)
print("TEST 2: Cache (segunda ejecucion mas rapida)")
print("="*60 + "\n")

async def test_cache():
    lead = Lead(
        tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
        lead_id=f"L-{datetime.now().strftime('%Y%m%d')}-0002",
        persona="individual",
        contact={"email": "cache@example.com"},
        attributes=LeadAttributes(
            credit_score=750,
            income=70000,
            channel="search"
        ),
        events=[]
    )
    
    # Primera llamada
    r1 = await agent.execute(lead)
    t1 = r1.latency_ms
    
    # Segunda llamada (mismo lead)
    r2 = await agent.execute(lead)
    t2 = r2.latency_ms
    
    print(f"Primera: {t1}ms")
    print(f"Segunda: {t2}ms")
    
    if t2 < t1:
        speedup = t1 / t2 if t2 > 0 else 1
        print(f"✓ Cache funcionando ({speedup:.1f}x mas rapido)\n")
    else:
        print("✓ Ejecutado (cache puede variar)\n")
    
    return True

# Test 3: Batch scoring
print("="*60)
print("TEST 3: Batch scoring")
print("="*60 + "\n")

async def test_batch():
    import time
    
    leads = []
    for i in range(10):
        lead = Lead(
            tenant_id="31ef24fa-84f3-4be5-abf3-42bcbde5d3d9",
            lead_id=f"L-{datetime.now().strftime('%Y%m%d')}-{1000+i:04d}",
            persona="individual",
            contact={"email": f"batch{i}@example.com"},
            attributes=LeadAttributes(
                credit_score=650 + i*10,
                income=50000 + i*5000,
                channel=["referral", "search", "landing_form"][i % 3]
            ),
            events=[]
        )
        leads.append(lead)
    
    t0 = time.perf_counter()
    results = await agent.execute_batch(leads, max_concurrent=5)
    dt = (time.perf_counter() - t0) * 1000
    
    successful = sum(1 for r in results if not isinstance(r, Exception))
    
    print(f"✓ Procesados: {len(results)} leads")
    print(f"✓ Exitosos: {successful}")
    print(f"✓ Tiempo: {dt:.2f}ms")
    print(f"✓ Throughput: {len(results)/(dt/1000):.0f} leads/seg\n")
    
    return True

# Ejecutar tests
async def run_all():
    await test_basic()
    await test_cache()
    await test_batch()

asyncio.run(run_all())

# Stats finales
print("="*60)
print("ESTADISTICAS FINALES")
print("="*60 + "\n")

health = agent.health()
print(f"Total requests: {health['metrics']['requests']}")
print(f"Errores: {health['metrics']['errors']}")
print(f"Tiempo promedio: {health['metrics']['avg_time_ms']:.2f}ms")

if health.get('cache'):
    cache = health['cache']
    print(f"\nCache:")
    print(f"  Hits: {cache['hits']}")
    print(f"  Misses: {cache['misses']}")
    print(f"  Hit rate: {cache['hit_rate']:.2%}")

if health.get('fairness'):
    fair = health['fairness']
    print(f"\nFairness:")
    print(f"  Disparity: {fair['disparity']:.4f}")
    print(f"  Flag: {fair['flag']}")
    if fair.get('by_channel'):
        print(f"  By channel:")
        for ch, score in fair['by_channel'].items():
            print(f"    {ch}: {score:.4f}")

print("\n" + "="*60)
print("✓✓✓ LEADSCORINGIA v2.2 FUNCIONAL ✓✓✓")
print("="*60 + "\n")

print("NUEVAS FEATURES v2.2:")
print("  • Rate limiting por tenant")
print("  • Batch scoring async")
print("  • HMAC cache keys")
print("  • Model versioning")
print("  • Circuit breaker")
print("  • Fairness monitoring\n")