import sys
sys.path.insert(0, '.')
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents.shared_layers.executors.llm_executor import get_llm

llm = get_llm()
prompt = "Responde solo con UN emoji de playa"

async def test():
    print("\n[1] GPT-4o-mini...")
    r1 = await llm.generate(prompt, model="gpt-4o-mini")
    print(f"    {r1['content']} - ${r1['cost']:.6f}")
    
    print("\n[2] Claude Haiku...")
    r2 = await llm.generate(prompt, model="claude-3-haiku-20240307")
    print(f"    {r2['content']} - ${r2['cost']:.6f}")
    
    print("\n[3] Grok...")
    r3 = await llm.generate(prompt, model="grok-beta")
    print(f"    {r3['content']} - ${r3['cost']:.6f}")
    
    print("\n" + "="*40)
    stats = llm.get_stats()
    print(f"Total: {stats['calls']} llamadas, ${stats['cost']:.6f}")

asyncio.run(test())
print("\nTODOS LOS MODELOS FUNCIONAN!")
