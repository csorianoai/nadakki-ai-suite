import sys
sys.path.insert(0, '.')
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents.shared_layers.executors.llm_executor import get_llm

print("="*50)
print("PRUEBA DE LLM EXECUTOR UNIFICADO")
print("="*50)

llm = get_llm()

print(f"\nModelos disponibles: {llm.get_models()}")

async def test_all_models():
    prompt = "Escribe UN emoji que represente el verano"
    
    # Test GPT-4o-mini
    print("\n[1] Probando GPT-4o-mini...")
    r1 = await llm.generate(prompt, model="gpt-4o-mini", tenant_id="sfrentals")
    print(f"    Resultado: {r1['content']}")
    print(f"    Costo: ${r1['cost']:.6f}")
    
    # Test DeepSeek
    print("\n[2] Probando DeepSeek...")
    r2 = await llm.generate(prompt, model="deepseek-chat", tenant_id="sfrentals")
    print(f"    Resultado: {r2['content']}")
    print(f"    Costo: ${r2['cost']:.6f}")
    
    # Test Claude
    print("\n[3] Probando Claude Haiku...")
    r3 = await llm.generate(prompt, model="claude-3-haiku-20240307", tenant_id="sfrentals")
    print(f"    Resultado: {r3['content']}")
    print(f"    Costo: ${r3['cost']:.6f}")
    
    # Estadisticas
    print("\n" + "="*50)
    print("ESTADISTICAS DE USO:")
    print("="*50)
    stats = llm.get_stats()
    print(f"Total llamadas: {stats['calls']}")
    print(f"Total tokens: {stats['tokens']}")
    print(f"Costo total: ${stats['cost']:.6f}")
    
asyncio.run(test_all_models())
print("\nLLM Executor funcionando correctamente!")
