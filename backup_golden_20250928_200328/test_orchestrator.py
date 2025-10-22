import json
import os
import logging

class AgentOrchestrator:
    def __init__(self, institution_id):
        self.institution_id = institution_id
        self.logger = logging.getLogger(__name__)
        self.agent_registry = self.load_agents()
        self.logger.info(f"[{self.institution_id}] Agents loaded: {self.agent_registry}")

    def load_agents(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "config", "tenants", f"{self.institution_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                config = json.load(f)
                return config.get("enabled_agents", {})
        self.logger.warning(f"[{self.institution_id}] Agent config not found. No agents activated.")
        return {}

if __name__ == "__main__":
    orchestrator = AgentOrchestrator("banreservas")
    print("Agentes activos para banreservas:", orchestrator.agent_registry)
