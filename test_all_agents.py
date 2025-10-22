# filepath: test_all_agents.py
"""Test runner masivo para todos los agentes de marketing"""
import asyncio
import sys
from pathlib import Path

# Lista de agentes actualizados a probar
AGENTS_TO_TEST = [
    "emailautomationia",
    "campaignoptimizeria", 
    "leadscoringia",
    "influencermatcheria",
    "abtestingimpactia",
    "socialpostgeneratoria",
    "brandsentimentia",
    "cashofferfilteria",
    "competitorintelligenceia",
    "contactqualityia",
    "contentviralityia",
    "conversioncohortia",
    "fidelizedprofileia",
    "geosegmentationia",
    "influencermatchia",
    "marketing_coordinator",
    "minimalformia",
    "productaffinityia",
    "videoreelautogenia"
]

async def test_agent_basic(agent_name: str):
    """Test básico: verificar que el agente se puede importar y crear"""
    try:
        # Importar módulo
        module = __import__(f"agents.marketing.{agent_name}", fromlist=["create_agent_instance"])
        
        # Verificar que tiene la función factory
        if not hasattr(module, "create_agent_instance"):
            return False, "Missing create_agent_instance function"
        
        # Crear instancia
        agent = module.create_agent_instance("tn_test_bank_001")
        
        # Verificar métodos requeridos
        required_methods = ["execute", "health_check", "get_metrics"]
        for method in required_methods:
            if not hasattr(agent, method):
                return False, f"Missing method: {method}"
        
        # Health check
        health = agent.health_check()
        if health.get("status") != "healthy":
            return False, f"Health check failed: {health}"
        
        # Get metrics
        metrics = agent.get_metrics()
        if "agent_version" not in metrics and "agent_name" not in metrics:
            return False, "Invalid metrics response"
        
        return True, "OK"
        
    except ImportError as e:
        return False, f"Import error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

async def run_all_tests():
    """Ejecuta tests para todos los agentes"""
    print("╔" + "═" * 78 + "╗")
    print("║" + " TEST MASIVO DE AGENTES DE MARKETING ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    results = []
    passed = 0
    failed = 0
    
    for agent_name in AGENTS_TO_TEST:
        print(f"Testing {agent_name}...", end=" ", flush=True)
        
        success, message = await test_agent_basic(agent_name)
        
        if success:
            print("✅ PASS")
            passed += 1
            results.append((agent_name, True, message))
        else:
            print(f"❌ FAIL: {message}")
            failed += 1
            results.append((agent_name, False, message))
    
    # Resumen
    print("\n" + "═" * 80)
    print("RESUMEN DE TESTS")
    print("═" * 80)
    print(f"Total agentes: {len(AGENTS_TO_TEST)}")
    print(f"✅ Pasaron: {passed}")
    print(f"❌ Fallaron: {failed}")
    print(f"Success rate: {(passed/len(AGENTS_TO_TEST)*100):.1f}%")
    print("═" * 80)
    
    # Detalles de fallos
    if failed > 0:
        print("\nAGENTES QUE FALLARON:")
        for agent_name, success, message in results:
            if not success:
                print(f"  ❌ {agent_name}: {message}")
    
    print("\n" + "═" * 80)
    
    if failed == 0:
        print("🎉 ¡TODOS LOS TESTS PASARON! Procediendo con auditoría completa...")
        print("═" * 80)
        return True
    else:
        print(f"⚠️  {failed} agente(s) requieren corrección antes de auditoría")
        print("═" * 80)
        return False

if __name__ == "__main__":
    all_passed = asyncio.run(run_all_tests())
    sys.exit(0 if all_passed else 1)