import os
import sys

print("="*80)
print("🔍 AUDITORÍA SIMPLE - NADAKKI AI SUITE")
print("="*80)

# Lista de agentes que deberían existir
expected_agents = [
    "riskanalysisia.py",
    "compliancecheckia.py", 
    "customersegmentia.py",
    "leadscoringia.py",
    "frauddetectia.py",
    "sentimentanalysisia.py",
    "churnpredictor.py",
    "productrecommenderia.py",
    "campaignoptimizeria.py",
    "contentgeneratoria.py",
    "sociallisteneria.py",
    "attributionmodelia.py",
    "personalizationengineia.py",
    "journeyoptimizeria.py",
    "budgetforecastia.py",
    "creativeanalyzeria.py",
    "marketingmixmodelia.py",
    "competitoranalyzeria.py",
    "abtestingia.py"
]

marketing_path = "agents/marketing"

print(f"\nVerificando agentes en: {marketing_path}/")
print("="*80)

found = []
missing = []
total_size = 0

for agent in expected_agents:
    filepath = os.path.join(marketing_path, agent)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        total_size += size
        found.append((agent, size))
        print(f"✅ {agent:35} {size:>10,} bytes")
    else:
        missing.append(agent)
        print(f"❌ {agent:35} MISSING")

print("\n" + "="*80)
print("📊 RESUMEN")
print("="*80)
print(f"Total Expected: {len(expected_agents)}")
print(f"Found: {len(found)}")
print(f"Missing: {len(missing)}")
print(f"Success Rate: {len(found)/len(expected_agents)*100:.1f}%")
print(f"Total Code Size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")

if len(found) == len(expected_agents):
    print("\n✅ ALL 19 AGENTS PRESENT - SUITE COMPLETE!")
else:
    print(f"\n⚠️  {len(missing)} AGENTS MISSING:")
    for m in missing:
        print(f"   - {m}")

print("="*80)

# Verificar tests
print("\n🧪 VERIFICANDO TESTS")
print("="*80)

test_files = [
    "test_risk_agent.py",
    "test_compliance_agent.py",
    "test_segment_agent.py",
    "test_lead_agent.py",
    "test_fraud_agent.py",
    "test_sentiment_agent.py",
    "test_churn_agent.py",
    "test_recommender_agent.py",
    "test_campaign_agent.py",
    "test_content_agent.py",
    "test_social_agent.py",
    "test_attribution_agent.py",
    "test_personalization_agent.py",
    "test_journey_agent.py",
    "test_budget_agent.py",
    "test_creative_agent.py",
    "test_mmm_agent.py",
    "test_competitor_agent.py",
    "test_abtest_agent.py"
]

tests_found = 0
for test in test_files:
    if os.path.exists(test):
        tests_found += 1
        print(f"✅ {test}")
    else:
        print(f"❌ {test}")

print(f"\nTests Found: {tests_found}/{len(test_files)}")
print("="*80)