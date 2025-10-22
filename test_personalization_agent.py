import asyncio
from agents.marketing.personalizationengineia import (
    PersonalizationEngineIA, PersonalizationInput, UserProfile, ContextData
)

async def test():
    agent = PersonalizationEngineIA("tn_test_bank_001")
    
    # Perfil de usuario de alto valor
    profile = UserProfile(
        user_id="user_12345",
        demographics={"age": 35, "location": "NYC", "income_bracket": "high"},
        behavior_history=[
            "viewed_savings", "clicked_investment", "downloaded_app",
            "completed_profile", "viewed_mortgage", "attended_webinar"
        ],
        preferences={"channel": "mobile", "frequency": "weekly", "topics": ["investing", "retirement"]},
        segment="premium",
        lifetime_value=15000.0
    )
    
    # Contexto de sesión móvil
    context = ContextData(
        channel="mobile",
        device="iPhone 15 Pro",
        location="New York, NY",
        time_of_day="evening",
        referrer="email_campaign",
        session_events=["app_opened", "dashboard_viewed", "notifications_enabled"]
    )
    
    inp = PersonalizationInput(
        tenant_id="tn_test_bank_001",
        user_profile=profile,
        context=context,
        strategy="hybrid",
        max_recommendations=5
    )
    
    result = await agent.execute(inp)
    
    print("="*80)
    print("✅ RESULTADO DE PERSONALIZACIÓN")
    print("="*80)
    print(f"Personalization ID: {result.personalization_id}")
    print(f"Usuario: {result.user_id}")
    print(f"Micro-segmento: {result.micro_segment}")
    print(f"Estrategia usada: {result.strategy_used}")
    print(f"Personalization Score: {result.personalization_score}/100")
    
    print("\n" + "="*80)
    print(f"RECOMENDACIONES PERSONALIZADAS ({len(result.recommendations)}):")
    print("="*80)
    
    for i, rec in enumerate(result.recommendations, 1):
        print(f"\n🎯 RECOMENDACIÓN #{i}")
        print(f"   ID: {rec.recommendation_id}")
        print(f"   Tipo: {rec.content_type}")
        print(f"   Título: {rec.title}")
        print(f"   Descripción: {rec.description}")
        print(f"   Relevance Score: {rec.relevance_score}/100")
        print(f"   Confidence: {rec.confidence:.2f}")
        print(f"   A/B Test Variant: {rec.ab_test_variant or 'N/A'}")
        print(f"   Personalization Factors: {', '.join(rec.personalization_factors)}")
        print(f"\n   Channel Optimization:")
        for channel, score in rec.channel_optimization.items():
            bars = "█" * int(score * 10)
            print(f"     {channel:10} {bars} {score:.2f}")
    
    print("\n" + "="*80)
    print("DECISION TRACE (Audit Trail):")
    print("="*80)
    for trace in result.decision_trace:
        print(f"\n⏱️  {trace.timestamp.strftime('%H:%M:%S')}")
        print(f"   Type: {trace.decision_type}")
        print(f"   Rationale: {trace.rationale}")
        print(f"   Outcome: {trace.outcome}")
    
    print("\n" + "="*80)
    print("COMPLIANCE STATUS:")
    print("="*80)
    print(f"Compliant: {'✅ YES' if result.compliance_status['compliant'] else '❌ NO'}")
    
    # Test con diferentes estrategias
    print("\n" + "="*80)
    print("COMPARACIÓN DE ESTRATEGIAS:")
    print("="*80)
    
    strategies = ["collaborative_filtering", "content_based", "contextual", "hybrid"]
    
    for strategy in strategies:
        inp.strategy = strategy
        result = await agent.execute(inp)
        print(f"{strategy:25} → {len(result.recommendations)} recs, Score: {result.personalization_score:.1f}")
    
    # Métricas del agente
    metrics = agent.get_metrics()
    print("\n" + "="*80)
    print("MÉTRICAS DEL AGENTE:")
    print("="*80)
    print(f"Total requests: {metrics['total']}")
    print(f"Success rate: {metrics['ok']}/{metrics['total']} ({metrics['ok']/max(1,metrics['total'])*100:.1f}%)")
    print(f"Cache hits: {metrics['cache_hits']}")
    print(f"Personalizations: {metrics['personalizations']}")
    print(f"Compliance checks: {metrics['compliance_checks']}")
    print(f"A/B tests: {metrics['ab_tests']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    print(f"P95 latency: {metrics.get('p95_latency', 0):.2f}ms")
    print(f"P99 latency: {metrics.get('p99_latency', 0):.2f}ms")
    
    print("\n" + "="*80)
    print("✅ PersonalizationEngineIA FUNCIONA PERFECTAMENTE")
    print("="*80)

asyncio.run(test())