import sys
sys.path.insert(0, '.')

from certification_system import certify_agent

# Probar los 2 agentes con 80
agents = [
    ("campaignstrategyorchestratoria", "CampaignStrategyOrchestratorAgentOperative"),
    ("emailautomationia", "EmailAutomationAgentOperative")
]

for module_name, class_name in agents:
    print(f"\n{'='*60}")
    print(f"AGENTE: {class_name}")
    print("="*60)
    result = certify_agent(module_name, class_name, verbose=True)
    print(f"Score: {result['score']}/100")
