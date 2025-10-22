import asyncio
from agents.marketing.emailautomationia import EmailAutomationIA, EmailAutomationInput, Personalization

async def test():
    agent = EmailAutomationIA("tn_test_bank_001")
    
    inp = EmailAutomationInput(
        tenant_id="tn_test_bank_001",
        language="es",
        jurisdiction="MX",
        audience_segment="high_value",
        key_message="Oferta especial de refinanciamiento",
        campaign_goal="open",
        variant_count=2,
        personalization=Personalization(first_name="Juan", product_name="Crédito Premium")
    )
    
    result = await agent.execute(inp)
    print("RESULTADO:", result.generation_id)
    print("Variantes:", len(result.variants))
    print("Hora recomendada:", result.recommended_send_hour)
    
    for v in result.variants:
        print(f"  {v.variant_id}: {v.subject}")
    
    metrics = agent.get_metrics()
    print("MÉTRICAS:", metrics)
    
    assert len(result.variants) == 2
    print("✅ EmailAutomationIA funciona")

asyncio.run(test())