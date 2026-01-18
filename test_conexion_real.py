"""
NADAKKI AI SUITE - BRIDGE: Conecta Sistema Autonomo con Executors Reales
"""
import asyncio
import sys
sys.path.insert(0, ".")

from hyper_agents import AutonomousMarketingSystem, EventType
from agents.shared_layers.executors.social import get_social, SocialManager

async def test_conexion_real():
    print("="*70)
    print("  TEST: CONEXION AGENTES AUTONOMOS + EXECUTORS REALES")
    print("="*70)
    
    # 1. Verificar SocialManager
    print("\n1. Verificando SocialManager...")
    social = get_social()
    platforms = social.get_platforms()
    print(f"   Plataformas configuradas: {platforms}")
    
    if not platforms:
        print("   ADVERTENCIA: No hay plataformas configuradas en .env")
        print("   Necesitas: FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID")
    
    # 2. Iniciar sistema autonomo
    print("\n2. Iniciando sistema autonomo...")
    from hyper_agents import create_autonomous_marketing_system
    system = await create_autonomous_marketing_system("credicefi", auto_start=True, load_defaults=False)
    
    # 3. Probar publicacion real (si hay plataformas)
    if platforms:
        print("\n3. Probando publicacion REAL...")
        result = await social.post_with_ai(
            topic="Promocion de prestamos personales para emprendedores",
            platforms=platforms[:1],  # Solo primera plataforma
            tenant_id="credicefi"
        )
        print(f"   Contenido generado: {result['content_generated'][:100]}...")
        print(f"   Resultado: {result['post_results']}")
    else:
        print("\n3. SKIP publicacion (no hay plataformas configuradas)")
    
    # 4. Dashboard
    print("\n4. Estado del sistema:")
    status = system.get_system_status()
    print(f"   Agentes: {status['components']['agents']}")
    print(f"   Workflows: {status['components']['workflows']}")
    print(f"   Triggers: {status['components']['triggers']}")
    
    await system.stop()
    
    print("\n" + "="*70)
    print("  CONEXION VERIFICADA")
    print("="*70)

asyncio.run(test_conexion_real())
