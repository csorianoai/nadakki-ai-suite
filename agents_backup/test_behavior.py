from agents.originacion.behavior_miner_v2 import BehaviorMiner

agent = BehaviorMiner('banreservas')

test_data = {
    'id': 'APP-004',
    'monthly_income': 120000,
    'avg_monthly_spending': 95000,
    'on_time_payment_ratio': 0.92,
    'avg_payment_delay_days': 1,
    'transaction_types_count': 8,
    'min_monthly_balance': 15000,
    'avg_monthly_balance': 45000,
    'digital_channel_usage': 0.85,
    'seasonal_spending_variance': 0.15,
    'credit_utilization': 0.45
}

result = agent.analyze_behavioral_patterns(test_data)
print('📈 RESULTADO BEHAVIORAL ANALYSIS:')
print('Stability Score:', result['stability_score'])
print('Behavioral Risk Level:', result['behavioral_risk_level'])
print('Future Prediction:', result['future_behavior_prediction']['prediction'])
print('Risk Behaviors:', len(result['risk_behaviors']))
print('Recommendations:', len(result['recommendations']))
print('Confidence Score:', result['confidence_score'])

status = agent.get_agent_status()
print('Status:', status['status'])
