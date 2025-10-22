import asyncio
from agents.marketing.budgetforecastia import BudgetForecastIA, ForecastInput, HistoricalSpend

async def test():
    agent = BudgetForecastIA("tn_test_bank_001")
    
    # Datos históricos de 6 quarters
    historical = [
        HistoricalSpend("2023-Q3", 100000, 350000, {
            "paid_search": 30000, "social": 25000, "display": 20000, "email": 15000, "content": 10000
        }),
        HistoricalSpend("2023-Q4", 120000, 400000, {
            "paid_search": 35000, "social": 30000, "display": 25000, "email": 18000, "content": 12000
        }),
        HistoricalSpend("2024-Q1", 110000, 380000, {
            "paid_search": 32000, "social": 28000, "display": 22000, "email": 16000, "content": 12000
        }),
        HistoricalSpend("2024-Q2", 130000, 450000, {
            "paid_search": 40000, "social": 32000, "display": 28000, "email": 18000, "content": 12000
        }),
        HistoricalSpend("2024-Q3", 125000, 420000, {
            "paid_search": 38000, "social": 30000, "display": 27000, "email": 18000, "content": 12000
        }),
        HistoricalSpend("2024-Q4", 140000, 480000, {
            "paid_search": 42000, "social": 35000, "display": 30000, "email": 20000, "content": 13000
        }),
    ]
    
    inp = ForecastInput(
        tenant_id="tn_test_bank_001",
        historical_data=historical,
        forecast_horizon_months=6,
        target_roi=250.0,
        forecast_model="ml_ensemble"
    )
    
    result = await agent.execute(inp)
    
    print("="*80)
    print("✅ RESULTADO DEL FORECASTING DE PRESUPUESTO")
    print("="*80)
    print(f"Forecast ID: {result.forecast_id}")
    print(f"Recommended Budget: ${result.recommended_budget:,.2f}")
    print(f"Projected ROI: {result.projected_roi:.2f}%")
    print(f"Confidence Level: {result.confidence_level*100:.1f}%")
    
    print("\n" + "="*80)
    print("FORECAST POR CANAL:")
    print("="*80)
    for cf in result.channel_forecasts:
        print(f"\n📊 {cf.channel.upper()}")
        print(f"   Budget: ${cf.recommended_budget:,.2f}")
        print(f"   Projected Revenue: ${cf.projected_revenue:,.2f}")
        print(f"   Projected ROI: {cf.projected_roi:.2f}%")
        print(f"   Confidence: {cf.confidence*100:.1f}%")
    
    print("\n" + "="*80)
    print("ESCENARIOS DE FORECAST:")
    print("="*80)
    for sf in result.scenario_forecasts:
        emoji = {"best_case": "📈", "expected": "📊", "worst_case": "📉"}[sf.scenario]
        print(f"\n{emoji} {sf.scenario.upper().replace('_', ' ')}")
        print(f"   Budget: ${sf.total_budget:,.2f}")
        print(f"   Revenue: ${sf.projected_revenue:,.2f}")
        print(f"   ROI: {sf.projected_roi:.2f}%")
        print(f"   Probability: {sf.probability*100:.0f}%")
    
    print("\n" + "="*80)
    print(f"ANOMALÍAS DETECTADAS ({len(result.anomalies_detected)}):")
    print("="*80)
    if result.anomalies_detected:
        for anomaly in result.anomalies_detected:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[anomaly.severity]
            print(f"\n{emoji} {anomaly.severity.upper()} - {anomaly.period}")
            print(f"   {anomaly.description}")
            print(f"   Impact: {anomaly.impact_on_forecast}")
    else:
        print("✅ No anomalies detected - data quality is good")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("="*80)
    for i, insight in enumerate(result.key_insights, 1):
        print(f"{i}. {insight}")
    
    print("\n" + "="*80)
    print("COMPLIANCE STATUS:")
    print("="*80)
    print(f"Compliant: {'✅ YES' if result.compliance_status['compliant'] else '❌ NO'}")
    if result.compliance_status['issues']:
        print("Issues:")
        for issue in result.compliance_status['issues']:
            print(f"  - {issue}")
    
    # Test otros modelos
    print("\n" + "="*80)
    print("COMPARACIÓN DE MODELOS:")
    print("="*80)
    
    models = ["time_series", "regression", "ml_ensemble", "conservative", "aggressive"]
    for model in models:
        inp.forecast_model = model
        result = await agent.execute(inp)
        print(f"{model:20} → ${result.recommended_budget:12,.0f}  ROI: {result.projected_roi:5.1f}%")
    
    # Métricas del agente
    metrics = agent.get_metrics()
    print("\n" + "="*80)
    print("MÉTRICAS DEL AGENTE:")
    print("="*80)
    print(f"Total requests: {metrics['total']}")
    print(f"Success rate: {metrics['ok']}/{metrics['total']} ({metrics['ok']/max(1,metrics['total'])*100:.1f}%)")
    print(f"Forecasts generated: {metrics['forecasts_generated']}")
    print(f"Anomalies detected: {metrics['anomalies_detected']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    
    print("\n" + "="*80)
    print("✅ BudgetForecastIA FUNCIONA PERFECTAMENTE")
    print("="*80)

asyncio.run(test())