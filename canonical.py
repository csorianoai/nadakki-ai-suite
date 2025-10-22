# filepath: canonical.py
"""
Canonical Agent Registry - Nadakki AI Suite v3.2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Central registry and factory for all 21 enterprise AI agents

This module provides the canonical interface for agent instantiation
and management across the Nadakki AI Suite.

Author: Nadakki AI Suite
Version: 3.2.0
"""

from typing import Dict, Any, Type, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger("CanonicalRegistry")

# ═══════════════════════════════════════════════════════════════════════
# AGENT IMPORTS - 21 AGENTES
# ═══════════════════════════════════════════════════════════════════════

from agents.marketing.leadscoringia import LeadScoringIA, create_agent_instance as create_lead_scoring
from agents.marketing.campaignoptimizeria import CampaignOptimizerIA, create_agent_instance as create_campaign_optimizer
from agents.marketing.attributionmodelia import AttributionModelIA, create_agent_instance as create_attribution
from agents.marketing.personalizationengineia import PersonalizationEngineIA, create_agent_instance as create_personalization
from agents.marketing.journeyoptimizeria import JourneyOptimizerIA, create_agent_instance as create_journey
from agents.marketing.budgetforecastia import BudgetForecastIA, create_agent_instance as create_budget_forecast
from agents.marketing.creativeanalyzeria import CreativeAnalyzerIA, create_agent_instance as create_creative
from agents.marketing.marketingmixmodelia import MarketingMixModelIA, create_agent_instance as create_mmm
from agents.marketing.competitoranalyzeria import CompetitorAnalyzerIA, create_agent_instance as create_competitor
from agents.marketing.abtestingia import ABTestingIA, create_agent_instance as create_abtest
from agents.marketing.abtestingimpactia import ABTestingImpactIA, create_agent_instance as create_abtest_impact
from agents.marketing.competitorintelligenceia import CompetitorIntelligenceIA, create_agent_instance as create_comp_intel
from agents.marketing.content_generator_v3 import ContentGeneratorIA, create_agent_instance as create_content_gen
from agents.marketing.contentperformanceia import ContentPerformanceIA, create_agent_instance as create_content_perf
from agents.marketing.socialpostgeneratoria import SocialPostGeneratorIA, create_agent_instance as create_social_post
from agents.marketing.customersegmentatonia import CustomerSegmentationIA, create_agent_instance as create_segmentation
from agents.marketing.retentionpredictorea import RetentionPredictorIA, create_agent_instance as create_retention
from agents.marketing.emailautomationia import EmailAutomationIA, create_agent_instance as create_email_auto
from agents.marketing.marketingorchestratorea import MarketingOrchestratorIA, create_agent_instance as create_orchestrator
from agents.marketing.influencermatcheria import InfluencerMatcherIA, create_agent_instance as create_influencer_matcher
from agents.marketing.influencermatchingia import InfluencerMatchingIA, create_agent_instance as create_influencer_matching

# ═══════════════════════════════════════════════════════════════════════
# AGENT METADATA
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class AgentMetadata:
    """Metadata for registered agents"""
    agent_id: str
    name: str
    description: str
    version: str
    category: str
    class_ref: Type
    factory_fn: Any
    capabilities: List[str]
    compliance_ready: bool

# ═══════════════════════════════════════════════════════════════════════
# CANONICAL REGISTRY - 21 AGENTES
# ═══════════════════════════════════════════════════════════════════════

