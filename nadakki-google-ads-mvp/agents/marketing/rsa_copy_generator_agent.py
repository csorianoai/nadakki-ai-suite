"""
NADAKKI AI Suite - RSA Ad Copy Generator Agent
Generate Responsive Search Ad Headlines and Descriptions
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from core.agents.action_plan import ActionPlan, OperationPriority

logger = logging.getLogger(__name__)


class RSAAdCopyGeneratorAgent:
    """
    RSA copy generator that:
    - Generates headlines (max 30 chars)
    - Generates descriptions (max 90 chars)
    - Validates against policy
    - Creates executable action plans
    """
    
    AGENT_ID = "rsa_copy_agent"
    AGENT_NAME = "RSAAdCopyGeneratorAgent"
    
    MAX_HEADLINE_LENGTH = 30
    MAX_DESCRIPTION_LENGTH = 90
    MIN_HEADLINES = 3
    MAX_HEADLINES = 15
    MIN_DESCRIPTIONS = 2
    MAX_DESCRIPTIONS = 4
    
    def __init__(self, policy_engine):
        self.policy_engine = policy_engine
    
    async def generate_ad_copy(self, tenant_id: str, product_info: Dict[str, Any],
                               num_headlines: int = 10, num_descriptions: int = 4) -> ActionPlan:
        """Generate RSA ad copy."""
        plan = ActionPlan(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            tenant_id=tenant_id,
            tags=["ads", "rsa", "copy", "creative"]
        )
        
        headline_candidates = self._generate_headlines(product_info, num_headlines * 2)
        description_candidates = self._generate_descriptions(product_info, num_descriptions * 2)
        
        headline_validation = await self.policy_engine.validate_content(headline_candidates, tenant_id)
        description_validation = await self.policy_engine.validate_content(description_candidates, tenant_id)
        
        approved_headlines = headline_validation["approved"][:num_headlines]
        approved_descriptions = description_validation["approved"][:num_descriptions]
        
        plan.analysis = {
            "product": product_info.get("name", "Unknown"),
            "headlines_generated": len(headline_candidates),
            "headlines_approved": len(approved_headlines),
            "headlines_rejected": len(headline_validation["rejected"]),
            "descriptions_generated": len(description_candidates),
            "descriptions_approved": len(approved_descriptions),
            "descriptions_rejected": len(description_validation["rejected"])
        }
        
        plan.rationale = self._build_rationale(plan.analysis)
        
        if len(approved_headlines) < self.MIN_HEADLINES:
            plan.risk_score = 0.8
            plan.risk_factors = [f"Only {len(approved_headlines)} headlines (min: {self.MIN_HEADLINES})"]
            return plan
        
        if len(approved_descriptions) < self.MIN_DESCRIPTIONS:
            plan.risk_score = 0.7
            plan.risk_factors = [f"Only {len(approved_descriptions)} descriptions (min: {self.MIN_DESCRIPTIONS})"]
            return plan
        
        plan.add_operation(
            operation_name="create_rsa_ad@v1",
            params={
                "ad_group_id": product_info.get("ad_group_id"),
                "headlines": [{"text": h} for h in approved_headlines],
                "descriptions": [{"text": d} for d in approved_descriptions],
                "final_url": product_info.get("landing_url"),
                "path1": product_info.get("path1", ""),
                "path2": product_info.get("path2", "")
            },
            priority=OperationPriority.MEDIUM,
            estimated_impact={"new_ad_variants": len(approved_headlines) * len(approved_descriptions)},
            requires_review=True
        )
        
        plan.requires_approval = True
        plan.approval_reason = "Creative content requires human review"
        plan.risk_score = 0.3
        
        return plan
    
    def _generate_headlines(self, product_info: Dict[str, Any], count: int) -> List[str]:
        """Generate headline candidates using templates."""
        templates = [
            "{name} - {benefit}", "Get {name} Today", "{benefit} with {name}",
            "Top Rated {category}", "{name} | {cta}", "Best {category} Deals",
            "{discount}% Off {name}", "Shop {name} Now", "{name} Sale Event",
            "Premium {category}", "{name} - Free Shipping", "Official {name} Store",
            "{cta} - {name}", "New {name} Arrivals", "{name} Starting at ${price}"
        ]
        
        name = product_info.get("name", "Product")[:15]
        benefit = product_info.get("benefit", "Quality")[:10]
        category = product_info.get("category", "Products")[:10]
        cta = product_info.get("cta", "Shop Now")[:8]
        discount = product_info.get("discount", "20")
        price = product_info.get("price", "99")
        
        headlines = []
        for template in templates[:count]:
            headline = template.format(name=name, benefit=benefit, category=category,
                                       cta=cta, discount=discount, price=price)
            if len(headline) <= self.MAX_HEADLINE_LENGTH:
                headlines.append(headline)
            else:
                headlines.append(headline[:self.MAX_HEADLINE_LENGTH-3] + "...")
        
        return headlines
    
    def _generate_descriptions(self, product_info: Dict[str, Any], count: int) -> List[str]:
        """Generate description candidates."""
        templates = [
            "Discover {name}. {benefit}. Shop our collection today and save!",
            "Looking for {category}? {name} offers {benefit}. Order now!",
            "{name} - The best {category} for your needs. Free shipping available.",
            "Get premium {category} with {name}. {benefit}. Shop the sale now.",
            "Transform your experience with {name}. Quality guaranteed. Shop today!",
            "{benefit} starts with {name}. Browse our {category} collection now."
        ]
        
        name = product_info.get("name", "Our Product")
        benefit = product_info.get("benefit", "Quality you can trust")
        category = product_info.get("category", "products")
        
        descriptions = []
        for template in templates[:count]:
            desc = template.format(name=name, benefit=benefit, category=category)
            if len(desc) <= self.MAX_DESCRIPTION_LENGTH:
                descriptions.append(desc)
            else:
                descriptions.append(desc[:self.MAX_DESCRIPTION_LENGTH-3] + "...")
        
        return descriptions
    
    def _build_rationale(self, analysis: Dict) -> str:
        return (
            f"Generated {analysis['headlines_generated']} headlines and "
            f"{analysis['descriptions_generated']} descriptions for {analysis['product']}. "
            f"After validation: {analysis['headlines_approved']} headlines and "
            f"{analysis['descriptions_approved']} descriptions approved."
        )
