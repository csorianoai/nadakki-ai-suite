import asyncio
from agents.marketing.socialpostgeneratoria import SocialPostGeneratorIA, SocialPostInput

async def test():
    agent = SocialPostGeneratorIA("tn_test_bank_001")
    
    inp = SocialPostInput(
        tenant_id="tn_test_bank_001",
        platform="instagram",
        post_tone="motivational",
        content_type="image_post",
        key_message="Tu futuro financiero empieza hoy con decisiones inteligentes",
        target_audience="millennials",
        call_to_action="Descubre cómo empezar ➡️",
        include_hashtags=True,
        variant_count=3
    )
    
    result = await agent.execute(inp)
    print("RESULTADO:", result.generation_id)
    print("Plataforma:", result.platform)
    print("Variantes:", len(result.variants))
    print("Recomendada:", result.recommended_variant)
    
    for variant in result.variants:
        print(f"\n{variant.variant_id}:")
        print(f"  Caption: {variant.caption[:80]}...")
        print(f"  Hashtags: {' '.join(variant.hashtags[:3])}")
        print(f"  Engagement: {variant.estimated_engagement:.2%}")
        if variant.compliance_flags:
            print(f"  ⚠️  Flags: {variant.compliance_flags}")
    
    print(f"\nTips: {result.posting_tips[0]}")
    
    metrics = agent.get_metrics()
    print(f"\nMÉTRICAS: {metrics['ok']}/{metrics['total']}")
    
    assert len(result.variants) == 3
    print("\n✅ SocialPostGeneratorIA funciona")

asyncio.run(test())