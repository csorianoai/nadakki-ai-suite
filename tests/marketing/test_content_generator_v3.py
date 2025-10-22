# filepath: tests/marketing/test_content_generator_v3.py
"""Tests para ContentGeneratorIA v3.2.0"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import asyncio
from agents.marketing.content_generator_v3 import (
    ContentGeneratorIA,
    ContentGenerationInput,
    PersonalizationData,
    create_agent_instance
)

async def test_basic():
    print("\n=== TEST 1: Generación Básica ===")
    agent = create_agent_instance("tn_test_bank")
    
    input_data = ContentGenerationInput(
        tenant_id="tn_test_bank",
        content_type="ad_copy",
        audience_segment="high_value",
        brand_tone="professional",
        key_message="Refinancia tu hipoteca con mejores tasas",
        language="es",
        jurisdiction="MX",
        variant_count=2
    )
    
    output = await agent.execute(input_data)
    
    assert len(output.variants) == 2
    print(f"✅ Generation ID: {output.generation_id}")
    print(f"✅ Variantes: {len(output.variants)}")
    print(f"✅ Compliance: {output.compliance_summary.passed}")
    
    for v in output.variants:
        print(f"  {v.variant_id}: {v.content[:60]}...")
        print(f"    CTR: {v.scores.estimated_ctr:.2%}, Compliance: {v.scores.compliance:.2f}")

async def test_variants_different_scores():
    """TEST CRÍTICO: Variantes deben tener scores DIFERENTES"""
    print("\n=== TEST 2: Scores Diferentes por Variante ===")
    agent = create_agent_instance("tn_test_bank")
    
    input_data = ContentGenerationInput(
        tenant_id="tn_test_bank",
        content_type="email_subject",
        audience_segment="mid_value",
        brand_tone="friendly",
        key_message="Oferta especial de crédito",
        language="es",
        jurisdiction="MX",
        variant_count=3
    )
    
    output = await agent.execute(input_data)
    
    ctrs = [v.scores.estimated_ctr for v in output.variants]
    brands = [v.scores.brand_alignment for v in output.variants]
    
    # Los scores DEBEN ser diferentes
    assert len(set(ctrs)) > 1, "❌ BUG: Todas las variantes tienen mismo CTR"
    assert len(set(brands)) > 1, "❌ BUG: Todas las variantes tienen mismo brand alignment"
    
    print(f"✅ CTRs únicos: {len(set(ctrs))}")
    print(f"✅ Brand alignments únicos: {len(set(brands))}")
    for i, v in enumerate(output.variants):
        print(f"  Var {i+1}: CTR={v.scores.estimated_ctr:.3f}, Brand={v.scores.brand_alignment:.3f}")

async def test_pii_masking():
    """TEST: PII debe ser enmascarado"""
    print("\n=== TEST 3: PII Masking ===")
    agent = create_agent_instance("tn_test_bank")
    
    input_data = ContentGenerationInput(
        tenant_id="tn_test_bank",
        content_type="ad_copy",
        audience_segment="high_value",
        brand_tone="professional",
        key_message="Contacta a john@example.com o llama al 8091234567",
        language="es",
        jurisdiction="MX"
    )
    
    output = await agent.execute(input_data)
    
    # El contenido NO debe tener email ni teléfono visible
    for v in output.variants:
        assert "john@example.com" not in v.content, "❌ Email no fue enmascarado"
        assert "8091234567" not in v.content, "❌ Teléfono no fue enmascarado"
        assert "[email_masked]" in v.content or "[phone_masked]" in v.content, "❌ No se aplicó masking"
    
    print(f"✅ PII fue enmascarado correctamente")
    print(f"  Contenido: {output.variants[0].content}")

async def test_cache_ttl():
    """TEST: Cache con TTL funciona"""
    print("\n=== TEST 4: Cache con TTL ===")
    agent = create_agent_instance("tn_test_bank", config={"cache_ttl_seconds": 2})
    
    input_data = ContentGenerationInput(
        tenant_id="tn_test_bank",
        content_type="ad_copy",
        audience_segment="high_value",
        brand_tone="professional",
        key_message="Test cache",
        language="es",
        jurisdiction="MX"
    )
    
    # Primera llamada
    output1 = await agent.execute(input_data)
    gen_id1 = output1.generation_id
    
    # Segunda llamada inmediata (debe usar cache)
    output2 = await agent.execute(input_data)
    gen_id2 = output2.generation_id
    
    assert gen_id1 == gen_id2, "❌ No usó cache"
    print(f"✅ Cache hit: gen_id igual")
    
    # Esperar que expire el TTL
    import time
    time.sleep(2.5)
    
    # Tercera llamada (cache expirado, debe regenerar)
    output3 = await agent.execute(input_data)
    gen_id3 = output3.generation_id
    
    assert gen_id3 != gen_id1, "❌ Usó cache expirado"
    print(f"✅ Cache expiró correctamente")
    
    metrics = agent.get_metrics()
    print(f"  Cache hits: {metrics['cache_hits']}")

async def test_autofix():
    """TEST: Auto-remediación funciona"""
    print("\n=== TEST 5: Auto-remediación ===")
    agent = create_agent_instance("tn_test_bank")
    
    input_data = ContentGenerationInput(
        tenant_id="tn_test_bank",
        content_type="ad_copy",
        audience_segment="high_value",
        brand_tone="urgent",
        key_message="Préstamo 100% garantizado sin verificación",
        language="es",
        jurisdiction="MX"
    )
    
    output = await agent.execute(input_data)
    
    # Debe haber intentado auto-fix
    has_autofix = any("autofix" in code for code in output.audit_trail.reason_codes)
    print(f"✅ Auto-fix aplicado: {has_autofix}")
    
    metrics = agent.get_metrics()
    print(f"  Autofix ratio: {metrics['autofix_ratio']}")
    
    for v in output.variants:
        print(f"  {v.variant_id}: compliance={v.scores.compliance:.2f}, flags={len(v.risk_flags)}")

async def test_circuit_breaker():
    """TEST: Circuit breaker funciona"""
    print("\n=== TEST 6: Circuit Breaker ===")
    agent = create_agent_instance("tn_test_bank")
    
    # Forzar fallos
    for i in range(6):
        agent.circuit_breaker.record_failure()
    
    status = agent.circuit_breaker.get_status()
    print(f"✅ Circuit breaker state: {status['state']}")
    print(f"  Failures: {status['failures']}")
    print(f"  Can execute: {status['can_execute']}")
    
    assert status['state'] == 'OPEN', "❌ Circuit breaker debería estar OPEN"
    
    # Resetear para no afectar otros tests
    agent.circuit_breaker.record_success()

async def run_all():
    print("╔═══════════════════════════════════════════════╗")
    print("║  TESTS CONTENTGENERATORIA v3.2.0             ║")
    print("╚═══════════════════════════════════════════════╝")
    
    try:
        await test_basic()
        await test_variants_different_scores()  # TEST CRÍTICO
        await test_pii_masking()
        await test_cache_ttl()
        await test_autofix()
        await test_circuit_breaker()
        
        print("\n" + "="*50)
        print("✅ TODOS LOS TESTS PASARON")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_all())