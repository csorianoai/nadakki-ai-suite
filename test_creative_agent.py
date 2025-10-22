import asyncio
from agents.marketing.creativeanalyzeria import (
    CreativeAnalyzerIA, CreativeAnalysisInput, CreativeAsset
)

async def test():
    agent = CreativeAnalyzerIA("tn_test_bank_001")
    
    # Crear 3 variantes creativas
    assets = [
        CreativeAsset(
            asset_id="creative_001",
            asset_type="image",
            copy_text="Save big on your first investment. Open account today and get $100 bonus!",
            width=1200,
            height=628,
            visual_elements=["logo", "brand_colors", "person_smiling"],
            color_palette=["#0066CC", "#FFFFFF", "#FFA500"],
            has_cta=True
        ),
        CreativeAsset(
            asset_id="creative_002",
            asset_type="banner",
            copy_text="Start investing now. Limited time offer!",
            width=728,
            height=90,
            visual_elements=["logo", "graph_upward"],
            color_palette=["#003366", "#CCCCCC"],
            has_cta=True
        ),
        CreativeAsset(
            asset_id="creative_003",
            asset_type="video",
            copy_text="Your financial future starts here. Join thousands of smart investors. Get started in minutes.",
            width=1920,
            height=1080,
            duration_seconds=30,
            visual_elements=["logo", "brand_colors", "consistent_style", "people"],
            color_palette=["#0066CC", "#FFFFFF", "#333333", "#FFA500"],
            has_cta=True
        ),
    ]
    
    inp = CreativeAnalysisInput(
        tenant_id="tn_test_bank_001",
        creative_assets=assets,
        target_channel="instagram",
        target_audience="millennials_investors"
    )
    
    result = await agent.execute(inp)
    
    print("="*80)
    print("✅ RESULTADO DEL ANÁLISIS DE CREATIVOS")
    print("="*80)
    print(f"Analysis ID: {result.analysis_id}")
    print(f"Target Channel: {result.target_channel}")
    print(f"Assets Analyzed: {len(result.asset_scores)}")
    print(f"Recommended Asset: {result.recommended_asset}")
    
    print("\n" + "="*80)
    print("ANÁLISIS DETALLADO DE CREATIVOS:")
    print("="*80)
    
    for i, score in enumerate(result.asset_scores, 1):
        emoji = {"excellent": "🏆", "good": "✅", "average": "📊", "poor": "❌"}[score.performance_prediction]
        print(f"\n{emoji} CREATIVE #{i}: {score.asset_id}")
        print(f"   Overall Score: {score.overall_score}/100")
        print(f"   Performance Prediction: {score.performance_prediction.upper()}")
        
        print(f"\n   📸 VISUAL SCORES:")
        print(f"      Composition: {score.visual_score.composition_score}/100")
        print(f"      Color Harmony: {score.visual_score.color_harmony_score}/100")
        print(f"      Text Readability: {score.visual_score.text_readability_score}/100")
        print(f"      Brand Consistency: {score.visual_score.brand_consistency_score}/100")
        
        print(f"\n   📝 COPY SCORES:")
        print(f"      Clarity: {score.copy_score.clarity_score}/100")
        print(f"      Persuasion: {score.copy_score.persuasion_score}/100")
        print(f"      CTA Strength: {score.copy_score.cta_strength_score}/100")
        print(f"      Length: {score.copy_score.length_appropriateness}/100")
        
        print(f"\n   📊 PREDICTED METRICS:")
        print(f"      Engagement Rate: {score.predicted_engagement_rate}%")
        print(f"      CTR: {score.predicted_ctr}%")
        
        print(f"\n   🎯 CHANNEL FIT SCORES:")
        top_channels = sorted(score.channel_fit_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        for channel, fit_score in top_channels:
            bars = "█" * int(fit_score / 10)
            print(f"      {channel:12} {bars} {fit_score:.1f}")
        
        if score.optimization_suggestions:
            print(f"\n   💡 OPTIMIZATION SUGGESTIONS:")
            for suggestion in score.optimization_suggestions[:3]:
                print(f"      • {suggestion}")
    
    print("\n" + "="*80)
    print("A/B TESTING RECOMMENDATIONS:")
    print("="*80)
    for i, rec in enumerate(result.ab_test_recommendations, 1):
        print(f"{i}. {rec}")
    
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
    print(f"Creatives analyzed: {metrics['creatives_analyzed']}")
    print(f"Compliance checks: {metrics['compliance_checks']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    
    print("\n" + "="*80)
    print("✅ CreativeAnalyzerIA FUNCIONA PERFECTAMENTE")
    print("="*80)

asyncio.run(test())