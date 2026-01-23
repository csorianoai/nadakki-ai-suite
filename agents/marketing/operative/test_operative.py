"""
═══════════════════════════════════════════════════════════════════════════════════════════════════
TEST DE AGENTES OPERATIVOS - NADAKKI AI SUITE
═══════════════════════════════════════════════════════════════════════════════════════════════════

Ejecuta tests para verificar que los agentes operativos funcionan correctamente.

Uso:
    python agents/marketing/operative/test_operative.py

═══════════════════════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import sys
import os

# Añadir path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


async def test_content_generator():
    """Test ContentGeneratorIA en modo operativo"""
    print("\n" + "=" * 60)
    print("TEST: ContentGeneratorIA (execute_operative)")
    print("=" * 60)
    
    try:
        from agents.marketing.contentgeneratoria import execute_operative
        
        result = await execute_operative(
            input_data={
                "topic": "Promoción de préstamos personales",
                "platform": "facebook",
                "tone": "professional"
            },
            tenant_id="banco_ejemplo",
            auto_execute=False,  # No ejecutar realmente
            use_mock=True        # Usar mock executor
        )
        
        print(f"Status: {result['status']}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print(f"Audit Hash: {result.get('audit_hash', 'N/A')}")
        
        if result['status'] == 'success':
            print("✅ TEST PASSED")
            return True
        elif result['status'] == 'pending_approval':
            print("✅ TEST PASSED (pending approval as expected)")
            return True
        else:
            print(f"⚠️ Unexpected status: {result['status']}")
            print(f"Error: {result.get('error', 'No error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Asegúrese de ejecutar inject_operative.py primero")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_email_automation():
    """Test EmailAutomationIA en modo operativo"""
    print("\n" + "=" * 60)
    print("TEST: EmailAutomationIA (execute_operative)")
    print("=" * 60)
    
    try:
        from agents.marketing.emailautomationia import execute_operative
        
        result = await execute_operative(
            input_data={
                "to_email": "test@example.com",
                "subject": "Test Email from NADAKKI",
                "content": "Este es un email de prueba del sistema NADAKKI AI Suite."
            },
            tenant_id="banco_ejemplo",
            action_type="SEND_EMAIL",
            auto_execute=False,
            use_mock=True
        )
        
        print(f"Status: {result['status']}")
        print(f"Audit Hash: {result.get('audit_hash', 'N/A')}")
        
        if result['status'] in ['success', 'pending_approval']:
            print("✅ TEST PASSED")
            return True
        else:
            print(f"❌ TEST FAILED: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_wrapper_directly():
    """Test del OperativeWrapper directamente"""
    print("\n" + "=" * 60)
    print("TEST: OperativeWrapper (directo)")
    print("=" * 60)
    
    try:
        from agents.marketing.wrappers.operative_wrapper import (
            OperativeWrapper, ActionType, TenantConfig, AutonomyLevel
        )
        from agents.marketing.executors.meta_executor import MockMetaExecutor
        
        # Crear agente dummy
        class DummyAgent:
            name = "DummyTestAgent"
            def execute(self, data, ctx):
                return {
                    "generated_content": f"Contenido generado para: {data.get('topic', 'test')}",
                    "confidence": 0.85,
                    "risk_level": "low"
                }
        
        # Crear wrapper
        config = TenantConfig(
            tenant_id="test_tenant",
            autonomy_level=AutonomyLevel.SEMI,
            confidence_threshold=0.7
        )
        
        wrapper = OperativeWrapper(
            base_agent=DummyAgent(),
            executor=MockMetaExecutor("test_tenant"),
            tenant_id="test_tenant",
            config=config
        )
        
        # Ejecutar
        result = await wrapper.execute_operative(
            input_data={"topic": "Test Topic"},
            action_type=ActionType.PUBLISH_CONTENT
        )
        
        print(f"Status: {result.status.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Analysis: {result.analysis.get('generated_content', 'N/A')[:50]}...")
        print(f"Audit Hash: {result.audit_hash}")
        
        if result.status.value in ['success', 'pending_approval']:
            print("✅ TEST PASSED")
            return True
        else:
            print(f"❌ TEST FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 80)
    print("NADAKKI AI SUITE - TEST DE AGENTES OPERATIVOS")
    print("=" * 80)
    
    results = []
    
    # Test wrapper directamente
    results.append(("OperativeWrapper", await test_wrapper_directly()))
    
    # Test agentes inyectados
    results.append(("ContentGeneratorIA", await test_content_generator()))
    results.append(("EmailAutomationIA", await test_email_automation()))
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE TESTS")
    print("=" * 80)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")
    
    passed_count = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed_count}/{len(results)} tests pasados")
    
    if passed_count == len(results):
        print("\n🎉 ¡Todos los tests pasaron!")
    else:
        print("\n⚠️ Algunos tests fallaron. Revise los errores arriba.")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
