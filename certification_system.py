# certification_system.py
"""
SISTEMA DE CERTIFICACIÓN NADAKKI OPERATIVE v2 - COMPLETO
Certifica los 36 agentes operativos
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, ".")

# MAPEO COMPLETO DE LOS 36 AGENTES
AGENT_MAP = {
    "abtestingia": "ABTestingAgentOperative",
    "abtestingimpactia": "ABTestingImpactAgentOperative",
    "attributionmodelia": "AttributionModelAgentOperative",
    "audiencesegmenteria": "AudienceSegmenterAgentOperative",
    "budgetforecastia": "BudgetForecastAgentOperative",
    "campaignoptimizeria": "CampaignOptimizerAgentOperative",
    "campaignstrategyorchestratoria": "CampaignStrategyOrchestratorAgentOperative",
    "cashofferfilteria": "CashOfferFilterAgentOperative",
    "channelattributia": "ChannelAttributAgentOperative",
    "competitoranalyzeria": "CompetitorAnalyzerAgentOperative",
    "competitorintelligenceia": "CompetitorIntelligenceAgentOperative",
    "contactqualityia": "ContactQualityAgentOperative",
    "contentgeneratoria": "ContentGeneratorAgentOperative",
    "contentperformanceia": "ContentPerformanceAgentOperative",
    "conversioncohortia": "ConversionCohortAgentOperative",
    "creativeanalyzeria": "CreativeAnalyzerAgentOperative",
    "customersegmentatonia": "CustomerSegmentationAgentOperative",
    "emailautomationia": "EmailAutomationAgentOperative",
    "geosegmentationia": "GeoSegmentationAgentOperative",
    "influencermatcheria": "InfluencerMatcherAgentOperative",
    "influencermatchingia": "InfluencerMatchingAgentOperative",
    "journeyoptimizeria": "JourneyOptimizerAgentOperative",
    "leadscoria": "LeadScorAgentOperative",
    "leadscoringia": "LeadScoringAgentOperative",
    "marketingmixmodelia": "MarketingMixModelAgentOperative",
    "marketingorchestratorea": "MarketingOrchestratorAgentOperative",
    "minimalformia": "MinimalFormAgentOperative",
    "personalizationengineia": "PersonalizationEngineAgentOperative",
    "predictiveleadia": "PredictiveLeadAgentOperative",
    "pricingoptimizeria": "PricingOptimizerAgentOperative",
    "productaffinityia": "ProductAffinityAgentOperative",
    "retentionpredictorea": "RetentionPredictorAgentOperative",
    "retentionpredictoria": "RetentionPredictorAgentOperative",
    "sentimentanalyzeria": "SentimentAnalyzerAgentOperative",
    "sociallisteningia": "SocialListeningAgentOperative",
    "socialpostgeneratoria": "SocialPostGeneratorAgentOperative"
}

async def certify_agent(agent_instance, agent_name):
    """Certifica un agente individual"""
    score = 0
    capabilities = {}
    
    # TEST 1: Binding operativo
    has_binding = hasattr(agent_instance, 'execute_operative')
    capabilities["operative_binding"] = has_binding
    if has_binding:
        score += 15
    else:
        return {"agent": agent_name, "score": 0, "level": "ANALYTICAL", "capabilities": {}}
    
    # TEST 2: Ejecución básica
    try:
        result = await agent_instance.execute_operative(
            input_data={"test": "certification", "topic": "test", "campaign": {"name": "test"}},
            tenant_id="certification",
            autonomy_level="semi",
            confidence=0.8
        )
        
        capabilities["basic_execution"] = result.get("ok", False)
        capabilities["has_audit"] = "audit_hash" in result
        capabilities["has_correlation"] = "correlation_id" in result
        
        if result.get("ok"):
            score += 20
        else:
            score += 10  # Bloqueado por política cuenta parcial
        
        if capabilities["has_audit"]:
            score += 10
        if capabilities["has_correlation"]:
            score += 10
            
    except Exception as e:
        capabilities["basic_execution"] = False
        capabilities["error"] = str(e)
    
    # TEST 3: Atributos
    if hasattr(agent_instance, 'agent_id'):
        score += 5
    if hasattr(agent_instance, 'version'):
        score += 5
    
    # TEST 4: Multi-tenant
    try:
        await agent_instance.execute_operative(
            input_data={"test": "multi"},
            tenant_id="tenant_2",
            autonomy_level="semi"
        )
        score += 15
        capabilities["multi_tenant"] = True
    except:
        capabilities["multi_tenant"] = False
    
    # TEST 5: Execute nativo
    if hasattr(agent_instance, 'execute') and callable(agent_instance.execute):
        score += 10
        capabilities["native_execute"] = True
    
    # Nivel
    if score >= 80:
        level = "ENTERPRISE_ELITE"
    elif score >= 65:
        level = "AUTONOMOUS"
    elif score >= 50:
        level = "OPERATIVE_ADV"
    elif score >= 30:
        level = "OPERATIVE_BASIC"
    else:
        level = "ANALYTICAL"
    
    return {
        "agent": agent_name,
        "score": score,
        "level": level,
        "capabilities": capabilities,
        "certified_at": datetime.now().isoformat()
    }

async def main():
    print("="*70)
    print("🎯 NADAKKI OPERATIVE - CERTIFICACIÓN COMPLETA (36 AGENTES)")
    print("="*70)
    
    results = []
    success = 0
    errors = 0
    
    for i, (module_name, class_name) in enumerate(AGENT_MAP.items(), 1):
        print(f"\r  [{i}/36] Certificando {module_name}...", end="", flush=True)
        
        try:
            exec(f"from agents.marketing.{module_name} import {class_name}", globals())
            agent = eval(f"{class_name}()")
            result = await certify_agent(agent, class_name)
            results.append(result)
            success += 1
        except Exception as e:
            results.append({
                "agent": class_name,
                "score": 0,
                "level": "ERROR",
                "error": str(e)
            })
            errors += 1
    
    print("\n")
    
    # Estadísticas
    valid_results = [r for r in results if r.get("score", 0) > 0]
    
    if valid_results:
        avg_score = sum(r["score"] for r in valid_results) / len(valid_results)
        enterprise = sum(1 for r in valid_results if r["score"] >= 80)
        autonomous = sum(1 for r in valid_results if 65 <= r["score"] < 80)
        operative = sum(1 for r in valid_results if 50 <= r["score"] < 65)
    else:
        avg_score = 0
        enterprise = autonomous = operative = 0
    
    # Guardar reporte
    Path("certifications").mkdir(exist_ok=True)
    report = {
        "generated_at": datetime.now().isoformat(),
        "version": "4.0.0-FINAL",
        "statistics": {
            "total_agents": 36,
            "certified_success": success,
            "certification_errors": errors,
            "average_score": round(avg_score, 1),
            "enterprise_ready": enterprise,
            "autonomous": autonomous,
            "operative": operative
        },
        "agents": {r["agent"]: r for r in results}
    }
    
    with open("certifications/consolidated_certification_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Resumen visual
    print("="*70)
    print("📊 RESUMEN DE CERTIFICACIÓN - 36 AGENTES")
    print("="*70)
    print(f"""
  ┌────────────────────────────────────────────────────────────────┐
  │                    ESTADÍSTICAS GLOBALES                       │
  ├────────────────────────────────────────────────────────────────┤
  │  Total Agentes:          {str(36).ljust(36)}│
  │  Certificados OK:        {str(success).ljust(36)}│
  │  Errores:                {str(errors).ljust(36)}│
  │  Puntuación Promedio:    {str(round(avg_score, 1)).ljust(36)}│
  ├────────────────────────────────────────────────────────────────┤
  │  🏆 ENTERPRISE_ELITE:    {str(enterprise).ljust(36)}│
  │  🤖 AUTONOMOUS:          {str(autonomous).ljust(36)}│
  │  ⚙️  OPERATIVE:           {str(operative).ljust(36)}│
  └────────────────────────────────────────────────────────────────┘
    """)
    
    # Tabla de resultados
    print("\n┌─────────────────────────────────────────────┬───────┬──────────────────┐")
    print("│ AGENTE                                      │ SCORE │ NIVEL            │")
    print("├─────────────────────────────────────────────┼───────┼──────────────────┤")
    
    for r in sorted(results, key=lambda x: x.get("score", 0), reverse=True):
        name = r["agent"][:43].ljust(43)
        score = str(r.get("score", 0)).ljust(5)
        level = r.get("level", "ERROR")[:16].ljust(16)
        print(f"│ {name} │ {score} │ {level} │")
    
    print("└─────────────────────────────────────────────┴───────┴──────────────────┘")
    
    print(f"\n✅ Reporte guardado: certifications/consolidated_certification_report.json")
    
    # Score final del sistema
    system_score = (enterprise / 36) * 100 if enterprise > 0 else 0
    print(f"\n🏆 SCORE SISTEMA NADAKKI: {system_score:.1f}% Enterprise-Ready")

if __name__ == "__main__":
    asyncio.run(main())
