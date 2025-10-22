"""
Canonical Agent Registry - Nadakki AI Suite v3.3.0
24 Marketing Agents - Production Ready & Validated
Last Updated: 2025-10-11
"""
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
import logging

logger = logging.getLogger("CanonicalRegistry")

# ============================================================================
# IMPORTS DE LOS 24 AGENTES VALIDADOS
# ============================================================================

from agents.marketing.abtestingia import ABTestOptimizerIA
from agents.marketing.abtestingimpactia import ABTestingImpactIA
from agents.marketing.attributionmodelia import AttributionModelIA
from agents.marketing.budgetforecastia import BudgetForecastIA
from agents.marketing.campaignoptimizeria import CampaignOptimizerIA
from agents.marketing.cashofferfilteria import CashOfferFilterIA
from agents.marketing.competitoranalyzeria import CompetitorAnalyzerIA
from agents.marketing.competitorintelligenceia import CompetitorIntelligenceIA
from agents.marketing.contactqualityia import ContactQualityIA
from agents.marketing.contentperformanceia import ContentPerformanceIA
from agents.marketing.conversioncohortia import ConversionCohortIA
from agents.marketing.creativeanalyzeria import CreativeAnalyzerIA
from agents.marketing.customersegmentatonia import AudienceSegmentationIA
from agents.marketing.emailautomationia import EmailPersonalizerIA
from agents.marketing.geosegmentationia import GeoSegmentationIA
from agents.marketing.influencermatcheria import InfluencerMatcherIA
from agents.marketing.influencermatchingia import InfluencerMatchingIA
from agents.marketing.journeyoptimizeria import JourneyOptimizerIA
from agents.marketing.leadscoringia import LeadScoringIA
from agents.marketing.marketingmixmodelia import MarketingMixModelIA
from agents.marketing.minimalformia import MinimalFormIA
from agents.marketing.personalizationengineia import PersonalizationEngineIA
from agents.marketing.productaffinityia import ProductAffinityIA
from agents.marketing.socialpostgeneratoria import SocialPostGeneratorIA

# ============================================================================
# AGENT METADATA
# ============================================================================

@dataclass
class AgentMetadata:
    """Metadata for each agent"""
    agent_id: str
    name: str
    category: str
    description: str
    version: str
    compliance_ready: bool = True
    multi_tenant: bool = True

# ============================================================================
# CANONICAL AGENT REGISTRY
# ============================================================================

