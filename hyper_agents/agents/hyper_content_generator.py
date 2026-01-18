"""
NADAKKI AI SUITE - HYPER CONTENT GENERATOR
Primer Hyper Agent - Generación de contenido marketing nivel 0.1%
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime

from ..core import (
    BaseHyperAgent, HyperAgentProfile, HyperAgentOutput, AutonomyLevel,
    ActionDef, ActionType, MemoryType
)


class HyperContentGenerator(BaseHyperAgent):
    """
    Hyper Agent nivel 0.1% para generación de contenido de marketing.
    
    Capacidades:
    - Generación de posts para redes sociales
    - Emails de marketing
    - Copy publicitario
    - Variaciones A/B testing
    """
    
    def __init__(self, tenant_id: str = "default"):
        profile = HyperAgentProfile(
            agent_id="hyper_content_generator",
            agent_name="Hyper Content Generator",
            description="Hyper Agent nivel 0.1% para generación de contenido",
            category="Content Creation",
            version="3.0.0",
            autonomy_level=AutonomyLevel.SEMI,
            default_model="gpt-4o-mini",
            fallback_model="deepseek-chat",
            max_tokens=1000,
            temperature=0.8,
            tenant_id=tenant_id,
            can_trigger_agents=["socialpostgeneratoria", "timingoptimizeria"],
            personality_traits=["creativo", "persuasivo", "adaptable", "analítico"]
        )
        super().__init__(profile)
        
        self.content_templates = {
            "social_post": "Post corto con emojis y hashtags",
            "email_subject": "Asunto de email atractivo",
            "ad_copy": "Copy publicitario convincente"
        }
    
    def get_system_prompt(self) -> str:
        """Retorna system prompt personalizado"""
        best_actions = self.rl_engine.get_best_actions("content_generation", 3)
        tips = "\n".join([f"- {a['action']}: conf={a['confidence']:.2f}" for a in best_actions]) if best_actions else ""
        
        return f"""Eres {self.profile.agent_name}, experto en marketing digital nivel elite.

PERSONALIDAD: {', '.join(self.profile.personality_traits)}

REGLAS:
1. Contenido original, nunca genérico
2. Adaptado a la plataforma
3. Call-to-action sutil
4. Emojis estratégicos (2-3)
5. Hashtags relevantes (2-3)
{f'APRENDIZAJES:{chr(10)}{tips}' if tips else ''}"""
    
    async def execute_task(
        self, 
        input_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Tuple[str, List[ActionDef]]:
        """Genera contenido usando el ciclo completo"""
        content_type = input_data.get("content_type", "social_post")
        topic = input_data.get("topic", "")
        platforms = input_data.get("platforms", ["facebook"])
        
        if not topic:
            raise ValueError("Se requiere 'topic'")
        
        # Usar contexto de pensamiento paralelo
        parallel = context.get("parallel_thoughts", {})
        consensus = parallel.get("consensus_level", 0.5)
        
        # Construir prompt
        prompt = f"""{self.get_system_prompt()}

Genera {content_type}:
TEMA: {topic}
PLATAFORMAS: {', '.join(platforms)}
CONSENSO PARALELO: {consensus:.2f}

Responde SOLO con el contenido final."""

        result = await self._generate(prompt)
        content = result.get("content", "").strip()
        
        if not content:
            raise ValueError("No se generó contenido")
        
        # Crear acciones
        actions = []
        if content_type == "social_post":
            actions.append(self.create_action(
                ActionType.PUBLISH_SOCIAL,
                {"content": content, "platforms": platforms},
                confidence=0.85 + (consensus * 0.1),
                reasoning=f"Generado con consenso {consensus:.2f}"
            ))
        
        # Guardar en memoria
        await self.memory.store(
            f"content_{datetime.utcnow().strftime('%H%M%S')}",
            {"topic": topic, "content": content[:150], "consensus": consensus},
            MemoryType.SHORT_TERM,
            0.6 + (consensus * 0.2),
            tags=[content_type] + platforms
        )
        
        # Actualizar RL
        self.rl_engine.update_policy("content_generation", content_type, True, consensus)
        
        return content, actions
    
    async def generate_variations(self, base_content: str, count: int = 3) -> List[str]:
        """Genera variaciones A/B"""
        prompt = f"""Genera {count} variaciones de:
"{base_content}"

Mantén el mensaje, varía el enfoque.
Responde numeradas (1., 2., 3.)"""

        result = await self._generate(prompt, temperature=0.9)
        text = result.get("content", "")
        
        variations = []
        for i in range(1, count + 1):
            if f"{i}." in text:
                start = text.find(f"{i}.") + len(f"{i}.")
                end = text.find(f"{i+1}.") if f"{i+1}." in text else len(text)
                var = text[start:end].strip()
                if var:
                    variations.append(var)
        
        return variations


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

async def hyper_generate_content(
    topic: str,
    content_type: str = "social_post",
    platforms: List[str] = None,
    tenant_id: str = "default"
) -> HyperAgentOutput:
    """
    Helper para generar contenido fácilmente.
    
    Args:
        topic: Tema del contenido
        content_type: Tipo de contenido
        platforms: Plataformas destino
        tenant_id: ID del tenant
    
    Returns:
        HyperAgentOutput con resultado
    """
    agent = HyperContentGenerator(tenant_id=tenant_id)
    return await agent.run({
        "topic": topic,
        "content_type": content_type,
        "platforms": platforms or ["facebook"]
    })


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 60)
        print("TEST: Hyper Content Generator")
        print("=" * 60)
        
        agent = HyperContentGenerator(tenant_id="sfrentals")
        print(f"\n🤖 {agent.profile.agent_name} v{agent.profile.version}")
        
        output = await agent.run({
            "topic": "Tours en bote por Miami - Verano 2026",
            "content_type": "social_post",
            "platforms": ["facebook", "instagram"]
        })
        
        print(f"\n✅ Éxito: {output.success}")
        print(f"📝 Contenido: {output.content}")
        print(f"🧠 Consenso: {output.parallel_thoughts.get('consensus_level', 0):.2f}" if output.parallel_thoughts else "")
        print(f"⚖️ Ética: {output.ethical_assessment.get('score', 0):.2f}" if output.ethical_assessment else "")
        print(f"🛡️ Seguridad: {output.safety_check.get('score', 0):.2f}" if output.safety_check else "")
        print(f"🎯 Self-score: {output.self_score:.2f}")
        print(f"⏱️ Tiempo: {output.execution_time_ms:.0f}ms")
        
        print("\n📊 Stats:", agent.get_full_stats())
        print("\n" + "=" * 60)
    
    asyncio.run(test())
