from agents.originacion.income_oracle_v2 import IncomeOracle

agent = IncomeOracle('banreservas')

test_data = {
    'id': 'APP-003',
    'monthly_income': 95000,
    'employment_type': 'full_time',
    'years_employed': 4
}

result = agent.verify_income_profile(test_data)
print('💰 RESULTADO INCOME VERIFICATION:')
print('Declared Income:', result['declared_income'])
print('Verified Income:', result['verified_income'])
print('Consistency Score:', result['consistency_score'])
print('Reliability Score:', result['reliability_score'])
print('Verification Status:', result['verification_status'])
print('Confidence Level:', result['confidence_level'])
print('Anomalies:', len(result['anomalies_detected']))

status = agent.get_agent_status()
print('Status:', status['status'])
