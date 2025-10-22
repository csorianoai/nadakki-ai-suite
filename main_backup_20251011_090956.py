# filepath: main.py
"""
NADAKKI AI SUITE v3.2.0 - Enterprise Marketing AI Agents
21 Enterprise-Grade AI Agents
"""

from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("NadakkiAISuite")

VERSION = "3.2.0"

# ═══════════════════════════════════════════════════════════════════════
# AGENT IMPORTS - 21 AGENTES CON DETECCIÓN DE ERRORES
# ═══════════════════════════════════════════════════════════════════════

AGENTS_TO_IMPORT = {
    "LeadScoringIA": "agents.marketing.leadscoringia",
    "CampaignOptimizerIA": "agents.marketing.campaignoptimizeria",
    "AttributionModelIA": "agents.marketing.attributionmodelia",
    "PersonalizationEngineIA": "agents.marketing.personalizationengineia",
    "JourneyOptimizerIA": "agents.marketing.journeyoptimizeria",
    "BudgetForecastIA": "agents.marketing.budgetforecastia",
    "CreativeAnalyzerIA": "agents.marketing.creativeanalyzeria",
    "MarketingMixModelIA": "agents.marketing.marketingmixmodelia",
    "CompetitorAnalyzerIA": "agents.marketing.competitoranalyzeria",
    "ABTestingIA": "agents.marketing.abtestingia",
    "ABTestingImpactIA": "agents.marketing.abtestingimpactia",
    "CompetitorIntelligenceIA": "agents.marketing.competitorintelligenceia",
    "ContentGeneratorIA": "agents.marketing.content_generator_v3",
    "ContentPerformanceIA": "agents.marketing.contentperformanceia",
    "SocialPostGeneratorIA": "agents.marketing.socialpostgeneratoria",
    "CustomerSegmentationIA": "agents.marketing.customersegmentatonia",
    "RetentionPredictorIA": "agents.marketing.retentionpredictorea",
    "EmailAutomationIA": "agents.marketing.emailautomationia",
    "MarketingOrchestratorIA": "agents.marketing.marketingorchestratorea",
    "InfluencerMatcherIA": "agents.marketing.influencermatcheria",
    "InfluencerMatchingIA": "agents.marketing.influencermatchingia"
}

# Importar agentes con manejo de errores
imported_agents = {}
failed_imports = {}

for class_name, module_path in AGENTS_TO_IMPORT.items():
    try:
        module = __import__(module_path, fromlist=[class_name])
        agent_class = getattr(module, class_name)
        imported_agents[class_name] = agent_class
        print(f"✅ {class_name}")
    except Exception as e:
        failed_imports[class_name] = str(e)
        print(f"❌ {class_name}: {str(e)[:50]}")

# ═══════════════════════════════════════════════════════════════════════
# AGENT REGISTRY - Solo agentes que se importaron correctamente
# ═══════════════════════════════════════════════════════════════════════

AGENT_REGISTRY = {}

# Definir registry para cada agente importado
registry_config = {
    "LeadScoringIA": ("lead_scoring", "Lead Scoring", "sales"),
    "CampaignOptimizerIA": ("campaign_optimizer", "Campaign Optimization", "marketing"),
    "AttributionModelIA": ("attribution_model", "Marketing Attribution", "analytics"),
    "PersonalizationEngineIA": ("personalization", "Personalization Engine", "marketing"),
    "JourneyOptimizerIA": ("journey_optimizer", "Journey Optimization", "customer_experience"),
    "BudgetForecastIA": ("budget_forecast", "Budget Forecasting", "planning"),
    "CreativeAnalyzerIA": ("creative_analyzer", "Creative Analysis", "analytics"),
    "MarketingMixModelIA": ("marketing_mix", "Marketing Mix Modeling", "analytics"),
    "CompetitorAnalyzerIA": ("competitor_analyzer", "Competitive Analysis", "intelligence"),
    "ABTestingIA": ("ab_testing", "A/B Testing", "experimentation"),
    "ABTestingImpactIA": ("ab_testing_impact", "A/B Testing Impact", "experimentation"),
    "CompetitorIntelligenceIA": ("competitor_intelligence", "Competitive Intelligence", "intelligence"),
    "ContentGeneratorIA": ("content_generator", "Content Generation", "content"),
    "ContentPerformanceIA": ("content_performance", "Content Performance", "analytics"),
    "SocialPostGeneratorIA": ("social_post_generator", "Social Post Generation", "content"),
    "CustomerSegmentationIA": ("customer_segmentation", "Customer Segmentation", "analytics"),
    "RetentionPredictorIA": ("retention_predictor", "Retention Prediction", "customer_experience"),
    "EmailAutomationIA": ("email_automation", "Email Automation", "marketing"),
    "MarketingOrchestratorIA": ("marketing_orchestrator", "Marketing Orchestration", "orchestration"),
    "InfluencerMatcherIA": ("influencer_matcher", "Influencer Matcher", "marketing"),
    "InfluencerMatchingIA": ("influencer_matching", "Influencer Matching", "marketing")
}