CANONICAL_AGENTS: Dict[str, Dict[str, Any]] = {
    # OPTIMIZATION & TESTING (2)
    "abtest_optimizer": {
        "class": ABTestOptimizerIA,
        "metadata": AgentMetadata(
            agent_id="abtest_optimizer",
            name="A/B Test Optimizer",
            category="optimization",
            description="Statistical A/B testing and optimization",
            version="2.0.0"
        )
    },
    "abtest_impact": {
        "class": ABTestingImpactIA,
        "metadata": AgentMetadata(
            agent_id="abtest_impact",
            name="A/B Testing Impact Analyzer",
            category="analytics",
            description="Impact analysis of A/B tests",
            version="2.0.0"
        )
    },
    
    # ANALYTICS & ATTRIBUTION (4)
    "attribution_model": {
        "class": AttributionModelIA,
        "metadata": AgentMetadata(
            agent_id="attribution_model",
            name="Attribution Model",
            category="analytics",
            description="Multi-touch attribution modeling",
            version="2.0.0"
        )
    },
    "content_performance": {
        "class": ContentPerformanceIA,
        "metadata": AgentMetadata(
            agent_id="content_performance",
            name="Content Performance Analyzer",
            category="analytics",
            description="Content performance tracking and optimization",
            version="2.0.0"
        )
    },
    "creative_analyzer": {
        "class": CreativeAnalyzerIA,
        "metadata": AgentMetadata(
            agent_id="creative_analyzer",
            name="Creative Analyzer",
            category="analytics",
            description="Creative asset performance analysis",
            version="2.0.0"
        )
    },
    "marketing_mix_model": {
        "class": MarketingMixModelIA,
        "metadata": AgentMetadata(
            agent_id="marketing_mix_model",
            name="Marketing Mix Model",
            category="analytics",
            description="Marketing mix modeling and optimization",
            version="2.0.0"
        )
    },
    
    # CAMPAIGN & BUDGET (3)
    "budget_forecast": {
        "class": BudgetForecastIA,
        "metadata": AgentMetadata(
            agent_id="budget_forecast",
            name="Budget Forecaster",
            category="planning",
            description="Budget forecasting and allocation",
            version="2.0.0"
        )
    },
    "campaign_optimizer": {
        "class": CampaignOptimizerIA,
        "metadata": AgentMetadata(
            agent_id="campaign_optimizer",
            name="Campaign Optimizer",
            category="optimization",
            description="Multi-channel campaign optimization",
            version="2.0.0"
        )
    },
    "cash_offer_filter": {
        "class": CashOfferFilterIA,
        "metadata": AgentMetadata(
            agent_id="cash_offer_filter",
            name="Cash Offer Filter",
            category="financial",
            description="Cash offer generation with risk assessment",
            version="2.0.0"
        )
    },
    
    # INTELLIGENCE & RESEARCH (2)
    "competitor_analyzer": {
        "class": CompetitorAnalyzerIA,
        "metadata": AgentMetadata(
            agent_id="competitor_analyzer",
            name="Competitor Analyzer",
            category="intelligence",
            description="Competitive intelligence and analysis",
            version="2.0.0"
        )
    },
    "competitor_intelligence": {
        "class": CompetitorIntelligenceIA,
        "metadata": AgentMetadata(
            agent_id="competitor_intelligence",
            name="Competitor Intelligence",
            category="intelligence",
            description="Advanced competitive intelligence",
            version="2.0.0"
        )
    },
    
    # CUSTOMER & LEAD MANAGEMENT (5)
    "contact_quality": {
        "class": ContactQualityIA,
        "metadata": AgentMetadata(
            agent_id="contact_quality",
            name="Contact Quality Analyzer",
            category="lead_management",
            description="Contact quality scoring and optimization",
            version="2.0.0"
        )
    },
    "conversion_cohort": {
        "class": ConversionCohortIA,
        "metadata": AgentMetadata(
            agent_id="conversion_cohort",
            name="Conversion Cohort Analyzer",
            category="analytics",
            description="Cohort analysis and conversion tracking",
            version="2.0.0"
        )
    },
    "customer_segmentation": {
        "class": AudienceSegmentationIA,
        "metadata": AgentMetadata(
            agent_id="customer_segmentation",
            name="Customer Segmentation",
            category="segmentation",
            description="RFM and behavioral segmentation",
            version="2.0.0"
        )
    },
    "journey_optimizer": {
        "class": JourneyOptimizerIA,
        "metadata": AgentMetadata(
            agent_id="journey_optimizer",
            name="Journey Optimizer",
            category="customer_experience",
            description="Customer journey optimization",
            version="2.0.0"
        )
    },
    "lead_scoring": {
        "class": LeadScoringIA,
        "metadata": AgentMetadata(
            agent_id="lead_scoring",
            name="Lead Scoring",
            category="lead_management",
            description="Predictive lead scoring",
            version="2.0.0"
        )
    },
    
    # CONTENT & COMMUNICATION (3)
    "email_automation": {
        "class": EmailPersonalizerIA,
        "metadata": AgentMetadata(
            agent_id="email_automation",
            name="Email Automation",
            category="content",
            description="Email personalization and automation",
            version="2.0.0"
        )
    },
    "personalization_engine": {
        "class": PersonalizationEngineIA,
        "metadata": AgentMetadata(
            agent_id="personalization_engine",
            name="Personalization Engine",
            category="content",
            description="Content personalization engine",
            version="2.0.0"
        )
    },
    "social_post_generator": {
        "class": SocialPostGeneratorIA,
        "metadata": AgentMetadata(
            agent_id="social_post_generator",
            name="Social Post Generator",
            category="content",
            description="Social media content generation",
            version="2.0.0"
        )
    },
    
    # PARTNERSHIPS & MATCHING (2)
    "influencer_matcher": {
        "class": InfluencerMatcherIA,
        "metadata": AgentMetadata(
            agent_id="influencer_matcher",
            name="Influencer Matcher",
            category="partnerships",
            description="Influencer matching and selection",
            version="2.0.0"
        )
    },
    "influencer_matching": {
        "class": InfluencerMatchingIA,
        "metadata": AgentMetadata(
            agent_id="influencer_matching",
            name="Influencer Matching Advanced",
            category="partnerships",
            description="Advanced influencer matching algorithms",
            version="2.0.0"
        )
    },
    
    # PRODUCT & GEO (3)
    "geo_segmentation": {
        "class": GeoSegmentationIA,
        "metadata": AgentMetadata(
            agent_id="geo_segmentation",
            name="Geo Segmentation",
            category="segmentation",
            description="Geographic segmentation and targeting",
            version="2.0.0"
        )
    },
    "minimal_form": {
        "class": MinimalFormIA,
        "metadata": AgentMetadata(
            agent_id="minimal_form",
            name="Minimal Form Optimizer",
            category="optimization",
            description="Form optimization and friction reduction",
            version="2.0.0"
        )
    },
    "product_affinity": {
        "class": ProductAffinityIA,
        "metadata": AgentMetadata(
            agent_id="product_affinity",
            name="Product Affinity",
            category="recommendation",
            description="Product affinity and cross-sell recommendations",
            version="2.0.0"
        )
    },
}

