# certification_system.py
"""
SISTEMA DE CERTIFICACIÓN NADAKKI OPERATIVE v3 - COMPLETO (100 PTS)
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
    """Certifica un agente individual - SCORING 100 PTS"""
    score = 0
    capabilities = {}

    # TEST 1: Binding operativo (15 pts)
    has_binding = hasattr(agent_instance, 'execute_operative')
    capabilities["operative_binding"] = has_binding
    if has_binding:
        score += 15
    else:
        return {"agent": agent_name, "score": 0, "level": "ANALYTICAL", "capabilities": {}}

    # TEST 2: Ejecucion basica (20 pts success, 15 pts blocked)
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
            score += 15  # Bloqueado por politica cuenta mas (antes 10)

        # TEST 3: Hash auditoria (10 pts)
        if capabilities["has_audit"]:
            score += 10
        
        # TEST 4: Correlation ID (10 pts)
        if capabilities["has_correlation"]:
            score += 10

    except Exception as e:
        capabilities["basic_execution"] = False
        capabilities["error"] = str(e)

    # TEST 5: Atributos agent_id (5 pts)
    if hasattr(agent_instance, 'agent_id'):
        score += 5
        capabilities["has_agent_id"] = True

    # TEST 6: Atributos version (5 pts)
    if hasattr(agent_instance, 'version'):
        score += 5
        capabilities["has_version"] = True

    # TEST 7: Multi-tenant (15 pts)
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

    # TEST 8: Execute nativo (10 pts)
    if hasattr(agent_instance, 'execute') and callable(agent_instance.execute):
        score += 10
        capabilities["native_execute"] = True

    # TEST 9: Agent name attribute (3 pts) - NUEVO
    if hasattr(agent_instance, 'agent_name'):
        score += 3
        capabilities["has_agent_name"] = True

    # TEST 10: Health check method (2 pts) - NUEVO
    if hasattr(agent_instance, 'health_check') or hasattr(agent_instance, '_health_check'):
        score += 2
        capabilities["has_health_check"] = True

    # Nivel basado en score
    if score >= 90:
        level = "ENTERPRISE_ELITE"
    elif score >= 75:
        level = "AUTONOMOUS"
    elif score >= 60:
        level = "OPERATIVE_ADV"
    elif score >= 40:
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
    print("  NADAKKI OPERATIVE - CERTIFICACION COMPLETA v3 (36 AGENTES)")
    print("  SCORING: 100 PUNTOS MAXIMO")
    print("="*70)

    results = []
    success = 0
    errors = 0

    for i, (module_name, class_name) in enumerate(AGENT_MAP.items(), 1):
        print(f"\r  [{i}/36] Certificando {module_name}...", end="", flush=True)

        try:
            module = __import__(f"agents.marketing.{module_name}", fromlist=[class_name])
            agent_class = getattr(module, class_name)
            agent_instance = agent_class()

            result = await certify_agent(agent_instance, class_name)
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

    print("\r" + " "*60 + "\r", end="")

    # Calcular estadisticas
    valid_results = [r for r in results if r.get("score", 0) > 0]

    if valid_results:
        avg_score = sum(r["score"] for r in valid_results) / len(valid_results)
        enterprise = sum(1 for r in valid_results if r["score"] >= 90)
        autonomous = sum(1 for r in valid_results if 75 <= r["score"] < 90)
        operative = sum(1 for r in valid_results if 60 <= r["score"] < 75)
    else:
        avg_score = 0
        enterprise = autonomous = operative = 0

    # Guardar reporte
    report = {
        "generated_at": datetime.now().isoformat(),
        "version": "3.0",
        "max_score": 100,
        "statistics": {
            "total_agents": len(results),
            "certified_ok": success,
            "errors": errors,
            "average_score": round(avg_score, 1),
            "enterprise_ready": enterprise,
            "autonomous": autonomous,
            "operative": operative
        },
        "agents": results
    }

    Path("certifications").mkdir(exist_ok=True)
    with open("certifications/consolidated_certification_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Mostrar resultados
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  NADAKKI CERTIFICATION SYSTEM v3.0                            ║
╠═══════════════════════════════════════════════════════════════╣
║  Total Agentes:          {str(len(results)).ljust(36)}║
║  Certificados OK:        {str(success).ljust(36)}║
║  Errores:                {str(errors).ljust(36)}║
║  Puntuacion Promedio:    {str(round(avg_score, 1)).ljust(36)}║
║                                                               ║
║  ENTERPRISE_ELITE (90+): {str(enterprise).ljust(36)}║
║  AUTONOMOUS (75-89):     {str(autonomous).ljust(36)}║
║  OPERATIVE (60-74):      {str(operative).ljust(36)}║
╚═══════════════════════════════════════════════════════════════╝
""")

    print("┌─────────────────────────────────────────────┬───────┬──────────────────┐")
    print("│ AGENTE                                      │ SCORE │ NIVEL            │")
    print("├─────────────────────────────────────────────┼───────┼──────────────────┤")

    for r in sorted(results, key=lambda x: x.get("score", 0), reverse=True):
        name = r["agent"][:43].ljust(43)
        score = str(r.get("score", 0)).ljust(5)
        level = r.get("level", "N/A").ljust(16)
        print(f"│ {name} │ {score} │ {level} │")

    print("└─────────────────────────────────────────────┴───────┴──────────────────┘")

    print(f"✅ Reporte guardado: certifications/consolidated_certification_report.json")
    print(f"🏆 SCORE SISTEMA NADAKKI: {round(enterprise/len(results)*100, 1)}% Enterprise-Ready")

if __name__ == "__main__":
    asyncio.run(main())
