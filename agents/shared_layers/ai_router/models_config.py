"""
NADAKKI AI SUITE - Models Configuration
Configuración de todos los modelos de IA disponibles con costos y capacidades
"""
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass

class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GROK = "grok"

class TaskComplexity(Enum):
    SIMPLE = "simple"      # FAQ, clasificación, extracción
    MEDIUM = "medium"      # Posts, emails, descripciones
    COMPLEX = "complex"    # Estrategia, análisis profundo
    CRITICAL = "critical"  # Decisiones de alto impacto

@dataclass
class ModelConfig:
    name: str
    provider: ModelProvider
    model_id: str
    input_cost_per_1m: float  # USD por 1M tokens
    output_cost_per_1m: float
    max_tokens: int
    speed: int  # 1-5, 5 = más rápido
    quality: int  # 1-5, 5 = mejor calidad
    best_for: list
    
# Configuración de todos los modelos disponibles
MODELS: Dict[str, ModelConfig] = {
    # === ECONÓMICOS (Alto volumen) ===
    "deepseek": ModelConfig(
        name="DeepSeek",
        provider=ModelProvider.DEEPSEEK,
        model_id="deepseek-chat",
        input_cost_per_1m=0.14,
        output_cost_per_1m=0.28,
        max_tokens=32000,
        speed=5,
        quality=3,
        best_for=["classification", "extraction", "faq", "batch_processing"]
    ),
    "gpt-4o-mini": ModelConfig(
        name="GPT-4o Mini",
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o-mini",
        input_cost_per_1m=0.15,
        output_cost_per_1m=0.60,
        max_tokens=128000,
        speed=5,
        quality=4,
        best_for=["posts", "emails", "descriptions", "summaries"]
    ),
    "claude-haiku": ModelConfig(
        name="Claude Haiku",
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-3-haiku-20240307",
        input_cost_per_1m=0.25,
        output_cost_per_1m=1.25,
        max_tokens=200000,
        speed=5,
        quality=4,
        best_for=["chat", "quick_responses", "translations"]
    ),
    
    # === BALANCEADOS (Calidad/Costo) ===
    "gpt-4o": ModelConfig(
        name="GPT-4o",
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o",
        input_cost_per_1m=2.50,
        output_cost_per_1m=10.00,
        max_tokens=128000,
        speed=4,
        quality=5,
        best_for=["content_creation", "analysis", "code", "complex_reasoning"]
    ),
    "claude-sonnet": ModelConfig(
        name="Claude Sonnet",
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-sonnet-4-20250514",
        input_cost_per_1m=3.00,
        output_cost_per_1m=15.00,
        max_tokens=200000,
        speed=4,
        quality=5,
        best_for=["strategy", "deep_analysis", "planning", "complex_decisions"]
    ),
    
    # === EXPERIMENTAL ===
    "grok": ModelConfig(
        name="Grok",
        provider=ModelProvider.GROK,
        model_id="grok-beta",
        input_cost_per_1m=5.00,
        output_cost_per_1m=15.00,
        max_tokens=131072,
        speed=4,
        quality=4,
        best_for=["creative", "unconventional", "real_time_info"]
    ),
}

# Mapeo de tareas a modelos recomendados
TASK_MODEL_MAP: Dict[str, list] = {
    # Tareas simples -> Modelos económicos
    "classification": ["deepseek", "gpt-4o-mini"],
    "extraction": ["deepseek", "gpt-4o-mini"],
    "faq": ["deepseek", "claude-haiku"],
    "translation": ["claude-haiku", "gpt-4o-mini"],
    
    # Tareas medias -> Modelos balanceados
    "social_post": ["gpt-4o-mini", "claude-haiku"],
    "email": ["gpt-4o-mini", "claude-haiku"],
    "blog_post": ["gpt-4o-mini", "gpt-4o"],
    "description": ["gpt-4o-mini", "deepseek"],
    "summary": ["gpt-4o-mini", "claude-haiku"],
    
    # Tareas complejas -> Modelos premium
    "strategy": ["claude-sonnet", "gpt-4o"],
    "analysis": ["gpt-4o", "claude-sonnet"],
    "planning": ["claude-sonnet", "gpt-4o"],
    "decision": ["claude-sonnet", "gpt-4o"],
    "code_generation": ["gpt-4o", "claude-sonnet"],
    
    # Tareas especiales
    "creative": ["grok", "gpt-4o"],
    "real_time": ["grok", "gpt-4o-mini"],
}

# Configuración de planes de precio
PRICING_PLANS = {
    "basic": {
        "name": "Básico",
        "price": 29,
        "default_model": "deepseek",
        "allowed_models": ["deepseek", "gpt-4o-mini"],
        "monthly_token_limit": 1_000_000,
        "premium_token_limit": 100_000,  # tokens en modelos premium
    },
    "professional": {
        "name": "Profesional", 
        "price": 99,
        "default_model": "gpt-4o-mini",
        "allowed_models": ["deepseek", "gpt-4o-mini", "claude-haiku", "gpt-4o"],
        "monthly_token_limit": 5_000_000,
        "premium_token_limit": 500_000,
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 299,
        "default_model": "gpt-4o-mini",
        "allowed_models": ["deepseek", "gpt-4o-mini", "claude-haiku", "gpt-4o", "claude-sonnet", "grok"],
        "monthly_token_limit": -1,  # ilimitado en económicos
        "premium_token_limit": 2_000_000,
    }
}

def get_model_config(model_name: str) -> ModelConfig:
    """Obtiene la configuración de un modelo"""
    return MODELS.get(model_name)

def get_models_for_task(task_type: str) -> list:
    """Obtiene modelos recomendados para un tipo de tarea"""
    return TASK_MODEL_MAP.get(task_type, ["gpt-4o-mini"])

def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Estima el costo de una llamada"""
    model = MODELS.get(model_name)
    if not model:
        return 0.0
    input_cost = (input_tokens / 1_000_000) * model.input_cost_per_1m
    output_cost = (output_tokens / 1_000_000) * model.output_cost_per_1m
    return round(input_cost + output_cost, 6)
