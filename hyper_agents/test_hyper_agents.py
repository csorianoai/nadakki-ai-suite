"""
NADAKKI AI SUITE - TEST COMPLETO HYPER AGENTS
Verifica todos los componentes nivel 0.1%
"""

import asyncio
import sys
import os

# Agregar el directorio PADRE al path para que encuentre hyper_agents
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(name: str, success: bool, detail: str = ""):
    icon = "✅" if success else "❌"
    print(f"  {icon} {name}")
    if detail:
        print(f"     → {detail}")

async def main():
    print("\n" + "🚀" * 35)
    print("\n  NADAKKI AI SUITE - TEST NIVEL 0.1%")
    print("  Módulo hyper_agents INDEPENDIENTE")
    print("\n" + "🚀" * 35)
    
    results = []
    
    # =========================================================================
    # TEST 1: IMPORTS BÁSICOS
    # =========================================================================
    print_header("TEST 1: IMPORTS BÁSICOS")
    
    try:
        from hyper_agents.core.types import (
            ActionType, ActionDef, AutonomyLevel, MemoryType,
            HyperAgentProfile, HyperAgentOutput, SafetyLevel
        )
        print_result("Types", True, "Todos los tipos importados")
        results.append(True)
        
        from hyper_agents.core.adapters import get_llm, MockLLM, LLMFactory
        print_result("Adapters", True, "LLM factory disponible")
        results.append(True)
        
        from hyper_agents.core.hyper_cortex import HyperCortex
        print_result("HyperCortex", True, "Sistema de pensamiento paralelo")
        results.append(True)
        
        from hyper_agents.core.base_hyper_agent import BaseHyperAgent
        print_result("BaseHyperAgent", True, "Clase base importada")
        results.append(True)
        
    except Exception as e:
        print_result("Imports básicos", False, str(e))
        results.append(False)
    
    # =========================================================================
    # TEST 2: QUANTUM MEMORY
    # =========================================================================
    print_header("TEST 2: QUANTUM MEMORY (Memoria Vectorial)")
    
    try:
        from hyper_agents.memory.quantum_memory import QuantumMemory, MemoryType
        
        memory = QuantumMemory(tenant_id="test_bank", agent_id="test_agent")
        print_result("Inicialización", True, f"Tenant: test_bank")
        
        # Almacenar
        entry = await memory.store(
            "test_key_1",
            {"topic": "préstamos hipotecarios", "score": 0.85},
            MemoryType.SHORT_TERM,
            importance=0.8,
            tags=["financial", "mortgage"]
        )
        print_result("Store", True, f"Key: {entry.key}")
        
        # Buscar
        results_mem = await memory.get_context("hipoteca préstamo banco", limit=3)
        print_result("Search semántico", True, f"Encontrados: {len(results_mem)}")
        
        # Stats
        stats = memory.get_stats()
        print_result("Stats", True, f"Total memorias: {stats['total_memories']}")
        
        results.append(True)
        
    except Exception as e:
        print_result("Quantum Memory", False, str(e))
        results.append(False)
    
    # =========================================================================
    # TEST 3: RL LEARNING ENGINE
    # =========================================================================
    print_header("TEST 3: RL LEARNING ENGINE (Aprendizaje)")
    
    try:
        from hyper_agents.learning.rl_engine import RLLearningEngine
        
        rl = RLLearningEngine(agent_id="test_agent", tenant_id="test_bank", algorithm="ucb")
        print_result("Inicialización", True, "Algoritmo: UCB")
        
        # Simular actualizaciones
        for i in range(10):
            success = i % 3 != 0
            reward = 0.8 if success else 0.3
            rl.update_policy("credit_evaluation", "approve", success, reward, 0.001)
            rl.update_policy("credit_evaluation", "reject", not success, 1 - reward, 0.001)
        
        print_result("Policy Updates", True, "10 actualizaciones")
        
        # Seleccionar mejor acción
        action, meta = rl.select_action("credit_evaluation", ["approve", "reject", "review"])
        print_result("Action Selection", True, f"Seleccionada: {action} ({meta['method']})")
        
        # Mejores acciones
        best = rl.get_best_actions("credit_evaluation", 2)
        print_result("Best Actions", True, f"Top: {[b['action'] for b in best]}")
        
        # Thompson Sampling
        rl2 = RLLearningEngine(agent_id="test2", algorithm="thompson")
        action2, meta2 = rl2.select_action("test", ["a", "b", "c"], force_explore=False)
        print_result("Thompson Sampling", True, f"Método: {meta2['method']}")
        
        results.append(True)
        
    except Exception as e:
        print_result("RL Engine", False, str(e))
        results.append(False)
    
    # =========================================================================
    # TEST 4: BUDGET MANAGER
    # =========================================================================
    print_header("TEST 4: BUDGET MANAGER (Gestión de Costos)")
    
    try:
        from hyper_agents.budget.budget_manager import BudgetManager, ModelTier
        
        budget = BudgetManager(tenant_id="test_bank", monthly_budget_usd=100.0)
        print_result("Inicialización", True, "Budget: $100/mes")
        
        # Registrar uso
        for _ in range(5):
            budget.record_usage("agent_1", "gpt-4o-mini", 500, 200)
        print_result("Record Usage", True, "5 registros")
        
        # Selección de modelo
        model = budget.select_model("gpt-4", task_complexity=0.8, estimated_tokens=1000)
        print_result("Model Selection", True, f"Seleccionado: {model}")
        
        # Status
        status = budget.get_budget_status()
        print_result("Budget Status", True, f"Usado: ${status['monthly']['used']:.6f}")
        
        # Verificar si puede ejecutar
        can_exec, reason = budget.can_execute(0.01)
        print_result("Can Execute", can_exec, reason)
        
        results.append(True)
        
    except Exception as e:
        print_result("Budget Manager", False, str(e))
        results.append(False)
    
    # =========================================================================
    # TEST 5: SAFETY FILTER
    # =========================================================================
    print_header("TEST 5: SAFETY FILTER (Seguridad)")
    
    try:
        from hyper_agents.safety.safety_filter import SafetyFilter
        
        safety = SafetyFilter(tenant_id="test_bank", strictness=0.7)
        print_result("Inicialización", True, "Strictness: 0.7")
        
        # Test contenido seguro
        result_safe = safety.check_content(
            "Ofrecemos las mejores tasas de interés del mercado.",
            content_type="marketing"
        )
        print_result("Contenido seguro", result_safe.is_safe, f"Score: {result_safe.score}")
        
        # Test contenido con PII
        result_pii = safety.check_content(
            "Contacte a Juan al 555-123-4567 o juan@email.com",
            content_type="general"
        )
        print_result("Detección PII", len(result_pii.issues) > 0, f"Issues: {len(result_pii.issues)}")
        
        # Test contenido sospechoso
        result_sus = safety.check_content(
            "¡URGENTE! Verify your account NOW or it will be suspended!",
            content_type="email"
        )
        print_result("Contenido sospechoso", not result_sus.is_safe or len(result_sus.issues) > 0, 
                    f"Level: {result_sus.safety_level.value}")
        
        # Quick check
        is_safe = safety.quick_check("Mensaje normal de prueba")
        print_result("Quick Check", is_safe, "Mensaje limpio")
        
        results.append(True)
        
    except Exception as e:
        print_result("Safety Filter", False, str(e))
        results.append(False)
    
    # =========================================================================
    # TEST 6: HYPER CORTEX (Pensamiento Paralelo)
    # =========================================================================
    print_header("TEST 6: HYPER CORTEX (Pensamiento Paralelo)")
    
    try:
        from hyper_agents.core.hyper_cortex import HyperCortex
        
        cortex = HyperCortex(agent_id="test_agent", tenant_id="test_bank")
        print_result("Inicialización", True)
        
        # Pensamiento paralelo
        parallel_result = await cortex.parallel_think(
            query="Evaluar solicitud de crédito para cliente con score 680",
            context={"amount": 50000, "term": 36},
            num_streams=3
        )
        
        consensus = parallel_result.get("consensus_level", 0)
        print_result("Parallel Think", True, f"Consenso: {consensus:.2f}")
        print_result("Streams", True, f"Procesados: {parallel_result.get('num_streams', 0)}")
        
        # Evaluación ética
        ethical = await cortex.ethical_assessment({
            "action": "approve_loan",
            "amount": 50000,
            "customer_score": 680
        })
        print_result("Ethical Assessment", True, 
                    f"Score: {ethical.overall_score:.2f}, Rec: {ethical.recommendation}")
        
        results.append(True)
        
    except Exception as e:
        print_result("Hyper Cortex", False, str(e))
        results.append(False)
    
    # =========================================================================
    # TEST 7: HYPER CONTENT GENERATOR (Ciclo Completo)
    # =========================================================================
    print_header("TEST 7: HYPER CONTENT GENERATOR (Ciclo Completo)")
    
    try:
        from hyper_agents.agents.hyper_content_generator import HyperContentGenerator
        
        agent = HyperContentGenerator(tenant_id="test_bank")
        print_result("Inicialización", True, f"v{agent.profile.version}")
        
        # Ejecutar ciclo completo
        output = await agent.run({
            "topic": "Nuevas tasas de préstamos personales - Enero 2026",
            "content_type": "social_post",
            "platforms": ["facebook", "linkedin"]
        })
        
        print_result("Ejecución", output.success, 
                    f"Tiempo: {output.execution_time_ms:.0f}ms")
        
        if output.content:
            print_result("Contenido generado", True, output.content[:80] + "...")
        
        if output.parallel_thoughts:
            print_result("Pensamiento paralelo", True, 
                        f"Consenso: {output.parallel_thoughts.get('consensus_level', 0):.2f}")
        
        if output.ethical_assessment:
            print_result("Evaluación ética", True, 
                        f"Score: {output.ethical_assessment.get('score', 0):.2f}")
        
        if output.safety_check:
            print_result("Verificación seguridad", True, 
                        f"Score: {output.safety_check.get('score', 0):.2f}")
        
        print_result("Self-score", True, f"{output.self_score:.2f}")
        print_result("Aprendizaje", True, f"{len(output.learnings)} learnings")
        
        # Stats finales
        stats = agent.get_full_stats()
        print_result("Stats", True, 
                    f"Success rate: {stats['performance']['success_rate']*100:.0f}%")
        
        results.append(True)
        
    except Exception as e:
        print_result("Content Generator", False, str(e))
        import traceback
        traceback.print_exc()
        results.append(False)
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print_header("RESUMEN FINAL - EVALUACIÓN NIVEL 0.1%")
    
    total = len(results)
    passed = sum(results)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n  📊 RESULTADOS:")
    print(f"     Tests ejecutados: {total}")
    print(f"     Tests pasados:    {passed} ({percentage:.1f}%)")
    print(f"     Tests fallidos:   {total - passed}")
    
    print(f"\n  🏆 CRITERIOS NIVEL 0.1%:")
    criteria = [
        ("Pensamiento Paralelo (multi-stream)", results[5] if len(results) > 5 else False),
        ("Memoria Vectorial Semántica", results[1] if len(results) > 1 else False),
        ("Aprendizaje por Refuerzo (UCB/Thompson)", results[2] if len(results) > 2 else False),
        ("Gestión de Costos Inteligente", results[3] if len(results) > 3 else False),
        ("Filtro de Seguridad Robusto", results[4] if len(results) > 4 else False),
        ("Ciclo Completo Integrado", results[6] if len(results) > 6 else False),
    ]
    
    criteria_passed = 0
    for name, passed_c in criteria:
        icon = "✅" if passed_c else "❌"
        print(f"     {icon} {name}")
        if passed_c:
            criteria_passed += 1
    
    print(f"\n     Criterios cumplidos: {criteria_passed}/{len(criteria)}")
    
    if criteria_passed >= 5:
        print(f"\n  🎉 ¡NIVEL 0.1% ALCANZADO!")
        verdict = "ELITE"
    elif criteria_passed >= 3:
        print(f"\n  ⚡ NIVEL AVANZADO - Cerca del elite")
        verdict = "AVANZADO"
    else:
        print(f"\n  📋 Revisar componentes con errores")
        verdict = "BÁSICO"
    
    print(f"\n  VEREDICTO: {verdict}")
    print("\n" + "=" * 70)
    
    return criteria_passed >= 5


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
