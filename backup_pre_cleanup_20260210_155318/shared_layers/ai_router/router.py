"""
NADAKKI AI SUITE - Intelligent AI Router
Router inteligente que selecciona el modelo óptimo según tarea, costo y calidad
"""
import os
import time
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from .models_config import (
    MODELS, ModelConfig, ModelProvider, TaskComplexity,
    TASK_MODEL_MAP, PRICING_PLANS, get_model_config, estimate_cost
)

logger = logging.getLogger("AIRouter")

class AIRouter:
    """
    Router inteligente que:
    1. Analiza la complejidad del prompt
    2. Considera el presupuesto del tenant
    3. Selecciona el modelo óptimo
    4. Implementa fallback en caso de error
    5. Trackea costos y uso
    """
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.deepseek_client = None
        self.grok_client = None
        self._init_clients()
        self.usage_tracker: Dict[str, Dict] = {}
        
    def _init_clients(self):
        """Inicializa los clientes de cada proveedor"""
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized")
            except ImportError:
                logger.warning("⚠️ OpenAI package not installed")
        
        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("✅ Anthropic client initialized")
            except ImportError:
                logger.warning("⚠️ Anthropic package not installed")
        
        # DeepSeek (usa API compatible con OpenAI)
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            try:
                from openai import OpenAI
                self.deepseek_client = OpenAI(
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com/v1"
                )
                logger.info("✅ DeepSeek client initialized")
            except ImportError:
                logger.warning("⚠️ DeepSeek requires OpenAI package")
        
        # Grok (xAI)
        grok_key = os.getenv("GROK_API_KEY")
        if grok_key:
            try:
                from openai import OpenAI
                self.grok_client = OpenAI(
                    api_key=grok_key,
                    base_url="https://api.x.ai/v1"
                )
                logger.info("✅ Grok client initialized")
            except ImportError:
                logger.warning("⚠️ Grok requires OpenAI package")
    
    def analyze_complexity(self, prompt: str, task_type: str = None) -> TaskComplexity:
        """Analiza la complejidad de un prompt"""
        prompt_lower = prompt.lower()
        word_count = len(prompt.split())
        
        # Indicadores de complejidad alta
        complex_indicators = [
            "estrategia", "strategy", "análisis", "analysis", "planificación",
            "planning", "decisión", "decision", "evaluar", "evaluate",
            "comparar", "compare", "profundo", "deep", "detallado", "detailed"
        ]
        
        # Indicadores de complejidad simple
        simple_indicators = [
            "resumir", "summarize", "clasificar", "classify", "extraer",
            "extract", "traducir", "translate", "listar", "list"
        ]
        
        # Calcular score de complejidad
        complex_score = sum(1 for indicator in complex_indicators if indicator in prompt_lower)
        simple_score = sum(1 for indicator in simple_indicators if indicator in prompt_lower)
        
        # Considerar longitud
        if word_count > 500:
            complex_score += 2
        elif word_count > 200:
            complex_score += 1
        
        # Determinar nivel
        if complex_score >= 3 or task_type in ["strategy", "analysis", "planning"]:
            return TaskComplexity.COMPLEX
        elif simple_score >= 2 or task_type in ["classification", "extraction", "faq"]:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MEDIUM
    
    def select_model(
        self,
        task_type: str,
        complexity: TaskComplexity = None,
        tenant_plan: str = "professional",
        prefer_speed: bool = False,
        prefer_quality: bool = False,
        max_cost: float = None
    ) -> str:
        """Selecciona el modelo óptimo según criterios"""
        
        # Obtener modelos permitidos por plan
        plan = PRICING_PLANS.get(tenant_plan, PRICING_PLANS["professional"])
        allowed_models = plan["allowed_models"]
        
        # Obtener modelos recomendados para la tarea
        recommended = TASK_MODEL_MAP.get(task_type, ["gpt-4o-mini"])
        
        # Filtrar por modelos permitidos
        candidates = [m for m in recommended if m in allowed_models]
        if not candidates:
            candidates = [plan["default_model"]]
        
        # Si hay preferencia de velocidad, ordenar por velocidad
        if prefer_speed:
            candidates.sort(key=lambda m: MODELS[m].speed, reverse=True)
        
        # Si hay preferencia de calidad, ordenar por calidad
        if prefer_quality:
            candidates.sort(key=lambda m: MODELS[m].quality, reverse=True)
        
        # Si hay límite de costo, filtrar
        if max_cost:
            candidates = [
                m for m in candidates 
                if estimate_cost(m, 1000, 500) <= max_cost
            ] or [candidates[0]]
        
        # Ajustar por complejidad
        if complexity == TaskComplexity.COMPLEX and "claude-sonnet" in allowed_models:
            if "claude-sonnet" in candidates:
                return "claude-sonnet"
            elif "gpt-4o" in candidates:
                return "gpt-4o"
        
        if complexity == TaskComplexity.SIMPLE:
            # Preferir el más económico
            candidates.sort(key=lambda m: MODELS[m].input_cost_per_1m)
        
        return candidates[0] if candidates else "gpt-4o-mini"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        task_type: str = "general",
        tenant_id: str = "default",
        tenant_plan: str = "professional",
        model_override: str = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Genera contenido usando el modelo óptimo
        
        Returns:
            Dict con: content, model_used, tokens, cost, latency_ms
        """
        start_time = time.time()
        
        # Analizar complejidad
        complexity = self.analyze_complexity(prompt, task_type)
        
        # Seleccionar modelo
        if model_override:
            model_name = model_override
        else:
            model_name = self.select_model(
                task_type=task_type,
                complexity=complexity,
                tenant_plan=tenant_plan,
                **kwargs
            )
        
        model_config = MODELS.get(model_name)
        if not model_config:
            model_name = "gpt-4o-mini"
            model_config = MODELS["gpt-4o-mini"]
        
        logger.info(f"🤖 Using model: {model_name} for task: {task_type} (complexity: {complexity.value})")
        
        # Intentar generar con fallback
        try:
            result = await self._call_model(
                model_name=model_name,
                model_config=model_config,
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
        except Exception as e:
            logger.warning(f"⚠️ Primary model {model_name} failed: {e}. Trying fallback...")
            # Fallback a gpt-4o-mini
            fallback_model = "gpt-4o-mini" if model_name != "gpt-4o-mini" else "deepseek"
            result = await self._call_model(
                model_name=fallback_model,
                model_config=MODELS[fallback_model],
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            result["fallback_used"] = True
            result["original_model"] = model_name
        
        # Calcular métricas
        latency_ms = int((time.time() - start_time) * 1000)
        result["latency_ms"] = latency_ms
        result["complexity"] = complexity.value
        result["task_type"] = task_type
        
        # Trackear uso
        self._track_usage(tenant_id, result)
        
        return result
    
    async def _call_model(
        self,
        model_name: str,
        model_config: ModelConfig,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Llama al modelo específico"""
        
        provider = model_config.provider
        model_id = model_config.model_id
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # OpenAI / GPT
        if provider == ModelProvider.OPENAI:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            response = self.openai_client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
        
        # Anthropic / Claude
        elif provider == ModelProvider.ANTHROPIC:
            if not self.anthropic_client:
                raise Exception("Anthropic client not initialized")
            system = system_prompt or "You are a helpful assistant."
            response = self.anthropic_client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
        
        # DeepSeek
        elif provider == ModelProvider.DEEPSEEK:
            if not self.deepseek_client:
                raise Exception("DeepSeek client not initialized")
            response = self.deepseek_client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
        
        # Grok
        elif provider == ModelProvider.GROK:
            if not self.grok_client:
                raise Exception("Grok client not initialized")
            response = self.grok_client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
        
        else:
            raise Exception(f"Unknown provider: {provider}")
        
        # Calcular costo
        cost = estimate_cost(model_name, input_tokens, output_tokens)
        
        return {
            "content": content,
            "model_used": model_name,
            "model_id": model_id,
            "provider": provider.value,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": cost,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _track_usage(self, tenant_id: str, result: Dict):
        """Trackea el uso por tenant"""
        if tenant_id not in self.usage_tracker:
            self.usage_tracker[tenant_id] = {
                "total_tokens": 0,
                "total_cost": 0,
                "calls": 0,
                "by_model": {}
            }
        
        tracker = self.usage_tracker[tenant_id]
        tracker["total_tokens"] += result.get("total_tokens", 0)
        tracker["total_cost"] += result.get("cost_usd", 0)
        tracker["calls"] += 1
        
        model = result.get("model_used", "unknown")
        if model not in tracker["by_model"]:
            tracker["by_model"][model] = {"tokens": 0, "cost": 0, "calls": 0}
        tracker["by_model"][model]["tokens"] += result.get("total_tokens", 0)
        tracker["by_model"][model]["cost"] += result.get("cost_usd", 0)
        tracker["by_model"][model]["calls"] += 1
    
    def get_usage(self, tenant_id: str) -> Dict:
        """Obtiene estadísticas de uso de un tenant"""
        return self.usage_tracker.get(tenant_id, {})
    
    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos disponibles (con cliente inicializado)"""
        available = []
        if self.openai_client:
            available.extend(["gpt-4o", "gpt-4o-mini"])
        if self.anthropic_client:
            available.extend(["claude-sonnet", "claude-haiku"])
        if self.deepseek_client:
            available.append("deepseek")
        if self.grok_client:
            available.append("grok")
        return available


# Instancia global del router
_router_instance = None

def get_router() -> AIRouter:
    """Obtiene la instancia singleton del router"""
    global _router_instance
    if _router_instance is None:
        _router_instance = AIRouter()
    return _router_instance

# Función de conveniencia para uso directo
async def generate(prompt: str, **kwargs) -> Dict[str, Any]:
    """Genera contenido usando el router inteligente"""
    router = get_router()
    return await router.generate(prompt, **kwargs)
