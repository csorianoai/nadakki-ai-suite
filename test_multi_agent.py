import asyncio
import json
from datetime import datetime
from nadakki_operative_final import OperativeMixin

# Importar algunos agentes bindeados
try:
    from agents.marketing.contentgeneratoria import ContentGeneratorIA
    from agents.marketing.personalizationengineia import PersonalizationEngineIA
    from agents.marketing.campaignoptimizeria import CampaignOptimizerIA
    from agents.marketing.leadscoringia import LeadScoringIA
    from agents.marketing.sentimentanalyzeria import SentimentAnalyzerIA
    AGENTS_LOADED = True
except ImportError as e:
    print(f"⚠️  Error importando agentes: {e}")
    AGENTS_LOADED = False

async def test_multi_agent_system():
    """Test del sistema multi-agente para Credicefi"""
    
    print("🧪 NADAKKI OPERATIVE - MULTI-AGENT TEST SUITE")
    print("=" * 60)
    print("Tenant: Credicefi")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if not AGENTS_LOADED:
        print("❌ No se pudieron importar agentes")
        return False
    
    # Configurar sistema
    OperativeMixin.configure()
    
    # Estado inicial
    status = OperativeMixin.get_status()
    print(f"\n🔧 Sistema: {status['bound_count']} agentes bindeados")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Content Generator (normal operation)
    print("\n1️⃣  ContentGeneratorIA - Generación de contenido")
    try:
        agent = ContentGeneratorIA()
        result = await agent.execute_operative(
            input_data={
                "topic": "nuevos préstamos educativos",
                "target_audience": "estudiantes universitarios",
                "tone": "inspirador",
                "length": "medium"
            },
            tenant_id="credicefi",
            autonomy_level="semi",
            confidence=0.82
        )
        
        if result["status"] == "success":
            print(f"   ✅ Éxito: {result['reason']}")
            print(f"   📊 Confianza: {result['confidence']:.2f}")
            print(f"   ⏱️  Tiempo: {result['execution_time_ms']:.2f}ms")
            tests_passed += 1
        else:
            print(f"   ❌ Falló: {result['status']} - {result['reason']}")
        
        tests_total += 1
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # Test 2: Personalization Engine (high confidence)
    print("\n2️⃣  PersonalizationEngineIA - Personalización")
    try:
        agent = PersonalizationEngineIA()
        result = await agent.execute_operative(
            input_data={
                "customer_id": "cli_789012",
                "product_category": "tarjetas de crédito",
                "interaction_history": ["consulta", "aprobación", "uso regular"],
                "demographics": {"age": 35, "income": "medium"}
            },
            tenant_id="credicefi",
            autonomy_level="full_auto",
            confidence=0.91
        )
        
        if result["status"] == "success":
            print(f"   ✅ Éxito: Personalización completada")
            print(f"   🔒 Nivel riesgo: {result['risk_level']}")
            print(f"   🆔 Correlation ID: {result['correlation_id'][-8:]}")
            tests_passed += 1
        else:
            print(f"   ❌ Falló: {result['status']}")
        
        tests_total += 1
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # Test 3: Campaign Optimizer (blocked by policy - keyword)
    print("\n3️⃣  CampaignOptimizerIA - Bloqueo por política")
    try:
        agent = CampaignOptimizerIA()
        result = await agent.execute_operative(
            input_data={
                "campaign_name": "oferta especial spam para nuevos clientes",
                "budget": 50000,
                "channels": ["email", "social", "sms"]
            },
            tenant_id="credicefi",
            confidence=0.75
        )
        
        # Este DEBERÍA ser bloqueado por la keyword "spam"
        if result["status"] in ["blocked_by_policy", "pending_approval"]:
            print(f"   ✅ Correctamente bloqueado: {result['reason']}")
            tests_passed += 1
        else:
            print(f"   ⚠️  No bloqueado como esperado: {result['status']}")
        
        tests_total += 1
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # Test 4: Lead Scoring (multi-tenancy test)
    print("\n4️⃣  LeadScoringIA - Scoring de leads")
    try:
        agent = LeadScoringIA()
        result = await agent.execute_operative(
            input_data={
                "lead_data": {
                    "name": "María González",
                    "email": "maria.g@empresa.com",
                    "company": "TechCorp",
                    "annual_revenue": 2500000,
                    "interaction_score": 85
                },
                "scoring_model": "premium_v1"
            },
            tenant_id="credicefi",
            autonomy_level="semi",
            confidence=0.78
        )
        
        if result["status"] == "success":
            print(f"   ✅ Éxito: Lead scoring completado")
            print(f"   📈 Data keys: {list(result['data'].keys())}")
            tests_passed += 1
        else:
            print(f"   ❌ Falló: {result['status']}")
        
        tests_total += 1
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # Test 5: Sentiment Analysis (low confidence - requires approval)
    print("\n5️⃣  SentimentAnalyzerIA - Baja confianza")
    try:
        agent = SentimentAnalyzerIA()
        result = await agent.execute_operative(
            input_data={
                "text": "los clientes están contentos con las nuevas tasas pero preocupados por los plazos",
                "source": "redes_sociales",
                "language": "es"
            },
            tenant_id="credicefi",
            autonomy_level="semi",
            confidence=0.65  # Por debajo del threshold de 0.75
        )
        
        if result["status"] == "pending_approval":
            print(f"   ✅ Correcto: Requiere aprobación (confianza baja)")
            print(f"   📉 Confianza: {result['confidence']:.2f} < 0.75")
            tests_passed += 1
        else:
            print(f"   ⚠️  Estado inesperado: {result['status']}")
        
        tests_total += 1
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    print(f"   Total tests: {tests_total}")
    print(f"   ✅ Pasados: {tests_passed}")
    print(f"   ❌ Fallados: {tests_total - tests_passed}")
    print(f"   📈 Porcentaje: {(tests_passed/tests_total*100):.1f}%" if tests_total > 0 else "N/A")
    
    # Verificar audit trail
    from nadakki_operative_final import ImmutableAuditLogger
    audit = ImmutableAuditLogger()
    is_valid, errors = audit.verify_chain("credicefi")
    
    print(f"\n🔐 AUDIT TRAIL")
    print(f"   Integridad: {'✅ VÁLIDO' if is_valid else '❌ CORRUPTO'}")
    if errors:
        print(f"   Errores: {len(errors)}")
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = asyncio.run(test_multi_agent_system())
    exit(0 if success else 1)
