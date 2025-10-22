import asyncio
import importlib
import os
import sys
import time
from datetime import datetime

print("="*100)
print("🔍 AUDITORÍA COMPLETA - NADAKKI AI SUITE")
print("="*100)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)

# Agentes y sus tests
agents_map = {
    "LeadScoringIA": {
        "module": "agents.marketing.leadscoringia",
        "class": "LeadScoringIA",
        "test": "test_lead_agent.py"
    },
    "CampaignOptimizerIA": {
        "module": "agents.marketing.campaignoptimizeria",
        "class": "CampaignOptimizerIA",
        "test": "test_campaign_agent.py"
    },
    "AttributionModelIA": {
        "module": "agents.marketing.attributionmodelia",
        "class": "AttributionModelIA",
        "test": "test_attribution_agent.py"
    },
    "PersonalizationEngineIA": {
        "module": "agents.marketing.personalizationengineia",
        "class": "PersonalizationEngineIA",
        "test": "test_personalization_agent.py"
    },
    "JourneyOptimizerIA": {
        "module": "agents.marketing.journeyoptimizeria",
        "class": "JourneyOptimizerIA",
        "test": "test_journey_agent.py"
    },
    "BudgetForecastIA": {
        "module": "agents.marketing.budgetforecastia",
        "class": "BudgetForecastIA",
        "test": "test_budget_agent.py"
    },
    "CreativeAnalyzerIA": {
        "module": "agents.marketing.creativeanalyzeria",
        "class": "CreativeAnalyzerIA",
        "test": "test_creative_agent.py"
    },
    "MarketingMixModelIA": {
        "module": "agents.marketing.marketingmixmodelia",
        "class": "MarketingMixModelIA",
        "test": "test_mmm_agent.py"
    },
    "CompetitorAnalyzerIA": {
        "module": "agents.marketing.competitoranalyzeria",
        "class": "CompetitorAnalyzerIA",
        "test": "test_competitor_agent.py"
    },
    "ABTestingIA": {
        "module": "agents.marketing.abtestingia",
        "class": "ABTestingIA",
        "test": "test_abtest_agent.py"
    }
}

results = []

