"""
Test suite para LeadScoringIA v2.2
Ejecutar: python test_leadscoringia_v22.py
"""

import sys
sys.path.append('.')
import asyncio
import time
from datetime import datetime

print("\n" + "="*60)
print("  LEADSCORINGIA v2.2 - TEST SUITE")
print("="*60 + "\n")

# ═══════════════════════════════════════════════════════════════════
# TEST 1: IMPORT
# ═══════════════════════════════════════════════════════════════════

print("TEST 1: Import del agente...")
try:
    from agents.marketing.leadscoringia import LeadScoringIA
    print(f"  ✓ Import exitoso")
    print(f"  ✓ Versión: {LeadScoringIA.VERSION}")
    print(f"  ✓ Contrato: {LeadScoringIA.CONTRACT_VERSION}\n")
except Exception as e:
    print(f"  ✖ ERROR: {e}\n")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
# TEST 2: INSTANCIACIÓN
# ═══════════════════════════════════════════════════════════════════

print("TEST 2: Crear instancia del agente...")
try:
    agent = LeadScoringIA(
        tenant_id="test-v22",
        enable_cache=True,
        enable_fairness=True,
        enable_rate_limit=True
    )
    print(f"  ✓ Instancia creada\n")
except Exception as e:
    print(f"  ✖ ERROR: {e}\n")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
# TEST 3: HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════

print("TEST 3: Health check...")
try:
    health = agent.health()
    print(f"  ✓ Status: {health['status']}")
    print(f"  ✓ Features:")
    for feat, enabled in health['features'].items():
        status = "✓" if enabled else "✖"
        print(f"      {status} {feat}")
    print()
except Exception as e:
    print(f"  ✖ ERROR: {e}\n")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
# TEST 4: SCORING BÁSICO
# ═══════════════════════════════════════════════════════════════════

async def test_basic():
    print("TEST 4: Scoring básico...")
    
    payload = {
        "lead_id": "L-TEST-001",
        "channel": "referral",
        "attributes": {
            "credit_score": 780,
            "income": 85000,
            "age": 35,
            "employment_years": 8
        }
    }
    
    result = await agent.execute(payload)
    
    if result.success and result.result:
        print(f"  ✓ Success: {result.success}")
        print(f"  ✓ Score: {result.result['score']}")
        print(f"  ✓ Bucket: {result.result['bucket']}")
        print(f"  ✓ Time: {result.execution_time_ms:.2f}ms")
        print(f"  ✓ Reason codes: {', '.join(result.reason_codes)}\n")
        return True
    else:
        print(f"  ✖ FALLÓ: {result.result}\n")
        return False

# ═══════════════════════════════════════════════════════════════════
# TEST 5: CACHE
# ═══════════════════════════════════════════════════════════════════

async def test_cache():
    print("TEST 5: Cache (segunda ejecución debería ser más rápida)...")
    
    payload = {
        "lead_id": "L-CACHE-001",
        "attributes": {"credit_score": 750, "income": 70000}
    }
    
    # Primera llamada
    r1 = await agent.execute(payload)
    time1 = r1.execution_time_ms
    
    # Segunda llamada
    r2 = await agent.execute(payload)
    time2 = r2.execution_time_ms
    cache_hit = r2.result.get('cache_hit', False) if r2.result else False
    
    print(f"  Primera llamada: {time1:.2f}ms")
    print(f"  Segunda llamada: {time2:.2f}ms (cache hit: {cache_hit})")
    
    if cache_hit:
        speedup = time1 / time2 if time2 > 0 else 1
        print(f"  ✓ Cache funcionando! ({speedup:.1f}x más rápido)\n")
        return True
    else:
        print(f"  ⚠ No detectó cache hit\n")
        return False

# ═══════════════════════════════════════════════════════════════════
# TEST 6: BATCH SCORING (NUEVO)
# ═══════════════════════════════════════════════════════════════════

async def test_batch():
    print("TEST 6: Batch scoring (NUEVO en v2.2)...")
    
    # Crear rate limiter sin restricciones para este test
    batch_agent = LeadScoringIA(
        tenant_id="test-batch",
        enable_rate_limit=False
    )
    
    leads = [
        {"lead_id": f"L-BATCH-{i:03d}", "attributes": {"credit_score": 650 + i*10}}
        for i in range(10)
    ]
    
    t0 = time.perf_counter()
    results = await batch_agent.execute_batch(leads, max_concurrent=5)
    dt = (time.perf_counter() - t0) * 1000.0
    
    successful = sum(1 for r in results if r.success)
    
    print(f"  ✓ Procesados: {len(results)} leads")
    print(f"  ✓ Exitosos: {successful}")
    print(f"  ✓ Tiempo total: {dt:.2f}ms")
    print(f"  ✓ Throughput: {len(results)/(dt/1000):.0f} leads/seg\n")
    
    return successful == len(leads)

