import sys
sys.path.insert(0, '.')
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents.shared_layers.executors.llm_executor import get_llm

llm = get_llm()
prompt = "Responde SOLO con un emoji de playa"

async def test():
    print("\n" + "="*50)
    print("PRUEBA DE TODOS LOS MODELOS")
    print("="*50)
    
    print("\n[1] GPT-4o-mini...")
    r1 = await llm.generate(prompt, model="gpt-4o-mini")
    print(f"    Resultado: {r1['content']}  |  Costo: ${r1['cost']:.6f}")
    
    print("\n[2] DeepSeek...")
    r2 = await llm.generate(prompt, model="deepseek-chat")
    print(f"    Resultado: {r2['content']}  |  Costo: ${r2['cost']:.6f}")
    
    print("\n[3] Claude Haiku...")
    r3 = await llm.generate(prompt, model="claude-3-haiku-20240307")
    print(f"    Resultado: {r3['content']}  |  Costo: ${r3['cost']:.6f}")
    
    print("\n[4] Grok...")
    r4 = await llm.generate(prompt, model="grok-beta")
    print(f"    Resultado: {r4['content']}  |  Costo: ${r4['cost']:.6f}")
    
    print("\n" + "="*50)
    print("ESTADISTICAS TOTALES")
    print("="*50)
    stats = llm.get_stats()
    print(f"Llamadas: {stats['calls']}")
    print(f"Tokens: {stats['tokens']}")
    print(f"Costo total: ${stats['cost']:.6f}")
    print("\nPor modelo:")
    for model, data in stats['by_model'].items():
        print(f"  {model}: {data['calls']} calls, ${data['cost']:.6f}")

asyncio.run(test())
print("\n" + "="*50)
print("TODOS LOS MODELOS FUNCIONANDO!")
print("="*50)