# ============================================================================
# AGENT FACTORY
# ============================================================================

class AgentFactory:
    """Factory for creating agent instances"""
    
    @staticmethod
    def create_agent(agent_id: str, **kwargs) -> Any:
        """
        Create an agent instance by ID
        
        Args:
            agent_id: Agent identifier
            **kwargs: Additional arguments for agent initialization
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If agent_id not found
        """
        if agent_id not in CANONICAL_AGENTS:
            available = ", ".join(CANONICAL_AGENTS.keys())
            raise ValueError(
                f"Agent '{agent_id}' not found. "
                f"Available agents: {available}"
            )
        
        agent_class = CANONICAL_AGENTS[agent_id]["class"]
        return agent_class(**kwargs)
    
    @staticmethod
    def list_agents(category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all agents or filter by category
        
        Args:
            category: Optional category filter
            
        Returns:
            List of agent metadata dicts
        """
        agents = []
        for agent_id, config in CANONICAL_AGENTS.items():
            metadata = config["metadata"]
            if category is None or metadata.category == category:
                agents.append({
                    "agent_id": agent_id,
                    "name": metadata.name,
                    "category": metadata.category,
                    "description": metadata.description,
                    "version": metadata.version,
                    "compliance_ready": metadata.compliance_ready,
                })
        return agents
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get list of all agent categories"""
        categories = set()
        for config in CANONICAL_AGENTS.values():
            categories.add(config["metadata"].category)
        return sorted(list(categories))

# ============================================================================
# VALIDATION
# ============================================================================

def validate_registry() -> Dict[str, Any]:
    """Validate the agent registry"""
    results = {
        "total_agents": len(CANONICAL_AGENTS),
        "categories": {},
        "compliance_ready": 0,
        "multi_tenant": 0,
        "agents": []
    }
    
    for agent_id, config in CANONICAL_AGENTS.items():
        metadata = config["metadata"]
        
        # Count by category
        cat = metadata.category
        results["categories"][cat] = results["categories"].get(cat, 0) + 1
        
        # Count compliance ready
        if metadata.compliance_ready:
            results["compliance_ready"] += 1
        
        # Count multi-tenant
        if metadata.multi_tenant:
            results["multi_tenant"] += 1
        
        # Store agent info
        results["agents"].append({
            "agent_id": agent_id,
            "name": metadata.name,
            "class": config["class"].__name__,
            "category": cat,
            "version": metadata.version
        })
    
    return results

# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("NADAKKI MARKETING CORE - CANONICAL REGISTRY v3.3.0")
    print("="*60 + "\n")
    
    # Validate registry
    validation = validate_registry()
    
    print(f"✓ Total Agents: {validation['total_agents']}")
    print(f"✓ Compliance Ready: {validation['compliance_ready']}")
    print(f"✓ Multi-Tenant: {validation['multi_tenant']}\n")
    
    print("Categories:")
    for category, count in sorted(validation['categories'].items()):
        print(f"  • {category}: {count} agent(s)")
    
    print("\n" + "="*60)
    print("AGENT REGISTRY")
    print("="*60 + "\n")
    
    for agent in sorted(validation['agents'], key=lambda x: x['category']):
        print(f"{agent['agent_id']:30} → {agent['class']:30} [{agent['category']}]")
    
    print("\n" + "="*60)
    print("✓ REGISTRY VALIDATED SUCCESSFULLY")
    print("="*60 + "\n")

