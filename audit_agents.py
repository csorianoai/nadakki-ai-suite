"""
Auditoría completa de los 24 agentes marketing
Prueba directa sin pasar por API o main.py
"""

import sys
sys.path.append('.')
import traceback
import asyncio
import inspect
import json
from datetime import datetime
from typing import Dict, Any, List

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.CYAN}→ {text}{Colors.RESET}")

# Datos de prueba para cada agente
TEST_DATA = {
    "leadscoringia": {
        "lead_id": "L-TEST-001",
        "attributes": {
            "credit_score": 820,
            "income": 75000,
            "age": 40,
            "employment_years": 10
        }
    },
    "customersegmentation": {
        "customer_id": "C-TEST-001",
        "attributes": {
            "age": 35,
            "income": 60000,
            "account_balance": 15000,
            "transaction_count": 50
        }
    },
    "campaignoptimizer": {
        "campaign_id": "CAMP-TEST-001",
        "metrics": {
            "impressions": 10000,
            "clicks": 250,
            "conversions": 15,
            "cost": 500
        }
    },
    # Datos genéricos para otros agentes
    "default": {
        "id": "TEST-001",
        "data": {
            "test_field": "test_value",
            "numeric_field": 100
        }
    }
}

async def test_agent(agent_id: str, agent_class, tenant_id: str) -> Dict[str, Any]:
    """Prueba un agente específico"""
    result = {
        "agent_id": agent_id,
        "success": False,
        "error": None,
        "execution_time_ms": 0,
        "result_type": None,
        "has_execute": False,
        "is_async": False
    }
    
    try:
        # Crear instancia
        agent = agent_class(tenant_id=tenant_id)
        result["has_execute"] = hasattr(agent, 'execute')
        
        if not result["has_execute"]:
            result["error"] = "No tiene método execute()"
            return result
        
        result["is_async"] = inspect.iscoroutinefunction(agent.execute)
        
        # Obtener datos de prueba
        test_data = TEST_DATA.get(agent_id, TEST_DATA["default"])
        
        # Ejecutar
        import time
        start = time.perf_counter()
        
        if result["is_async"]:
            agent_result = await agent.execute(test_data)
        else:
            agent_result = agent.execute(test_data)
        
        result["execution_time_ms"] = (time.perf_counter() - start) * 1000
        result["result_type"] = type(agent_result).__name__
        result["success"] = True
        
        # Intentar convertir resultado a dict para inspeccionarlo
        if hasattr(agent_result, 'dict'):
            result["sample_result"] = str(agent_result.dict())[:200]
        elif hasattr(agent_result, '__dict__'):
            result["sample_result"] = str(agent_result.__dict__)[:200]
        else:
            result["sample_result"] = str(agent_result)[:200]
        
    except Exception as e:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
    
    return result

async def main():
    print_header("AUDITORÍA DE AGENTES MARKETING")
    
    # Importar canonical
    print_info("Importando canonical...")
    try:
        from agents.marketing.canonical import CANONICAL_AGENTS
        print_success(f"Canonical cargado: {len(CANONICAL_AGENTS)} agentes")
    except Exception as e:
        print_error(f"Error importando canonical: {e}")
        return
    
    # Configuración
    tenant_id = "audit-test-tenant"
    results = []
    
    print(f"\nProbando {len(CANONICAL_AGENTS)} agentes...\n")
    
    # Probar cada agente
    for i, (agent_id, agent_info) in enumerate(CANONICAL_AGENTS.items(), 1):
        agent_name = agent_info.get("name", agent_id)
        agent_class = agent_info.get("class")
        
        print(f"{Colors.YELLOW}[{i}/{len(CANONICAL_AGENTS)}]{Colors.RESET} {agent_name} ({agent_id})")
        
        if not agent_class:
            print_error("  No tiene clase definida")
            results.append({
                "agent_id": agent_id,
                "success": False,
                "error": "No class defined"
            })
            continue
        
        result = await test_agent(agent_id, agent_class, tenant_id)
        results.append(result)
        
        if result["success"]:
            print_success(f"  Ejecutado en {result['execution_time_ms']:.2f}ms")
            print(f"    Tipo: {result['result_type']}, Async: {result['is_async']}")
        else:
            print_error(f"  Falló: {result['error']}")
    
    # Resumen
    print_header("RESUMEN DE AUDITORÍA")
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"Total agentes: {len(results)}")
    print_success(f"Exitosos: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print_error(f"Fallidos: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    
    # Detalles de agentes fallidos
    if failed:
        print(f"\n{Colors.RED}AGENTES FALLIDOS:{Colors.RESET}")
        for r in failed:
            print(f"\n  • {r['agent_id']}")
            print(f"    Error: {r['error']}")
            if r.get('traceback'):
                print(f"    Traceback (últimas 5 líneas):")
                lines = r['traceback'].split('\n')[-6:-1]
                for line in lines:
                    print(f"      {line}")
    
    # Estadísticas de tipos
    if successful:
        print(f"\n{Colors.GREEN}ESTADÍSTICAS:{Colors.RESET}")
        async_count = sum(1 for r in successful if r.get('is_async'))
        sync_count = len(successful) - async_count
        print(f"  Async: {async_count}")
        print(f"  Sync: {sync_count}")
        
        avg_time = sum(r['execution_time_ms'] for r in successful) / len(successful)
        print(f"  Tiempo promedio: {avg_time:.2f}ms")
    
    # Guardar reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"audit_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }, f, indent=2, default=str)
    
    print(f"\n{Colors.CYAN}Reporte guardado en: {report_file}{Colors.RESET}")
    
    # Resultado final
    if len(failed) == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ TODOS LOS AGENTES FUNCIONAN CORRECTAMENTE{Colors.RESET}")
        print(f"{Colors.CYAN}→ El problema está en main.py o canonical.py{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ HAY AGENTES CON PROBLEMAS{Colors.RESET}")
        print(f"{Colors.CYAN}→ Necesitamos corregir estos agentes primero{Colors.RESET}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
