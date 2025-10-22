import asyncio
from agents.marketing.campaignoptimizeria import CampaignOptimizerIA, CampaignOptimizationInput

async def test():
    agent = CampaignOptimizerIA("tn_test_bank_001")
    
    inp = CampaignOptimizationInput(
        tenant_id="tn_test_bank_001",
        campaign_objective="conversion",
        total_budget=50000.0,
        channels=["email", "social", "paid_ads"],
        target_audience_size=100000,
        language="es",
        jurisdiction="MX",
        duration_days=30
    )
    
    result = await agent.execute(inp)
    print("RESULTADO:", result.optimization_id)
    print("ROI Esperado:", result.total_expected_roi)
    print("Alcance Total:", result.total_expected_reach)
    print("Estrategia:", result.recommended_strategy)
    print("\nCanales:")
    
    for alloc in result.channel_allocations:
        print(f"  {alloc.channel}: ${alloc.allocated_budget:.2f} (ROI: {alloc.expected_roi}x, Reach: {alloc.expected_reach:,})")
    
    metrics = agent.get_metrics()
    success_rate = metrics["ok"] / max(1, metrics["total"])
    print(f"\nMÉTRICAS: Success rate = {success_rate:.1%}")
    
    assert result.total_expected_roi > 0
    assert len(result.channel_allocations) == 3
    print("\n✅ CampaignOptimizerIA funciona")

asyncio.run(test())