CANONICAL_AGENTS: Dict[str, AgentMetadata] = {
    # Sales & Lead Management (1)
    "lead_scoring_ia": AgentMetadata(
        agent_id="lead_scoring_ia",
        name="Lead Scoring & Qualification Engine",
        description="Multi-dimensional lead scoring with buying signals detection",
        version="3.2.0",
        category="sales",
        class_ref=LeadScoringIA,
        factory_fn=create_lead_scoring,
        capabilities=["scoring", "qualification", "prioritization", "pii_detection"],
        compliance_ready=True
    ),
    
    # Marketing Core (5)
    "campaign_optimizer_ia": AgentMetadata(
        agent_id="campaign_optimizer_ia",
        name="Campaign Optimization Engine",
        description="Multi-channel budget optimization and ROI prediction",
        version="3.2.0",
        category="marketing",
        class_ref=CampaignOptimizerIA,
        factory_fn=create_campaign_optimizer,
        capabilities=["optimization", "budget_allocation", "roi_prediction"],
        compliance_ready=True
    ),
    
    "personalization_engine_ia": AgentMetadata(
        agent_id="personalization_engine_ia",
        name="Personalization Engine",
        description="Real-time content and offer personalization",
        version="3.2.0",
        category="marketing",
        class_ref=PersonalizationEngineIA,
        factory_fn=create_personalization,
        capabilities=["personalization", "segmentation", "real_time"],
        compliance_ready=True
    ),
    
    "email_automation_ia": AgentMetadata(
        agent_id="email_automation_ia",
        name="Email Automation Engine",
        description="Intelligent email campaign automation",
        version="3.2.0",
        category="marketing",
        class_ref=EmailAutomationIA,
        factory_fn=create_email_auto,
        capabilities=["email_automation", "campaign_management", "personalization"],
        compliance_ready=True
    ),
    
    "influencer_matcher_ia": AgentMetadata(
        agent_id="influencer_matcher_ia",
        name="Influencer Matcher Engine",
        description="Advanced influencer discovery and matching",
        version="3.2.0",
        category="marketing",
        class_ref=InfluencerMatcherIA,
        factory_fn=create_influencer_matcher,
        capabilities=["influencer_matching", "brand_fit", "audience_analysis"],
        compliance_ready=True
    ),
    
    "influencer_matching_ia": AgentMetadata(
        agent_id="influencer_matching_ia",
        name="Influencer Matching Engine",
        description="AI-powered influencer discovery and brand fit analysis",
        version="3.2.0",
        category="marketing",
        class_ref=InfluencerMatchingIA,
        factory_fn=create_influencer_matching,
        capabilities=["influencer_matching", "brand_fit", "roi_prediction"],
        compliance_ready=True
    ),
    
    # Analytics (5)
    "attribution_model_ia": AgentMetadata(
        agent_id="attribution_model_ia",
        name="Marketing Attribution Engine",
        description="Multi-touch attribution with ML-powered path analysis",
        version="3.2.0",
        category="analytics",
        class_ref=AttributionModelIA,
        factory_fn=create_attribution,
        capabilities=["attribution", "path_analysis", "conversion_tracking"],
        compliance_ready=True
    ),
    
    "creative_analyzer_ia": AgentMetadata(
        agent_id="creative_analyzer_ia",
        name="Creative Performance Analyzer",
        description="Creative asset performance analysis and optimization",
        version="3.2.0",
        category="analytics",
        class_ref=CreativeAnalyzerIA,
        factory_fn=create_creative,
        capabilities=["creative_analysis", "performance_tracking", "optimization"],
        compliance_ready=True
    ),
    
    "marketing_mix_model_ia": AgentMetadata(
        agent_id="marketing_mix_model_ia",
        name="Marketing Mix Modeling Engine",
        description="Statistical MMM with channel contribution analysis",
        version="3.2.0",
        category="analytics",
        class_ref=MarketingMixModelIA,
        factory_fn=create_mmm,
        capabilities=["mmm", "channel_analysis", "roi_modeling"],
        compliance_ready=True
    ),
    
    "content_performance_ia": AgentMetadata(
        agent_id="content_performance_ia",
        name="Content Performance Analyzer",
        description="Content performance tracking and optimization",
        version="3.2.0",
        category="analytics",
        class_ref=ContentPerformanceIA,
        factory_fn=create_content_perf,
        capabilities=["content_analysis", "performance_tracking", "optimization"],
        compliance_ready=True
    ),
    
    "customer_segmentation_ia": AgentMetadata(
        agent_id="customer_segmentation_ia",
        name="Customer Segmentation Engine",
        description="Advanced customer segmentation with ML",
        version="3.2.0",
        category="analytics",
        class_ref=CustomerSegmentationIA,
        factory_fn=create_segmentation,
        capabilities=["segmentation", "clustering", "profiling"],
        compliance_ready=True
    ),
    
    # Customer Experience (2)
    "journey_optimizer_ia": AgentMetadata(
        agent_id="journey_optimizer_ia",
        name="Customer Journey Optimizer",
        description="Multi-touchpoint journey optimization and next-best-action",
        version="3.2.0",
        category="customer_experience",
        class_ref=JourneyOptimizerIA,
        factory_fn=create_journey,
        capabilities=["journey_mapping", "optimization", "nba"],
        compliance_ready=True
    ),
    
    "retention_predictor_ia": AgentMetadata(
        agent_id="retention_predictor_ia",
        name="Retention Prediction Engine",
        description="Customer retention prediction and churn prevention",
        version="3.2.0",
        category="customer_experience",
        class_ref=RetentionPredictorIA,
        factory_fn=create_retention,
        capabilities=["retention_prediction", "churn_analysis", "prevention"],
        compliance_ready=True
    ),
    
    # Planning (1)
    "budget_forecast_ia": AgentMetadata(
        agent_id="budget_forecast_ia",
        name="Budget Forecasting Engine",
        description="ML-powered marketing budget forecasting and planning",
        version="3.2.0",
        category="planning",
        class_ref=BudgetForecastIA,
        factory_fn=create_budget_forecast,
        capabilities=["forecasting", "planning", "scenario_analysis"],
        compliance_ready=True
    ),
    
    # Intelligence (2)
    "competitor_analyzer_ia": AgentMetadata(
        agent_id="competitor_analyzer_ia",
        name="Competitive Analysis Engine",
        description="Comprehensive competitor analysis with SWOT and gap identification",
        version="3.2.0",
        category="intelligence",
        class_ref=CompetitorAnalyzerIA,
        factory_fn=create_competitor,
        capabilities=["competitive_analysis", "swot", "gap_analysis"],
        compliance_ready=True
    ),
    
    "competitor_intelligence_ia": AgentMetadata(
        agent_id="competitor_intelligence_ia",
        name="Competitive Intelligence Engine",
        description="Advanced competitive intelligence and market analysis",
        version="3.2.0",
        category="intelligence",
        class_ref=CompetitorIntelligenceIA,
        factory_fn=create_comp_intel,
        capabilities=["competitive_intelligence", "market_analysis", "benchmarking"],
        compliance_ready=True
    ),
    
    # Experimentation (2)
    "ab_testing_ia": AgentMetadata(
        agent_id="ab_testing_ia",
        name="A/B Testing & Experimentation Engine",
        description="Statistical testing with multi-variant support",
        version="3.2.0",
        category="experimentation",
        class_ref=ABTestingIA,
        factory_fn=create_abtest,
        capabilities=["ab_testing", "statistical_analysis", "experimentation"],
        compliance_ready=True
    ),
    
    "ab_testing_impact_ia": AgentMetadata(
        agent_id="ab_testing_impact_ia",
        name="A/B Testing Impact Analysis Engine",
        description="Deep impact analysis of A/B tests with statistical rigor",
        version="3.2.0",
        category="experimentation",
        class_ref=ABTestingImpactIA,
        factory_fn=create_abtest_impact,
        capabilities=["impact_analysis", "statistical_testing", "power_analysis"],
        compliance_ready=True
    ),
    
    # Content (2)
    "content_generator_ia": AgentMetadata(
        agent_id="content_generator_ia",
        name="Content Generation Engine",
        description="AI-