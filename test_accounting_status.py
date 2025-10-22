from agentes_contabilidad_completos import AccountingOrchestrator
import asyncio

async def check_status():
    accounting = AccountingOrchestrator()
    health = await accounting.get_accounting_health()
    print('📊 ESTADO CONTABILIDAD COMPLETO:')
    print(f'  🤖 Agentes: {len(health["enabled_agents"])}')
    print(f'  🎯 Features: {health["total_agents"]}')
    print(f'  ✅ Estado: {health["status"]}')

asyncio.run(check_status())
