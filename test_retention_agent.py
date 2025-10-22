import asyncio
from agents.marketing.retentionpredictorea import RetentionPredictorIA, RetentionPredictionInput, CustomerBehavior

async def test():
    agent = RetentionPredictorIA("tn_test_bank_001")
    
    customers = [
        CustomerBehavior(
            customer_id="cust_001",
            days_since_signup=90,
            days_since_last_login=2,
            days_since_last_transaction=5,
            total_transactions=25,
            avg_transaction_value=150,
            login_frequency_30d=15,
            support_tickets_30d=0,
            product_usage_score=8.5,
            nps_score=80
        ),
        CustomerBehavior(
            customer_id="cust_002",
            days_since_signup=180,
            days_since_last_login=45,
            days_since_last_transaction=60,
            total_transactions=5,
            avg_transaction_value=80,
            login_frequency_30d=1,
            support_tickets_30d=3,
            product_usage_score=2.0,
            nps_score=-20
        ),
        CustomerBehavior(
            customer_id="cust_003",
            days_since_signup=365,
            days_since_last_login=10,
            days_since_last_transaction=15,
            total_transactions=50,
            avg_transaction_value=200,
            login_frequency_30d=8,
            support_tickets_30d=1,
            product_usage_score=7.0,
            nps_score=50
        ),
    ]
    
    inp = RetentionPredictionInput(
        tenant_id="tn_test_bank_001",
        customers=customers,
        prediction_horizon_days=30
    )
    
    result = await agent.execute(inp)
    print("✅ RESULTADO:", result.prediction_id)
    print("Retention Score:", result.retention_score)
    print("High-risk customers:", len(result.high_risk_customers))
    
    print("\nDistribución de riesgo:")
    for risk, count in result.risk_distribution.items():
        print(f"  {risk}: {count}")
    
    print("\nAnálisis detallado (primeros 2):")
    for pred in result.predictions[:2]:
        print(f"\n  Customer: {pred.customer_id}")
        print(f"  Churn Risk: {pred.churn_risk} ({pred.churn_probability}%)")
        print(f"  Stage: {pred.retention_stage}")
        print(f"  LTV at Risk: ${pred.predicted_ltv_impact}")
        print(f"  Warning Signals: {len(pred.early_warning_signals)}")
        if pred.early_warning_signals:
            print(f"    Top signal: {pred.early_warning_signals[0].signal_type}")
        print(f"  Top intervention: {pred.intervention_strategies[0].action}")
    
    metrics = agent.get_metrics()
    print(f"\nMÉTRICAS: {metrics['ok']}/{metrics['total']}, Critical: {metrics['critical_risk_detected']}")
    print("\n✅ RetentionPredictorIA funciona")

asyncio.run(test())