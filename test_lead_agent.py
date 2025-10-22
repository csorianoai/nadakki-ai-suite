import asyncio
from agents.marketing.leadscoringia import LeadScoringIA, LeadScoringInput, LeadData

async def test():
    agent = LeadScoringIA("tn_test_bank_001")
    
    lead = LeadData(
        lead_id="lead_12345",
        source="web",
        company_name="Tech Corp",
        company_size=250,
        annual_revenue=5_000_000,
        job_title="CFO",
        website_visits=8,
        content_downloads=3,
        email_opens=5,
        form_submissions=1,
        days_since_last_activity=1
    )
    
    inp = LeadScoringInput(
        tenant_id="tn_test_bank_001",
        lead_data=lead,
        language="es",
        jurisdiction="MX"
    )
    
    result = await agent.execute(inp)
    print("RESULTADO:", result.scoring_id)
    print("Clasificación:", result.classification)
    print("Score Total:", result.scores.total_score)
    print("Prioridad:", result.priority_rank)
    print("\nScores detallados:")
    print(f"  Fit: {result.scores.fit_score}")
    print(f"  Engagement: {result.scores.engagement_score}")
    print(f"  Urgency: {result.scores.urgency_score}")
    print(f"  Value: {result.scores.value_score}")
    print(f"\nBuying Signals: {result.buying_signals.signals_detected}")
    print(f"Signal Strength: {result.buying_signals.signal_strength}")
    
    metrics = agent.get_metrics()
    success_rate = metrics["ok"] / max(1, metrics["total"])
    print(f"\nMÉTRICAS: Success rate = {success_rate:.1%}")
    
    assert result.classification in ["hot", "warm", "cold", "unqualified"]
    assert result.scores.total_score > 0
    print("\n✅ LeadScoringIA funciona")

asyncio.run(test())