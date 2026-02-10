# ===============================================================================
# NADAKKI AI Suite - PolicyEngine
# core/policies/engine.py
# Day 2 - Component 2 of 5
# ===============================================================================

"""
Policy engine for validating Google Ads operations before execution.

MVP Rules (3 core policies):
1. daily_max_usd - Maximum daily spend per campaign
2. percent_change_max - Maximum % change in budget per operation
3. approval_gate - Operations above threshold require human approval

Rules are defined in YAML per tenant:
    config/policies/{tenant_id}.yaml

With global defaults in:
    config/policies/default.yaml

Content Validation:
- validate_content() checks ad copy against forbidden words/phrases
- Extensible for future compliance rules (e.g., financial disclaimers)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import os
import logging

logger = logging.getLogger("nadakki.policies.engine")


# -----------------------------------------------------------------------------
# Policy Result Types
# -----------------------------------------------------------------------------

class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class PolicyResult:
    """Result of policy evaluation."""
    decision: PolicyDecision
    rule_name: str = ""
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOW
    
    @property
    def needs_approval(self) -> bool:
        return self.decision == PolicyDecision.REQUIRE_APPROVAL
    
    def to_dict(self) -> dict:
        return {
            "decision": self.decision.value,
            "rule_name": self.rule_name,
            "reason": self.reason,
            "details": self.details,
            "evaluated_at": self.evaluated_at.isoformat(),
        }


@dataclass
class ContentValidationResult:
    """Result of content/copy validation."""
    valid: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "violations": self.violations,
            "warnings": self.warnings,
        }


# -----------------------------------------------------------------------------
# Default Policies
# -----------------------------------------------------------------------------

DEFAULT_POLICIES = {
    "daily_max_usd": {
        "enabled": True,
        "max_daily_budget_usd": 10000.0,
        "description": "Maximum daily budget per campaign in USD",
    },
    "percent_change_max": {
        "enabled": True,
        "max_percent_change": 50.0,
        "description": "Maximum percentage change in budget per operation",
    },
    "approval_gate": {
        "enabled": True,
        "threshold_usd": 5000.0,
        "description": "Operations above this USD amount require human approval",
    },
    "content_policy": {
        "enabled": True,
        "forbidden_words": [
            "guaranteed", "free money", "get rich",
            "no risk", "100% guaranteed",
        ],
        "required_disclaimers": [],  # Populated per industry
        "max_headline_length": 30,
        "max_description_length": 90,
    },
}


# ---------------------------------------------================================
# Policy Engine
# -------------------------====================================================

class PolicyEngine:
    """
    Evaluates operations against tenant-specific policies.
    
    Usage:
        engine = PolicyEngine()
        
        # Load tenant policies (YAML or dict)
        engine.load_tenant_policies("bank01", {...})
        
        # Validate an operation
        result = engine.validate_operation(
            tenant_id="bank01",
            operation_name="update_campaign_budget@v1",
            payload={"budget_id": "b1", "new_budget": 8000, "previous_budget": 5000},
        )
        
        if not result.allowed:
            print(f"Denied: {result.reason}")
        
        # Validate ad copy
        content_result = engine.validate_content(
            tenant_id="bank01",
            content={"headlines": ["Get Free Money Now!"], "descriptions": ["..."]},
        )
    """
    
    def __init__(self, policies_dir: str = None):
        self._tenant_policies: Dict[str, dict] = {}
        self._policies_dir = policies_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config", "policies"
        )
        logger.info("PolicyEngine initialized")
    
    # ---------------------------------------------------------------------
    # Policy Loading
    # ---------------------------------------------------------------------
    
    def load_tenant_policies(self, tenant_id: str, policies: dict = None):
        """
        Load policies for a tenant.
        
        If policies dict provided, uses that.
        Otherwise, tries to load from YAML file.
        Falls back to DEFAULT_POLICIES.
        """
        if policies:
            # Merge with defaults
            merged = {**DEFAULT_POLICIES}
            for key, value in policies.items():
                if key in merged and isinstance(merged[key], dict):
                    merged[key] = {**merged[key], **value}
                else:
                    merged[key] = value
            
            self._tenant_policies[tenant_id] = merged
            logger.info(f"Loaded custom policies for tenant: {tenant_id}")
            return
        
        # Try YAML file
        yaml_path = os.path.join(self._policies_dir, f"{tenant_id}.yaml")
        if os.path.exists(yaml_path):
            try:
                import yaml
                with open(yaml_path, 'r') as f:
                    file_policies = yaml.safe_load(f)
                
                if file_policies:
                    self.load_tenant_policies(tenant_id, file_policies)
                    return
            except ImportError:
                logger.warning("PyYAML not installed. Using default policies.")
            except Exception as e:
                logger.error(f"Error loading policies from {yaml_path}: {e}")
        
        # Use defaults
        self._tenant_policies[tenant_id] = {**DEFAULT_POLICIES}
        logger.info(f"Using default policies for tenant: {tenant_id}")
    
    def get_policies(self, tenant_id: str) -> dict:
        """Get policies for a tenant (loads defaults if not yet loaded)."""
        if tenant_id not in self._tenant_policies:
            self.load_tenant_policies(tenant_id)
        return self._tenant_policies[tenant_id]
    
    # ---------------------------------------------------------------------
    # Operation Validation
    # ---------------------------------------------------------------------
    
    def validate_operation(
        self,
        tenant_id: str,
        operation_name: str,
        payload: dict,
    ) -> PolicyResult:
        """
        Validate an operation against all applicable policies.
        
        Returns the most restrictive result:
        DENY > REQUIRE_APPROVAL > ALLOW
        """
        policies = self.get_policies(tenant_id)
        results: List[PolicyResult] = []
        
        # Run all applicable rules
        if "budget" in operation_name.lower():
            results.append(self._check_daily_max(policies, payload, tenant_id))
            results.append(self._check_percent_change(policies, payload, tenant_id))
            results.append(self._check_approval_gate(policies, payload, tenant_id))
        
        # If no rules applied, allow by default
        if not results:
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                rule_name="no_applicable_rules",
                reason="No policies apply to this operation",
            )
        
        # Return most restrictive
        denied = [r for r in results if r.decision == PolicyDecision.DENY]
        if denied:
            return denied[0]
        
        approval_needed = [r for r in results if r.decision == PolicyDecision.REQUIRE_APPROVAL]
        if approval_needed:
            return approval_needed[0]
        
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            rule_name="all_policies_passed",
            reason=f"All {len(results)} policies passed",
        )
    
    # ---------------------------------------------------------------------
    # Individual Rules
    # ---------------------------------------------------------------------
    
    def _check_daily_max(
        self, policies: dict, payload: dict, tenant_id: str
    ) -> PolicyResult:
        """Rule 1: Maximum daily budget."""
        rule = policies.get("daily_max_usd", {})
        
        if not rule.get("enabled", True):
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                rule_name="daily_max_usd",
                reason="Rule disabled",
            )
        
        max_budget = rule.get("max_daily_budget_usd", 10000.0)
        new_budget = payload.get("new_budget", 0)
        
        if new_budget > max_budget:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                rule_name="daily_max_usd",
                reason=(
                    f"Budget ${new_budget:.2f} exceeds maximum "
                    f"${max_budget:.2f} for tenant {tenant_id}"
                ),
                details={
                    "new_budget": new_budget,
                    "max_allowed": max_budget,
                    "excess": new_budget - max_budget,
                },
            )
        
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            rule_name="daily_max_usd",
            reason=f"Budget ${new_budget:.2f} within limit ${max_budget:.2f}",
        )
    
    def _check_percent_change(
        self, policies: dict, payload: dict, tenant_id: str
    ) -> PolicyResult:
        """Rule 2: Maximum percentage change."""
        rule = policies.get("percent_change_max", {})
        
        if not rule.get("enabled", True):
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                rule_name="percent_change_max",
                reason="Rule disabled",
            )
        
        max_pct = rule.get("max_percent_change", 50.0)
        new_budget = payload.get("new_budget", 0)
        previous_budget = payload.get("previous_budget")
        
        if not previous_budget or previous_budget <= 0:
            # No previous budget to compare - allow
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                rule_name="percent_change_max",
                reason="No previous budget for comparison",
            )
        
        pct_change = abs(new_budget - previous_budget) / previous_budget * 100
        
        if pct_change > max_pct:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                rule_name="percent_change_max",
                reason=(
                    f"Change {pct_change:.1f}% exceeds maximum "
                    f"{max_pct:.1f}% for tenant {tenant_id}"
                ),
                details={
                    "previous_budget": previous_budget,
                    "new_budget": new_budget,
                    "percent_change": round(pct_change, 2),
                    "max_percent": max_pct,
                },
            )
        
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            rule_name="percent_change_max",
            reason=f"Change {pct_change:.1f}% within limit {max_pct:.1f}%",
        )
    
    def _check_approval_gate(
        self, policies: dict, payload: dict, tenant_id: str
    ) -> PolicyResult:
        """Rule 3: Approval required above threshold."""
        rule = policies.get("approval_gate", {})
        
        if not rule.get("enabled", True):
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                rule_name="approval_gate",
                reason="Rule disabled",
            )
        
        threshold = rule.get("threshold_usd", 5000.0)
        new_budget = payload.get("new_budget", 0)
        
        if new_budget > threshold:
            return PolicyResult(
                decision=PolicyDecision.REQUIRE_APPROVAL,
                rule_name="approval_gate",
                reason=(
                    f"Budget ${new_budget:.2f} exceeds approval threshold "
                    f"${threshold:.2f} for tenant {tenant_id}"
                ),
                details={
                    "new_budget": new_budget,
                    "threshold": threshold,
                },
            )
        
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            rule_name="approval_gate",
            reason=f"Budget ${new_budget:.2f} below approval threshold ${threshold:.2f}",
        )
    
    # ---------------------------------------------------------------------
    # Content Validation
    # ---------------------------------------------------------------------
    
    def validate_content(
        self,
        tenant_id: str,
        content: dict,
    ) -> ContentValidationResult:
        """
        Validate ad copy content against content policies.
        
        Args:
            tenant_id: Tenant for policy lookup
            content: Dict with keys like "headlines", "descriptions", "paths"
            
        Returns:
            ContentValidationResult with violations and warnings
        """
        policies = self.get_policies(tenant_id)
        content_policy = policies.get("content_policy", {})
        
        if not content_policy.get("enabled", True):
            return ContentValidationResult(valid=True)
        
        violations = []
        warnings = []
        
        forbidden_words = content_policy.get("forbidden_words", [])
        max_headline = content_policy.get("max_headline_length", 30)
        max_description = content_policy.get("max_description_length", 90)
        
        # Check headlines
        for i, headline in enumerate(content.get("headlines", [])):
            headline_lower = headline.lower()
            
            # Length check
            if len(headline) > max_headline:
                violations.append(
                    f"Headline {i+1} exceeds {max_headline} chars "
                    f"({len(headline)} chars): '{headline[:30]}...'"
                )
            
            # Forbidden words
            for word in forbidden_words:
                if word.lower() in headline_lower:
                    violations.append(
                        f"Headline {i+1} contains forbidden phrase: '{word}'"
                    )
        
        # Check descriptions
        for i, desc in enumerate(content.get("descriptions", [])):
            desc_lower = desc.lower()
            
            if len(desc) > max_description:
                violations.append(
                    f"Description {i+1} exceeds {max_description} chars "
                    f"({len(desc)} chars)"
                )
            
            for word in forbidden_words:
                if word.lower() in desc_lower:
                    violations.append(
                        f"Description {i+1} contains forbidden phrase: '{word}'"
                    )
        
        # Check required disclaimers
        required = content_policy.get("required_disclaimers", [])
        all_text = " ".join(
            content.get("headlines", []) + content.get("descriptions", [])
        ).lower()
        
        for disclaimer in required:
            if disclaimer.lower() not in all_text:
                warnings.append(
                    f"Missing required disclaimer: '{disclaimer}'"
                )
        
        return ContentValidationResult(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
        )
    
    # ---------------------------------------------------------------------
    # Admin / Info
    # ---------------------------------------------------------------------
    
    def get_all_loaded_tenants(self) -> List[str]:
        """List all tenants with loaded policies."""
        return list(self._tenant_policies.keys())
    
    def get_rules_summary(self, tenant_id: str) -> List[dict]:
        """Get a summary of all rules for a tenant."""
        policies = self.get_policies(tenant_id)
        summary = []
        
        for rule_name, rule_config in policies.items():
            if isinstance(rule_config, dict):
                summary.append({
                    "rule": rule_name,
                    "enabled": rule_config.get("enabled", True),
                    "description": rule_config.get("description", ""),
                })
        
        return summary
