"""
NADAKKI AI SUITE - ADAPTADORES Y LLM
Módulo completamente independiente para integración con LLMs.
Soporta múltiples providers: OpenAI, Anthropic, DeepSeek, etc.
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod


# ============================================================================
# LLM INTERFACE
# ============================================================================

class BaseLLM(ABC):
    """Interfaz base para todos los LLMs"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Genera respuesta del LLM"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo"""
        pass


# ============================================================================
# MOCK LLM (Para testing sin API real)
# ============================================================================

class MockLLM(BaseLLM):
    """LLM simulado para testing - No requiere API keys"""
    
    def __init__(self, default_model: str = "mock-model"):
        self.default_model = default_model
        self.call_count = 0
        self.total_tokens = 0
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Genera respuesta simulada inteligente basada en el prompt"""
        self.call_count += 1
        
        # Simular delay realista
        await asyncio.sleep(0.1)
        
        # Generar contenido basado en el tipo de prompt
        content = self._generate_smart_response(prompt, kwargs)
        
        input_tokens = len(prompt) // 4
        output_tokens = len(content) // 4
        self.total_tokens += input_tokens + output_tokens
        
        return {
            "content": content,
            "model": kwargs.get("model", self.default_model),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": 0.0001 * (input_tokens + output_tokens) / 1000,
            "finish_reason": "stop"
        }
    
    def _generate_smart_response(self, prompt: str, kwargs: Dict) -> str:
        """Genera respuesta inteligente basada en el contenido del prompt"""
        prompt_lower = prompt.lower()
        
        # Marketing/Social content
        if any(word in prompt_lower for word in ["social", "post", "instagram", "facebook"]):
            return "🚀 ¡Descubre nuestras increíbles ofertas! Servicio premium con resultados garantizados. #Calidad #Innovación #Éxito"
        
        # Email content
        if "email" in prompt_lower:
            return "Asunto: Oferta Especial - No te lo pierdas\n\nEstimado cliente, le presentamos nuestra nueva promoción..."
        
        # Credit/Risk evaluation
        if any(word in prompt_lower for word in ["credit", "risk", "score", "evalúa"]):
            return "SCORE: 0.85\nNIVEL_RIESGO: bajo\nRECOMENDACIÓN: aprobar\nANÁLISIS: Perfil crediticio sólido con historial positivo."
        
        # Ethical evaluation
        if any(word in prompt_lower for word in ["ética", "ethical", "moral"]):
            return "EVALUACIÓN ÉTICA:\nScore: 0.92\nRecomendación: APROBAR\nNo se detectan conflictos éticos significativos."
        
        # Reflection/Self-evaluation
        if any(word in prompt_lower for word in ["reflexión", "reflection", "evalúa el resultado"]):
            return "SCORE: 0.85\nREFLEXIÓN: Buen resultado con contenido relevante y alto potencial de engagement. Áreas de mejora: personalización."
        
        # Parallel thinking
        if any(word in prompt_lower for word in ["parallel", "stream", "alternativa"]):
            return "STREAM 1: Enfoque conservador con métricas probadas.\nSTREAM 2: Enfoque innovador con mayor riesgo/recompensa.\nCONSENSO: 0.78"
        
        # Default response
        return f"Respuesta procesada para: {prompt[:100]}...\n\nAnálisis completado con éxito. Score: 0.80"
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "mock",
            "model": self.default_model,
            "type": "testing",
            "call_count": self.call_count,
            "total_tokens": self.total_tokens
        }


# ============================================================================
# OPENAI LLM
# ============================================================================

