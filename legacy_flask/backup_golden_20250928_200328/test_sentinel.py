from agents.originacion.sentinel_bot_v2 import SentinelBot

agent = SentinelBot('banreservas')

test_data = {
    'id': 'APP-001',
    'monthly_income': 75000,
    'total_debt': 250000,
    'credit_score': 680,
    'years_employed': 3
}

result = agent.analyze_risk_profile(test_data)
print('📊 RESULTADO ANALISIS:')
print('Risk Score:', result['risk_score'])
print('Risk Level:', result['risk_level'])
print('Recommendation:', result['recommendation'])

status = agent.get_agent_status()
print('Status:', status['status'])
