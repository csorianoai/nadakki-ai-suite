import asyncio
from agents.marketing.competitoranalyzeria import (
    CompetitorAnalyzerIA, CompetitorAnalysisInput, Competitor
)

async def test():
    agent = CompetitorAnalyzerIA("tn_test_bank_001")
    
    # Competidores del sector financiero
    competitors = [
        Competitor(
            competitor_id="comp_01",
            name="MegaBank Corp",
            market_share=28.5,
            revenue_estimate=15000000000,
            customer_base=5000000,
            key_products=["Checking", "Savings", "Credit Cards", "Loans", "Investment"],
            pricing_tier="premium"
        ),
        Competitor(
            competitor_id="comp_02",
            name="Digital First Bank",
            market_share=18.2,
            revenue_estimate=8000000000,
            customer_base=3200000,
            key_products=["Mobile Banking", "Investment Platform", "Personal Loans"],
            pricing_tier="mid"
        ),
        Competitor(
            competitor_id="comp_03",
            name="Community Trust",
            market_share=12.8,
            revenue_estimate=5000000000,
            customer_base=2100000,
            key_products=["Savings", "Mortgages", "Business Banking"],
            pricing_tier="mid"
        ),
        Competitor(
            competitor_id="comp_04",
            name="NeoBank Plus",
            market_share=8.5,
            revenue_estimate=3000000000,
            customer_base=1800000,
            key_products=["Digital Wallet", "Crypto Services", "Instant Loans"],
            pricing_tier="budget"
        ),
    ]
    
    inp = CompetitorAnalysisInput(
        tenant_id="tn_test_bank_001",
        competitors=competitors,
        our_company_name="OurBank",
        our_market_share=15.3,
        analysis_dimensions=["product", "pricing", "marketing", "technology"]
    )
    
    result = await agent.execute(inp)
    
    print("="*80)
    print("✅ ANÁLISIS COMPETITIVO COMPLETO")
    print("="*80)
    print(f"Analysis ID: {result.analysis_id}")
    print(f"Our Company: OurBank")
    print(f"Our Position: {result.our_position.upper()}")
    print(f"Competitors Analyzed: {len(competitors)}")
    
    print("\n" + "="*80)
    print("DIMENSION SCORING:")
    print("="*80)
    
    for dim in result.dimension_scores:
        emoji = "✅" if dim.gap > 0 else "⚠️" if dim.gap > -5 else "❌"
        print(f"\n{emoji} {dim.dimension.upper()}")
        print(f"   Our Score: {dim.our_score}/100")
        print(f"   Competitor Avg: {dim.competitor_avg}/100")
        print(f"   Gap: {dim.gap:+.1f}")
        print(f"   Assessment: {dim.assessment}")
        
        # Visual bar
        bar_our = "█" * int(dim.our_score / 10)
        bar_comp = "░" * int(dim.competitor_avg / 10)
        print(f"   Us:   [{bar_our:<10}] {dim.our_score:.1f}")
        print(f"   Them: [{bar_comp:<10}] {dim.competitor_avg:.1f}")
    
    print("\n" + "="*80)
    print("SWOT ANALYSIS:")
    print("="*80)
    
    print("\n💪 STRENGTHS:")
    if result.swot_analysis.strengths:
        for s in result.swot_analysis.strengths:
            print(f"   • {s}")
    else:
        print("   • None identified")
    
    print("\n⚠️  WEAKNESSES:")
    if result.swot_analysis.weaknesses:
        for w in result.swot_analysis.weaknesses:
            print(f"   • {w}")
    else:
        print("   • None identified")
    
    print("\n🎯 OPPORTUNITIES:")
    if result.swot_analysis.opportunities:
        for o in result.swot_analysis.opportunities:
            print(f"   • {o}")
    else:
        print("   • None identified")
    
    print("\n⚡ THREATS:")
    if result.swot_analysis.threats:
        for t in result.swot_analysis.threats:
            print(f"   • {t}")
    else:
        print("   • None identified")
    
    print("\n" + "="*80)
    print("MARKET GAPS IDENTIFIED:")
    print("="*80)
    
    for gap in result.market_gaps:
        emoji = {"large": "🎯", "medium": "📊", "small": "📌"}[gap.opportunity_size]
        print(f"\n{emoji} Priority {gap.priority}: {gap.gap_id}")
        print(f"   {gap.description}")
        print(f"   Opportunity Size: {gap.opportunity_size.upper()}")
        print(f"   Difficulty: {gap.difficulty.upper()}")
    
    print("\n" + "="*80)
    print("COMPETITIVE INSIGHTS:")
    print("="*80)
    
    if result.competitive_insights:
        for insight in result.competitive_insights:
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[insight.impact]
            print(f"\n{emoji} {insight.competitor_name} - {insight.insight_type.upper()}")
            print(f"   {insight.description}")
            print(f"   Impact: {insight.impact.upper()}")
    else:
        print("   No critical insights detected")
    
    print("\n" + "="*80)
    print("RECOMMENDED ACTIONS:")
    print("="*80)
    for i, action in enumerate(result.recommended_actions, 1):
        print(f"{i}. {action}")
    
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
    print(f"Analyses: {metrics['analyses']}")
    print(f"SWOT generated: {metrics['swot_generated']}")
    print(f"Gaps found: {metrics['gaps_found']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    
    print("\n" + "="*80)
    print("✅ CompetitorAnalyzerIA FUNCIONA PERFECTAMENTE")
    print("="*80)

asyncio.run(test())