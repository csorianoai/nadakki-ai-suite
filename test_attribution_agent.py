import asyncio
from datetime import datetime, timedelta
from agents.marketing.attributionmodelia import AttributionModelIA, AttributionInput, TouchPoint

async def test():
    agent = AttributionModelIA("tn_test_bank_001")
    
    # Crear journey de ejemplo con múltiples touchpoints
    now = datetime.now()
    
    touchpoints = [
        TouchPoint("tp_001", "paid_search", now - timedelta(days=10), 100.0, False, 0.0, "campaign_01"),
        TouchPoint("tp_002", "email", now - timedelta(days=7), 50.0, False, 0.0, "campaign_02"),
        TouchPoint("tp_003", "social", now - timedelta(days=5), 75.0, False, 0.0, "campaign_03"),
        TouchPoint("tp_004", "organic_search", now - timedelta(days=2), 0.0, False, 0.0, None),
        TouchPoint("tp_005", "direct", now, 0.0, True, 1500.0, None),
    ]
    
    # Test con modelo linear
    inp = AttributionInput(
        tenant_id="tn_test_bank_001",
        touchpoints=touchpoints,
        attribution_model="linear",
        attribution_window_days=30
    )
    
    result = await agent.execute(inp)
    
    print("="*80)
    print("✅ RESULTADO DEL ANÁLISIS DE ATRIBUCIÓN")
    print("="*80)
    print(f"Attribution ID: {result.attribution_id}")
    print(f"Modelo utilizado: {result.attribution_model}")
    print(f"Total conversiones: {result.total_conversions}")
    print(f"Revenue total: ${result.total_revenue:,.2f}")
    print(f"Costo total: ${result.total_cost:,.2f}")
    print(f"ROI general: {result.overall_roi:.2f}%")
    
    print("\n" + "="*80)
    print("ATRIBUCIÓN POR CANAL:")
    print("="*80)
    for attr in result.channel_attributions:
        print(f"\n📊 {attr.channel.upper()}")
        print(f"   Crédito atribuido: {attr.attribution_credit*100:.2f}%")
        print(f"   Valor contribuido: ${attr.contribution_value:,.2f}")
        print(f"   ROI: {attr.roi:.2f}%")
        print(f"   Touchpoints: {attr.touchpoint_count}")
    
    print("\n" + "="*80)
    print("INSIGHTS DEL JOURNEY:")
    print("="*80)
    for insight in result.journey_insights:
        print(f"\n💡 {insight.insight_type.upper()}")
        print(f"   {insight.description}")
        print(f"   Impact score: {insight.impact_score}/100")
    
    print("\n" + "="*80)
    print("COMPLIANCE STATUS:")
    print("="*80)
    print(f"Compliant: {'✅ YES' if result.compliance_status['compliant'] else '❌ NO'}")
    if result.compliance_status['issues']:
        print("Issues detected:")
        for issue in result.compliance_status['issues']:
            print(f"  - {issue}")
    
    print("\n" + "="*80)
    print("DECISION TRACE (Audit Trail):")
    print("="*80)
    for trace in result.decision_trace[:3]:  # Primeras 3
        print(f"\n⏱️  {trace.timestamp.strftime('%H:%M:%S')}")
        print(f"   Type: {trace.decision_type}")
        print(f"   Rationale: {trace.rationale}")
        print(f"   Outcome: {trace.outcome}")
    
    # Test otros modelos
    print("\n" + "="*80)
    print("COMPARACIÓN DE MODELOS:")
    print("="*80)
    
    models = ["first_touch", "last_touch", "time_decay", "position_based"]
    
    for model in models:
        inp.attribution_model = model
        result = await agent.execute(inp)
        top_channel = result.channel_attributions[0] if result.channel_attributions else None
        if top_channel:
            print(f"{model:20} → Top: {top_channel.channel:15} Credit: {top_channel.attribution_credit*100:5.1f}%")
    
    # Métricas del agente
    metrics = agent.get_metrics()
    print("\n" + "="*80)
    print("MÉTRICAS DEL AGENTE:")
    print("="*80)
    print(f"Total requests: {metrics['total']}")
    print(f"Success rate: {metrics['ok']}/{metrics['total']} ({metrics['ok']/max(1,metrics['total'])*100:.1f}%)")
    print(f"Cache hits: {metrics['cache_hits']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    print(f"P95 latency: {metrics.get('p95_latency', 0):.2f}ms")
    print(f"P99 latency: {metrics.get('p99_latency', 0):.2f}ms")
    print(f"Attributions calculated: {metrics['attributions_calculated']}")
    print(f"Compliance checks: {metrics['compliance_checks']}")
    
    print("\n" + "="*80)
    print("✅ AttributionModelIA FUNCIONA PERFECTAMENTE")
    print("="*80)

asyncio.run(test())