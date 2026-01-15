import sys
sys.path.insert(0, '.')
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents.shared_layers.executors.llm_executor import get_llm

llm = get_llm()
prompt = "Responde SOLO con un emoji de playa"

async def test():
    print("\n" + "="*60)
    print("   PRUEBA COMPLETA DE TODOS LOS MODELOS")
    print("="*60)
    
    print("\n[1/4] GPT-4o-mini (OpenAI)...")
    r1 = await llm.generate(prompt, model="gpt-4o-mini")
    print(f"       Resultado: {r1['content']}  |  Costo: ${r1['cost']:.6f}")
    
    print("\n[2/4] DeepSeek...")
    r2 = await llm.generate(prompt, model="deepseek-chat")
    print(f"       Resultado: {r2['content']}  |  Costo: ${r2['cost']:.6f}")
    
    print("\n[3/4] Claude Haiku (Anthropic)...")
    r3 = await llm.generate(prompt, model="claude-3-haiku-20240307")
    print(f"       Resultado: {r3['content']}  |  Costo: ${r3['cost']:.6f}")
    
    print("\n[4/4] Grok (xAI)...")
    r4 = await llm.generate(prompt, model="grok-beta")
    print(f"       Resultado: {r4['content']}  |  Costo: ${r4['cost']:.6f}")
    
    print("\n" + "="*60)
    print("   ESTADISTICAS TOTALES")
    print("="*60)
    stats = llm.get_stats()
    print(f"   Llamadas totales: {stats['calls']}")
    print(f"   Tokens totales: {stats['tokens']}")
    print(f"   Costo total: ${stats['cost']:.6f}")
    print("\n   Por modelo:")
    for model, data in stats['by_model'].items():
        print(f"      {model}: {data['calls']} calls, ${data['cost']:.6f}")
    print("="*60)

asyncio.run(test())
print("\n   TODOS LOS MODELOS FUNCIONANDO!")
print("="*60)
