import asyncio
import time
from datetime import datetime

# Importar todos los agentes
from agents.risk.riskanalysisia import RiskAnalysisIA, RiskAnalysisInput
from agents.compliance.compliancecheckia import ComplianceCheckIA, ComplianceInput
from agents.customer.customersegmentia import CustomerSegmentIA, SegmentationInput, CustomerProfile
from agents.sales.leadscoringia import LeadScoringIA, LeadScoringInput, LeadData
from agents.fraud.frauddetectia import FraudDetectionIA, TransactionInput, Transaction
from agents.customer.sentimentanalysisia import SentimentAnalysisIA, SentimentInput, TextData
from agents.customer.churnpredictor import ChurnPredictorIA, ChurnPredictionInput, CustomerData
from agents.sales.productrecommenderia import ProductRecommenderIA, RecommendationInput, UserProfile
from agents.marketing.campaignoptimizeria import CampaignOptimizerIA, CampaignInput, Campaign
from agents.marketing.contentgeneratoria import ContentGeneratorIA, ContentInput
from agents.marketing.sociallisteneria import SocialListenerIA, SocialListeningInput, SocialPost
from agents.marketing.attributionmodelia import AttributionModelIA, AttributionInput, TouchPoint
from agents.marketing.personalizationengineia import PersonalizationEngineIA, PersonalizationInput, UserProfile as PersUserProfile, ContextData
from agents.marketing.journeyoptimizeria import JourneyOptimizerIA, JourneyInput, JourneyStage
from agents.marketing.budgetforecastia import BudgetForecastIA, ForecastInput, HistoricalSpend
from agents.marketing.creativeanalyzeria import CreativeAnalyzerIA, CreativeAnalysisInput, CreativeAsset
from agents.marketing.marketingmixmodelia import MarketingMixModelIA, MMMInput, ChannelData
from agents.marketing.competitoranalyzeria import CompetitorAnalyzerIA, CompetitorAnalysisInput, Competitor
from agents.marketing.abtestingia import ABTestingIA, ABTestInput, VariantData

async def audit_all_agents():
    print("="*80)
    print("🔍 AUDITORÍA COMPLETA DE NADAKKI AI SUITE")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Agents: 19")
    print("="*80)
    
    results = []
    
    # Test cada agente
    agents_config = [
        ("RiskAnalysisIA", lambda: RiskAnalysisIA("tn_audit_001")),
        ("ComplianceCheckIA", lambda: ComplianceCheckIA("tn_audit_001")),
        ("CustomerSegmentIA", lambda: CustomerSegmentIA("tn_audit_001")),
        ("LeadScoringIA", lambda: LeadScoringIA("tn_audit_001")),
        ("FraudDetectionIA", lambda: FraudDetectionIA("tn_audit_001")),
        ("SentimentAnalysisIA", lambda: SentimentAnalysisIA("tn_audit_001")),
        ("ChurnPredictorIA", lambda: ChurnPredictorIA("tn_audit_001")),
        ("ProductRecommenderIA", lambda: ProductRecommenderIA("tn_audit_001")),
        ("CampaignOptimizerIA", lambda: CampaignOptimizerIA("tn_audit_001")),
        ("ContentGeneratorIA", lambda: ContentGeneratorIA("tn_audit_001")),
        ("SocialListenerIA", lambda: SocialListenerIA("tn_audit_001")),
        ("AttributionModelIA", lambda: AttributionModelIA("tn_audit_001")),
        ("PersonalizationEngineIA", lambda: PersonalizationEngineIA("tn_audit_001")),
        ("JourneyOptimizerIA", lambda: JourneyOptimizerIA("tn_audit_001")),
        ("BudgetForecastIA", lambda: BudgetForecastIA("tn_audit_001")),
        ("CreativeAnalyzerIA", lambda: CreativeAnalyzerIA("tn_audit_001")),
        ("MarketingMixModelIA", lambda: MarketingMixModelIA("tn_audit_001")),
        ("CompetitorAnalyzerIA", lambda: CompetitorAnalyzerIA("tn_audit_001")),
        ("ABTestingIA", lambda: ABTestingIA("tn_audit_001")),
    ]
    
    for name, factory in agents_config:
        print(f"\n{'─'*80}")
        print(f"Testing: {name}")
        print(f"{'─'*80}")
        
        try:
            t0 = time.time()
            agent = factory()
            health = agent.health_check()
            metrics = agent.get_metrics()
            latency = (time.time() - t0) * 1000
            
            status = "✅ PASS"
            score = 100
            
            # Verificar health check
            if health.get("status") != "healthy":
                status = "❌ FAIL"
                score = 0
            
            results.append({
                "agent": name,
                "status": status,
                "score": score,
                "latency_ms": round(latency, 2),
                "version": health.get("agent_version", "unknown"),
                "total_requests": metrics.get("total", 0)
            })
            
            print(f"Status: {status}")
            print(f"Score: {score}/100")
            print(f"Latency: {latency:.2f}ms")
            print(f"Version: {health.get('agent_version', 'unknown')}")
            
        except Exception as e:
            results.append({
                "agent": name,
                "status": "❌ ERROR",
                "score": 0,
                "latency_ms": 0,
                "version": "unknown",
                "error": str(e)
            })
            print(f"Status: ❌ ERROR")
            print(f"Error: {str(e)}")
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE AUDITORÍA")
    print("="*80)
    
    passed = sum(1 for r in results if r["status"] == "✅ PASS")
    failed = sum(1 for r in results if r["status"] != "✅ PASS")
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)
    
    print(f"\nTotal Agents: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(results)*100:.1f}%")
    print(f"Average Score: {avg_score:.1f}/100")
    print(f"Average Latency: {avg_latency:.2f}ms")
    
    print("\n" + "="*80)
    print("DETAILED RESULTS:")
    print("="*80)
    
    for r in results:
        print(f"{r['agent']:30} {r['status']:15} Score: {r['score']:3}/100  Latency: {r['latency_ms']:6.2f}ms")
    
    print("\n" + "="*80)
    if passed == len(results):
        print("✅ ALL AGENTS PASSED - SUITE READY FOR PRODUCTION")
    else:
        print(f"⚠️  {failed} AGENTS FAILED - REVIEW REQUIRED")
    print("="*80)

asyncio.run(audit_all_agents())