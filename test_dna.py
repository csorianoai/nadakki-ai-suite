from agents.originacion.dna_profiler_v2 import DNAProfiler

agent = DNAProfiler('banreservas')

test_data = {
    'id': 'APP-002',
    'age': 28,
    'location': 'santo_domingo',
    'monthly_income': 85000,
    'assets': 500000,
    'spending_pattern': 'conservative',
    'credit_score': 720,
    'credit_history_years': 5,
    'employment_type': 'full_time',
    'education': 'university'
}

result = agent.create_credit_dna(test_data)
print('🧬 RESULTADO DNA PROFILING:')
print('Unique DNA:', result['unique_dna'])
print('Risk Inheritance:', result['risk_inheritance'])
print('Profile Strength:', result['profile_strength'])
print('DNA Signatures:', len(result['dna_signatures']))

status = agent.get_agent_status()
print('Status:', status['status'])
