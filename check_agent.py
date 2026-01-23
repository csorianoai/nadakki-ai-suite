from agents.marketing.campaignstrategyorchestratoria import CampaignStrategyOrchestratorAgentOperative

agent = CampaignStrategyOrchestratorAgentOperative()

print("=== CampaignStrategyOrchestratorAgentOperative ===")
print(f"agent_id: {getattr(agent, 'agent_id', 'NO TIENE')}")
print(f"agent_name: {getattr(agent, 'agent_name', 'NO TIENE')}")
print(f"version: {getattr(agent, 'version', 'NO TIENE')}")
print(f"execute_operative: {hasattr(agent, 'execute_operative')}")
print(f"execute: {hasattr(agent, 'execute')}")
print(f"health_check: {hasattr(agent, 'health_check')}")
