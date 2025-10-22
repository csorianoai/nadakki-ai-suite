import asyncio
from agents.marketing.influencermatcheria import (
    InfluencerMatcherIA, InfluencerMatchInput, CampaignRequirements, InfluencerProfile
)

async def test():
    agent = InfluencerMatcherIA("tn_test_bank_001")
    
    influencers = [
        InfluencerProfile("inf_1", "@financeguru", "instagram", 150000, 0.045, "finance", 2500, "US", True),
        InfluencerProfile("inf_2", "@moneytalks", "youtube", 85000, 0.032, "personal_finance", 1800, "US", False),
        InfluencerProfile("inf_3", "@investpro", "linkedin", 45000, 0.025, "investing", 1200, "US", True),
    ]
    
    reqs = CampaignRequirements(
        target_audience="millennials_finance",
        budget=10000,
        platforms=["instagram", "youtube"],
        content_niche="finance",
        min_followers=50000,
        min_engagement_rate=0.025
    )
    
    inp = InfluencerMatchInput(
        tenant_id="tn_test_bank_001",
        campaign_requirements=reqs,
        available_influencers=influencers
    )
    
    result = await agent.execute(inp)
    print("RESULTADO:", result.matching_id)
    print("Matches encontrados:", len(result.matches))
    print("Top recomendación:", result.top_recommendation)
    print("Alcance estimado:", f"{result.total_estimated_reach:,}")
    print("Costo estimado: $", result.total_estimated_cost)
    
    for match in result.matches[:3]:
        print(f"\n  {match.handle}: Score {match.match_score.total_score} (ROI: {match.estimated_roi}x)")
    
    metrics = agent.get_metrics()
    print(f"\nMÉTRICAS: {metrics['ok']}/{metrics['total']} exitosos")
    
    assert len(result.matches) > 0
    print("\n✅ InfluencerMatcherIA funciona")

asyncio.run(test())