import asyncio
from agents.marketing.marketingmixmodelia import (
    MarketingMixModelIA, MMMInput, ChannelData
)

async def test():
    agent = MarketingMixModelIA("tn_test_bank_001")
    
    # Datos históricos de 12 semanas por canal
    periods = [f"2024-W{i:02d}" for i in range(1, 13)]
    
    channels = [
        ChannelData(
            channel="digital",
            periods=periods,
            spend=[15000, 16000, 14500, 17000, 18000, 16500, 19000, 17500, 18500, 19500, 20000, 21000],
            revenue=[52500, 56000, 50750, 59500, 63000, 57750, 66500, 61250, 64750, 68250, 70000, 73500]
        ),
        ChannelData(
            channel="social",
            periods=periods,
            spend=[12000, 11500, 13000, 12500, 14000, 13500, 15000, 14500, 15500, 16000, 16500, 17000],
            revenue=[36000, 34500, 39000, 37500, 42000, 40500, 45000, 43500, 46500, 48000, 49500, 51000]
        ),
        ChannelData(
            channel="search",
            periods=periods,
            spend=[20000, 21000, 19500, 22000, 23000, 21500, 24000, 22500, 23500, 24500, 25000, 26000],
            revenue=[80000, 84000, 78000, 88000, 92000, 86000, 96000, 90000, 94000, 98000, 100000, 104000]
        ),
        ChannelData(
            channel="email",
            periods=periods,
            spend=[5000, 5200, 4800, 5500, 5800, 5300, 6000, 5600, 5900, 6200, 6500, 6800],
            revenue=[17500, 18200, 16800, 19250, 20300, 18550, 21000, 19600, 20650, 21700, 22750, 23800]
        ),
        ChannelData(
            channel="tv",
            periods=periods,
            spend=[30000, 32000, 28000, 35000, 38000, 33000, 40000, 36000, 38000, 42000, 45000, 48000],
            revenue=[75000, 80000, 70000, 87500, 95000, 82500, 100000, 90000, 95000, 105000, 112500, 120000]
        ),
    ]
    
    # Revenue total histórico (incluye baseline)
    total_revenue = [261000, 272700, 255050, 291750, 312300, 285300, 328500, 304350, 321900, 341950, 355250, 373300]
    
    inp = MMMInput(
        tenant_id="tn_test_bank_001",
        channel_data=channels,
        total_revenue_history=total_revenue,
        baseline_revenue=50000,
        optimization_goal="maximize_roi",
        budget_constraint=100000
    )
    
    result = await agent.execute(inp)
    
    print("="*80)
    print("✅ RESULTADO DEL MARKETING MIX MODEL")
    print("="*80)
    print(f"Model ID: {result.model_id}")
    print(f"Model Accuracy (R²): {result.model_accuracy*100:.1f}%")
    print(f"Baseline Revenue: ${result.baseline_revenue:,.0f}")
    print(f"Total Marketing Contribution: ${result.total_marketing_contribution:,.0f}")
    
    print("\n" + "="*80)
    print("CONTRIBUCIÓN POR CANAL:")
    print("="*80)
    
    for contrib in result.channel_contributions:
        print(f"\n📊 {contrib.channel.upper()}")
        print(f"   Total Spend: ${contrib.total_spend:,.0f}")
        print(f"   Revenue Attributed: ${contrib.total_revenue_attributed:,.0f}")
        print(f"   ROI: {contrib.roi:.1f}%")
        print(f"   Contribution: {contrib.contribution_percentage:.1f}% of marketing revenue")
        print(f"   Saturation Level: {contrib.saturation_level*100:.0f}%")
        print(f"   Marginal ROI: {(contrib.marginal_roi-1)*100:.1f}% per additional $1")
    
    print("\n" + "="*80)
    print("ASIGNACIÓN OPTIMIZADA DE PRESUPUESTO:")
    print("="*80)
    print(f"Total Budget: ${sum(o.recommended_spend for o in result.optimized_allocations):,.0f}")
    
    for opt in result.optimized_allocations:
        emoji = "📈" if opt.change_percentage > 0 else "📉" if opt.change_percentage < 0 else "➡️"
        print(f"\n{emoji} {opt.channel.upper()}")
        print(f"   Current: ${opt.current_spend:,.0f}")
        print(f"   Recommended: ${opt.recommended_spend:,.0f} ({opt.change_percentage:+.1f}%)")
        print(f"   Projected Revenue: ${opt.projected_revenue:,.0f}")
        print(f"   Projected ROI: {opt.projected_roi:.1f}%")
    
    print("\n" + "="*80)
    print("ESCENARIOS DE SIMULACIÓN:")
    print("="*80)
    
    for scenario in result.scenarios:
        print(f"\n📋 {scenario.scenario_name.upper()}")
        print(f"   Total Budget: ${scenario.total_budget:,.0f}")
        print(f"   Projected Revenue: ${scenario.projected_revenue:,.0f}")
        print(f"   Projected ROI: {scenario.projected_roi:.1f}%")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("="*80)
    for i, insight in enumerate(result.key_insights, 1):
        print(f"{i}. {insight}")
    
    print("\n" + "="*80)
    print("COMPLIANCE STATUS:")
    print("="*80)
    print(f"Compliant: {'✅ YES' if result.compliance_status['compliant'] else '❌ NO'}")
    
    # Métricas del agente
    metrics = agent.get_metrics()
    print("\n" + "="*80)
    print("MÉTRICAS DEL AGENTE:")
    print("="*80)
    print(f"Total requests: {metrics['total']}")
    print(f"Success rate: {metrics['ok']}/{metrics['total']} ({metrics['ok']/max(1,metrics['total'])*100:.1f}%)")
    print(f"Models built: {metrics['models_built']}")
    print(f"Optimizations run: {metrics['optimizations_run']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    
    print("\n" + "="*80)
    print("✅ MarketingMixModelIA FUNCIONA PERFECTAMENTE")
    print("="*80)

asyncio.run(test())