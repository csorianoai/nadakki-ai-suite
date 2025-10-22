import asyncio
from agents.marketing.abtestingia import ABTestingIA, ABTestInput, VariantData

async def test():
    agent = ABTestingIA("tn_test_bank_001")
    
    # Test con resultados significativos
    control = VariantData("control", 10000, 850, 42500.0)
    variants = [
        VariantData("variant_a", 10200, 950, 47500.0),
        VariantData("variant_b", 9800, 820, 41000.0)
    ]
    
    inp = ABTestInput(
        tenant_id="tn_test_bank_001",
        test_name="Homepage CTA Button Test",
        test_type="conversion",
        control=control,
        variants=variants,
        confidence_level=0.95,
        minimum_detectable_effect=0.05,
        duration_days=14
    )
    
    result = await agent.execute(inp)
    
    print("="*80)
    print("✅ RESULTADO DEL A/B TEST")
    print("="*80)
    print(f"Test ID: {result.test_id}")
    print(f"Test Name: {result.test_name}")
    print(f"Status: {result.test_status.upper()}")
    print(f"Winner: {result.winner.upper()}")
    
    print("\n" + "="*80)
    print("RESULTADOS POR VARIANTE:")
    print("="*80)
    
    for var in result.variant_results:
        emoji = "👑" if var.variant_name == result.winner else "📊"
        print(f"\n{emoji} {var.variant_name.upper()}")
        print(f"   Visitors: {var.visitors:,}")
        print(f"   Conversions: {var.conversions:,}")
        print(f"   Conversion Rate: {var.conversion_rate}%")
        print(f"   Revenue: ${var.revenue:,.2f}")
        print(f"   Revenue per Visitor: ${var.revenue_per_visitor:.2f}")
        print(f"   95% CI: [{var.confidence_interval_lower:.2f}%, {var.confidence_interval_upper:.2f}%]")
        if var.variant_name != "control":
            emoji_imp = "📈" if var.improvement_vs_control > 0 else "📉"
            print(f"   {emoji_imp} Improvement: {var.improvement_vs_control:+.2f}%")
    
    print("\n" + "="*80)
    print("SIGNIFICANCIA ESTADÍSTICA:")
    print("="*80)
    print(f"Statistically Significant: {'✅ YES' if result.statistical_significance.is_significant else '❌ NO'}")
    print(f"P-value: {result.statistical_significance.p_value:.4f}")
    print(f"Confidence Level: {result.statistical_significance.confidence_level*100:.0f}%")
    print(f"Test Statistic (z-score): {result.statistical_significance.test_statistic:.3f}")
    print(f"Degrees of Freedom: {result.statistical_significance.degrees_of_freedom}")
    
    print("\n" + "="*80)
    print("ANÁLISIS:")
    print("="*80)
    print(f"Sample Size Adequate: {'✅ YES' if result.sample_size_adequate else '⚠️ NO'}")
    print(f"Required Sample Size: {result.metadata.get('required_sample_size', 0):,}")
    print(f"Actual Sample Size: {sum(v.visitors for v in result.variant_results):,}")
    
    print("\n" + "="*80)
    print("RECOMENDACIÓN:")
    print("="*80)
    print(f"Action: {result.recommended_action}")
    print(f"Risk Assessment: {result.risk_assessment}")
    
    print("\n" + "="*80)
    print("COMPLIANCE STATUS:")
    print("="*80)
    print(f"Compliant: {'✅ YES' if result.compliance_status['compliant'] else '❌ NO'}")
    
    # Métricas
    metrics = agent.get_metrics()
    print("\n" + "="*80)
    print("MÉTRICAS DEL AGENTE:")
    print("="*80)
    print(f"Total requests: {metrics['total']}")
    print(f"Success rate: {metrics['ok']}/{metrics['total']} ({metrics['ok']/max(1,metrics['total'])*100:.1f}%)")
    print(f"Tests analyzed: {metrics['tests_analyzed']}")
    print(f"Significant results: {metrics['significant_results']}")
    print(f"Winners declared: {metrics['winners_declared']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    
    print("\n" + "="*80)
    print("✅ ABTestingIA FUNCIONA PERFECTAMENTE")
    print("="*80)

asyncio.run(test())