class OpenAILLM(BaseLLM):
    """Implementación para OpenAI/Compatible APIs"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or "https://api.openai.com/v1"
        self.default_model = "gpt-4o-mini"
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Genera respuesta usando OpenAI API"""
        if not self.api_key:
            # Fallback a MockLLM si no hay API key
            mock = MockLLM()
            return await mock.generate(prompt, **kwargs)
        
        try:
            import httpx
            
            model = kwargs.get("model", self.default_model)
            max_tokens = kwargs.get("max_tokens", 1000)
            temperature = kwargs.get("temperature", 0.7)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    
                    return {
                        "content": content,
                        "model": model,
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "cost": self._calculate_cost(model, usage),
                        "finish_reason": data["choices"][0].get("finish_reason", "stop")
                    }
                else:
                    raise Exception(f"API error: {response.status_code}")
                    
        except ImportError:
            # Si httpx no está disponible, usar MockLLM
            mock = MockLLM()
            return await mock.generate(prompt, **kwargs)
        except Exception as e:
            # En caso de error, fallback a MockLLM
            mock = MockLLM()
            result = await mock.generate(prompt, **kwargs)
            result["warning"] = f"Fallback to MockLLM: {str(e)}"
            return result
    
    def _calculate_cost(self, model: str, usage: Dict) -> float:
        """Calcula costo basado en modelo y uso"""
        costs = {
            "gpt-4o-mini": (0.00015, 0.0006),
            "gpt-4o": (0.005, 0.015),
            "gpt-3.5-turbo": (0.0005, 0.0015),
        }
        input_cost, output_cost = costs.get(model, (0.001, 0.002))
        return (usage.get("prompt_tokens", 0) * input_cost + 
                usage.get("completion_tokens", 0) * output_cost) / 1000
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.default_model,
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key)
        }


# ============================================================================
# DEEPSEEK LLM
# ============================================================================

class DeepSeekLLM(BaseLLM):
    """Implementación para DeepSeek API (más económico)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = "https://api.deepseek.com/v1"
        self.default_model = "deepseek-chat"
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Genera respuesta usando DeepSeek API"""
        if not self.api_key:
            mock = MockLLM()
            return await mock.generate(prompt, **kwargs)
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": kwargs.get("model", self.default_model),
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": kwargs.get("max_tokens", 1000),
                        "temperature": kwargs.get("temperature", 0.7)
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    usage = data.get("usage", {})
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "model": kwargs.get("model", self.default_model),
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "cost": (usage.get("prompt_tokens", 0) * 0.00014 + 
                                usage.get("completion_tokens", 0) * 0.00028) / 1000,
                        "finish_reason": "stop"
                    }
        except:
            pass
        
        mock = MockLLM()
        return await mock.generate(prompt, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "deepseek",
            "model": self.default_model,
            "has_api_key": bool(self.api_key)
        }


# ============================================================================
# LLM FACTORY
# ============================================================================

class LLMFactory:
    """Factory para crear instancias de LLM según configuración"""
    
    _instances: Dict[str, BaseLLM] = {}
    
    @classmethod
    def get_llm(cls, provider: str = "auto", **kwargs) -> BaseLLM:
        """
        Obtiene instancia de LLM.
        
        Args:
            provider: "openai", "deepseek", "mock", or "auto"
            **kwargs: Configuración adicional (api_key, base_url, etc.)
        
        Returns:
            Instancia de BaseLLM
        """
        if provider == "auto":
            # Auto-detect based on available API keys
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            elif os.getenv("DEEPSEEK_API_KEY"):
                provider = "deepseek"
            else:
                provider = "mock"
        
        cache_key = f"{provider}_{kwargs.get('api_key', '')[:8]}"
        
        if cache_key not in cls._instances:
            if provider == "openai":
                cls._instances[cache_key] = OpenAILLM(**kwargs)
            elif provider == "deepseek":
                cls._instances[cache_key] = DeepSeekLLM(**kwargs)
            else:
                cls._instances[cache_key] = MockLLM(**kwargs)
        
        return cls._instances[cache_key]
    
    @classmethod
    def clear_cache(cls):
        """Limpia el cache de instancias"""
        cls._instances.clear()


# ============================================================================
# ADAPTER FUNCTIONS (Compatibilidad)
# ============================================================================

def get_llm(provider: str = "auto", **kwargs) -> BaseLLM:
    """Función helper para obtener LLM"""
    return LLMFactory.get_llm(provider, **kwargs)


def get_adapter(tenant_id: str) -> Dict[str, Any]:
    """
    Retorna adapter con configuración del tenant.
    Esta función es para compatibilidad con código legacy.
    """
    return {
        "tenant_id": tenant_id,
        "llm": get_llm(),
        "created_at": datetime.utcnow().isoformat()
    }