for agent_name, config in agents_map.items():
    print(f"\n{'─'*100}")
    print(f"📊 EVALUANDO: {agent_name}")
    print(f"{'─'*100}")
    
    score = 0
    status = "❌ FAIL"
    details = {}
    
    try:
        # 1. Verificar módulo existe (10 puntos)
        module_path = config["module"].replace(".", "/") + ".py"
        if os.path.exists(module_path):
            score += 10
            details["module_exists"] = "✅ (10 pts)"
            print(f"   ✅ Módulo existe: {module_path}")
        else:
            details["module_exists"] = "❌ (0 pts)"
            print(f"   ❌ Módulo NO existe: {module_path}")
        
        # 2. Verificar test existe (10 puntos)
        if os.path.exists(config["test"]):
            score += 10
            details["test_exists"] = "✅ (10 pts)"
            print(f"   ✅ Test existe: {config['test']}")
        else:
            details["test_exists"] = "❌ (0 pts)"
            print(f"   ⚠️  Test NO existe: {config['test']}")
        
        # 3. Importar módulo (20 puntos)
        try:
            module = importlib.import_module(config["module"])
            score += 20
            details["import_success"] = "✅ (20 pts)"
            print(f"   ✅ Import exitoso")
        except Exception as e:
            details["import_success"] = f"❌ (0 pts) - {str(e)[:50]}"
            print(f"   ❌ Import falló: {str(e)[:100]}")
            raise
        
        # 4. Instanciar clase (20 puntos)
        try:
            AgentClass = getattr(module, config["class"])
            agent = AgentClass("tn_audit_001")
            score += 20
            details["instantiation"] = "✅ (20 pts)"
            print(f"   ✅ Instanciación exitosa")
        except Exception as e:
            details["instantiation"] = f"❌ (0 pts) - {str(e)[:50]}"
            print(f"   ❌ Instanciación falló: {str(e)[:100]}")
            raise
        
        # 5. Health check (20 puntos)
        try:
            health = agent.health_check()
            if health.get("status") == "healthy":
                score += 20
                details["health_check"] = "✅ (20 pts)"
                print(f"   ✅ Health check: {health.get('status')}")
            else:
                details["health_check"] = f"⚠️  (10 pts) - Status: {health.get('status')}"
                score += 10
                print(f"   ⚠️  Health check: {health.get('status')}")
        except Exception as e:
            details["health_check"] = f"❌ (0 pts) - {str(e)[:50]}"
            print(f"   ❌ Health check falló: {str(e)[:100]}")
        
        # 6. Get metrics (20 puntos)
        try:
            metrics = agent.get_metrics()
            if isinstance(metrics, dict) and "agent_name" in metrics:
                score += 20
                details["get_metrics"] = "✅ (20 pts)"
                print(f"   ✅ Métricas disponibles")
            else:
                details["get_metrics"] = "⚠️  (10 pts) - Incompleto"
                score += 10
                print(f"   ⚠️  Métricas incompletas")
        except Exception as e:
            details["get_metrics"] = f"❌ (0 pts) - {str(e)[:50]}"
            print(f"   ❌ Get metrics falló: {str(e)[:100]}")
        
        # Determinar status
        if score >= 90:
            status = "🏆 EXCELLENT"
        elif score >= 70:
            status = "✅ GOOD"
        elif score >= 50:
            status = "⚠️  FAIR"
        else:
            status = "❌ FAIL"
        
        print(f"\n   📊 SCORE FINAL: {score}/100 - {status}")
        
    except Exception as e:
        print(f"\n   ❌ ERROR CRÍTICO: {str(e)[:200]}")
        details["critical_error"] = str(e)[:100]
    
    results.append({
        "agent": agent_name,
        "score": score,
        "status": status,
        "details": details
    })

# RESUMEN FINAL
print("\n" + "="*100)
print("📈 RESUMEN EJECUTIVO")
print("="*100)

total_agents = len(results)
avg_score = sum(r["score"] for r in results) / total_agents if results else 0

print(f"\nAgentes Evaluados: {total_agents}")
print(f"Score Promedio: {avg_score:.1f}/100")

# Distribución por status
excellent = sum(1 for r in results if "EXCELLENT" in r["status"])
good = sum(1 for r in results if "GOOD" in r["status"])
fair = sum(1 for r in results if "FAIR" in r["status"])
fail = sum(1 for r in results if "FAIL" in r["status"])

print(f"\n🏆 Excellent (90-100): {excellent}")
print(f"✅ Good (70-89): {good}")
print(f"⚠️  Fair (50-69): {fair}")
print(f"❌ Fail (<50): {fail}")

print("\n" + "="*100)
print("RANKING DE AGENTES:")
print("="*100)
print(f"{'#':3} {'Agent':30} {'Score':10} {'Status':20}")
print("-"*100)

sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
for i, r in enumerate(sorted_results, 1):
    print(f"{i:2}. {r['agent']:30} {r['score']:3}/100    {r['status']:20}")

print("\n" + "="*100)
print("DESGLOSE DETALLADO:")
print("="*100)

for r in sorted_results:
    print(f"\n{r['agent']} - {r['score']}/100")
    for key, value in r['details'].items():
        print(f"  • {key}: {value}")

print("\n" + "="*100)
if avg_score >= 80:
    print("✅ SUITE EN BUEN ESTADO - CALIDAD ALTA")
elif avg_score >= 60:
    print("⚠️  SUITE FUNCIONAL - REQUIERE MEJORAS")
else:
    print("❌ SUITE REQUIERE TRABAJO - CALIDAD BAJA")
print("="*100)