for class_name, agent_class in imported_agents.items():
    if class_name in registry_config:
        key, name, category = registry_config[class_name]
        AGENT_REGISTRY[key] = {
            "class": agent_class,
            "name": name,
            "description": f"{name} Engine",
            "version": "3.2.0",
            "category": category
        }

# ═══════════════════════════════════════════════════════════════════════
# NADAKKI AI SUITE CLASS
# ═══════════════════════════════════════════════════════════════════════

class NadakkiAISuite:
    """Enterprise AI Suite for Financial Marketing"""
    
    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None):
        if not tenant_id.startswith("tn_"):
            raise ValueError("Invalid tenant_id format")
        
        self.tenant_id = tenant_id
        self.version = VERSION
        self.config = config or {}
        self._agents: Dict[str, Any] = {}
        
        logger.info(f"Nadakki AI Suite v{VERSION} initialized for tenant: {tenant_id}")
    
    def get_agent(self, agent_key: str, agent_config: Optional[Dict] = None) -> Any:
        if agent_key not in AGENT_REGISTRY:
            available = ", ".join(AGENT_REGISTRY.keys())
            raise ValueError(f"Unknown agent: {agent_key}. Available: {available}")
        
        if agent_key in self._agents:
            return self._agents[agent_key]
        
        agent_class = AGENT_REGISTRY[agent_key]["class"]
        agent = agent_class(self.tenant_id, agent_config)
        self._agents[agent_key] = agent
        
        logger.info(f"Agent created: {agent_key}")
        return agent
    
    def list_agents(self) -> Dict[str, Dict[str, str]]:
        return {
            key: {
                "name": info["name"],
                "description": info["description"],
                "version": info["version"],
                "category": info["category"]
            }
            for key, info in AGENT_REGISTRY.items()
        }
    
    def health_check(self) -> Dict[str, Any]:
        health = {"suite_version": self.version, "tenant_id": self.tenant_id, "agents": {}}
        for key, agent in self._agents.items():
            try:
                health["agents"][key] = agent.health_check()
            except Exception as e:
                health["agents"][key] = {"status": "error", "error": str(e)}
        return health
    
    def get_metrics(self) -> Dict[str, Any]:
        metrics = {"suite_version": self.version, "tenant_id": self.tenant_id, "agents": {}}
        for key, agent in self._agents.items():
            try:
                metrics["agents"][key] = agent.get_metrics()
            except Exception as e:
                metrics["agents"][key] = {"error": str(e)}
        return metrics

def create_suite(tenant_id: str, config: Optional[Dict] = None) -> NadakkiAISuite:
    return NadakkiAISuite(tenant_id, config)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("NADAKKI AI SUITE v3.2.0 - Enterprise Marketing AI Agents")
    print("="*80)
    
    print(f"\n📦 IMPORT STATUS:")
    print(f"   Successfully Imported: {len(imported_agents)}/21")
    print(f"   Failed Imports: {len(failed_imports)}/21")
    
    if failed_imports:
        print(f"\n❌ FAILED IMPORTS:")
        for name, error in failed_imports.items():
            print(f"   - {name}: {error[:60]}")
    
    print(f"\n✅ REGISTERED AGENTS: {len(AGENT_REGISTRY)}")
    
    categories = {}
    for key, info in AGENT_REGISTRY.items():
        cat = info["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Agents by Category:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count}")
    
    print("\n" + "="*80)
    print(f"✅ Ready for Production - {len(AGENT_REGISTRY)} Agents Available")
    print("="*80 + "\n")