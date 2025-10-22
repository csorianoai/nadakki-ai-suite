"""
Test local para LeadScoringIA v2.2 usando schemas.canonical.Lead.
Requisitos mínimos inferidos del modelo canónico:
- lead_id con patrón 'L-YYYYMMDD-####'
- persona (dict)
- contact (dict)
- attributes.channel requerido dentro de attributes
- events[i].ts requerido
"""

import asyncio
from datetime import datetime, timezone
from schemas.canonical import Lead, LeadScoringOutput
from agents.marketing.leadscoringia import LeadScoringIA

TENANT = "31ef24fa-84f3-4be5-abf3-42bcbde5d3d9"

def mk_lead(lead_id: str) -> Lead:
    # lead_id debe cumplir '^L-\\d{8}-\\d{4}$'
    # channel va dentro de attributes (según errores previos)
    now_iso = datetime.now(timezone.utc).isoformat()
    return Lead.model_validate({
        "tenant_id": TENANT,
        "lead_id": lead_id,
        "persona": {"type": "individual"},
        "contact": {"email": "lead@test.com"},
        "attributes": {
            "credit_score": 780,
            "income": 85000,
            "age": 38,
            "employment_years": 8,
            "channel": "search"
        },
        "events": [
            {"type": "form_submit", "ts": now_iso}
        ]
    })

async def test_basic(agent: LeadScoringIA):
    print("\nTEST 1: Scoring básico")
    lead = mk_lead(datetime.now(timezone.utc).strftime("L-%Y%m%d-0001"))
    result: LeadScoringOutput = await agent.execute(lead)
    print("  success:", result.success)
    print("  score:", result.result.get("score"))
    print("  bucket:", result.result.get("bucket"))
    print("  components:", result.result.get("components"))
    print("  latency(ms):", result.execution_time_ms)

async def test_cache(agent: LeadScoringIA):
    print("\nTEST 2: Cache (segunda llamada debería ser cacheable)")
    lead = mk_lead(datetime.now(timezone.utc).strftime("L-%Y%m%d-0002"))
    r1 = await agent.execute(lead)
    r2 = await agent.execute(lead)  # mismo lead_id + atributos -> cache hit
    print("  first_call_ms:", r1.execution_time_ms, " second_call_ms:", r2.execution_time_ms)
    print("  cache_hit_flag(second):", r2.result.get("cache_hit", False))

async def test_batch(agent: LeadScoringIA):
    print("\nTEST 3: Batch scoring")
    base = datetime.now(timezone.utc).strftime("L-%Y%m%d")
    leads = [mk_lead(f"{base}-{i:04d}") for i in range(10, 15)]
    outputs = await agent.execute_batch(leads, max_concurrent=5)
    ok = sum(1 for o in outputs if isinstance(o, LeadScoringOutput) and o.success)
    print(f"  batch size={len(outputs)} success={ok}")

async def main():
    print("\n" + "="*60)
    print("  LEADSCORINGIA v2.2 - TEST LOCAL")
    print("="*60)

    agent = LeadScoringIA(TENANT, config={
        # opcional: ajusta pesos/umbrales si quieres
        "rate_limit": {"rate": 100, "capacity": 200}
    })

    health = agent.health()
    print("Version:", agent.VERSION)
    print("Contrato:", agent.CONTRACT_VERSION)
    print("Status:", health["status"])
    print("Features activas:", sum(1 for v in health["features"].values() if v))

    await test_basic(agent)
    await test_cache(agent)
    await test_batch(agent)

if __name__ == "__main__":
    asyncio.run(main())
