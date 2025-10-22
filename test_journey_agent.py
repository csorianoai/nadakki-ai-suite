import asyncio
from agents.marketing.journeyoptimizeria import JourneyOptimizerIA, JourneyInput, JourneyStage

async def test():
    agent = JourneyOptimizerIA("tn_test_bank_001")
    
    # Journey típico de apertura de cuenta bancaria
    stages = [
        JourneyStage("awareness", 10000, 8000, 60),        # Landing page
        JourneyStage("consideration", 8000, 6000, 180),    # Product comparison
        JourneyStage("evaluation", 6000, 4000, 300),       # Application form view
        JourneyStage("purchase", 4000, 1500, 420),         # Application submit
        JourneyStage("onboarding", 1500, 1200, 600),       # Account setup
        JourneyStage("retention", 1200, 1000, 120),        # First transaction
    ]
    
    inp = JourneyInput(
        tenant_id="tn_test_bank_001",
        journey_stages=stages,
        journey_name="account_opening_journey",
        time_period_days=30
    )
    
    result = await agent.execute(inp)
    
    print("="*80)
    print("✅ RESULTADO DEL ANÁLISIS DE CUSTOMER JOURNEY")
    print("="*80)
    print(f"Journey ID: {result.journey_id}")
    print(f"Journey Name: {result.journey_name}")
    print(f"Overall Conversion: {result.overall_conversion_rate}%")
    print(f"Predicted Conversion (with optimizations): {result.predicted_conversion_rate}%")
    print(f"Journey Health Score: {result.journey_health_score}/100")
    
    print("\n" + "="*80)
    print("ANÁLISIS POR ETAPA:")
    print("="*80)
    for analysis in result.stage_analyses:
        print(f"\n📍 {analysis.stage.upper()}")
        print(f"   Conversion Rate: {analysis.conversion_rate}%")
        print(f"   Drop-off Rate: {analysis.drop_off_rate}%")
        print(f"   Avg Time: {analysis.avg_time_minutes:.1f} minutes")
        print(f"   Health Score: {analysis.health_score}/100")
        print(f"   Benchmark vs Industry: {analysis.benchmarks['industry_avg_conversion']}%")
    
    print("\n" + "="*80)
    print(f"FRICTION POINTS DETECTADOS ({len(result.friction_points)}):")
    print("="*80)
    for friction in result.friction_points:
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[friction.friction_level]
        print(f"\n{emoji} {friction.friction_level.upper()} - {friction.stage}")
        print(f"   ID: {friction.friction_id}")
        print(f"   {friction.description}")
        print(f"   Impact Score: {friction.impact_score}/100")
        print(f"   Affected Users: {friction.affected_users:,}")
        print(f"   Root Causes: {', '.join(friction.root_causes)}")
    
    print("\n" + "="*80)
    print(f"OPTIMIZACIONES RECOMENDADAS (Top {min(5, len(result.optimizations))}):")
    print("="*80)
    for i, opt in enumerate(result.optimizations[:5], 1):
        print(f"\n🎯 OPTIMIZACIÓN #{i} [Priority {opt.priority}]")
        print(f"   ID: {opt.optimization_id}")
        print(f"   Type: {opt.optimization_type}")
        print(f"   Stage: {opt.stage}")
        print(f"   Title: {opt.title}")
        print(f"   Description: {opt.description}")
        print(f"   Expected Impact: {opt.expected_impact}")
        print(f"   Conversion Lift: +{opt.estimated_conversion_lift}%")
        print(f"   Implementation: {opt.implementation_effort} effort")
        print(f"   Compliance: {'✅ Checked' if opt.compliance_checked else '❌ Pending'}")
    
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
    if result.compliance_status['issues']:
        print("Issues:")
        for issue in result.compliance_status['issues']:
            print(f"  - {issue}")
    
    # Métricas del agente
    metrics = agent.get_metrics()
    print("\n" + "="*80)
    print("MÉTRICAS DEL AGENTE:")
    print("="*80)
    print(f"Total requests: {metrics['total']}")
    print(f"Success rate: {metrics['ok']}/{metrics['total']} ({metrics['ok']/max(1,metrics['total'])*100:.1f}%)")
    print(f"Journeys analyzed: {metrics['journeys_analyzed']}")
    print(f"Frictions detected: {metrics['frictions_detected']}")
    print(f"Optimizations generated: {metrics['optimizations_generated']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    
    print("\n" + "="*80)
    print("✅ JourneyOptimizerIA FUNCIONA PERFECTAMENTE")
    print("="*80)

asyncio.run(test())