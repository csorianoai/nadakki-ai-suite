import asyncio
from agents.marketing.customersegmentatonia import CustomerSegmentationIA, SegmentationInput, CustomerData

async def test():
    agent = CustomerSegmentationIA("tn_test_bank_001")
    
    customers = [
        CustomerData("cust_001", 10, 15, 5000, 333, 365),
        CustomerData("cust_002", 200, 2, 500, 250, 400),
        CustomerData("cust_003", 30, 8, 3000, 375, 180),
    ]
    
    inp = SegmentationInput(
        tenant_id="tn_test_bank_001",
        customers=customers
    )
    
    result = await agent.execute(inp)
    print("✅ RESULTADO:", result.segmentation_id)
    print("Clientes analizados:", len(result.segments))
    print("\nDistribución:")
    for seg, count in result.segment_distribution.items():
        print(f"  {seg}: {count}")
    
    print("\nPrimeros 3 segmentos:")
    for s in result.segments[:3]:
        print(f"  {s.customer_id}: {s.rfm_scores.rfm_segment} (Churn risk: {s.churn_risk}, LTV: ${s.predicted_ltv})")
    
    metrics = agent.get_metrics()
    print(f"\nMÉTRICAS: {metrics['ok']}/{metrics['total']}")
    print("\n✅ CustomerSegmentationIA funciona")

asyncio.run(test())