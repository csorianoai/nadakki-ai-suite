# ===============================================================================
# NADAKKI AI Suite - RSAAdCopyGeneratorIA
# agents/marketing/rsa_ad_copy_generator_agent.py
# Day 4 - Component 2 of 3
# ===============================================================================

"""
RSA Ad Copy Generator Agent - creates responsive search ad copy.

Generates ad headlines and descriptions based on:
- Knowledge Base templates (industry-specific)
- Guardrails (forbidden words, length limits)
- Campaign context (goal, service, brand)
- Ad copy best practices from rules.yaml

Validates all generated copy against content guardrails before outputting.

Usage:
    generator = RSAAdCopyGeneratorIA(knowledge_store)
    
    plan = generator.generate_ad_copy(
        tenant_id="bank01",
        context={
            "service": "Personal Loans",
            "brand_name": "CrediBank",
            "goal": "leads",
            "industry": "financial_services",
            "usp": ["Low rates", "Fast approval", "No hidden fees"],
        }
    )
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from core.knowledge.yaml_store import YamlKnowledgeStore
from core.agents.action_plan import ActionPlan, OperationPriority

logger = logging.getLogger("nadakki.agents.rsa_generator")


class RSAAdCopyGeneratorIA:
    """
    Generates compliant RSA ad copy based on templates and guardrails.
    
    Phase 1: Template-based generation (rules + patterns)
    Phase 2: LLM-powered generation (with KB context injection)
    """
    
    AGENT_NAME = "RSAAdCopyGeneratorIA"
    VERSION = "1.0.0"
    
    # RSA Requirements
    MIN_HEADLINES = 8
    MAX_HEADLINES = 15
    MIN_DESCRIPTIONS = 3
    MAX_DESCRIPTIONS = 4
    MAX_HEADLINE_LENGTH = 30
    MAX_DESCRIPTION_LENGTH = 90
    
    def __init__(self, knowledge_store: YamlKnowledgeStore):
        self.kb = knowledge_store
        logger.info(f"{self.AGENT_NAME} v{self.VERSION} initialized")
    
    # ---------------------------------------------------------------------
    # Main Entry Point
    # ---------------------------------------------------------------------
    
    def generate_ad_copy(
        self,
        tenant_id: str,
        context: dict,
    ) -> ActionPlan:
        """
        Generate RSA ad copy and return as ActionPlan.
        
        Args:
            context: Dict with:
                - service: str (e.g., "Personal Loans")
                - brand_name: str (e.g., "CrediBank")
                - goal: str ("leads", "sales", "awareness")
                - industry: str (default: "financial_services")
                - usp: list[str] (unique selling points)
                - target_audience: str (optional)
                - tone: str ("professional", "friendly", "urgent") default: "professional"
                - cta_variations: list[str] (optional custom CTAs)
        """
        service = context.get("service", "Financial Services")
        brand = context.get("brand_name", "")
        industry = context.get("industry", "financial_services")
        goal = context.get("goal", "leads")
        usps = context.get("usp", [])
        tone = context.get("tone", "professional")
        
        logger.info(
            f"[{tenant_id}] Generating RSA copy: service={service}, "
            f"brand={brand}, goal={goal}, tone={tone}"
        )
        
        # 1. Generate headlines
        headlines = self._generate_headlines(context)
        
        # 2. Generate descriptions
        descriptions = self._generate_descriptions(context)
        
        # 3. Validate against guardrails
        valid, violations, warnings = self.kb.validate_copy(
            tenant_id, headlines, descriptions, industry
        )
        
        # 4. Fix violations by filtering out bad ones
        if not valid:
            headlines, descriptions = self._fix_violations(
                headlines, descriptions, violations, context
            )
            # Re-validate
            valid, violations, warnings = self.kb.validate_copy(
                tenant_id, headlines, descriptions, industry
            )
        
        # 5. Build ActionPlan
        plan = ActionPlan(
            tenant_id=tenant_id,
            agent_name=self.AGENT_NAME,
            title=f"RSA Ad Copy - {service} ({brand})",
            description=(
                f"Generated {len(headlines)} headlines and {len(descriptions)} descriptions "
                f"for {service}. Validated against {industry} guardrails."
            ),
            rationale=self._build_rationale(context, headlines, descriptions, warnings),
        )
        
        # Get matched RSA rules
        rsa_rules = self.kb.match_rules(tenant_id, {"ad_type": "rsa"}, industry)
        plan.rules_consulted = [r["id"] for r in rsa_rules]
        
        # Add the ad copy as plan metadata (it's data, not an operation)
        plan.benchmarks_referenced = {
            "headlines": headlines,
            "descriptions": descriptions,
            "ad_strength_estimate": self._estimate_ad_strength(headlines, descriptions),
            "validation": {
                "valid": valid,
                "violations": violations,
                "warnings": warnings,
            },
        }
        
        # Add a monitoring operation to track new ad performance
        plan.add_operation(
            operation_name="get_campaign_metrics@v1",
            payload={
                "metrics": ["ad_strength", "ctr", "impressions"],
                "context": "post_ad_creation_monitoring",
            },
            description="Monitor new RSA ad performance after 48 hours",
            priority=OperationPriority.LOW,
        )
        
        plan.risk_score = 0.2 if valid else 0.5
        plan.propose()
        
        logger.info(
            f"[{tenant_id}] RSA copy generated: {len(headlines)} headlines, "
            f"{len(descriptions)} descriptions, valid={valid}, "
            f"ad_strength={plan.benchmarks_referenced['ad_strength_estimate']}"
        )
        
        return plan
    
    # ---------------------------------------------------------------------
    # Headline Generation
    # ---------------------------------------------------------------------
    
    def _generate_headlines(self, context: dict) -> List[str]:
        """Generate up to 15 headlines based on context."""
        service = context.get("service", "Our Services")
        brand = context.get("brand_name", "")
        usps = context.get("usp", [])
        goal = context.get("goal", "leads")
        tone = context.get("tone", "professional")
        ctas = context.get("cta_variations", [])
        
        headlines = []
        
        # Brand + Service headlines
        if brand:
            headlines.append(f"{brand} {service}"[:self.MAX_HEADLINE_LENGTH])
            headlines.append(f"{brand} - Apply Now"[:self.MAX_HEADLINE_LENGTH])
        
        # Service-focused headlines
        headlines.append(f"{service} Made Easy"[:self.MAX_HEADLINE_LENGTH])
        headlines.append(f"Best {service} Options"[:self.MAX_HEADLINE_LENGTH])
        headlines.append(f"Compare {service} Rates"[:self.MAX_HEADLINE_LENGTH])
        
        # CTA headlines
        cta_templates = ctas or self._get_cta_templates(goal, tone)
        for cta in cta_templates[:3]:
            headlines.append(cta[:self.MAX_HEADLINE_LENGTH])
        
        # USP headlines
        for usp in usps[:4]:
            headlines.append(usp[:self.MAX_HEADLINE_LENGTH])
        
        # Trust headlines
        trust_headlines = self._get_trust_headlines(context)
        headlines.extend(trust_headlines[:3])
        
        # Urgency/benefit headlines based on tone
        if tone == "urgent":
            headlines.append("Limited Time Offer"[:self.MAX_HEADLINE_LENGTH])
            headlines.append("Don't Miss Out"[:self.MAX_HEADLINE_LENGTH])
        elif tone == "friendly":
            headlines.append("We're Here To Help"[:self.MAX_HEADLINE_LENGTH])
            headlines.append("Your Goals, Our Priority"[:self.MAX_HEADLINE_LENGTH])
        
        # Deduplicate and trim
        seen = set()
        unique = []
        for h in headlines:
            h_clean = h.strip()
            if h_clean and h_clean.lower() not in seen and len(h_clean) <= self.MAX_HEADLINE_LENGTH:
                seen.add(h_clean.lower())
                unique.append(h_clean)
        
        return unique[:self.MAX_HEADLINES]
    
    def _get_cta_templates(self, goal: str, tone: str) -> List[str]:
        """Get CTA templates based on goal and tone."""
        ctas = {
            "leads": {
                "professional": ["Apply Online Today", "Get Started Now", "Request Your Quote"],
                "friendly": ["See Your Options", "Let's Get Started", "Find What Fits"],
                "urgent": ["Apply Now - Limited", "Act Fast - Apply", "Start Today"],
            },
            "sales": {
                "professional": ["Buy Now", "Shop Today", "Get Yours Now"],
                "friendly": ["Explore Options", "Find Your Match", "See What's New"],
                "urgent": ["Limited Offer - Buy", "Flash Sale - Shop", "Ending Soon"],
            },
            "awareness": {
                "professional": ["Learn More Today", "Discover More", "See How It Works"],
                "friendly": ["Come See For Yourself", "Check It Out", "See What We Do"],
                "urgent": ["Find Out Now", "Don't Miss This", "See Why - Now"],
            },
        }
        return ctas.get(goal, ctas["leads"]).get(tone, ctas["leads"]["professional"])
    
    def _get_trust_headlines(self, context: dict) -> List[str]:
        """Generate trust-building headlines."""
        industry = context.get("industry", "")
        
        trust = ["Trusted & Reliable", "Licensed & Regulated"]
        
        if industry == "financial_services" or industry == "banking":
            trust.extend(["FDIC Insured", "Secure & Protected"])
        elif industry == "insurance":
            trust.extend(["Licensed Agents", "Coverage You Trust"])
        elif industry == "lending":
            trust.extend(["Transparent Terms", "No Hidden Fees"])
        
        return [t for t in trust if len(t) <= self.MAX_HEADLINE_LENGTH]
    
    # ---------------------------------------------------------------------
    # Description Generation
    # ---------------------------------------------------------------------
    
    def _generate_descriptions(self, context: dict) -> List[str]:
        """Generate up to 4 descriptions based on context."""
        service = context.get("service", "our services")
        brand = context.get("brand_name", "us")
        usps = context.get("usp", [])
        goal = context.get("goal", "leads")
        industry = context.get("industry", "financial_services")
        
        descriptions = []
        
        # Primary description - service + CTA
        primary = (
            f"Explore {service.lower()} with {brand}. "
            f"Competitive rates and flexible options. Apply online today."
        )
        descriptions.append(primary[:self.MAX_DESCRIPTION_LENGTH])
        
        # USP-focused description
        if usps:
            usp_text = ", ".join(usps[:3])
            usp_desc = f"{brand} offers {service.lower()}: {usp_text}. See your options now."
            descriptions.append(usp_desc[:self.MAX_DESCRIPTION_LENGTH])
        
        # Trust description
        trust_desc = self._get_trust_description(context)
        descriptions.append(trust_desc[:self.MAX_DESCRIPTION_LENGTH])
        
        # Benefit description
        benefit = (
            f"Find the right {service.lower()} for your needs. "
            f"Quick application process. Get a decision today."
        )
        descriptions.append(benefit[:self.MAX_DESCRIPTION_LENGTH])
        
        return descriptions[:self.MAX_DESCRIPTIONS]
    
    def _get_trust_description(self, context: dict) -> str:
        """Generate trust-focused description."""
        brand = context.get("brand_name", "We")
        industry = context.get("industry", "")
        
        if industry in ("financial_services", "banking"):
            return (
                f"Choose {brand} for secure, regulated financial services. "
                f"Thousands of satisfied customers. Terms and conditions apply."
            )
        elif industry == "insurance":
            return (
                f"Protect what matters with {brand}. Licensed agents, "
                f"comprehensive coverage. Get your free quote today."
            )
        else:
            return (
                f"Trust {brand} for reliable, professional service. "
                f"Serving customers since day one. Learn more today."
            )
    
    # ---------------------------------------------------------------------
    # Violation Fixing
    # ---------------------------------------------------------------------
    
    def _fix_violations(
        self,
        headlines: List[str],
        descriptions: List[str],
        violations: List[str],
        context: dict,
    ) -> Tuple[List[str], List[str]]:
        """Remove headlines/descriptions that violate guardrails."""
        # Parse which headlines/descriptions to remove
        bad_headline_indices = set()
        bad_desc_indices = set()
        
        for v in violations:
            v_lower = v.lower()
            if "headline" in v_lower:
                try:
                    idx = int(v_lower.split("headline")[1].strip().split()[0]) - 1
                    bad_headline_indices.add(idx)
                except (ValueError, IndexError):
                    pass
            elif "description" in v_lower:
                try:
                    idx = int(v_lower.split("description")[1].strip().split()[0]) - 1
                    bad_desc_indices.add(idx)
                except (ValueError, IndexError):
                    pass
        
        # Filter out bad ones
        clean_headlines = [
            h for i, h in enumerate(headlines) if i not in bad_headline_indices
        ]
        clean_descriptions = [
            d for i, d in enumerate(descriptions) if i not in bad_desc_indices
        ]
        
        # Ensure minimums
        if len(clean_headlines) < self.MIN_HEADLINES:
            fillers = self._get_filler_headlines(context, self.MIN_HEADLINES - len(clean_headlines))
            clean_headlines.extend(fillers)
        
        if len(clean_descriptions) < self.MIN_DESCRIPTIONS:
            brand = context.get("brand_name", "us")
            clean_descriptions.append(
                f"Learn more about what {brand} can offer. Visit our website today."
                [:self.MAX_DESCRIPTION_LENGTH]
            )
        
        return clean_headlines, clean_descriptions
    
    def _get_filler_headlines(self, context: dict, count: int) -> List[str]:
        """Generate safe filler headlines."""
        brand = context.get("brand_name", "")
        fillers = [
            "Get Started Today",
            "See Your Options",
            "Apply In Minutes",
            "Quick & Simple",
            "Start Your Journey",
            "Your Goals Matter",
            f"Choose {brand}" if brand else "Smart Choice",
        ]
        return [f[:self.MAX_HEADLINE_LENGTH] for f in fillers[:count]]
    
    # ---------------------------------------------------------------------
    # Ad Strength Estimation
    # ---------------------------------------------------------------------
    
    def _estimate_ad_strength(
        self, headlines: List[str], descriptions: List[str]
    ) -> str:
        """
        Estimate Google Ads' Ad Strength rating.
        Based on number of assets and variety.
        """
        score = 0
        
        # Headline count (15 max = best)
        if len(headlines) >= 12:
            score += 3
        elif len(headlines) >= 8:
            score += 2
        elif len(headlines) >= 5:
            score += 1
        
        # Description count (4 max = best)
        if len(descriptions) >= 4:
            score += 2
        elif len(descriptions) >= 3:
            score += 1
        
        # Headline variety (check for diverse patterns)
        unique_starts = set(h.split()[0].lower() for h in headlines if h.strip())
        if len(unique_starts) >= 6:
            score += 2
        elif len(unique_starts) >= 4:
            score += 1
        
        # Length variety
        lengths = [len(h) for h in headlines]
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            if 15 <= avg_len <= 25:
                score += 1
        
        # Map score to Ad Strength
        if score >= 7:
            return "Excellent"
        elif score >= 5:
            return "Good"
        elif score >= 3:
            return "Average"
        else:
            return "Poor"
    
    # ---------------------------------------------------------------------
    # Rationale
    # ---------------------------------------------------------------------
    
    def _build_rationale(
        self,
        context: dict,
        headlines: List[str],
        descriptions: List[str],
        warnings: List[str],
    ) -> str:
        """Build rationale for the generated ad copy."""
        parts = [
            f"Generated {len(headlines)} headlines and {len(descriptions)} descriptions.",
            f"Service: {context.get('service', 'N/A')}",
            f"Goal: {context.get('goal', 'N/A')}",
            f"Tone: {context.get('tone', 'professional')}",
        ]
        
        usps = context.get("usp", [])
        if usps:
            parts.append(f"USPs incorporated: {', '.join(usps)}")
        
        if warnings:
            parts.append(f"Warnings: {'; '.join(warnings)}")
        
        return "\n".join(parts)
    
    # ---------------------------------------------------------------------
    # Quick Preview
    # ---------------------------------------------------------------------
    
    def preview_ad(self, tenant_id: str, context: dict) -> dict:
        """
        Quick preview of generated ad copy without ActionPlan.
        Useful for dashboard display.
        """
        headlines = self._generate_headlines(context)
        descriptions = self._generate_descriptions(context)
        industry = context.get("industry", "financial_services")
        
        valid, violations, warnings = self.kb.validate_copy(
            tenant_id, headlines, descriptions, industry
        )
        
        return {
            "headlines": headlines,
            "descriptions": descriptions,
            "headline_count": len(headlines),
            "description_count": len(descriptions),
            "ad_strength": self._estimate_ad_strength(headlines, descriptions),
            "valid": valid,
            "violations": violations,
            "warnings": warnings,
        }
