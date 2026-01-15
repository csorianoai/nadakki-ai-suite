import sys
sys.path.insert(0, '.')
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Reimportar para cargar cambios
import importlib
import agents.shared_layers.executors.llm_executor as llm_mod
importlib.reload(llm_mod)

llm_mod._llm = None
llm = llm_mod.get_llm()

prompt = "Responde SOLO con un emoji de playa"

async def test():
    print("\n" + "="*60)
    print("   PRUEBA FINAL - TODOS LOS MODELOS")
    print("="*60)
    
    print("\n[1/4] GPT-4o-mini...")
    r1 = await llm.generate(prompt, model="gpt-4o-mini")
    print(f"       {r1['content']}  |  ${r1['cost']:.6f}")
    
    print("\n[2/4] DeepSeek...")
    r2 = await llm.generate(prompt, model="deepseek-chat")
    print(f"       {r2['content']}  |  ${r2['cost']:.6f}")
    
    print("\n[3/4] Claude Haiku...")
    r3 = await llm.generate(prompt, model="claude-3-haiku-20240307")
    print(f"       {r3['content']}  |  ${r3['cost']:.6f}")
    
    print("\n[4/4] Grok-3...")
    r4 = await llm.generate(prompt, model="grok-3")
    print(f"       {r4['content']}  |  ${r4['cost']:.6f}")
    
    print("\n" + "="*60)
    stats = llm.get_stats()
    print(f"   TOTAL: {stats['calls']} llamadas | ${stats['cost']:.6f}")
    print("="*60)

asyncio.run(test())
print("\n   4/4 MODELOS FUNCIONANDO!")