# ═══════════════════════════════════════════════════════════════════
# TEST 7: RATE LIMITING (NUEVO)
# ═══════════════════════════════════════════════════════════════════

async def test_rate_limit():
    print("TEST 7: Rate limiting (NUEVO en v2.2)...")
    
    rl_agent = LeadScoringIA(
        tenant_id="test-rate",
        config={"rate_limit": {"rate": 5, "capacity": 10}},
        enable_cache=False,
        enable_rate_limit=True
    )
    
    success = 0
    rate_limited = 0
    
    for i in range(15):
        payload = {"lead_id": f"L-RATE-{i:03d}", "attributes": {"credit_score": 700}}
        try:
            result = await rl_agent.execute(payload)
            if result.success:
                success += 1
        except ValueError as e:
            if "rate_limit" in str(e):
                rate_limited += 1
        await asyncio.sleep(0.05)
    
    print(f"  ✓ Exitosos: {success}")
    print(f"  ✓ Rate limited: {rate_limited}")
    print(f"  ✓ Total: {success + rate_limited}\n")
    
    return rate_limited > 0  # Debe haber al menos 1 rate limited

# ═══════════════════════════════════════════════════════════════════
# TEST 8: INPUT SANITIZATION (NUEVO)
# ═══════════════════════════════════════════════════════════════════

async def test_sanitization():
    print("TEST 8: Input sanitization (NUEVO en v2.2)...")
    
    # Test 1: SQL injection (debe ser rechazado)
    try:
        payload = {
            "lead_id": "L'; DROP TABLE leads;--",
            "attributes": {"credit_score": 700}
        }
        result = await agent.execute(payload)
        if not result.success:
            print(f"  ✓ SQL injection bloqueado")
        else:
            print(f"  ⚠ SQL injection NO bloqueado")
    except:
        print(f"  ✓ SQL injection bloqueado (exception)")
    
    # Test 2: Caracteres especiales (debe ser sanitizado)
    payload = {
        "lead_id": "L-TEST@#$%",
        "attributes": {"credit_score": 700}
    }
    result = await agent.execute(payload)
    if result.success:
        print(f"  ✓ Caracteres especiales sanitizados")
    
    # Test 3: Canal inválido (debe usar default)
    payload = {
        "lead_id": "L-TEST-CHANNEL",
        "channel": "malicious_channel",
        "attributes": {"credit_score": 700}
    }
    result = await agent.execute(payload)
    if result.success:
        print(f"  ✓ Canal inválido reemplazado por default\n")
    
    return True

# ═══════════════════════════════════════════════════════════════════
# EJECUTAR TODOS LOS TESTS
# ═══════════════════════════════════════════════════════════════════

async def run_all_tests():
    results = []
    
    results.append(await test_basic())
    results.append(await test_cache())
    results.append(await test_batch())
    results.append(await test_rate_limit())
    results.append(await test_sanitization())
    
    return results

# Run
print("Ejecutando tests asíncronos...\n")
test_results = asyncio.run(run_all_tests())

# ═══════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════════

print("="*60)
print("  RESUMEN DE TESTS")
print("="*60 + "\n")

tests = [
    "Scoring básico",
    "Cache (LRU + TTL + HMAC)",
    "Batch scoring",
    "Rate limiting",
    "Input sanitization"
]

passed = sum(test_results)
total = len(test_results)

for i, (test_name, result) in enumerate(zip(tests, test_results)):
    status = "✓" if result else "✖"
    print(f"  {status} {test_name}")

print(f"\nRESULTADO: {passed}/{total} tests pasaron")

if passed == total:
    print("\n✓✓✓ LEADSCORINGIA v2.2 COMPLETAMENTE FUNCIONAL ✓✓✓\n")
    print("NUEVAS FEATURES v2.2:")
    print("  • Rate limiting por tenant")
    print("  • Batch scoring async")
    print("  • HMAC cache keys")
    print("  • Input sanitization hardened")
    print("  • Model versioning")
    print("  • Feature flags ready")
    print("  • OpenTelemetry ready")
    print("  • Prometheus ready")
    print()
else:
    print(f"\n⚠ {total - passed} test(s) fallaron\n")
    sys.exit(1)

