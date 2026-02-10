"""
NADAKKI AI SUITE - LLM Executor Unificado
Punto unico de entrada para TODOS los agentes
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

from .base_executor import GenerationRequest, GenerationResponse
from .providers import OpenAIExecutor, AnthropicExecutor, DeepSeekExecutor, GrokExecutor

class LLMExecutor:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized: return
        self.executors = {}
        self.stats = {"calls": 0, "tokens": 0, "cost": 0.0, "by_model": {}}
        self._init_executors()
        self._initialized = True
    
    def _init_executors(self):
        print("Inicializando LLM Executors...")
        if os.getenv("OPENAI_API_KEY"):
            self.executors["openai"] = OpenAIExecutor(os.getenv("OPENAI_API_KEY"))
            print("   OK OpenAI")
        if os.getenv("ANTHROPIC_API_KEY"):
            self.executors["anthropic"] = AnthropicExecutor(os.getenv("ANTHROPIC_API_KEY"))
            print("   OK Anthropic")
        if os.getenv("DEEPSEEK_API_KEY"):
            self.executors["deepseek"] = DeepSeekExecutor(os.getenv("DEEPSEEK_API_KEY"))
            print("   OK DeepSeek")
        if os.getenv("GROK_API_KEY"):
            self.executors["grok"] = GrokExecutor(os.getenv("GROK_API_KEY"))
            print("   OK Grok")
    
    def _get_executor(self, model: str):
        m = model.lower()
        if "gpt" in m: return self.executors.get("openai")
        if "claude" in m: return self.executors.get("anthropic")
        if "deepseek" in m: return self.executors.get("deepseek")
        if "grok" in m: return self.executors.get("grok")
        return self.executors.get("openai")
    
    async def generate(self, prompt: str, model: str = "gpt-4o-mini", system_prompt: str = None, max_tokens: int = 2000, temperature: float = 0.7, tenant_id: str = "default") -> Dict[str, Any]:
        executor = self._get_executor(model)
        if not executor: raise ValueError(f"No executor for: {model}")
        request = GenerationRequest(prompt=prompt, model=model, max_tokens=max_tokens, temperature=temperature, system_prompt=system_prompt)
        response = await executor.generate(request)
        self.stats["calls"] += 1
        self.stats["tokens"] += response.total_tokens
        self.stats["cost"] += response.cost_usd
        if model not in self.stats["by_model"]:
            self.stats["by_model"][model] = {"calls": 0, "tokens": 0, "cost": 0.0}
        self.stats["by_model"][model]["calls"] += 1
        self.stats["by_model"][model]["tokens"] += response.total_tokens
        self.stats["by_model"][model]["cost"] += response.cost_usd
        return {"content": response.content, "model": response.model_used, "tokens": response.total_tokens, "cost": response.cost_usd, "latency_ms": response.latency_ms, "tenant": tenant_id, "ts": datetime.utcnow().isoformat()}
    
    def get_stats(self): return self.stats
    def get_models(self):
        models = []
        if "openai" in self.executors: models.extend(["gpt-4o", "gpt-4o-mini"])
        if "anthropic" in self.executors: models.extend(["claude-sonnet-4-20250514", "claude-3-haiku-20240307"])
        if "deepseek" in self.executors: models.append("deepseek-chat")
        if "grok" in self.executors: models.append("grok-beta")
        return models

_llm = None
def get_llm():
    global _llm
    if _llm is None: _llm = LLMExecutor()
    return _llm

async def generate(prompt: str, **kwargs):
    return await get_llm().generate(prompt, **kwargs)
