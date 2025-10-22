"""
NADAKKI AI SUITE - REGISTRY INTEGRADO
Registro completo de todos los agentes del ecosistema
"""

from agents_consolidated.originacion.documentvalidator import DocumentValidator
from agents_consolidated.originacion.riskassessor import RiskAssessor
from agents_consolidated.vigilancia.riskmonitor import RiskMonitor
from agents_consolidated.vigilancia.compliancetracker import ComplianceTracker

AGENT_REGISTRY = {
    "DocumentValidator": {
        "module": "agents_consolidated.originacion.documentvalidator",
        "class": "DocumentValidator",
        "ecosystem": "originacion",
        "type": "operational",
        "status": "active"
    },
    "RiskAssessor": {
        "module": "agents_consolidated.originacion.riskassessor",
        "class": "RiskAssessor", 
        "ecosystem": "originacion",
        "type": "operational",
        "status": "active"
    },
    "RiskMonitor": {
        "module": "agents_consolidated.vigilancia.riskmonitor",
        "class": "RiskMonitor",
        "ecosystem": "vigilancia", 
        "type": "operational",
        "status": "active"
    },
    "ComplianceTracker": {
        "module": "agents_consolidated.vigilancia.compliancetracker",
        "class": "ComplianceTracker",
        "ecosystem": "vigilancia",
        "type": "operational", 
        "status": "active"
    }
}

def get_operational_agents():
    return [name for name, config in AGENT_REGISTRY.items() if config.get("status") == "active"]

def create_agent_instance(agent_name, tenant_id=None):
    if agent_name == "DocumentValidator":
        return DocumentValidator(tenant_id=tenant_id)
    elif agent_name == "RiskAssessor":
        return RiskAssessor(tenant_id=tenant_id)
    elif agent_name == "RiskMonitor":
        return RiskMonitor(tenant_id=tenant_id)
    elif agent_name == "ComplianceTracker":
        return ComplianceTracker(tenant_id=tenant_id)
    else:
        raise ValueError(f"Agent {agent_name} not implemented")
