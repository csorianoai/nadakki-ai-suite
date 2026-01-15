import sys
sys.path.insert(0, '.')
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents.shared_layers.ai_router import get_router, MODELS

print("Verificando configuracion...")
router = get_router()

print("\nModelos disponibles:")
for model in router.get_available_models():
    config = MODELS.get(model)
    if config:
        print(f"   OK {model}: ${config.input_cost_per_1m}/${config.output_cost_per_1m} per 1M tokens")

print("\nProbando generacion de contenido real...")

async def test():
    result = await router.generate(
        prompt="Escribe un post corto para Facebook promocionando excursiones en bote en Miami. Maximo 2 oraciones en espanol.",
        task_type="social_post",
        tenant_id="sfrentals",
        tenant_plan="enterprise"
    )
    print(f"\nContenido generado:")
    print(f"   {result['content']}")
    print(f"\nMetricas:")
    print(f"   Modelo: {result['model_used']}")
    print(f"   Tokens: {result['total_tokens']}")
    print(f"   Costo: ${result['cost_usd']:.6f}")
    print(f"   Latencia: {result['latency_ms']}ms")
    return result

asyncio.run(test())
print("\nAI Router funcionando correctamente!")
