"""
NADAKKI AI Suite - Policy Engine
Multi-Tenant Policy Validation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import yaml
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class PolicyViolation:
    rule: str
    message: str
    severity: str  # ERROR, WARNING
    requires_approval: bool = False


@dataclass 
class PolicyResult:
    approved: bool
    violations: List[PolicyViolation]
    requires_approval: bool
    approval_reason: Optional[str] = None


class PolicyEngine:
    """Multi-tenant policy engine with YAML rules."""
    
    DEFAULT_POLICY = {
        "budget_limits": {"daily_max_usd": 1000, "change_max_percent": 50},
        "keyword_rules": {"prohibited": []},
        "approval_gates": []
    }
    
    def __init__(self, policies_dir: str = "config/policies"):
        self.policies_dir = policies_dir
        self._cache: Dict[str, dict] = {}
        os.makedirs(policies_dir, exist_ok=True)
    
    async def load_policy(self, tenant_id: str) -> dict:
        if tenant_id in self._cache:
            return self._cache[tenant_id]
        
        policy_file = os.path.join(self.policies_dir, f"{tenant_id}.yaml")
        if os.path.exists(policy_file):
            with open(policy_file) as f:
                policy = {**self.DEFAULT_POLICY, **yaml.safe_load(f)}
        else:
            policy = self.DEFAULT_POLICY.copy()
        
        self._cache[tenant_id] = policy
        return policy
    
    async def validate(self, request, current_state: dict = None) -> PolicyResult:
        policy = await self.load_policy(request.tenant_id)
        violations = []
        requires_approval = False
        approval_reason = None
        
        if request.operation_base in ["update_campaign_budget", "update_budget"]:
            new_budget = request.payload.get("new_budget", 0)
            limits = policy.get("budget_limits", {})
            
            # Max budget check
            max_budget = limits.get("daily_max_usd", 1000)
            if new_budget > max_budget:
                violations.append(PolicyViolation("daily_max_usd", f"Budget ${new_budget} exceeds max ${max_budget}", "ERROR"))
            
            # Percent change check
            if current_state and "current_budget" in current_state:
                current = current_state["current_budget"]
                if current > 0:
                    change_pct = abs(new_budget - current) / current * 100
                    max_change = limits.get("change_max_percent", 50)
                    if change_pct > max_change:
                        violations.append(PolicyViolation("percent_change_max", f"Change {change_pct:.1f}% exceeds max {max_change}%", "WARNING", requires_approval=True))
                        requires_approval = True
                        approval_reason = f"Budget change of {change_pct:.1f}%"
        
        if request.operation_base in ["add_keywords", "create_rsa_ad"]:
            prohibited = policy.get("keyword_rules", {}).get("prohibited", [])
            texts = []
            for key in ["keywords", "headlines", "descriptions"]:
                for item in request.payload.get(key, []):
                    texts.append(item.get("text", item) if isinstance(item, dict) else str(item))
            
            for text in texts:
                for phrase in prohibited:
                    if phrase.lower() in text.lower():
                        violations.append(PolicyViolation("prohibited_keywords", f"Contains prohibited: '{phrase}'", "ERROR"))
        
        return PolicyResult(
            approved=not any(v.severity == "ERROR" for v in violations),
            violations=violations,
            requires_approval=requires_approval,
            approval_reason=approval_reason
        )
    
    async def validate_content(self, content_list: List[str], tenant_id: str) -> dict:
        policy = await self.load_policy(tenant_id)
        prohibited = policy.get("keyword_rules", {}).get("prohibited", [])
        
        approved, rejected = [], []
        for content in content_list:
            issues = [f"Contains: {p}" for p in prohibited if p.lower() in content.lower()]
            if issues:
                rejected.append({"content": content, "reasons": issues})
            else:
                approved.append(content)
        
        return {"approved": approved, "rejected": rejected, "total": len(content_list)}
    
    def invalidate_cache(self, tenant_id: str = None):
        if tenant_id:
            self._cache.pop(tenant_id, None)
        else:
            self._cache.clear()
